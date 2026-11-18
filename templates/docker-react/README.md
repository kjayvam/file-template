# docker-react

React 앱용 개발·프로덕션 Compose와 Node→Nginx Dockerfile입니다. 백엔드가 없어도 실행됩니다. Nginx는 SPA 경로·정적 캐시·보안 헤더를 처리합니다.

```bash
python3 scripts/template-module.py add docker-react --project /path/to/project --with-dependencies --dry-run
```

명령은 카탈로그 루트에서 실행합니다. 신규 생성은 init --name 이름 --project 새경로 --modules docker-react을 사용합니다. 소유 파일·의존 관계·검증 계약은 [module.json](module.json), 전체 사용법은 [카탈로그 안내](../README.md)를 참고하세요.
