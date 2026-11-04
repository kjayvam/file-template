#!/usr/bin/env bash
set -euo pipefail

project_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

for tool in cargo npm; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "[오류] $tool 명령이 필요합니다. Docker 검증은 ./scripts/check.sh --docker 를 사용하세요." >&2
    exit 1
  fi
done

echo "=== 백엔드 컴파일 및 프론트엔드 빌드 ==="
(cd "$project_root/backend" && cargo check --locked)
(cd "$project_root/frontend" && npm run build)

echo "빌드 검사 완료."
