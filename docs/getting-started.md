# 시작하기

## 요구 사항

- 로컬 실행: Rust 1.99.1 (`cargo`, `rustfmt`), Node.js 22.12 이상(22 계열)과 npm
- 컨테이너 실행·검증: Docker Engine/Desktop과 Docker Compose v2
- 아래 명령은 별도 설명이 없으면 저장소 루트에서 실행합니다.

## 설치

```bash
rustup show
./scripts/setup.sh
```

`rustup show`는 루트의 `rust-toolchain.toml`에 지정된 도구를 준비합니다. `setup.sh`는 `.env`가 없을 때만 `.env.example`을 복사하고 프론트엔드 의존성을 `npm ci`로 설치합니다. 기존 `.env`를 덮어쓰지 않습니다. 로컬 백엔드는 `.env`를 자동 로드하지 않으며 기본 포트 8080을 사용합니다. 다른 포트를 쓰려면 `PORT`를 프로세스 환경 변수로 지정하세요.

## 로컬 실행

터미널 두 개에서 각각 실행합니다.

```bash
cd backend
cargo run --locked
```

```bash
cd frontend
npm run dev
```

- 프론트엔드: `http://localhost:5173`
- 백엔드: `http://localhost:8080/health`, `http://localhost:8080/api/v1/health`
- Vite는 `/api` 요청을 기본적으로 `http://localhost:8080`으로 전달합니다.
- 백엔드 주소를 바꾸려면 `VITE_API_BACKEND_URL=http://localhost:다른포트 npm run dev`를 사용합니다. 개발 Compose에서는 `http://backend:8080`이 지정됩니다.

## Docker 개발 환경

Rust와 Node가 없어도 실행할 수 있습니다. `.env`가 없다면 `.env.example`을 복사한 뒤 실행합니다.

```bash
docker compose --env-file .env -f docker/docker-compose.dev.yml up
```

현재 API는 DB를 사용하지 않으므로 `db` 서비스는 기본으로 실행되지 않습니다. PostgreSQL이 필요하면 `--profile postgres`를 붙입니다. Rust 코드를 바꾼 뒤에는 `restart backend`로 다시 컴파일합니다. 프로덕션 실행은 [Docker 단독 실행 가이드](docker/standalone.md)를 참고하세요.

## 검증

```bash
./scripts/check.sh
```

Rust 포맷 검사, `cargo test --locked`(컴파일 포함), `npm test`, `npm run build`를 실행합니다. 도구가 없거나 검사가 실패하면 0이 아닌 종료 코드를 반환합니다. 빌드만 검사하려면 `./scripts/build.sh`를 사용합니다.

```bash
./scripts/check.sh --backend
./scripts/check.sh --frontend
./scripts/check.sh --docker
```

`--docker`는 Rust 1.99.1과 Node 22 컨테이너에서 같은 검사를 실행하며 프론트엔드 설치도 `npm ci`로 수행합니다. `.env`나 실행 중인 DB·백엔드는 필요하지 않습니다. Rust 빌드 산출물과 `node_modules`는 Docker 볼륨에 두므로 로컬 실행용 파일을 덮어쓰지 않습니다. 첫 실행에는 이미지·의존성 다운로드가 필요합니다. 테스트 파일 위치와 개별 명령은 [테스트 안내](../tests/README.md)를 참고하세요.
