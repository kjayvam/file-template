# Changelog

[Keep a Changelog](https://keepachangelog.com/ko/1.1.0/) 형식을 따릅니다.

## [Unreleased]

### Added
- 프로젝트 초기 폴더 구조
- ai-common·rag 선택형 모듈 원본과 추가·제거 도구(`scripts/template-module.py`), 임시 프로젝트 수명주기 검증
- 빌드 컨텍스트별 `.dockerignore`(backend, frontend), Dependabot의 cargo·npm·docker·docker-compose 갱신, CodeQL의 Rust·Actions 분석
- `check.sh`의 Docker 이미지·`rust-toolchain.toml` Rust 버전 일치 검사, 새 프로젝트 시작 시 정리할 자리표시자 목록(`docs/getting-started.md`)

### Changed
- 서버형 DB(`db`)는 `--profile postgres`로만 실행하고, 앱 데이터(`app-data`)와 PostgreSQL 데이터(`pg-data`) 볼륨을 분리
- `check.sh --docker`와 개발 Compose의 Rust 빌드 산출물·`node_modules`를 Docker 볼륨으로 분리
- 백엔드 이미지를 root가 아닌 사용자로 실행하고 SIGTERM에 정상 종료
- 사용하지 않는 Rust 의존성(dotenvy, tower-http, chrono serde feature) 제거
- Release 워크플로가 CI를 재사용하고 쓰기 권한을 쓰지 않도록 변경
- MCP 예시를 보관된 `@modelcontextprotocol/server-postgres` 대신 특정 패키지에 묶이지 않는 형태로 변경, `ROADMAP.md` 최소 양식 작성, 빈 `examples/` 제거
- rag 데모 라우트가 백엔드가 열린 모든 곳에서 접근된다는 실제 동작으로 문서 수정
- 검사 스크립트의 Rust 이미지 버전을 `rust-toolchain.toml`에서 읽고 Docker 볼륨 접두사를 한 변수로 모음
- 백엔드 런타임 이미지 alpine 3.24, GitHub Actions checkout v7, 프론트엔드 TypeScript 7.0.2로 갱신
- Dependabot이 react·react-dom·타입 패키지와 vite·@vitejs/plugin-react를 한 PR로 묶고, Node 이미지의 22 계열 밖 major 갱신은 제안하지 않음
- 개발 Compose의 `cargo run`도 `--locked`로 잠금 파일을 사용
- axum 0.8.9, vite 8·@vitejs/plugin-react 6, react·react-dom 19로 갱신하고 rag 모듈의 기존 의존성 계열을 axum 0.8로 변경
- 프로덕션 Compose가 백엔드 8080 포트를 호스트에 열지 않고 Nginx `/api/` 프록시로만 접근, frontend 런타임 이미지를 `nginx:1.31-alpine`으로 고정
- `vite.config.ts`·`vitest.config.ts`를 `tsconfig.node.json`과 `@types/node` 22로 타입 검사
- jsdom 31.0.1로 갱신하고 jsdom이 요구하는 Node 하한에 맞춰 `engines`와 문서의 Node 요구 사항을 22.22.2 이상(22 계열)으로 변경. 시작하기에 Node 버전 변경 시 함께 바꿀 파일 목록, 외부 자료에 jsdom 추가
- @testing-library/jest-dom 7.0.1로 갱신, Dependabot이 `@types/node`의 22 계열 밖 major 갱신은 제안하지 않음
- 새 프로젝트 자리표시자 목록에 `LICENSE`·`ROADMAP.md` 추가, README 폴더 표에 `.claude/`, 외부 자료에 checkout·codeql-action·cargo-chef 추가
- Dependabot이 PostgreSQL 이미지의 major 갱신은 제안하지 않음(기존 `pg-data` 볼륨과 호환되지 않음)
- GitHub Actions를 커밋 SHA와 버전 주석으로 고정하고 CI에 Rust 빌드 캐시(`Swatinem/rust-cache`) 추가
- Nginx가 모든 응답에 `X-Content-Type-Options`·`X-Frame-Options`·`Referrer-Policy` 보안 헤더를 보냄
- ADR-0001 상태를 채택으로 변경(ai-common·rag 구현, 나머지 모듈은 제안), DB 가이드에 인라인 `UNIQUE`의 제약 이름 안내 추가
- 쓰지 않는 `docs/images/`와 review-code 스킬의 미지원 `background` 필드 제거, 모듈 Python 스크립트에 실행 권한 부여
- 새 프로젝트 자리표시자 목록에 프론트엔드 제목·시작 문구, AI 모듈 삭제 시 정리할 문서에 `docs/architecture.md`·`docs/guides/agent-knowledge.md`, README의 `.claude/` 설명에 `agent-memory/`·`workflows/` 추가
- Rust Alpine 이미지에 이미 있는 `musl-dev`의 중복 설치 제거(개발 Compose 재시작 시 네트워크 불필요), `.gitignore`에 에이전트 앱의 `.claude/worktrees/` 추가, CodeQL에 모듈 스크립트용 Python 분석 추가
- Dependabot이 Rust 이미지를 제안하지 않음(`rust-toolchain.toml`과 함께 수동 갱신), 개발 Compose의 PostgreSQL 포트를 `127.0.0.1`에만 열고 로컬 `npm run dev`는 Vite 기본값(localhost)만 사용
- 프로덕션 Compose의 PostgreSQL 기본 비밀번호(`change-me`) 제거, cargo-chef 0.1.78 고정, 모듈 검증 CI에 Cargo 레지스트리 캐시 추가
- `check.sh --docker`가 backend 소스를 읽기 전용으로 마운트

### Fixed
- Nginx가 `/api/` 접두사를 잘라 프로덕션에서 `/api/v1/health`가 404가 되던 문제
- CI와 시작 안내가 툴체인을 설치하지 않는 `rustup show` 대신 `rustup toolchain install`을 사용
- rag 데모 API가 `top_k` 생략 시 설정과 무관한 고정값 5를 쓰던 문제, `set_readers`의 빈 reader 허용
- 모듈 수명주기 검증의 임시 프로젝트가 `rust-toolchain.toml`을 받지 않아 네이티브·CI 실행이 고정되지 않은 기본 Rust로 컴파일하던 문제
- `check-template-modules.sh --docker`가 docker 없이 실행될 때 안내 없이 실패하던 문제
- rag가 변경 없는 문서를 다시 수집할 때도 모든 청크를 임베딩하던 문제
- rag 데모 API가 내부 저장소 오류(`store_unavailable`)를 공급자 장애처럼 502로 반환하던 문제(500으로 변경)
- 잘못된 `PORT` 값을 조용히 8080으로 바꾸던 문제(이제 시작 시 오류로 종료)
- `check-template-modules.sh`의 네이티브 실행이 Python 3.11 미만이나 rustfmt 없는 환경에서 원인 안내 없이 실패하던 문제
- 빌드 최적화 문서의 Dockerfile 명령이 실제와 달리 `--locked`·`--bin backend`를 빠뜨리던 부분, 외부 자료의 Tower 문서 링크를 잠금 파일 버전(0.5.3)으로 수정
- AI 확장 문서가 없는 `IdentityResolver`, Cargo 변경, 부분 제거를 현재 동작처럼 설명하던 부분과 데모 응답 형식 차이, DB·MCP 가이드의 실행·환경 변수 설명, README의 Docker 검증 산출물 설명
- 모듈 수명주기 검증이 고정된 backend 파일 5개만 복사해, 프로젝트가 backend 파일을 추가하면 임시 프로젝트 컴파일이 실패하던 문제(이제 `target`·`.env` 계열을 뺀 backend 전체 복사)
- Docker 실행 안내의 `cp .env.example .env`가 기존 `.env`를 덮어쓰던 부분, Nginx 설정 주석이 upstream keepalive 없이 백엔드 연결이 재사용되는 것처럼 설명하던 부분
- Docker 가이드의 에이전트 상태 볼륨 이름이 공유 템플릿 가이드(`p_agent_state_<프로젝트>_<인스턴스>`)와 다르던 부분, 새 프로젝트 정리 목록에서 빠진 볼륨 이름 문서·CodeQL Python 항목·외부 자료 정리
