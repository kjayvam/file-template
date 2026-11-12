# 단독 실행 가이드 (Standalone Mode)

단독 실행 모드는 외부 공유 인프라나 특수 스크립트 없이, 표준 **Docker Engine**과 **Docker Compose**만으로 프로젝트를 개발하고 배포하는 방식입니다.

템플릿을 새로 clone하여 개인 PC나 독립 서버에서 곧바로 작업할 때 기본으로 사용합니다.

---

## 1. 사전 요구 사항

- Docker Engine 24.0 이상
- Docker Compose v2 (Compose CLI)
- 로컬 환경 설정 파일:
  ```bash
  cp .env.example .env
  ```

---

## 2. 개발 환경 실행 (Dev Mode)

개발 환경에서는 Vite 개발 서버(HMR)와 `cargo run`으로 실행한 Rust 서버를 사용합니다. Rust 코드를 바꾸면 `restart backend`로 다시 컴파일합니다.

```bash
# 개발용 Compose 실행 (Vite HMR + Rust 개발 빌드)
docker compose --env-file .env -f docker/docker-compose.dev.yml up

# Rust 코드 변경 반영
docker compose --env-file .env -f docker/docker-compose.dev.yml restart backend
```

* **Frontend**: `http://localhost:5173` (Vite 개발 서버 + HMR)
* **Backend**: `http://localhost:8080` (Rust API 서버)
* **Database**:
  * **SQLite 선택 시**: 별도 컨테이너 불필요 (로컬 볼륨/파일로 직접 I/O)
  * **서버형 DB(PostgreSQL/MySQL) 선택 시**: `--profile postgres`를 붙여 `db` 서비스 실행 (`localhost:5432`)

### 개발 모드 볼륨 마운트 구조
* `./frontend` → 컨테이너 내부 `/app` (코드 수정 시 브라우저 즉시 갱신)
* `./backend` → 컨테이너 내부 `/app` (재시작 시 수정 코드로 재컴파일)
* `cargo-cache` 볼륨 → Cargo 의존성 다운로드 캐싱
* `backend-target` 볼륨 → 컨테이너용 빌드 산출물을 호스트 `backend/target`과 분리해 재컴파일 시간 단축

---

## 3. 프로덕션 환경 실행 (Prod Mode)

프로덕션 환경에서는 멀티스테이지 빌드를 통해 최적화된 경량 컨테이너를 구동합니다.

```bash
# 프로덕션 빌드 및 백그라운드 실행
docker compose --env-file .env -f docker/docker-compose.yml up --build -d
```

* **Frontend**: Nginx가 React 빌드 산출물(정적 에셋)을 서빙하며, `/api/*` 경로 요청을 백엔드로 리버스 프록시합니다 (`http://localhost:80`).
* **Backend**: 컴파일된 단일 바이너리만 포함된 초경량(수십 MB) 런타임 이미지로 동작합니다.
* **Database**: SQLite 파일은 `app-data`, PostgreSQL(`--profile postgres`)은 `pg-data` 볼륨에 보존됩니다. 프로덕션 Compose는 DB 포트를 호스트에 열지 않습니다.

---

## 4. 환경 변수 주입 규칙

* 모든 비밀 값과 서비스 설정은 저장소 루트의 `.env` 파일에서 주입됩니다. Compose는 기본적으로 첫 Compose 파일이 있는 `docker/`에서 `.env`를 찾으므로 `--env-file .env`를 붙여 실행합니다.
* `.env` 파일은 절대 Git에 커밋하지 않으며, 신규 변수 추가 시 이름만 `.env.example`에 등록합니다.
* 컨테이너 내부 통신 호스트명:
  * 백엔드에서 DB 접속: `DATABASE_HOST=db` (Docker DNS)
  * 프론트엔드 Nginx에서 백엔드 접속: `http://backend:8080`

---

## 5. 컨테이너 정리 및 볼륨 관리

```bash
# 컨테이너 및 네트워크 종료 (데이터 볼륨 유지)
docker compose --env-file .env -f docker/docker-compose.yml down

# 주의: 데이터베이스 데이터까지 모두 초기화할 때만 -v 사용
docker compose --env-file .env -f docker/docker-compose.yml down -v
```
