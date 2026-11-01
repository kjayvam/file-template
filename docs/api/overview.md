# API 설계 가이드

## 개요

RESTful API 엔드포인트 설계 표준, HTTP 상태 코드, 공통 요청/응답 규격 및 에러 핸들링 지침을 정의합니다.

## 엔드포인트 설계 원칙

1. **명사 및 복수형 사용**: 리소스 경로는 명사의 복수형(`kebab-case`)을 사용합니다.
   - 좋은 예: `GET /api/v1/users`, `POST /api/v1/order-items`
   - 나쁜 예: `GET /api/v1/getUsers`, `POST /api/v1/create_user`
2. **계층 관계 표현**: 하위 리소스는 상위 리소스 뒤에 중첩하여 표현합니다.
   - 예: `GET /api/v1/users/{userId}/orders`
3. **버전 관리**: API 경로 첫 부분에 버전을 명시합니다 (`/api/v1/`).
4. **소문자 및 하이픈**: URL 경로에는 소문자와 하이픈(`-`)만 사용합니다 (언더스코어나 대문자 지양).

## HTTP 메서드 규약

| 메서드 | 용도 | 멱등성(Idempotent) | 성공 상태 코드 |
| --- | --- | --- | --- |
| `GET` | 리소스 조회 | O | `200 OK` |
| `POST` | 새 리소스 생성 / 처리 요청 | X | `201 Created` |
| `PUT` | 리소스 전체 교체/수정 | O | `200 OK` |
| `PATCH` | 리소스 부분 수정 | O / X | `200 OK` |
| `DELETE` | 리소스 삭제 | O | `204 No Content` / `200 OK` |

## 공통 응답 규격

모든 API 응답은 일관된 JSON 구조를 반환합니다.

### 1. 성공 응답 (Success)

```json
{
  "success": true,
  "data": {
    "id": "usr_12345",
    "name": "홍길동",
    "email": "user@example.com"
  },
  "meta": {
    "page": 1,
    "pageSize": 20,
    "totalCount": 100
  }
}
```

### 2. 실패 응답 (Error)

```json
{
  "success": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "입력값이 올바르지 않습니다.",
    "details": [
      {
        "field": "email",
        "reason": "올바른 이메일 형식이 아닙니다."
      }
    ]
  }
}
```

## 주요 HTTP 상태 코드

- `200 OK`: 요청 성공 및 결과 반환
- `201 Created`: 리소스 생성 성공
- `204 No Content`: 요청 성공, 반환할 본문 데이터 없음 (예: DELETE)
- `400 Bad Request`: 요청 파라미터 또는 본문 유효성 검증 실패
- `401 Unauthorized`: 인증되지 않은 요청 (토큰 누락 또는 유효하지 않음)
- `403 Forbidden`: 인증되었으나 해당 리소스에 대한 접근 권한 없음
- `404 Not Found`: 요청한 리소스를 찾을 수 없음
- `409 Conflict`: 리소스 상태 충돌 (예: 이미 존재하는 이메일 중복 가입)
- `500 Internal Server Error`: 서버 내부 예외 및 처리되지 않은 에러

## 인증 및 인가

- 클라이언트는 `Authorization` HTTP 헤더에 Bearer 토큰 형식으로 인증 정보를 전달합니다:
  ```http
  Authorization: Bearer <access_token>
  ```
