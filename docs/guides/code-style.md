# 코드 스타일 가이드

## 개요

일관된 코드 품질과 가독성을 유지하기 위한 코딩 표준 및 규칙을 정의합니다.

## 기본 원칙

1. **가독성 우선**: 코드는 작성하는 시간보다 읽히는 시간이 훨씬 깁니다. 명확하고 의도가 드러나는 코드를 작성합니다.
2. **조기 반환 (Early Return)**: 깊은 중첩(nesting)을 피하고 예외 상황이나 유효하지 않은 조건은 함수 초기에 반환합니다.
3. **단일 책임 원칙**: 함수나 클래스는 한 가지 작업만 명확하게 수행하도록 작게 유지합니다.
4. **부수 효과(Side Effect) 최소화**: 순수 함수를 지향하고, 전역 상태 변경이나 예상치 못한 데이터 변형을 지양합니다.

## 명명 규칙 (Naming Conventions)

| 대상 | 표기법 | 예시 |
| --- | --- | --- |
| **변수 및 함수** | `camelCase` | `getUserById`, `isLoading` |
| **클래스 및 인터페이스/타입** | `PascalCase` | `UserService`, `UserProfile` |
| **상수 (Environment/Config)** | `UPPER_SNAKE_CASE` | `MAX_RETRY_COUNT`, `DEFAULT_PAGE_SIZE` |
| **파일명 (모듈/유틸)** | `kebab-case` 또는 `camelCase` (일관성 유지) | `user-service.js`, `formatDate.js` |
| **컴포넌트 파일명** | `PascalCase` | `UserProfileCard.jsx` |

- **불리언 변수/함수**: 상태를 명확히 표현할 수 있도록 접두사를 붙입니다 (`is`, `has`, `can`, `should` 등).
  - 예: `isActive`, `hasPermission`, `canSubmit`

## 주석 및 문서화

- **왜(Why)**에 집중: 코드가 '무엇을(What)' 하는지는 코드 자체로 설명하고, 주석은 **왜 그렇게 작성했는지(Why)** 배경과 의도를 설명합니다.
- 복잡한 비즈니스 로직이나 공용 함수에는 JSDoc/TSDoc 형태의 함수 명세를 작성합니다:
  ```javascript
  /**
   * 사용자 ID로 프로필 정보를 조회합니다.
   *
   * @param {string} userId - 조회할 사용자의 고유 ID
   * @returns {Promise<UserProfile>} 사용자 프로필 정보
   * @throws {NotFoundError} 사용자가 존재하지 않을 경우 발생
   */
  async function getUserProfile(userId) { ... }
  ```

## 에러 처리

- 에러를 조용히 무시(`catch {}` 후 아무것도 하지 않음)하지 않습니다. 반드시 로깅하거나 상위 호출자에게 전파합니다.
- 예측 가능한 예외는 커스텀 에러 클래스(`CustomError`, `NotFoundError` 등)를 정의하여 일관된 에러 응답을 지원합니다.
