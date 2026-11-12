#!/usr/bin/env bash
set -euo pipefail

project_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
toolchain_file="$project_root/rust-toolchain.toml"
# Docker 검증 볼륨 이름 접두사입니다. 새 프로젝트에서는 프로젝트 이름으로 바꿔 다른 프로젝트와 공유하지 않게 합니다.
volume_prefix="file-template"

require_tool() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "[오류] $1 명령이 필요합니다. 설치 후 재시도하거나 ./scripts/check.sh --docker 를 사용하세요." >&2
    exit 1
  fi
}

rust_version() {
  sed -n 's/^channel *= *"\(.*\)"/\1/p' "$toolchain_file"
}

# Dependabot 등이 한쪽만 올려 버전이 어긋나지 않도록 Docker 이미지의 Rust 버전을 rust-toolchain.toml과 비교합니다.
# --docker 내부 실행처럼 루트 파일이 마운트되지 않은 환경에서는 건너뜁니다.
check_rust_pins() {
  [ -f "$toolchain_file" ] || return 0
  local version file found
  version="$(rust_version)"
  for file in backend/Dockerfile docker/docker-compose.dev.yml; do
    found="$( (grep -oE 'rust:[0-9][0-9.]*' "$project_root/$file" || true) | sort -u | tr '\n' ' ')"
    if [ "$found" != "rust:$version " ]; then
      echo "[오류] $file의 Rust 이미지(${found:+${found% }}${found:-없음})가 rust-toolchain.toml의 $version과 다릅니다." >&2
      exit 1
    fi
  done
}

check_backend() {
  require_tool cargo
  check_rust_pins
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
    check_rust_pins
    # 빌드 산출물(target)과 node_modules는 Docker 볼륨에 두어 호스트용 빌드·의존성을 덮어쓰지 않습니다.
    docker run --rm \
      --mount "type=bind,src=$project_root/backend,dst=/workspace/backend" \
      --mount "type=bind,src=$project_root/scripts,dst=/workspace/scripts,readonly" \
      --mount "type=volume,src=$volume_prefix-check-cargo,dst=/usr/local/cargo/registry" \
      --mount "type=volume,src=$volume_prefix-check-target,dst=/check-target" \
      --env CARGO_TARGET_DIR=/check-target \
      "rust:$(rust_version)-alpine" \
      sh -ec 'apk add --no-cache bash musl-dev; rustup component add rustfmt; /workspace/scripts/check.sh --backend'
    docker run --rm \
      --mount "type=bind,src=$project_root/frontend,dst=/workspace/frontend" \
      --mount "type=bind,src=$project_root/scripts,dst=/workspace/scripts,readonly" \
      --mount "type=volume,src=$volume_prefix-check-node-modules,dst=/workspace/frontend/node_modules" \
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
