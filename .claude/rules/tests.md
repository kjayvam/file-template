---
paths:
  - "tests/**/*"
  - "backend/src/**/*.rs"
  - "backend/tests/**/*.rs"
  - "frontend/src/**/*"
  - "frontend/vitest.config.ts"
  - "templates/**/*"
  - "scripts/*template*"
---

# 테스트 규칙

- Rust 단위 테스트는 `backend/src/`의 `#[cfg(test)]` 모듈, API 통합 테스트는 `backend/tests/`에 둡니다.
- React 테스트는 `frontend/src/`의 대상 코드 옆에 `*.test.ts` 또는 `*.test.tsx`로 둡니다.
- E2E 테스트는 `tests/e2e/`에 둡니다. 현재 러너가 없으므로 실행한 것으로 보고하지 않습니다.
- 테스트용 데이터는 `tests/fixtures/`에 두고, 실제 비밀 값이나 운영 데이터는 쓰지 않습니다.
- 프론트엔드 공통 설정은 `frontend/src/test/setup.ts`에 둡니다.
- 전체 검증은 루트의 `./scripts/check.sh`, 개별 테스트는 `cd backend && cargo test --locked`, `cd frontend && npm test`입니다.
- 필요한 도구가 없거나 실행하지 못한 검사는 통과로 보고하지 않습니다. Docker 검증은 `./scripts/check.sh --docker`입니다.
- 모듈 원본은 `templates/<module>/files/` 아래에 테스트까지 포함합니다. 가상 데모 corpus는 모듈 내부에 둘 수 있습니다. 적용·제거는 `./scripts/check-template-modules.sh --docker`로 임시 프로젝트에서 검증하고 기본형에 직접 설치하지 않습니다.
