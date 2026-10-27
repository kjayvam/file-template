---
paths:
  - "migrations/**/*"
---

# 마이그레이션 규칙

- 파일은 `NNNN_설명.up.sql` / `NNNN_설명.down.sql` 쌍으로 만듭니다. 번호는 기존 마지막 번호 + 1입니다.
- 이미 만들어진 파일은 수정하지 않습니다. 변경은 새 번호의 파일로 추가합니다.
- `down.sql`은 `up.sql`의 변경을 정확히 되돌려야 합니다.
- SQL은 PostgreSQL 문법으로 작성합니다.
