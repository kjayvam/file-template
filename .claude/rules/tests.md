---
paths:
  - "tests/**/*"
---

# 테스트 규칙

- 단위 테스트는 `tests/unit/`, 통합 테스트는 `tests/integration/`, E2E 테스트는 `tests/e2e/`에 둡니다.
- 테스트용 데이터는 `tests/fixtures/`에 두고, 실제 비밀 값이나 운영 데이터는 쓰지 않습니다.
- 공통 설정은 `tests/setup.js`에 둡니다.
