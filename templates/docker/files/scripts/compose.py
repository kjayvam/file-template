#!/usr/bin/env python3
"""설치한 Docker 실행 모듈의 Compose 파일만 조립합니다."""
import argparse
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('environment', choices=['dev', 'prod'])
    parser.add_argument('--dry-run', action='store_true')
    args, command = parser.parse_known_args()
    if command and command[0] == '--':
        command = command[1:]
    if not command:
        parser.error('up, down, config 등 Compose 명령을 지정하세요')
    subprocess.run([sys.executable, str(ROOT / 'scripts/modules.py'), 'check', '--project', str(ROOT)], check=True)
    state = json.loads((ROOT / '.template-modules.json').read_text())
    name = state.get('project', {}).get('name', 'my-project')
    if not re.fullmatch(r'[a-z][a-z0-9-]*', name):
        raise ValueError('프로젝트 이름이 올바르지 않습니다.')
    files = [f for info in state['modules'].values() for f in info.get('compose_files', {}).get(args.environment, [])]
    if not files:
        raise ValueError('Docker 실행 모듈이 없습니다. docker-rust·docker-react·docker-postgres 중 필요한 모듈을 추가하세요.')
    invocation = ['docker', 'compose', '--project-directory', str(ROOT), '--project-name', name]
    for file in files:
        path = ROOT / file
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(ROOT):
            raise ValueError(f'Compose 경로 확인 필요: {file}')
        invocation += ['-f', str(path)]
    invocation += command
    if args.dry_run:
        print(shlex.join(invocation))
    else:
        subprocess.run(invocation, cwd=ROOT, check=True)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f'[오류] {error}', file=sys.stderr)
        sys.exit(1)
