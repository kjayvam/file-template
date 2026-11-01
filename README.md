# file-template

Rust 백엔드(Axum)와 React(TypeScript, Vite) 프론트엔드, PostgreSQL 기반의 풀스택 파일 구조 템플릿입니다. 초기 상태에서 어디서든 복제하여 사용할 수 있도록 설계되었습니다.

## 폴더 구조

| 경로 | 용도 |
| --- | --- |
| `backend/` | Rust 백엔드 API 서버 (Axum, Tokio) |
| `frontend/` | React + TypeScript 프론트엔드 (Vite) |
| `docker/` | Docker 실행 설정 및 컨테이너 MCP (`docker/mcp/`) |
| `docs/` | 프로젝트 문서 (아키텍처, API 가이드, 개발 가이드) |
| `docs/docker/` | Docker 단독 실행 및 도커 공유 템플릿 연계 가이드 |
| `tests/` | 단위·통합·E2E 테스트와 테스트 데이터 |
| `config/` | 환경별 설정 YAML |
| `migrations/` | DB 마이그레이션 SQL |
| `scripts/` | 개발·빌드·배포 스크립트 |
| `examples/` | 사용 예제 |
| [`external/`](external/README.md) | GitHub 저장소와 기타 외부 자료 목록 |
| `.github/` | GitHub 워크플로 및 협업 설정 |

외부 자료의 이름, URL, 용도는 `external/`에서 관리합니다. 프로젝트 지침은 [CLAUDE.md](CLAUDE.md)를 참고하세요.
