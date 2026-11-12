#!/usr/bin/env bash
set -euo pipefail

project_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

require_tool() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "[오류] $1 명령이 필요합니다. 설치 후 재시도하거나 ./scripts/check.sh --docker 를 사용하세요." >&2
    exit 1
  fi
}

check_backend() {
  require_tool cargo
  (
    cd "$project_root/backend"
    cargo fmt -- --check
    # cargo test가 라이브러리·바이너리·테스트를 모두 컴파일하므로 별도 cargo check는 생략합니다.
    cargo test --locked
  )
}

check_frontend() {
  require_tool npm
  (
    cd "$project_root/frontend"
    npm test
    npm run build
  )
}

if [ "$#" -gt 1 ]; then
  echo "사용법: $0 [--backend|--frontend|--docker]" >&2
  exit 2
fi

case "${1:-}" in
  "")
    require_tool cargo
    require_tool npm
    check_backend
    check_frontend
    ;;
  --backend) check_backend ;;
  --frontend) check_frontend ;;
  --docker)
    require_tool docker
    # 빌드 산출물(target)과 node_modules는 Docker 볼륨에 두어 호스트용 빌드·의존성을 덮어쓰지 않습니다.
    docker run --rm \
      --mount "type=bind,src=$project_root/backend,dst=/workspace/backend" \
      --mount "type=bind,src=$project_root/scripts,dst=/workspace/scripts,readonly" \
      --mount type=volume,src=file-template-check-cargo,dst=/usr/local/cargo/registry \
      --mount type=volume,src=file-template-check-target,dst=/check-target \
      --env CARGO_TARGET_DIR=/check-target \
      rust:1.99.1-alpine \
      sh -ec 'apk add --no-cache bash musl-dev; rustup component add rustfmt; /workspace/scripts/check.sh --backend'
    docker run --rm \
      --mount "type=bind,src=$project_root/frontend,dst=/workspace/frontend" \
      --mount "type=bind,src=$project_root/scripts,dst=/workspace/scripts,readonly" \
      --mount type=volume,src=file-template-check-node-modules,dst=/workspace/frontend/node_modules \
      --workdir /workspace/frontend \
      node:22-alpine \
      sh -ec 'apk add --no-cache bash; npm ci; /workspace/scripts/check.sh --frontend'
    ;;
  *)
    echo "사용법: $0 [--backend|--frontend|--docker]" >&2
    exit 2
    ;;
esac

echo "검증 완료: ${1:-전체}"
