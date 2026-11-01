#!/usr/bin/env bash
set -euo pipefail

echo "=== 개발 환경을 세팅합니다 ==="

if [ ! -f .env ]; then
  echo ".env 파일이 없어 .env.example로부터 생성합니다."
  cp .env.example .env
fi

if command -v cargo >/dev/null 2>&1; then
  echo "Rust 툴체인이 확인되었습니다."
else
  echo "[참고] 로컬에 Rust(cargo)가 설치되어 있지 않으면 Docker를 통해 실행할 수 있습니다."
fi

if command -v npm >/dev/null 2>&1; then
  echo "프론트엔드 의존성을 설치합니다..."
  (cd frontend && npm install)
fi

echo "세팅 완료: docker compose -f docker/docker-compose.dev.yml up 으로 개발 환경을 시작하세요."
