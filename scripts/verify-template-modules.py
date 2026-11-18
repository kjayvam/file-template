#!/usr/bin/env python3
"""Exercise recipes in disposable projects; never install into the source checkout."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "scripts/template-module.py"
# Copy the whole backend so files a project adds after cloning (modules, routes) still compile.
# Build output and secret files never enter the disposable project.
BACKEND_IGNORE = shutil.ignore_patterns("target", ".env", ".env.*", "*.env", ".DS_Store")
# The disposable project lives outside the checkout, so copy the pin or rustup falls back to its default toolchain.
OPTIONAL_FILES = ["rust-toolchain.toml", "CLAUDE.md", "AGENTS.md"]


def execute(command, *, cwd, env=None, succeeds=True):
    result = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True)
    if (result.returncode == 0) != succeeds:
        raise RuntimeError(f"Unexpected exit {result.returncode}: {' '.join(map(str, command))}\n{result.stdout}\n{result.stderr}")
    return result


def fingerprint(project):
    return {p.relative_to(project).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in project.rglob("*") if p.is_file() and not p.is_symlink()}


def verify_wiki():
    """Exercise data-preserving install/remove without any backend or Rust tools."""
    definition = json.loads((ROOT / "templates/llm-wiki/module.json").read_text())
    listing = execute([sys.executable, str(TOOL), "list"], cwd=ROOT)
    assert f"llm-wiki {definition['version']} requires=-" in listing.stdout
    with tempfile.TemporaryDirectory(prefix="template-wiki-check-") as scratch:
        scratch = Path(scratch)
        project = scratch / "project"
        project.mkdir()
        for name in ("CLAUDE.md", "AGENTS.md"):
            shutil.copyfile(ROOT / name, project / name)
        original = fingerprint(project)
        tool = TOOL
        checks = 0

        def module(action, *, dry=False, succeeds=True):
            nonlocal checks
            before = fingerprint(project)
            command = [sys.executable, str(tool), action, "llm-wiki", "--project", str(project)]
            if dry:
                command.append("--dry-run")
            result = execute(command, cwd=project, succeeds=succeeds)
            if dry or not succeeds:
                assert fingerprint(project) == before, "실패·미리보기 중 프로젝트가 변경됨"
            checks += 1
            return result

        module("add", dry=True)
        assert fingerprint(project) == original
        assert not (project / "knowledge").exists()
        instructions = project / "CLAUDE.md"
        initial_instructions = instructions.read_text()
        instructions.write_text(initial_instructions + "\n## 규칙\n")
        module("add", succeeds=False)
        assert not (project / "knowledge").exists()
        instructions.write_text(initial_instructions)

        collision = project / "knowledge/README.md"
        collision.mkdir(parents=True)
        module("add", succeeds=False)
        collision.rmdir()
        outside = scratch / "outside.md"
        outside.write_text("외부 자료 보존\n")
        collision.symlink_to(outside)
        module("add", succeeds=False)
        assert outside.read_text() == "외부 자료 보존\n"
        collision.unlink()

        module("add")
        module("add", succeeds=False)
        assert not (project / "backend").exists(), "위키가 Rust 프로젝트를 요구하면 안 됨"
        state = json.loads((project / ".template-modules.json").read_text())
        info = state["modules"]["llm-wiki"]
        assert info["seed_files"] == definition["seed_files"]
        assert not info["files"]
        assert instructions.read_text().count("<!-- BEGIN template:llm-wiki:instructions -->") == 1
        for name in info["seed_files"]:
            installed = project / name
            assert installed.read_bytes() == (ROOT / "templates/llm-wiki/files" / name).read_bytes()
            installed.write_text(installed.read_text() + "\n<!-- 프로젝트에서 수정한 지식 -->\n")
        for name in ("knowledge/raw/원본.md", "knowledge/wiki/topics/주제.md", "knowledge/.obsidian/app.json"):
            path = project / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("프로젝트 자료\n")
        knowledge = fingerprint(project / "knowledge")
        registered = instructions.read_text()
        instructions.write_text(registered.replace("<!-- END template:llm-wiki:instructions -->", "<!-- 수정한 연결 블록 -->"))
        module("remove", succeeds=False)
        instructions.write_text(registered + "\n프로젝트의 별도 지침\n")
        module("remove", dry=True)

        tool = scratch / "detached/scripts/template-module.py"
        tool.parent.mkdir(parents=True)
        shutil.copyfile(TOOL, tool)
        assert not (tool.parent.parent / "templates").exists()
        module("remove")
        assert not (project / ".template-modules.json").exists()
        assert fingerprint(project / "knowledge") == knowledge
        assert instructions.read_text() == initial_instructions + "\n프로젝트의 별도 지침\n"
        assert (project / "AGENTS.md").read_bytes() == (ROOT / "AGENTS.md").read_bytes()

        # Reattach existing knowledge without reverting even modified seed files.
        tool = TOOL
        missing = "templates/topic.md"
        (project / "knowledge" / missing).unlink()
        before_reattach = fingerprint(project / "knowledge")
        module("add", dry=True)
        assert fingerprint(project / "knowledge") == before_reattach
        result = module("add")
        assert "재사용: knowledge/wiki/index.md" in result.stdout
        assert "추가: knowledge/templates/topic.md" in result.stdout
        knowledge[missing] = hashlib.sha256((ROOT / "templates/llm-wiki/files/knowledge" / missing).read_bytes()).hexdigest()
        assert fingerprint(project / "knowledge") == knowledge
        status = execute([sys.executable, str(tool), "status", "--project", str(project)], cwd=project)
        assert "llm-wiki" in json.loads(status.stdout)["modules"]
        module("remove")
        assert fingerprint(project / "knowledge") == knowledge
        assert not (project / ".template-modules.json").exists()
        print(f"통과: 위키 단독 설치·제거·재추가, 자료 보존, 카탈로그 없는 제거, 충돌·미리보기 {checks}회", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wiki-only", action="store_true", help="Rust 없이 LLM Wiki 수명주기만 검사")
    args = parser.parse_args()
    verify_wiki()
    if args.wiki_only:
        return
    with tempfile.TemporaryDirectory(prefix="template-module-check-") as scratch:
        scratch = Path(scratch)
        project = scratch / "project"
        project.mkdir()
        shutil.copytree(ROOT / "backend", project / "backend", ignore=BACKEND_IGNORE)
        for name in OPTIONAL_FILES:
            if (ROOT / name).is_file():
                shutil.copyfile(ROOT / name, project / name)
        original = {p.relative_to(project).as_posix(): p.read_bytes() for p in project.rglob("*") if p.is_file()}
        env = os.environ.copy()
        env.setdefault("CARGO_TARGET_DIR", str(scratch / "target"))
        checks = 0
        tool = TOOL

        def module(action, name, succeeds=True, dry=False):
            nonlocal checks
            before = fingerprint(project)
            command = [sys.executable, str(tool), action, name, "--project", str(project)]
            if dry:
                command.append("--dry-run")
            result = execute(command, cwd=project, succeeds=succeeds)
            if not succeeds or dry:
                assert fingerprint(project) == before, "Rejected operation/dry run changed files"
                checks += 1
            return result

        def verify(label, installed):
            expected = 200 if "rag" in installed else 404
            # The probe is only a lifecycle test fixture, not installed application code.
            (project / "backend/tests/lifecycle_probe.rs").write_text(f'''use axum::{{body::Body, http::Request}};
use tower::ServiceExt;

#[tokio::test]
async fn selected_modules_register_only_their_routes() {{
    let response = backend::app()
        .oneshot(
            Request::builder()
                .method("POST")
                .uri("/api/ai/v1/query")
                .header("content-type", "application/json")
                .body(Body::from(r#"{{"question":"로그 보관 기간은 7일입니다."}}"#))
                .unwrap(),
        )
        .await
        .unwrap();
    assert_eq!(response.status().as_u16(), {expected});
}}
''')
            backend = project / "backend"
            execute(["cargo", "fmt", "--", "--check"], cwd=backend, env=env)
            result = execute(["cargo", "test", "--locked", "--quiet"], cwd=backend, env=env)
            totals = [int(n) for n in re.findall(r"test result: ok\. (\d+) passed", result.stdout)]
            assert sum(totals) > 0, "No tests executed"
            assert not (project / "templates").exists(), "Runtime must not depend on catalog"
            print(f"PASS {label}: fmt, {sum(totals)} Rust tests (includes lifecycle probe)", flush=True)

        verify("base", [])
        module("add", "rag", succeeds=False)
        module("add", "ai-common", dry=True)
        module("add", "ai-common")
        module("add", "ai-common", succeeds=False)
        verify("ai-common installed", ["ai-common"])

        collision = project / "backend/src/features/ai/rag/mod.rs"
        collision.parent.mkdir(parents=True)
        collision.write_text("// existing project file\n")
        module("add", "rag", succeeds=False)
        collision.unlink()
        outside = scratch / "outside.txt"
        outside.write_text("external content")
        collision.symlink_to(outside)
        module("add", "rag", succeeds=False)
        assert outside.read_text() == "external content"
        collision.unlink()

        module("add", "rag")
        module("remove", "ai-common", succeeds=False)
        module("add", "llm-wiki")
        verify("rag + ai-common + llm-wiki installed; catalog absent", ["ai-common", "rag", "llm-wiki"])
        tool = scratch / "detached/scripts/template-module.py"
        tool.parent.mkdir(parents=True)
        shutil.copyfile(TOOL, tool)
        assert not (tool.parent.parent / "templates").exists()
        wiki_index = project / "knowledge/wiki/index.md"
        wiki_index.write_text("# 프로젝트에서 축적한 지식\n")
        backend_before = fingerprint(project / "backend")
        module("remove", "llm-wiki")
        assert wiki_index.read_text() == "# 프로젝트에서 축적한 지식\n"
        assert fingerprint(project / "backend") == backend_before
        assert set(json.loads((project / ".template-modules.json").read_text())["modules"]) == {"ai-common", "rag"}
        owned = project / "backend/src/features/ai/rag/chunk.rs"
        unchanged = owned.read_bytes()
        owned.write_bytes(unchanged + b"\n// project customization\n")
        module("remove", "rag", succeeds=False)
        owned.write_bytes(unchanged)

        library = project / "backend/src/lib.rs"
        valid = library.read_text()
        library.write_text(valid.replace(".merge(rag::http::demo_router())", ".merge(rag::http::demo_router()) /* customized */"))
        module("remove", "rag", succeeds=False)
        library.write_text(valid + "\n// unrelated project customization\n")
        kept = project / "var/ai/keep.txt"
        kept.parent.mkdir(parents=True)
        kept.write_text("project data must survive module removal")
        notes = project / "backend/src/features/ai/rag/project-notes.txt"
        notes.write_text("unowned project file")

        module("remove", "rag", dry=True)
        module("remove", "rag")
        assert not (project / "backend/tests/ai_rag.rs").exists()
        verify("rag removed; common remains", ["ai-common"])
        module("remove", "ai-common")
        verify("all modules removed; base restored", [])

        for name, data in original.items():
            expected = data + b"\n// unrelated project customization\n" if name == "backend/src/lib.rs" else data
            assert (project / name).read_bytes() == expected, name
        assert not (project / ".template-modules.json").exists()
        assert not (project / "backend/src/features/ai/common").exists()
        assert kept.read_text() == "project data must survive module removal"
        assert notes.read_text() == "unowned project file"
        print(f"PASS {checks} refusal/dry-run checks; shared changes, user files and data preserved; manifests/lock restored", flush=True)


if __name__ == "__main__":
    main()
