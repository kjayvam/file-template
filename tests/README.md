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

## 템플릿 모듈 수명주기

`./scripts/check-template-modules.sh --docker`는 임시 프로젝트에서 기본형 → ai-common → rag+ai-common → ai-common → 기본형 순서로 Rust 포맷·컴파일·테스트를 실행합니다. 각 단계에서 query 라우트의 존재·제거도 검사합니다. 원본 프로젝트에는 모듈을 설치하지 않습니다.

현재 ai-common 계약 테스트는 3개, rag 테스트는 12개입니다. 모듈 테스트 외에 기존 health 4개와 단계별 라우트 probe 1개를 함께 실행합니다. 파일 충돌·의존 순서·수정된 파일과 블록·심볼릭 링크·dry-run 등 9개의 거부/미리보기 검사도 수행합니다. 모듈 제거 뒤 기존 Cargo·lock·기존 코드 변경·사용자 파일·데이터가 보존되는지 확인합니다.

정확한 적용 절차·소유 경로·한계는 [카탈로그](../templates/README.md)를 참고하세요. 가상 corpus는 rag 모듈의 `demo/corpus.json`에 있으며 실제 모델의 검색·생성 품질 성적으로 보고하지 않습니다. 네이티브 검증은 Python 3.11+·Rust·rustfmt가 필요합니다.
