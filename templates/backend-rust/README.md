# backend-rust

Axum API와 health 테스트, Cargo.lock·Rust 버전 고정을 제공합니다. 프론트엔드·DB·Docker가 필요하지 않습니다. 기능은 backend/src/features/<기능>/에 둡니다.

```bash
python3 scripts/template-module.py add backend-rust --project /path/to/project --with-dependencies --dry-run
```

명령은 카탈로그 루트에서 실행합니다. 신규 생성은 init --name 이름 --project 새경로 --modules backend-rust을 사용합니다. 소유 파일·의존 관계·검증 계약은 [module.json](module.json), 전체 사용법은 [카탈로그 안내](../README.md)를 참고하세요.
