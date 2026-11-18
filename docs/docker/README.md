# 선택형 Docker 가이드

Docker는 앱과 별도 모듈입니다. 앱만 선택하면 Dockerfile·Compose를 생성하지 않습니다.

| 모듈 | 제공 내용 |
| --- | --- |
| docker | 설치된 Compose 조각을 모으는 scripts/compose.py |
| docker-rust | Rust Dockerfile, backend dev/prod 서비스 |
| docker-react | React/Nginx Dockerfile, frontend dev/prod 서비스 |
| docker-postgres | PostgreSQL dev/prod 서비스, pg-data 볼륨 |
| docker-web-api | React→Rust 개발 프록시와 Nginx API 프록시 |

```bash
# 카탈로그에서 조립
python3 scripts/template-module.py init --name sample --project ../sample --preset fullstack-docker
# 생성 프로젝트에서 실행
cd ../sample
python3 scripts/compose.py dev up
python3 scripts/compose.py prod up --build
```

동시에 같은 포트를 쓰는 다른 프로젝트는 Compose 조각의 호스트 포트를 변경합니다. Docker 프로젝트 이름·네트워크·볼륨은 생성 시 이름으로 분리하지만 호스트 포트는 자동 할당하지 않습니다. Rust는 127.0.0.1:8080, React 개발은 127.0.0.1:5173, React 프로덕션은 127.0.0.1:8088입니다.

독립 앱은 상대 앱에 의존하지 않습니다. PostgreSQL은 설치한 경우에만 실행하며 dev의 localhost:5432 외에는 DB 포트를 공개하지 않습니다. PASSWORD를 .env 또는 프로세스 환경 변수로 지정해야 하며 앱 드라이버는 포함하지 않습니다.

[단독 실행](standalone.md) · [공유 환경 확장 예시](shared-template.md) · [빌드 최적화](build-optimization.md) · [컨테이너 MCP 안내](mcp.md)
