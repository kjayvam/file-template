# docker

선택 모듈의 dev/prod Compose 조각을 모으는 Python 실행 도구입니다. 서비스는 docker-rust·docker-react·docker-postgres를 선택해야 생깁니다.

```bash
python3 scripts/template-module.py add docker --project /path/to/project --with-dependencies --dry-run
```

명령은 카탈로그 루트에서 실행합니다. 신규 생성은 init --name 이름 --project 새경로 --modules docker을 사용합니다. 소유 파일·의존 관계·검증 계약은 [module.json](module.json), 전체 사용법은 [카탈로그 안내](../README.md)를 참고하세요.
