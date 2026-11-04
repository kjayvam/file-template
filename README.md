# file-template

Rust 백엔드(Axum)와 React(TypeScript, Vite) 프론트엔드 기반의 풀스택 파일 구조 템플릿입니다. 데이터베이스(SQLite, PostgreSQL 등)는 상황에 따라 유연하게 선택하여 사용할 수 있도록 엔진 중립적으로 설계되었습니다.

## 폴더 구조

| 경로 | 용도 |
| --- | --- |
| `backend/` | Rust 백엔드 API 서버 (Axum, Tokio), `src/lib.rs`의 라우터와 `tests/`의 API 통합 테스트 |
| `frontend/` | React + TypeScript 프론트엔드 (Vite), `src/**/*.test.tsx`의 컴포넌트 테스트와 `src/test/setup.ts`의 공통 설정 |
| `docker/` | Docker 실행 설정 및 컨테이너 MCP (`docker/mcp/`) |
| `docs/` | 프로젝트 문서 (아키텍처, API 가이드, 개발 가이드) |
| `docs/docker/` | Docker 단독 실행 및 도커 공유 템플릿 연계 가이드 |
| `tests/` | 테스트 배치 안내, 공용 테스트 데이터와 향후 E2E 테스트 자리 |
| `config/` | 환경별 설정 YAML |
| `migrations/` | DB 마이그레이션 SQL |
| `scripts/` | 환경 설정(`setup.sh`), 빌드(`build.sh`), 포맷·테스트·빌드 검증(`check.sh`), 배포 예시 |
| `rust-toolchain.toml` | 로컬·CI가 사용할 Rust 버전과 rustfmt 고정 |
| `examples/` | 사용 예제 |
| [`external/`](external/README.md) | GitHub 저장소와 기타 외부 자료 목록 |
| `.github/` | GitHub 워크플로 및 협업 설정 |

외부 자료의 이름, URL, 용도는 `external/`에서 관리합니다. 프로젝트 지침은 [CLAUDE.md](CLAUDE.md)를 참고하세요.

## 시작과 검증

로컬 개발에는 Rust 1.99.1(`rustfmt` 포함), Node.js 22.12 이상(22 계열)과 npm이 필요합니다. Rust는 `rust-toolchain.toml`로 고정됩니다. 루트에서 실행합니다.

```bash
./scripts/setup.sh
./scripts/check.sh
```

`check.sh`는 Rust 포맷·컴파일·API 통합 테스트와 React 컴포넌트 테스트·프로덕션 빌드를 실행합니다. 필요한 도구가 없거나 검사가 실패하면 오류로 종료합니다. 빌드만 확인하려면 `./scripts/build.sh`를 사용합니다.

Rust와 Node를 설치하지 않고 Docker로 동일한 검사를 실행할 수도 있습니다.

```bash
./scripts/check.sh --docker
```

Docker 검증은 `.env` 없이 실행되며, 의존성과 빌드 결과는 로컬 소스 폴더에, Cargo 다운로드 캐시는 `file-template-check-cargo` 볼륨에 남습니다. 상세 실행 방법은 [시작하기](docs/getting-started.md), 테스트 위치는 [테스트 안내](tests/README.md)를 참고하세요.

개인 설정인 `CLAUDE.local.md`, `.claude/settings.local.json`과 `.env` 계열은 Git에서 제외합니다. `backend/Cargo.lock`, `frontend/package-lock.json`, `.env.example`은 버전 관리합니다.
