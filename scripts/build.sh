#!/usr/bin/env bash
set -euo pipefail

echo "=== 백엔드 및 프론트엔드 빌드 검사 ==="

if command -v cargo >/dev/null 2>&1; then
  echo "1. 백엔드(Rust) 컴파일 검사..."
  (cd backend && cargo check)
else
  echo "[스킵] 로컬에 cargo가 없어 Docker 빌드로 대체 권장"
fi

if command -v npm >/dev/null 2>&1; then
  echo "2. 프론트엔드(TypeScript/React) 빌드 검사..."
  (cd frontend && npm run build)
else
  echo "[스킵] 로컬에 npm이 없어 Docker 빌드로 대체 권장"
fi

echo "빌드 검사 완료."
