# docker-rust

Rust 앱용 개발·프로덕션 Compose와 멀티스테이지 Dockerfile입니다. 독립 API는 localhost:8080에 연결됩니다. DB는 포함하지 않습니다.

```bash
python3 scripts/template-module.py add docker-rust --project /path/to/project --with-dependencies --dry-run
```

명령은 카탈로그 루트에서 실행합니다. 신규 생성은 init --name 이름 --project 새경로 --modules docker-rust을 사용합니다. 소유 파일·의존 관계·검증 계약은 [module.json](module.json), 전체 사용법은 [카탈로그 안내](../README.md)를 참고하세요.
