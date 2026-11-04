#!/usr/bin/env bash
set -euo pipefail

project_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
if [ "$#" -gt 1 ]; then
  echo "사용법: $0 [--docker]" >&2
  exit 2
fi
case "${1:-}" in
  "")
    if ! command -v python3 >/dev/null 2>&1 || ! command -v cargo >/dev/null 2>&1; then
      echo "[오류] Python 3.11+, Rust가 필요합니다. --docker 로 검증할 수 있습니다." >&2
      exit 1
    fi
    python3 "$project_root/scripts/verify-template-modules.py"
    ;;
  --docker)
    docker run --rm \
      --mount "type=bind,src=$project_root/backend,dst=/workspace/backend,readonly" \
      --mount "type=bind,src=$project_root/templates,dst=/workspace/templates,readonly" \
      --mount "type=bind,src=$project_root/scripts,dst=/workspace/scripts,readonly" \
      --mount type=volume,src=file-template-check-cargo,dst=/usr/local/cargo/registry \
      --mount type=volume,src=file-template-modules-target,dst=/module-target \
      --env CARGO_TARGET_DIR=/module-target \
      rust:1.99.1-alpine \
      sh -ec 'apk add --no-cache python3 musl-dev; rustup component add rustfmt; python3 /workspace/scripts/verify-template-modules.py'
    ;;
  *) echo "사용법: $0 [--docker]" >&2; exit 2 ;;
esac
