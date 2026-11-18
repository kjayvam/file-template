# frontend-react

백엔드 없이 실행할 수 있는 React/TypeScript 앱입니다. API 연결은 web-api, Docker 실행은 docker-react를 추가합니다. 기능은 frontend/src/features/<기능>/에 둡니다.

```bash
python3 scripts/template-module.py add frontend-react --project /path/to/project --with-dependencies --dry-run
```

명령은 카탈로그 루트에서 실행합니다. 신규 생성은 init --name 이름 --project 새경로 --modules frontend-react을 사용합니다. 소유 파일·의존 관계·검증 계약은 [module.json](module.json), 전체 사용법은 [카탈로그 안내](../README.md)를 참고하세요.
