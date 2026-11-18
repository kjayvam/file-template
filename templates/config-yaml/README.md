# config-yaml

환경별 비밀이 아닌 YAML 설정 양식입니다. 이름을 생성 시 치환합니다. 로더·설정 병합·Docker 빌드 컨텍스트 조정은 실제 앱 요구에 맞게 구현합니다.

```bash
python3 scripts/template-module.py add config-yaml --project /path/to/project --with-dependencies --dry-run
```

명령은 카탈로그 루트에서 실행합니다. 신규 생성은 init --name 이름 --project 새경로 --modules config-yaml을 사용합니다. 소유 파일·의존 관계·검증 계약은 [module.json](module.json), 전체 사용법은 [카탈로그 안내](../README.md)를 참고하세요.
