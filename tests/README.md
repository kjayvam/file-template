# 테스트 안내

각 언어의 기본 도구가 테스트를 발견하도록 아래 위치를 사용합니다.

| 종류 | 위치 | 실행 |
| --- | --- | --- |
| Rust 단위 테스트 | `backend/src/`의 `#[cfg(test)]` 모듈 | `cd backend && cargo test --locked` |
| Rust API 통합 테스트 | `backend/tests/*.rs` | `cd backend && cargo test --locked` |
| React 컴포넌트·단위 테스트 | `frontend/src/**/*.test.ts`, `frontend/src/**/*.test.tsx` | `cd frontend && npm test` |
| 프론트엔드 공통 설정 | `frontend/src/test/setup.ts` | Vitest가 자동 로드 |
| 공용 테스트 데이터 | `tests/fixtures/` | 필요한 테스트에서 사용 |
| E2E 테스트 | `tests/e2e/` | 아직 러너와 실행 테스트 없음 |

루트의 `./scripts/check.sh`는 포맷·컴파일·모든 구현된 테스트·프론트엔드 빌드를 실행합니다. `--backend`, `--frontend`로 대상을 한정하거나 `--docker`로 로컬 Rust·Node 설치 없이 실행할 수 있습니다. `cd frontend && npm run test:watch`는 개발 중 테스트 감시 모드입니다.

현재 API 테스트는 서버 포트를 열지 않고 실제 Axum 라우터의 두 health 경로, JSON 필드·시각, 없는 경로의 404, 지원하지 않는 POST의 405를 검사합니다. React 테스트는 연결 대기, 정상 응답, HTTP 오류, 네트워크 오류, 잘못된 JSON 응답을 검사합니다. DB와 외부 API는 사용하지 않습니다.

테스트에는 가상 데이터만 사용하고 운영 데이터나 비밀 값은 넣지 않습니다. 프론트엔드 테스트는 실행 후 DOM과 mock을 정리합니다. CI와 로컬은 동일한 `check.sh`를 사용하며, 테스트가 없는 E2E까지 검증했다고 보고하지 않습니다.
