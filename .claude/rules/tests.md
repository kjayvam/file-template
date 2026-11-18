---
paths:
  - "tests/**/*"
  - "templates/**/*"
  - "scripts/**/*"
---

# 테스트 규칙

- 카탈로그 원본은 templates/<모듈>/files에 둡니다. 생성 프로젝트의 Rust API 테스트는 backend/tests, React 테스트는 코드 옆에 둡니다.
- 모듈 원본을 바꾸면 코드·설정·테스트·문서를 함께 관리합니다.
- 구조·충돌·보존은 ./scripts/check.sh --structure, 전체 조합·앱 테스트·빌드는 ./scripts/check.sh --docker로 확인합니다.
- 루트에 앱이나 AI 모듈을 설치하지 않고 임시 프로젝트에서 검증합니다. 비밀 값·개인 설정·로컬 빌드 산출물을 복사하지 않습니다.
- Docker Compose 설정 검사는 Docker가 있을 때 실행합니다. 실행하지 못한 검사는 통과로 보고하지 않습니다.
- 생성 프로젝트의 scripts/check.sh는 설치한 앱만 검사합니다. 최소형과 위키형은 구조 검사만 실행합니다.
- E2E 러너는 아직 없습니다. 실행한 것으로 보고하지 않습니다.
