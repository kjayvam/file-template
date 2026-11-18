#!/usr/bin/env bash
set -euo pipefail
project_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
python3 "$project_root/scripts/modules.py" check --project "$project_root"
[ -f "$project_root/.env" ] || cp "$project_root/.env.example" "$project_root/.env"
if [ -f "$project_root/frontend/package.json" ]; then
  if command -v npm >/dev/null 2>&1; then (cd "$project_root/frontend" && npm ci)
  else echo "npm이 없습니다. Docker로 검사하거나 Node 22.22.2 이상(22 계열)을 설치하세요."; fi
fi
echo "준비 완료. README.md의 선택 모듈 실행 방법을 확인하세요."
