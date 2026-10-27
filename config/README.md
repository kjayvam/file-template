# 환경별 설정

비밀이 아닌 설정 값을 환경별로 나눠 두는 폴더입니다.

- `default.yml`: 모든 환경의 기본값
- `development.yml`, `test.yml`, `production.yml`: 환경별로 덮어쓰는 값

## 규칙

- 비밀번호, 토큰, API 키는 여기에 넣지 않고 환경 변수로 주입합니다. (`.env.example` 참고)
- 이 파일들을 읽어 들이는 코드는 `src/config/`에 둡니다.
- 권장 적용 순서: `default.yml` → 환경별 파일 → 환경 변수
