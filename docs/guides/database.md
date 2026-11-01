# 데이터베이스 가이드

## 개요

프로젝트의 데이터베이스 설계 원칙, 명명 규칙, 그리고 마이그레이션 관리 지침을 정의합니다.

## 기본 명명 규칙

| 대상 | 표기법 | 예시 | 비고 |
| --- | --- | --- | --- |
| **테이블 (Tables)** | `snake_case` (복수형) | `users`, `order_items` | 단수형 지양 |
| **컬럼 (Columns)** | `snake_case` | `email`, `created_at` | 약어 지양 |
| **기본키 (Primary Key)** | `id` | `id` | UUID 또는 BIGINT/IDENTITY |
| **외래키 (Foreign Key)** | `{참조테이블_단수}_id` | `user_id`, `order_id` | 참조 대상 명시 |
| **인덱스 (Index)** | `idx_{테이블}_{컬럼}` | `idx_users_email` | 복합 인덱스는 순서대로 나열 |
| **유니크 인덱스 (Unique)** | `uq_{테이블}_{컬럼}` | `uq_users_email` | 유니크 제약 조건 |

## 필수 공통 컬럼

모든 엔티티 테이블에는 다음 메타데이터 컬럼을 포함하는 것을 권장합니다:

- `created_at`: 레코드 생성 시각 (`TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP`)
- `updated_at`: 레코드 최종 수정 시각 (`TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP`)
- `deleted_at`: 논리 삭제(Soft Delete) 적용 시 사용 (선택 사항)

## 마이그레이션 규칙 (`migrations/`)

1. **파일 쌍 구성**: 새 마이그레이션은 항상 `NNNN_설명.up.sql`과 `NNNN_설명.down.sql` 쌍으로 생성합니다.
   - 예: `0001_create_users.up.sql`, `0001_create_users.down.sql`
2. **불변성**: 이미 적용되었거나 main 브랜치에 병합된 마이그레이션 파일은 절대 수정하지 않습니다. 수정이 필요할 경우 새 번호의 마이그레이션을 추가합니다.
3. **완전한 롤백 보장**: `down.sql`은 `up.sql`의 변경 사항을 완벽히 되돌릴 수 있어야 합니다.
4. **트랜잭션 안전성**: 데이터가 많은 테이블에 `ALTER TABLE`이나 인덱스 생성을 진행할 때는 락(Lock) 경합을 최소화하는 쿼리를 작성합니다.

## 성능 및 인덱스 가이드

- `WHERE`, `JOIN`, `ORDER BY` 절에 자주 사용되는 컬럼은 인덱스 지정을 고려합니다.
- 과도한 인덱스는 `INSERT`/`UPDATE` 성능을 저하시키므로 실제 쿼리 패턴과 실행 계획(`EXPLAIN`)을 기반으로 추가합니다.
- 외래키 컬럼에는 조인 성능을 위해 기본적으로 인덱스를 생성합니다.
