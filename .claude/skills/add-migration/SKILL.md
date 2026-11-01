---
name: add-migration
description: 새 DB 마이그레이션 파일 쌍(up/down)을 migrations/ 폴더에 만든다. 테이블이나 컬럼을 추가, 변경, 삭제해야 할 때 사용한다.
disable-model-invocation: true
argument-hint: "[설명]"
---

사용자가 알려준 변경 내용으로 새 마이그레이션 파일 쌍을 만듭니다. 변경 내용을 모르면 먼저 물어봅니다.

1. `migrations/`에서 가장 큰 번호를 찾습니다. (예: `0001`)
2. 다음 번호(4자리)로 `NNNN_설명.up.sql`, `NNNN_설명.down.sql` 두 파일을 만듭니다. 설명 부분은 소문자 snake_case입니다.
3. `up.sql`에는 변경 SQL을, `down.sql`에는 그 변경을 정확히 되돌리는 SQL을 프로젝트에서 선택한 데이터베이스(SQLite, PostgreSQL 등) 문법으로 씁니다.
4. 기존 마이그레이션 파일은 수정하지 않습니다.
5. 만든 파일 이름과 내용을 간단히 알려줍니다.
