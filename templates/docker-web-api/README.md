# docker-web-api

web-api·docker-rust·docker-react를 묶는 연결 모듈입니다. 개발 Vite 프록시와 프로덕션 Nginx의 /api/ 경로를 backend:8080으로 연결합니다.

```bash
python3 scripts/template-module.py add docker-web-api --project /path/to/project --with-dependencies --dry-run
```

명령은 카탈로그 루트에서 실행합니다. 신규 생성은 init --name 이름 --project 새경로 --modules docker-web-api을 사용합니다. 소유 파일·의존 관계·검증 계약은 [module.json](module.json), 전체 사용법은 [카탈로그 안내](../README.md)를 참고하세요.
