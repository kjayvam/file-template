# file-template

Rust 백엔드(Axum)와 React(TypeScript, Vite) 프론트엔드 기반의 풀스택 파일 구조 템플릿입니다. 데이터베이스(SQLite, PostgreSQL 등)는 상황에 따라 유연하게 선택하여 사용할 수 있도록 엔진 중립적으로 설계되었습니다.

## 폴더 구조

| 경로 | 용도 |
| --- | --- |
| `backend/` | Rust 백엔드 API 서버 (Axum, Tokio), `src/lib.rs`의 라우터와 `tests/`의 API 통합 테스트 |
| `frontend/` | React + TypeScript 프론트엔드 (Vite), `src/**/*.test.tsx`의 컴포넌트 테스트와 `src/test/setup.ts`의 공통 설정 |
| `docker/` | Docker 실행 설정 및 컨테이너 MCP (`docker/mcp/`) |
| `docs/` | 프로젝트 문서와 선택형 AI 구조·평가 설계 (`guides/ai-extensions.md`, `guides/ai-evaluation.md`) |
| `docs/docker/` | Docker 단독 실행 및 도커 공유 템플릿 연계 가이드 |
| `tests/` | 테스트 배치 안내, 공용 테스트 데이터와 향후 E2E 테스트 자리 |
| `config/` | 환경별 설정 YAML |
| `migrations/` | DB 마이그레이션 SQL |
| `scripts/` | 환경·빌드·기본형 검증, 모듈 추가·제거(`template-module.py`)와 임시 프로젝트 검증(`check-template-modules.sh`) |
| [`templates/`](templates/README.md) | ai-common·rag의 선택형 원본, 의존·소유 파일 목록과 적용·제거 안내 |
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

Docker 검증은 `.env` 없이 실행되며, Cargo 다운로드 캐시·Rust 빌드 산출물·`node_modules`는 `file-template-check-*` 볼륨에 두어 호스트의 `backend/target`, `frontend/node_modules`를 덮어쓰지 않습니다. 프론트엔드 빌드 결과(`frontend/dist`)만 로컬 폴더에 생깁니다. 상세 실행 방법은 [시작하기](docs/getting-started.md), 테스트 위치는 [테스트 안내](tests/README.md)를 참고하세요.

개인 설정인 `CLAUDE.local.md`, `.claude/settings.local.json`과 `.env` 계열은 Git에서 제외합니다. `backend/Cargo.lock`, `frontend/package-lock.json`, `.env.example`은 버전 관리합니다.

## 선택형 AI 확장 설계

프로젝트에 필요한 RAG·Agent·화면·어댑터만 추가하고 제거하는 모듈형 템플릿을 제안합니다. 작은 프로젝트는 기존 Rust·React 안에 배치하고 별도 서버·workspace·콘솔은 필요할 때 선택합니다. ai-common·rag 0.1.0 원본과 추가·제거 도구를 제공합니다. 기본형에는 AI 모듈이 설치돼 있지 않으며 Agent·UI·live 공급자·품질 평가기는 후속 범위입니다.

- [폴더·파일 구조, 활성화 방식, API·모듈 계약](docs/guides/ai-extensions.md)
- [평가 데이터, 지표·통과 기준, offline/live CI](docs/guides/ai-evaluation.md)
- [구조 선택 이유와 대안 비교](docs/adr/0001-optional-ai-extensions.md)


모듈별 적용·제거 명령은 [템플릿 카탈로그](templates/README.md)에 있습니다. 실제 프로젝트를 수정하지 않고 전체 수명주기를 검사하려면 다음을 실행합니다.

```bash
./scripts/check-template-modules.sh --docker
```

Python 3.11+·Rust·rustfmt가 있으면 `--docker` 없이 검사할 수 있습니다. [에이전트 지식 정리 권장안](docs/guides/agent-knowledge.md)은 로컬 Markdown·연결·검토·검색 흐름을 선택적으로 적용하는 방법을 설명합니다.
