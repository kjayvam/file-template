# postgres

PostgreSQL 마이그레이션 up/down 예시입니다. 앱 드라이버·스키마 실행기는 포함하지 않습니다. DB 컨테이너는 docker-postgres를 선택합니다.

```bash
python3 scripts/template-module.py add postgres --project /path/to/project --with-dependencies --dry-run
```

명령은 카탈로그 루트에서 실행합니다. 신규 생성은 init --name 이름 --project 새경로 --modules postgres을 사용합니다. 소유 파일·의존 관계·검증 계약은 [module.json](module.json), 전체 사용법은 [카탈로그 안내](../README.md)를 참고하세요.
