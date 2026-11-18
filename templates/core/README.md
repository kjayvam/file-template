# core

기술 중립 공통부입니다. 프로젝트 문서·에이전트 지침·환경 변수 양식·검사 스크립트·CI를 제공합니다. init에서 항상 포함하며 제거하지 않습니다. 앱·DB·Docker는 포함하지 않습니다.

```bash
python3 scripts/template-module.py add core --project /path/to/project --with-dependencies --dry-run
```

명령은 카탈로그 루트에서 실행합니다. 신규 생성은 init --name 이름 --project 새경로 --modules core을 사용합니다. 소유 파일·의존 관계·검증 계약은 [module.json](module.json), 전체 사용법은 [카탈로그 안내](../README.md)를 참고하세요.
