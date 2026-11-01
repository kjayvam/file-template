# Docker

- `Dockerfile`: 앱 이미지
- `docker-compose.yml`: 앱 + PostgreSQL 개발 환경
- `mcp/`: 컨테이너 내부 에이전트용 MCP 설정 및 가이드 (`docker/mcp/README.md`)

## 실행 (저장소 루트에서)

```bash
cp .env.example .env
docker compose --env-file .env -f docker/docker-compose.yml up --build
```

## 참고

- `.dockerignore`는 빌드 컨텍스트인 저장소 루트에 있어야 적용되므로 루트에 두었습니다.
- 로컬 실행용 `.env`의 `DATABASE_HOST=localhost`는 유지하고, 앱 컨테이너에서는 Compose의 `environment`로 `DATABASE_HOST=db`를 덮어씁니다.
- 현재 앱 예제는 시작 문구를 출력한 뒤 종료합니다. 웹 서버와 DB 연결은 프로젝트에 맞게 구현하세요.
- `migrations/`의 SQL은 컨테이너 시작 시 자동 적용되지 않습니다. 선택한 마이그레이션 도구로 실행하세요.
