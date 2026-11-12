#!/usr/bin/env python3
"""Exercise recipes in disposable projects; never install into the source checkout."""
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "scripts/template-module.py"
BASE_FILES = ["backend/Cargo.toml", "backend/Cargo.lock", "backend/src/lib.rs", "backend/src/main.rs", "backend/tests/health.rs"]


def execute(command, *, cwd, env=None, succeeds=True):
    result = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True)
    if (result.returncode == 0) != succeeds:
        raise RuntimeError(f"Unexpected exit {result.returncode}: {' '.join(map(str, command))}\n{result.stdout}\n{result.stderr}")
    return result


def fingerprint(project):
    return {p.relative_to(project).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in project.rglob("*") if p.is_file() and not p.is_symlink()}


def main():
    with tempfile.TemporaryDirectory(prefix="template-module-check-") as scratch:
        scratch = Path(scratch)
        project = scratch / "project"
        project.mkdir()
        for name in BASE_FILES:
            target = project / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        original = {name: (project / name).read_bytes() for name in BASE_FILES}
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
        verify("rag + ai-common installed; catalog absent", ["ai-common", "rag"])
        tool = scratch / "detached/scripts/template-module.py"
        tool.parent.mkdir(parents=True)
        shutil.copyfile(TOOL, tool)
        assert not (tool.parent.parent / "templates").exists()
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
