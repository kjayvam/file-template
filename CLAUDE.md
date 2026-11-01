# my-project

Rust 백엔드(Axum)와 React(TypeScript, Vite) 프론트엔드 기반의 풀스택 템플릿입니다. DB(SQLite, PostgreSQL 등)는 프로젝트 상황에 맞게 자유롭게 선택할 수 있으며, 초기 상태에서 어디서든 활용 가능한 뼈대로 구성되어 있습니다.

## 폴더 구조

- `backend/`: Rust API 서버 (`Cargo.toml`, `src/main.rs`, `Dockerfile`)
- `frontend/`: React + TypeScript 웹 클라이언트 (`package.json`, `src/`, `Dockerfile`)
- `docker/`: Docker Compose (`docker-compose.yml`, `docker-compose.dev.yml`), Nginx 프록시, `mcp/` (컨테이너 내 에이전트용)
- `docs/`: 프로젝트 문서 (아키텍처, API 가이드, 개발 가이드 등) 및 `docs/docker/` (Docker 가이드)
- `tests/`: `unit/`, `integration/`, `e2e/`, `fixtures/`
- `config/`: 환경별 설정 YAML (비밀 값 없음)
- `migrations/`: DB 마이그레이션 SQL (`NNNN_설명.up.sql` / `NNNN_설명.down.sql`)
- `external/`: GitHub 저장소와 기타 외부 자료 목록 (`external/README.md`)
- `scripts/`, `examples/`, `.github/`

## 명령어

- `./scripts/setup.sh`: 개발 환경 세팅 (.env 복사 및 의존성 설치)
- `./scripts/build.sh`: 백엔드/프론트엔드 빌드 및 컴파일 검사
- `docker compose --env-file .env -f docker/docker-compose.dev.yml up`: 개발 환경 실행 (HMR + Rust 핫리로딩)
- `docker compose --env-file .env -f docker/docker-compose.yml up --build`: 프로덕션 Docker 실행 (저장소 루트에서)
- 로컬 직접 실행:
  - 백엔드: `cd backend && cargo run`
  - 프론트엔드: `cd frontend && npm run dev`

## 규칙

- `.env`와 비밀 값(토큰, 키, 비밀번호)은 읽거나 출력하거나 커밋하지 않습니다. 새 환경 변수는 이름만 `.env.example`에 추가합니다.
- 이미 적용된 마이그레이션 파일은 수정하지 않고, 새 번호의 up/down 파일 쌍을 추가합니다.
- 커밋 메시지는 `type: 요약` 형식입니다. (`feat:`, `fix:` 등, CONTRIBUTING.md 참고)
- 새 폴더나 명령어를 추가하면 README.md의 폴더 표도 함께 갱신합니다.
- GitHub 저장소와 기타 외부 자료의 링크·설명은 `external/`에 기록합니다. 항목마다 이름, URL, 용도를 적습니다.

## 서브에이전트 (`.claude/agents/`)

- `code-reviewer`: 코드 검토 (읽기 전용)
- `security-reviewer`: 보안 검토. `security-checklist` 스킬을 미리 불러옵니다
- `codebase-researcher`: 코드베이스 조사. 알게 된 내용을 `.claude/agent-memory/`에 기록합니다
- `test-runner`: 테스트를 실행하고 실패한 것만 요약합니다
- 서브에이전트는 이 대화 내용을 볼 수 없으므로, 위임할 때 필요한 규칙과 맥락을 메시지에 적어서 넘깁니다.
