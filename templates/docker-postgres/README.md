# docker-postgres

PostgreSQL dev/prod 서비스와 pg-data 볼륨입니다. DATABASE_NAME·DATABASE_USER·DATABASE_PASSWORD 이름을 공유 .env.example에 연결합니다. 비밀번호 기본값은 없고 앱 DB 드라이버를 설치하지 않습니다.

```bash
python3 scripts/template-module.py add docker-postgres --project /path/to/project --with-dependencies --dry-run
```

명령은 카탈로그 루트에서 실행합니다. 신규 생성은 init --name 이름 --project 새경로 --modules docker-postgres을 사용합니다. 소유 파일·의존 관계·검증 계약은 [module.json](module.json), 전체 사용법은 [카탈로그 안내](../README.md)를 참고하세요.
