#!/usr/bin/env python3
"""표준 모듈 카탈로그에서 프로젝트를 생성하고 모듈을 추가·제거합니다."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import tomllib

CATALOG = Path(__file__).resolve().parent.parent / "templates"
STATE = ".template-modules.json"


class Conflict(Exception):
    pass


def checked_path(root, name):
    rel = Path(name)
    if rel.is_absolute() or not rel.parts or any(
        p in ("..", ".git") or (p.startswith(".env") and p != ".env.example") or p.endswith(".env")
        for p in rel.parts
    ):
        raise Conflict(f"허용하지 않는 경로: {name}")
    path = root / rel
    for part in [path, *path.parents]:
        if part == root:
            break
        if part.is_symlink():
            raise Conflict(f"심볼릭 링크 경로는 수동 처리 필요: {name}")
        if part != path and part.exists() and not part.is_dir():
            raise Conflict(f"상위 경로가 디렉터리가 아닙니다: {name}")
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


def resolve_modules(names):
    """의존 관계를 위상 정렬하며, 한 파일도 쓰기 전에 순환을 거부합니다."""
    ordered, visiting = [], set()

    def visit(name):
        if name in visiting:
            raise Conflict(f"모듈 의존 순환: {name}")
        if name in ordered:
            return
        visiting.add(name)
        for dependency in manifest(name)["requires"]:
            visit(dependency)
        visiting.remove(name)
        ordered.append(name)

    for name in names:
        visit(name)
    return ordered


def current_bytes(root, name, changes):
    if name in changes:
        return changes[name][1]
    path = checked_path(root, name)
    if path.exists() and not path.is_file():
        raise Conflict(f"파일 경로가 디렉터리입니다: {name}")
    return path.read_bytes() if path.exists() else None


def change(root, name, after, changes):
    before = changes[name][0] if name in changes else current_bytes(root, name, {})
    changes[name] = (before, after)


def plan_add(root, module, state, changes=None):
    changes = {} if changes is None else changes
    if module in state["modules"]:
        raise Conflict(f"이미 적용됨: {module}")
    definition = manifest(module)
    missing = set(definition["requires"]) - state["modules"].keys()
    if missing:
        raise Conflict(f"먼저 추가할 모듈: {', '.join(sorted(missing))}")
    rust_package = definition.get("rust_package", "backend")
    rust_dependencies = definition["existing_rust_dependencies"]
    if rust_package is None and rust_dependencies:
        raise Conflict("Rust 의존성이 있는 모듈은 rust_package를 지정해야 합니다.")
    cargo = {}
    if rust_package is not None:
        data = current_bytes(root, "backend/Cargo.toml", changes)
        if data is None:
            raise Conflict("backend/Cargo.toml이 없습니다. backend-rust를 먼저 추가하세요.")
        cargo = tomllib.loads(data.decode())
        if cargo["package"]["name"] != rust_package:
            raise Conflict(f"이 모듈은 {rust_package} crate 이름 기준입니다. 테스트 import를 먼저 조정하세요.")
    for name, prefix in rust_dependencies.items():
        spec = cargo.get("dependencies", {}).get(name, "")
        version = spec.get("version", "") if isinstance(spec, dict) else spec
        if str(version).lstrip("^~=").split(".")[:len(prefix.split("."))] != prefix.split("."):
            raise Conflict(f"기존 의존성 확인 필요: {name} {prefix} 계열")
    owned = {}
    seeds = definition.get("seed_files", [])
    source = CATALOG / module / "files"
    actual = sorted(p.relative_to(source).as_posix() for p in source.rglob("*") if p.is_file() and p.name != ".DS_Store")
    if len(set(definition["owned_files"] + seeds)) != len(actual) or sorted(definition["owned_files"] + seeds) != actual:
        raise Conflict(f"원본 파일과 owned_files·seed_files 목록 불일치: {module}")
    project_name = state.get("project", {}).get("name", "my-project")
    claimed = {path for info in state["modules"].values()
               for path in [*info["files"], *info.get("seed_files", [])]}
    for name in actual:
        if name in claimed:
            raise Conflict(f"다른 모듈이 소유한 파일입니다: {name}")
        existing = current_bytes(root, name, changes)
        if existing is not None:
            if name in seeds:
                continue
            raise Conflict(f"기존 파일을 덮어쓰지 않습니다: {name}")
        data = checked_path(source.resolve(), name).read_bytes()
        # 명시된 파일만 치환합니다. 코드·잠금 파일·임의 사용자 자료에는 적용하지 않습니다.
        if name in definition.get("render_files", []):
            data = data.replace(b"__PROJECT_NAME__", project_name.encode())
        change(root, name, data, changes)
        if name not in seeds:
            owned[name] = digest(data)
    integrations = definition["integrations"]
    for item in integrations:
        name, anchor, block = item["path"], item["anchor"], item["block"]
        data = current_bytes(root, name, changes)
        if data is None:
            raise Conflict(f"연결 대상 파일이 없습니다: {name}")
        current = data.decode()
        if current.count(anchor) != 1 or block in current:
            raise Conflict(f"연결 지점을 유일하게 찾을 수 없습니다: {name}")
        replacement = block + anchor if item["position"] == "before" else anchor + block
        change(root, name, current.replace(anchor, replacement, 1).encode(), changes)
    state["modules"][module] = {
        "version": definition["version"], "requires": definition["requires"],
        "files": owned, "integrations": integrations,
        "seed_files": seeds, "compose_files": definition.get("compose_files", {}),
    }
    return changes


def plan_remove(root, module, state):
    if module not in state["modules"]:
        raise Conflict(f"적용되지 않은 모듈: {module}")
    dependents = [name for name, info in state["modules"].items() if module in info["requires"]]
    if dependents:
        raise Conflict(f"먼저 제거할 모듈: {', '.join(sorted(dependents))}")
    if module == "core":
        raise Conflict("core는 프로젝트 공통 계약입니다. 자동 제거하지 않습니다.")
    info = state["modules"][module]
    changes = {}
    for name, expected in info["files"].items():
        data = current_bytes(root, name, {})
        if data is None or digest(data) != expected:
            raise Conflict(f"변경되거나 없는 파일은 자동 제거하지 않습니다: {name}")
        change(root, name, None, changes)
    for item in reversed(info["integrations"]):
        name, block = item["path"], item["block"]
        data = current_bytes(root, name, changes)
        if data is None or data.decode().count(block) != 1:
            raise Conflict(f"연결 블록이 수정되었습니다. 수동 병합 필요: {name}")
        change(root, name, data.decode().replace(block, "", 1).encode(), changes)
    del state["modules"][module]
    return changes


def validate_project(root, state):
    if not state["modules"]:
        raise Conflict("설치 기록이 없습니다. init 또는 add로 모듈을 적용하세요.")
    owners = {}
    for module, info in state["modules"].items():
        missing = set(info["requires"]) - state["modules"].keys()
        if missing:
            raise Conflict(f"{module}의 의존 모듈 누락: {', '.join(sorted(missing))}")
        for name in [*info["files"], *info.get("seed_files", [])]:
            path = checked_path(root, name)
            if not path.is_file():
                raise Conflict(f"{module}의 표준 파일 누락: {name}")
            if name in owners:
                raise Conflict(f"파일 소유권 중복: {name}")
            owners[name] = module
        for item in info["integrations"]:
            path = checked_path(root, item["path"])
            if not path.is_file() or path.read_text().count(item["block"]) != 1:
                raise Conflict(f"{module}의 연결 블록 확인 필요: {item['path']}")
    print(f"통과: {len(state['modules'])}개 모듈의 의존 관계·표준 파일·연결 블록")


def atomic_write(path, data, mode):
    # 같은 디렉터리의 임시 파일을 교체하므로 쓰기 실패가 기존 파일을 잘라내지 않습니다.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".template-write-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
        temporary.chmod(mode)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def write_changes(root, changes):
    for name, (before, _) in changes.items():
        if current_bytes(root, name, {}) != before:
            raise Conflict(f"검토 중 파일이 변경되었습니다: {name}")
    completed, created_dirs = [], []
    try:
        for name, (before, after) in changes.items():
            path = checked_path(root, name)
            if current_bytes(root, name, {}) != before:
                raise Conflict(f"적용 중 파일이 변경되었습니다: {name}")
            for parent in reversed([path.parent, *path.parent.parents]):
                if parent == root or root in parent.parents:
                    if not parent.exists():
                        parent.mkdir()
                        created_dirs.append(parent)
            mode = path.stat().st_mode & 0o777 if before is not None else (0o755 if path.suffix == ".sh" else 0o644)
            if after is None:
                path.unlink()
            else:
                atomic_write(path, after, mode)
            completed.append((path, before, after, mode))
    except (OSError, Conflict):
        for path, before, after, mode in reversed(completed):
            current = path.read_bytes() if path.is_file() else None
            if current == after:
                if before is None:
                    path.unlink(missing_ok=True)
                else:
                    atomic_write(path, before, mode)
        for parent in reversed(created_dirs):
            try:
                parent.rmdir()
            except OSError:
                pass
        raise
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
    parser.add_argument("action", choices=["list", "init", "status", "check", "add", "remove"])
    parser.add_argument("module", nargs="?")
    parser.add_argument("--project", type=Path)
    parser.add_argument("--name", help="새 프로젝트 이름: 소문자·숫자·하이픈")
    parser.add_argument("--modules", nargs="*", default=[])
    parser.add_argument("--preset", choices=["minimal", "api", "web", "fullstack", "fullstack-docker", "knowledge"])
    parser.add_argument("--with-dependencies", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if args.action == "list":
        for path in sorted(CATALOG.glob("*/module.json")):
            item = manifest(path.parent.name)
            print(f"{item['id']} {item['version']} requires={','.join(item['requires']) or '-'}")
        return 0
    if args.project is None:
        parser.error("--project로 대상 프로젝트를 지정하세요")
    if args.project.is_symlink():
        raise Conflict("프로젝트 루트의 심볼릭 링크는 허용하지 않습니다.")
    root = args.project.absolute()
    root = root.resolve()
    if (CATALOG / "core/module.json").is_file() and root == CATALOG.parent.resolve() and args.action not in ("check", "status"):
        raise Conflict("카탈로그 원본에 설치할 수 없습니다. 별도 프로젝트 경로를 지정하세요.")
    if args.action == "init":
        if args.module:
            parser.error("init은 --modules 또는 --preset을 사용하세요")
        if not args.name or not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", args.name):
            parser.error("--name에 소문자로 시작하는 영문·숫자·하이픈 이름을 지정하세요")
        if root.exists() and (not root.is_dir() or any(root.iterdir())):
            raise Conflict("init 대상은 새 경로 또는 빈 디렉터리여야 합니다.")
        if not root.parent.is_dir():
            raise Conflict("init 대상의 상위 디렉터리를 먼저 만드세요.")
        presets = {
            "minimal": [], "api": ["backend-rust"], "web": ["frontend-react"],
            "fullstack": ["web-api"], "fullstack-docker": ["docker-web-api"],
            "knowledge": ["llm-wiki"],
        }
        names = resolve_modules(["core", *presets.get(args.preset, []), *args.modules])
        state = {"schema_version": 1, "project": {"name": args.name}, "modules": {}}
        changes = {}
        for name in names:
            plan_add(root, name, state, changes)
    else:
        if not root.is_dir():
            parser.error("기존 프로젝트 디렉터리를 지정하세요")
        if args.modules or args.preset or args.name:
            parser.error("--modules·--preset·--name은 init에서만 사용합니다")
        state = read_state(root)
        if args.action == "status":
            print(json.dumps(state, ensure_ascii=False, indent=2))
            return 0
        if args.action == "check":
            validate_project(root, state)
            return 0
        if not args.module:
            parser.error("모듈 이름이 필요합니다")
        if args.action == "add" and args.with_dependencies:
            if args.module in state["modules"]:
                raise Conflict(f"이미 적용됨: {args.module}")
            changes = {}
            for name in resolve_modules([args.module]):
                if name not in state["modules"]:
                    plan_add(root, name, state, changes)
        else:
            changes = (plan_add if args.action == "add" else plan_remove)(root, args.module, state)
    after = (json.dumps(state, ensure_ascii=False, indent=2) + "\n").encode() if state["modules"] else None
    change(root, STATE, after, changes)
    for name, (old, new) in sorted(changes.items()):
        print(f"{'추가' if old is None else '제거' if new is None else '연결 수정'}: {name}")
    if not args.dry_run:
        write_changes(root, changes)
    print("미리보기 완료" if args.dry_run else "완료: 대상 프로젝트에서 ./scripts/check.sh를 실행하세요")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (Conflict, OSError, ValueError, KeyError, TypeError) as error:
        print(f"[오류] {error}", file=sys.stderr)
        sys.exit(1)
