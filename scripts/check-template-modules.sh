#!/usr/bin/env bash
set -euo pipefail

project_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
# check.sh와 같은 Docker 볼륨 접두사·이미지 규칙을 사용해 Cargo 다운로드 캐시를 공유합니다.
. "$project_root/scripts/docker-common.sh"
if [ "$#" -gt 1 ]; then
  echo "사용법: $0 [--docker]" >&2
  exit 2
fi
case "${1:-}" in
  "")
    # template-module.py는 Python 3.11의 tomllib을, 검증은 cargo fmt(rustfmt)를 사용합니다.
    if ! command -v python3 >/dev/null 2>&1 \
      || ! python3 -c 'import sys; sys.exit(sys.version_info < (3, 11))' \
      || ! command -v cargo >/dev/null 2>&1 \
      || ! (cd "$project_root/backend" && cargo fmt --version) >/dev/null 2>&1; then
      echo "[오류] Python 3.11+, Rust(rustfmt 포함)가 필요합니다. --docker 로 검증할 수 있습니다." >&2
      exit 1
    fi
    python3 "$project_root/scripts/verify-template-modules.py"
    ;;
  --docker)
    if ! command -v docker >/dev/null 2>&1; then
      echo "[오류] docker 명령이 필요합니다." >&2
      exit 1
    fi
    check_image modules "rust:$(rust_version)-alpine" "apk add --no-cache python3 && rustup component add rustfmt"
    docker run --rm \
      --mount "type=bind,src=$project_root/backend,dst=/workspace/backend,readonly" \
      --mount "type=bind,src=$project_root/templates,dst=/workspace/templates,readonly" \
      --mount "type=bind,src=$project_root/scripts,dst=/workspace/scripts,readonly" \
      --mount "type=bind,src=$project_root/rust-toolchain.toml,dst=/workspace/rust-toolchain.toml,readonly" \
      --mount "type=bind,src=$project_root/CLAUDE.md,dst=/workspace/CLAUDE.md,readonly" \
      --mount "type=bind,src=$project_root/AGENTS.md,dst=/workspace/AGENTS.md,readonly" \
      --mount "type=volume,src=$volume_prefix-check-cargo,dst=/usr/local/cargo/registry" \
      --mount "type=volume,src=$volume_prefix-modules-target,dst=/module-target" \
      --env CARGO_TARGET_DIR=/module-target \
      "$image" \
      python3 /workspace/scripts/verify-template-modules.py
    ;;
  *) echo "사용법: $0 [--docker]" >&2; exit 2 ;;
esac
