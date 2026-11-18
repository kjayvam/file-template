#!/usr/bin/env python3
"""설치 기록에 있는 앱만 검사합니다. 생성된 프로젝트는 카탈로그가 필요 없습니다."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parent.parent


def run(command, **kwargs):
    subprocess.run(command, check=True, **kwargs)


def tool(name):
    if shutil.which(name) is None:
        raise RuntimeError(f"{name} 명령이 필요합니다. --docker 또는 로컬 도구 설치를 확인하세요.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--docker', action='store_true')
    parser.add_argument('--build', action='store_true')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--backend', action='store_true')
    group.add_argument('--frontend', action='store_true')
    args = parser.parse_args()
    run([sys.executable, str(ROOT / 'scripts/modules.py'), 'check', '--project', str(ROOT)])
    state = json.loads((ROOT / '.template-modules.json').read_text())
    installed = state['modules']
    backend = 'backend-rust' in installed and not args.frontend
    frontend = 'frontend-react' in installed and not args.backend
    if (args.backend and not backend) or (args.frontend and not frontend):
        raise RuntimeError('요청한 앱 모듈이 설치돼 있지 않습니다.')
    if args.docker and (backend or frontend):
        tool('docker')
    if backend:
        rust = tomllib.loads((ROOT / 'rust-toolchain.toml').read_text())['toolchain']['channel']
        if 'docker-rust' in installed:
            dockerfile = (ROOT / 'backend/Dockerfile').read_text()
            dev = (ROOT / 'docker/compose.backend.dev.yml').read_text()
            for source in (dockerfile, dev):
                if set(re.findall(r'rust:([0-9.]+)', source)) != {rust}:
                    raise RuntimeError('Rust 도구 버전과 Docker 이미지 버전이 다릅니다.')
        if not args.docker:
            tool('cargo')
            if not args.build:
                run(['cargo', 'fmt', '--', '--check'], cwd=ROOT / 'backend')
            run(['cargo', 'check' if args.build else 'test', '--locked'], cwd=ROOT / 'backend')
    if frontend and not args.docker:
        tool('npm')
        if not args.build:
            run(['npm', 'test'], cwd=ROOT / 'frontend')
        run(['npm', 'run', 'build'], cwd=ROOT / 'frontend')
    if args.docker and (backend or frontend):
        name = state.get('project', {}).get('name', 'my-project')
        if not re.fullmatch(r'[a-z][a-z0-9-]*', name):
            raise RuntimeError('설치 기록의 프로젝트 이름이 올바르지 않습니다.')

        def image(kind, base, packages):
            recipe = f'FROM {base}\nRUN {packages}\n'
            tag = f'template-tools-{kind}:{hashlib.sha256(recipe.encode()).hexdigest()[:12]}'
            exists = subprocess.run(['docker', 'image', 'inspect', tag], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if exists.returncode:
                run(['docker', 'build', '--quiet', '-t', tag, '-'], input=recipe, text=True)
            return tag

        if backend:
            tag = image('rust', f'rust:{rust}-alpine', 'rustup component add rustfmt')
            command = 'cargo check --locked' if args.build else 'cargo fmt -- --check && cargo test --locked'
            run(['docker', 'run', '--rm',
                 '--mount', f'type=bind,src={ROOT / "backend"},dst=/app,readonly',
                 '--mount', f'type=volume,src={name}-check-cargo,dst=/usr/local/cargo/registry',
                 '--mount', f'type=volume,src={name}-check-target,dst=/target',
                 '-e', 'CARGO_TARGET_DIR=/target', '-w', '/app', tag, 'sh', '-ec', command])
        if frontend:
            command = 'npm ci && ' + ('' if args.build else 'npm test && ') + 'npm run build'
            run(['docker', 'run', '--rm',
                 '--mount', f'type=bind,src={ROOT / "frontend"},dst=/app',
                 '--mount', f'type=volume,src={name}-check-node-modules,dst=/app/node_modules',
                 '-w', '/app', 'node:22-alpine', 'sh', '-ec', command])
    print('완료: 선택 모듈 빌드' if args.build else '완료: 선택 모듈 구조·테스트·빌드')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f'[오류] {error}', file=sys.stderr)
        sys.exit(1)
