#!/usr/bin/env python3
"""Apply/remove reviewed file recipes to an explicitly selected template project."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import tomllib

CATALOG = Path(__file__).resolve().parent.parent / "templates"
STATE = ".template-modules.json"


class Conflict(Exception):
    pass


def checked_path(root, name):
    rel = Path(name)
    if rel.is_absolute() or not rel.parts or any(p in ("..", ".git") or p.startswith(".env") or p.endswith(".env") for p in rel.parts):
        raise Conflict(f"허용하지 않는 경로: {name}")
    path = root / rel
    for part in [path, *path.parents]:
        if part == root:
            break
        if part.is_symlink():
            raise Conflict(f"심볼릭 링크 경로는 수동 처리 필요: {name}")
    if not path.resolve().is_relative_to(root):
        raise Conflict(f"프로젝트 밖 경로: {name}")
    return path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_state(root):
    path = checked_path(root, STATE)
    state = json.loads(path.read_text()) if path.exists() else {"schema_version": 1, "modules": {}}
    if state.get("schema_version") != 1 or not isinstance(state.get("modules"), dict):
        raise Conflict("지원하지 않는 모듈 기록 형식")
    return state


def manifest(module):
    if not re.fullmatch(r"[a-z][a-z0-9-]*", module):
        raise Conflict("잘못된 모듈 이름")
    path = CATALOG / module / "module.json"
    if not path.is_file():
        raise Conflict(f"없는 모듈: {module}")
    value = json.loads(path.read_text())
    if value["id"] != module or value["schema_version"] != 1:
        raise Conflict("모듈 정의 불일치")
    return value


def plan_add(root, module, state):
    if module in state["modules"]:
        raise Conflict(f"이미 적용됨: {module}")
    definition = manifest(module)
    missing = set(definition["requires"]) - state["modules"].keys()
    if missing:
        raise Conflict(f"먼저 추가할 모듈: {', '.join(sorted(missing))}")
    cargo = tomllib.loads(checked_path(root, "backend/Cargo.toml").read_text())
    if cargo["package"]["name"] != "backend":
        raise Conflict("이 recipe는 backend crate 이름 기준입니다. 이름을 바꾼 프로젝트는 테스트 import를 먼저 조정하세요.")
    for name, prefix in definition["existing_rust_dependencies"].items():
        spec = cargo.get("dependencies", {}).get(name, "")
        version = spec.get("version", "") if isinstance(spec, dict) else spec
        parts = str(version).lstrip("^~=").split(".")
        expected = prefix.split(".")
        if parts[:len(expected)] != expected:
            raise Conflict(f"기존 의존성 확인 필요: {name} {prefix} 계열")
    changes = {}
    owned = {}
    source = CATALOG / module / "files"
    actual = sorted(p.relative_to(source).as_posix() for p in source.rglob("*") if p.is_file() and p.name != ".DS_Store")
    if sorted(definition["owned_files"]) != actual:
        raise Conflict("원본 파일과 owned_files 목록 불일치")
    for name in actual:
        target = checked_path(root, name)
        origin = checked_path(source.resolve(), name)
        if target.exists():
            raise Conflict(f"기존 파일을 덮어쓰지 않습니다: {name}")
        data = origin.read_bytes()
        changes[name] = (None, data)
        owned[name] = digest(data)
    integrations = definition["integrations"]
    for item in integrations:
        name, anchor, block = item["path"], item["anchor"], item["block"]
        path = checked_path(root, name)
        before = changes[name][0] if name in changes else path.read_bytes()
        current = changes[name][1].decode() if name in changes else before.decode()
        if current.count(anchor) != 1 or block in current:
            raise Conflict(f"연결 지점을 유일하게 찾을 수 없습니다: {name}")
        replacement = block + anchor if item["position"] == "before" else anchor + block
        changes[name] = (before, current.replace(anchor, replacement, 1).encode())
    state["modules"][module] = {"version": definition["version"], "requires": definition["requires"], "files": owned, "integrations": integrations}
    return changes


def plan_remove(root, module, state):
    if module not in state["modules"]:
        raise Conflict(f"적용되지 않은 모듈: {module}")
    dependents = [name for name, info in state["modules"].items() if module in info["requires"]]
    if dependents:
        raise Conflict(f"먼저 제거할 모듈: {', '.join(sorted(dependents))}")
    info = state["modules"][module]
    changes = {}
    for name, expected in info["files"].items():
        path = checked_path(root, name)
        if not path.is_file() or digest(path.read_bytes()) != expected:
            raise Conflict(f"변경되거나 없는 파일은 자동 제거하지 않습니다: {name}")
        changes[name] = (path.read_bytes(), None)
    for item in reversed(info["integrations"]):
        name, block = item["path"], item["block"]
        path = checked_path(root, name)
        before = changes[name][0] if name in changes else path.read_bytes()
        current = changes[name][1].decode() if name in changes else before.decode()
        if current.count(block) != 1:
            raise Conflict(f"연결 블록이 수정되었습니다. 수동 병합 필요: {name}")
        changes[name] = (before, current.replace(block, "", 1).encode())
    del state["modules"][module]
    return changes


def write_changes(root, changes):
    # Preflight all files before the first write, including installation metadata.
    for name, (before, _) in changes.items():
        path = checked_path(root, name)
        current = path.read_bytes() if path.exists() else None
        if current != before:
            raise Conflict(f"검토 중 파일이 변경되었습니다: {name}")
    completed = []
    try:
        for name, (before, after) in changes.items():
            path = checked_path(root, name)
            path.parent.mkdir(parents=True, exist_ok=True)
            completed.append((path, before, after))
            if after is None:
                path.unlink()
            else:
                path.write_bytes(after)
    except OSError:
        for path, before, after in reversed(completed):
            current = path.read_bytes() if path.exists() else None
            if current == after:
                if before is None:
                    path.unlink(missing_ok=True)
                else:
                    path.write_bytes(before)
        raise
    # Only prune empty parents of module-owned files; preserve user files and data.
    for name, (_, after) in changes.items():
        if after is None:
            parent = (root / name).parent
            while parent != root:
                try:
                    parent.rmdir()
                except OSError:
                    break
                parent = parent.parent


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["list", "status", "add", "remove"])
    parser.add_argument("module", nargs="?")
    parser.add_argument("--project", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if args.action == "list":
        for path in sorted(CATALOG.glob("*/module.json")):
            item = json.loads(path.read_text())
            print(f"{item['id']} {item['version']} requires={','.join(item['requires']) or '-'}")
        return 0
    if args.project is None or not args.project.is_dir():
        parser.error("--project 에 기존 프로젝트 디렉터리를 지정하세요")
    root = args.project.resolve()
    state = read_state(root)
    if args.action == "status":
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return 0
    if not args.module:
        parser.error("모듈 이름이 필요합니다")
    changes = (plan_add if args.action == "add" else plan_remove)(root, args.module, state)
    state_path = checked_path(root, STATE)
    before = state_path.read_bytes() if state_path.exists() else None
    after = (json.dumps(state, ensure_ascii=False, indent=2) + "\n").encode() if state["modules"] else None
    changes[STATE] = (before, after)
    for name, (old, new) in sorted(changes.items()):
        print(f"{'추가' if old is None else '제거' if new is None else '연결 수정'}: {name}")
    if not args.dry_run:
        write_changes(root, changes)
    print("미리보기 완료" if args.dry_run else "완료: 검증 명령을 실행하세요")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (Conflict, OSError, ValueError, KeyError) as error:
        print(f"[오류] {error}", file=sys.stderr)
        sys.exit(1)
