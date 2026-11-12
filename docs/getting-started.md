# 시작하기

## 요구 사항

- 로컬 실행: Rust 1.99.1 (`cargo`, `rustfmt`), Node.js 22.12 이상(22 계열)과 npm
- 컨테이너 실행·검증: Docker Engine/Desktop과 Docker Compose v2
- 아래 명령은 별도 설명이 없으면 저장소 루트에서 실행합니다.

## 설치

```bash
rustup toolchain install
./scripts/setup.sh
```

인자 없는 `rustup toolchain install`은 루트의 `rust-toolchain.toml`에 지정된 Rust 버전과 `rustfmt`를 설치합니다(rustup 1.28 이상). `rustup show`는 상태만 보여 주며 설치하지 않습니다. `setup.sh`는 `.env`가 없을 때만 `.env.example`을 복사하고 프론트엔드 의존성을 `npm ci`로 설치합니다. 기존 `.env`를 덮어쓰지 않습니다. 로컬 백엔드는 `.env`를 자동 로드하지 않으며 기본 포트 8080을 사용합니다. 다른 포트를 쓰려면 `PORT`를 프로세스 환경 변수로 지정하세요.

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

Rust 포맷 검사, `cargo test --locked`(컴파일 포함), `npm test`, `npm run build`를 실행합니다. `backend/Dockerfile`·`docker/docker-compose.dev.yml`의 Rust 이미지 버전이 `rust-toolchain.toml`과 다르면 실패합니다. 도구가 없거나 검사가 실패하면 0이 아닌 종료 코드를 반환합니다. 빌드만 검사하려면 `./scripts/build.sh`를 사용합니다.

```bash
./scripts/check.sh --backend
./scripts/check.sh --frontend
./scripts/check.sh --docker
```

`--docker`는 Rust 1.99.1과 Node 22 컨테이너에서 같은 검사를 실행하며 프론트엔드 설치도 `npm ci`로 수행합니다. `.env`나 실행 중인 DB·백엔드는 필요하지 않습니다. Rust 빌드 산출물과 `node_modules`는 Docker 볼륨에 두므로 로컬 실행용 파일을 덮어쓰지 않습니다. 첫 실행에는 이미지·의존성 다운로드가 필요합니다. 테스트 파일 위치와 개별 명령은 [테스트 안내](../tests/README.md)를 참고하세요.

## 템플릿으로 새 프로젝트 시작하기

이 저장소를 복제해 새 프로젝트를 만들 때 아래 자리표시자와 템플릿 전용 내용을 정리합니다.

| 위치 | 정리할 내용 |
| --- | --- |
| `README.md`, `CLAUDE.md` 제목 | 템플릿 이름(`file-template`, `my-project`)을 프로젝트 이름으로 변경 |
| `.github/CODEOWNERS`, `.github/ISSUE_TEMPLATE/config.yml` | `@OWNER`, `OWNER/REPO`를 실제 사용자·저장소로 변경 |
| `SECURITY.md`, `CODE_OF_CONDUCT.md` | `<보안 담당 이메일>`, `<연락처 이메일>` 채우기 |
| `.github/FUNDING.yml` | 후원 링크가 없으면 파일 삭제 |
| `config/*.yml`, `.env.example`, `docker/docker-compose*.yml`, `docker/mcp/README.md` | 기본 이름 `my-project`, `my_project`와 DB 이름 변경 |
| `scripts/check.sh`, `scripts/check-template-modules.sh` | `volume_prefix`를 프로젝트 이름으로 변경. 다른 프로젝트와 Docker 검증용 빌드 산출물·`node_modules` 볼륨을 공유하지 않게 합니다 |
| `CHANGELOG.md` | 템플릿 이력을 지우고 `[Unreleased]`부터 다시 시작 |
| `migrations/0001_create_users.*` | PostgreSQL 예시입니다. 어느 DB에도 적용하기 전에 실제 스키마로 바꾸거나 삭제 |
| `scripts/deploy.sh`, `scripts/seed-db.sh` | 실패로 끝나는 자리표시자. 실제 명령으로 작성 |
| `external/README.md` | 템플릿 작성용 참고 자료 중 프로젝트와 무관한 항목 정리 |

선택형 AI 모듈을 쓰지 않으면 `templates/`, `scripts/template-module.py`, `scripts/verify-template-modules.py`, `scripts/check-template-modules.sh`, `.github/workflows/template-modules.yml`, AI 설계 문서(`docs/guides/ai-*.md`, `docs/adr/0001-optional-ai-extensions.md`)를 함께 지울 수 있습니다. 지운 뒤에는 `README.md`, `CLAUDE.md`, `docs/index.md`, `tests/README.md`, `.claude/rules/tests.md`의 관련 설명도 정리합니다.

Rust 버전을 올릴 때는 `rust-toolchain.toml`, `backend/Dockerfile`, `docker/docker-compose.dev.yml`을 함께 바꿉니다. 세 곳이 다르면 `check.sh`가 실패합니다. 문서의 버전 표기(`README.md`, `CLAUDE.md`, 이 문서, `templates/README.md`, `docs/docker/build-optimization.md`)도 같이 갱신합니다.
