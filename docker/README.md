# Docker 실행 설정

본 디렉토리는 Rust 백엔드, React(TypeScript) 프론트엔드, 선택적 데이터베이스 및 에이전트 도구를 위한 Docker 구성 파일을 관리합니다.

* **DB 선택의 유연성**: SQLite를 사용할 경우 별도의 `db` 컨테이너 없이 볼륨 마운트만으로 동작하며, PostgreSQL이나 MySQL 등 서버형 DB가 필요한 경우에만 `db` 서비스를 기동합니다.

자세한 아키텍처 및 운용 방법은 [Docker 활용 가이드](../docs/docker/README.md)를 참고하세요.

---

## 구성 파일 안내

- `docker-compose.yml`: 프로덕션 모드 (최적화 멀티스테이지 빌드 + Nginx 리버스 프록시)
- `docker-compose.dev.yml`: 개발 모드 (Vite HMR + Rust 개발 런타임 + 소스 볼륨 마운트)
- `nginx/default.conf`: 프론트엔드 정적 서빙 및 `/api/*` 요청의 백엔드 리버스 프록시 설정
- `mcp/`: 컨테이너 내부 에이전트용 MCP 설정 및 가이드 ([`docker/mcp/README.md`](mcp/README.md))

---

## 실행 방법 (저장소 루트에서)

### 1. 개발 환경 실행 (Hot-reload & HMR)

```bash
cp .env.example .env
docker compose --env-file .env -f docker/docker-compose.dev.yml up --build
```
* Frontend (Vite): `http://localhost:5173`
* Backend (Rust): `http://localhost:8080`
* PostgreSQL: `localhost:5432`

### 2. 프로덕션 빌드 및 실행

```bash
docker compose --env-file .env -f docker/docker-compose.yml up --build -d
```
* Web (Nginx): `http://localhost:80`
* Backend: `http://localhost:8080`

---

## 관련 문서

- [단독 실행 가이드](../docs/docker/standalone.md)
- [도커 공유 템플릿 연계 가이드](../docs/docker/shared-template.md)
- [빌드 및 이미지 최적화 가이드](../docs/docker/build-optimization.md)
