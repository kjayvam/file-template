# check.sh·build.sh·check-template-modules.sh가 Docker로 실행할 때 함께 쓰는 설정입니다.
# 직접 실행하지 않고, project_root를 정한 스크립트에서 source 합니다.

# Docker 볼륨·검사 이미지 이름 접두사입니다. 새 프로젝트에서는 프로젝트 이름으로 바꿔 다른 프로젝트와 공유하지 않게 합니다.
volume_prefix="file-template"
# frontend/Dockerfile·개발 Compose와 같은 Node 22 계열 이미지입니다.
node_base_image="node:22-alpine"

rust_version() {
  sed -n 's/^channel *= *"\(.*\)"/\1/p' "$project_root/rust-toolchain.toml"
}

# 검사 도구를 설치한 로컬 이미지를 한 번만 만들고 재사용해 재실행 때 패키지를 내려받지 않습니다.
# 태그에 기본 이미지와 설치 명령의 체크섬을 넣으므로 버전이나 설치 내용이 바뀌면 새 이미지를 만듭니다.
# 사용: check_image 이름 기본이미지 "설치 명령" (결과 태그는 image 변수)
check_image() {
  local recipe
  recipe="$(printf 'FROM %s\nRUN %s' "$2" "$3")"
  image="$volume_prefix-check-$1:$(printf '%s' "$recipe" | cksum | cut -d ' ' -f 1)"
  if ! docker image inspect "$image" >/dev/null 2>&1; then
    printf '%s\n' "$recipe" | docker build --quiet --tag "$image" - >/dev/null
  fi
}

# check.sh와 build.sh가 같은 이미지를 쓰도록 설치 내용을 한곳에 둡니다.
use_rust_check_image() {
  check_image rust "rust:$(rust_version)-alpine" "apk add --no-cache bash && rustup component add rustfmt"
}

use_node_check_image() {
  check_image node "$node_base_image" "apk add --no-cache bash"
}
