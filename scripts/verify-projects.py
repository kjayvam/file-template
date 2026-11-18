#!/usr/bin/env python3
"""임시 프로젝트에서 모듈 조립·충돌·실행 조합을 검증합니다."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / 'scripts/template-module.py'


def execute(command, *, succeeds=True, cwd=ROOT):
    result = subprocess.run([str(c) for c in command], cwd=cwd, text=True, capture_output=True)
    if (result.returncode == 0) != succeeds:
        raise RuntimeError(f"예상하지 않은 종료 {result.returncode}: {command}\n{result.stdout}\n{result.stderr}")
    return result


def fingerprint(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*') if p.is_file() and not p.is_symlink()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--docker', action='store_true')
    parser.add_argument('--structure-only', action='store_true')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('module_tool', TOOL)
    module_tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module_tool)
    assert (ROOT / 'templates/core/files/scripts/modules.py').read_bytes() == TOOL.read_bytes(), '배포 도구 사본이 원본과 다름'
    # Check every catalog source, including modules not in presets.
    all_modules = [p.parent.name for p in (ROOT / 'templates').glob('*/module.json')]
    module_tool.resolve_modules(all_modules)
    for name in all_modules:
        value = module_tool.manifest(name)
        source = ROOT / 'templates' / name / 'files'
        actual = {p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file() and p.name != '.DS_Store'}
        assert actual == set(value['owned_files'] + value.get('seed_files', [])), name
        assert len(actual) == len(value['owned_files'] + value.get('seed_files', [])), name
        assert set(value.get('render_files', [])) <= actual, name
        for paths in value.get('compose_files', {}).values():
            assert set(paths) <= set(value['owned_files']), name
            for path in paths:
                json.loads((source / path).read_text())
    with tempfile.TemporaryDirectory(prefix='template-assembly-') as temporary:
        scratch = Path(temporary).resolve()

        def cli(*command, succeeds=True):
            return execute([sys.executable, TOOL, *command], succeeds=succeeds)

        def init(path, *extra, succeeds=True):
            return cli('init', '--project', path, '--name', 'module-check', *extra, succeeds=succeeds)

        # Inject a real filesystem commit failure after one file was replaced.
        rollback = scratch / 'rollback'
        rollback.mkdir()
        existing = rollback / 'existing.txt'
        existing.write_bytes(b'original')
        existing.chmod(0o600)
        original_replace = module_tool.os.replace
        def fail_once(source, destination):
            if Path(destination).name == 'second.txt':
                raise OSError('검증용 파일 교체 실패')
            return original_replace(source, destination)
        module_tool.os.replace = fail_once
        try:
            try:
                module_tool.write_changes(rollback, {
                    'existing.txt': (b'original', b'changed'),
                    'new/second.txt': (None, b'new'),
                })
                raise AssertionError('쓰기 실패를 거부하지 않음')
            except OSError:
                pass
        finally:
            module_tool.os.replace = original_replace
        assert fingerprint(rollback) == {'existing.txt': b'original'}
        assert existing.stat().st_mode & 0o777 == 0o600
        assert not (rollback / 'new').exists()
        assert not list(rollback.glob('.template-write-*'))
        # Dependency cycles must fail before planning any files.
        original_catalog = module_tool.CATALOG
        fake = scratch / 'cyclic-catalog'
        for name, other in [('one', 'two'), ('two', 'one')]:
            (fake / name).mkdir(parents=True)
            (fake / name / 'module.json').write_text(json.dumps({
                'id': name, 'schema_version': 1, 'requires': [other],
            }))
        module_tool.CATALOG = fake
        try:
            try:
                module_tool.resolve_modules(['one'])
                raise AssertionError('의존 순환을 허용함')
            except module_tool.Conflict:
                pass
        finally:
            module_tool.CATALOG = original_catalog
        target = scratch / 'dry'
        init(target, '--preset', 'fullstack-docker', '--modules', 'rag', 'llm-wiki', '--dry-run')
        assert not target.exists(), 'dry-run이 디렉터리를 생성함'
        init(target, '--modules', 'unknown', succeeds=False)
        assert not target.exists(), '실패한 조립이 파일을 생성함'
        init(target, '--modules', 'backend-rust', 'frontend-react', succeeds=True)
        before = fingerprint(target)
        init(target, '--preset', 'minimal', succeeds=False)
        assert fingerprint(target) == before
        cli('add', 'core', '--project', target, succeeds=False)
        cli('remove', 'core', '--project', target, succeeds=False)
        # Plan all dependencies before writing: an integration conflict must not install dependencies.
        minimal = scratch / 'conflict'
        init(minimal)
        (minimal / 'frontend').mkdir()
        (minimal / 'frontend/src').write_text('상위 경로 충돌')
        before = fingerprint(minimal)
        cli('add', 'web-api', '--with-dependencies', '--project', minimal, succeeds=False)
        assert fingerprint(minimal) == before, '의존 모듈 일부만 설치됨'
        (minimal / 'frontend/src').unlink()
        outside = scratch / 'outside'
        outside.mkdir()
        (minimal / 'frontend/src').symlink_to(outside, target_is_directory=True)
        cli('add', 'frontend-react', '--with-dependencies', '--project', minimal, succeeds=False)
        assert not list(outside.iterdir()), '심볼릭 링크 밖에 기록됨'
        (minimal / 'frontend/src').unlink()
        # A late conflict in the final integration must leave the entire transaction unchanged.
        (minimal / '.env.example').write_text('사용자 환경 변수 양식\n')
        before = fingerprint(minimal)
        cli('add', 'docker-postgres', '--with-dependencies', '--project', minimal, succeeds=False)
        assert fingerprint(minimal) == before
        # User edits are accepted by structural validation, but protected on removal.
        cli('check', '--project', target)
        app = target / 'frontend/src/App.tsx'
        app.write_text(app.read_text() + '\n// 사용자 수정\n')
        cli('check', '--project', target)
        before = fingerprint(target)
        cli('remove', 'frontend-react', '--project', target, succeeds=False)
        assert fingerprint(target) == before
        print('통과: 카탈로그 계약, 초기화·dry-run·일괄 조립 충돌·쓰기 실패 복구·의존 순환·심볼릭 링크·사용자 수정 보호', flush=True)
        variants = [
            ('minimal', []), ('api', []), ('web', []), ('fullstack', []),
            ('knowledge', []), ('minimal', ['docker-rust']), ('minimal', ['docker-react']),
            ('minimal', ['docker-postgres']), ('fullstack-docker', ['docker-postgres', 'rag', 'llm-wiki', 'config-yaml']),
        ]
        for index, (preset, extras) in enumerate(variants):
            project = scratch / f'project {index}'
            command = ['--preset', preset]
            if extras:
                command += ['--modules', *extras]
            init(project, *command)
            state = json.loads((project / '.template-modules.json').read_text())
            modules = state['modules']
            cli('check', '--project', project)
            execute([sys.executable, project / 'scripts/modules.py', 'check', '--project', project])
            assert ('backend-rust' in modules) == (project / 'backend').is_dir()
            assert ('frontend-react' in modules) == (project / 'frontend').is_dir()
            assert '__PROJECT_NAME__' not in (project / 'README.md').read_text()
            assert 'module-check' in (project / 'CLAUDE.md').read_text()
            if 'frontend-react' in modules:
                assert '__PROJECT_NAME__' not in (project / 'frontend/src/App.tsx').read_text()
            if 'docker' in modules:
                for environment in ['dev', 'prod']:
                    result = execute([sys.executable, project / 'scripts/compose.py', environment, '--dry-run', 'config'])
                    assert '--project-name module-check' in result.stdout
                    if shutil.which('docker'):
                        config = execute([sys.executable, project / 'scripts/compose.py', environment, 'config', '--no-interpolate', '--format', 'json'])
                        document = json.loads(config.stdout[config.stdout.index('{'):])
                        expected = set()
                        for installed, service in [('docker-rust', 'backend'), ('docker-react', 'frontend'), ('docker-postgres', 'db')]:
                            if installed in modules:
                                expected.add(service)
                        assert set(document['services']) == expected
                        if 'docker-web-api' in modules:
                            assert 'backend' in document['services']['frontend']['depends_on']
            if 'docker-rust' in modules:
                pin_file = project / 'docker/compose.backend.dev.yml'
                original_pin = pin_file.read_text()
                pin_file.write_text(original_pin.replace('rust:1.99.1-alpine', 'rust:0.0.0-alpine'))
                execute([project / 'scripts/check.sh', '--backend'], succeeds=False)
                pin_file.write_text(original_pin)
            if args.structure_only:
                if preset in ['minimal', 'knowledge'] and not extras:
                    execute([project / 'scripts/check.sh'])
            else:
                # Run actual application checks for standalone apps and the complete connected app.
                if index in (0, 1, 2, 8):
                    result = execute([project / 'scripts/check.sh', *(['--docker'] if args.docker else [])])
                    print(result.stdout[-1300:], flush=True)
            if index == 8:
                # Remove in reverse dependency order; connections and env fragments must restore base files.
                for name in ['docker-web-api', 'docker-postgres', 'docker-react', 'docker-rust', 'web-api', 'rag', 'ai-common', 'llm-wiki', 'config-yaml', 'postgres', 'docker', 'frontend-react', 'backend-rust']:
                    cli('remove', name, '--project', project)
                    cli('check', '--project', project)
                assert set(json.loads((project / '.template-modules.json').read_text())['modules']) == {'core'}
                assert (project / 'knowledge/wiki/index.md').is_file()
                assert not (project / 'backend').exists()
                # Docker frontend checks create ignored dist/node_modules/tsbuildinfo, which are user files.
                assert not (project / 'frontend/src/App.tsx').exists()
                execute([project / 'scripts/check.sh'])
            print(f'통과: 조합 {index + 1}/{len(variants)} {preset} {extras}', flush=True)
        # Detached removal of an app with a shared integration restored first.
        clean = scratch / 'detached'
        init(clean, '--preset', 'fullstack')
        detached = clean / 'scripts/modules.py'
        execute([sys.executable, detached, 'remove', 'backend-rust', '--project', clean], succeeds=False)
        for name in ['web-api', 'frontend-react', 'backend-rust']:
            execute([sys.executable, detached, 'remove', name, '--project', clean])
        assert not (clean / 'backend').exists() and not (clean / 'frontend').exists()
        print('통과: 카탈로그 없는 앱 제거·의존 순서 보호·공통부 복원', flush=True)


if __name__ == '__main__':
    main()
