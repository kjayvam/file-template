#!/usr/bin/env bash
set -euo pipefail

project_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
. "$project_root/scripts/docker-common.sh"

usage() {
  echo "사용법: $0 [--docker]" >&2
  exit 2
}

require_tool() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "[오류] $1 명령이 필요합니다. 로컬 설치 없이 확인하려면 ./scripts/build.sh --docker 를 사용하세요." >&2
    exit 1
  fi
}

[ "$#" -le 1 ] || usage
case "${1:-}" in "" | --docker) ;; *) usage ;; esac

echo "=== 백엔드 컴파일 및 프론트엔드 빌드 ==="
case "${1:-}" in
  "")
    require_tool cargo
    require_tool npm
    (cd "$project_root/backend" && cargo check --locked)
    (cd "$project_root/frontend" && npm run build)
    ;;
  --docker)
    if ! command -v docker >/dev/null 2>&1; then
      echo "[오류] docker 명령이 필요합니다." >&2
      exit 1
    fi
    # check.sh --docker와 같은 검사 이미지·볼륨을 써서 캐시를 공유하고 호스트의 target·node_modules를 덮어쓰지 않습니다.
    use_rust_check_image
    docker run --rm \
      --mount "type=bind,src=$project_root/backend,dst=/workspace/backend,readonly" \
      --mount "type=volume,src=$volume_prefix-check-cargo,dst=/usr/local/cargo/registry" \
      --mount "type=volume,src=$volume_prefix-check-target,dst=/check-target" \
      --env CARGO_TARGET_DIR=/check-target \
      --workdir /workspace/backend \
      "$image" \
      cargo check --locked
    use_node_check_image
    docker run --rm \
      --mount "type=bind,src=$project_root/frontend,dst=/workspace/frontend" \
      --mount "type=volume,src=$volume_prefix-check-node-modules,dst=/workspace/frontend/node_modules" \
      --workdir /workspace/frontend \
      "$image" \
      sh -ec 'npm ci; npm run build'
    ;;
  *) usage ;;
esac

echo "빌드 검사 완료."
