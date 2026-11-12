# my-project

Rust 백엔드(Axum)와 React(TypeScript, Vite) 프론트엔드 기반의 풀스택 템플릿입니다. DB(SQLite, PostgreSQL 등)는 프로젝트 상황에 맞게 자유롭게 선택할 수 있으며, 초기 상태에서 어디서든 활용 가능한 뼈대로 구성되어 있습니다.

## 폴더 구조

- `backend/`: Rust API 서버 (`src/main.rs`는 실행, `src/lib.rs`는 라우터), API 통합 테스트는 `backend/tests/`
- `frontend/`: React + TypeScript 웹 클라이언트. 컴포넌트 테스트는 `src/**/*.test.tsx`, 공통 설정은 `src/test/setup.ts`
- `docker/`: Docker Compose (`docker-compose.yml`, `docker-compose.dev.yml`), Nginx 프록시, `mcp/` (컨테이너 내 에이전트용)
- `docs/`: 프로젝트 문서 (아키텍처, API 가이드, 개발 가이드 등) 및 `docs/docker/` (Docker 가이드)
- `tests/`: 테스트 배치 안내(`README.md`), 향후 E2E 테스트(`e2e/`), 공용 데이터(`fixtures/`)
- `config/`: 환경별 설정 YAML (비밀 값 없음)
- `migrations/`: DB 마이그레이션 SQL (`NNNN_설명.up.sql` / `NNNN_설명.down.sql`)
- `external/`: GitHub 저장소와 기타 외부 자료 목록 (`external/README.md`)
- `templates/`: ai-common·rag 선택형 원본, module.json의 의존·소유 파일·공유 연결 지점. 적용 방법은 templates/README.md
- `scripts/`, `.github/`

## 명령어

- 도구: Rust 1.99.1 (`rust-toolchain.toml`, `rustfmt` 포함), Node.js 22.12 이상(22 계열)과 npm. CI와 Docker 검증도 같은 계열을 사용합니다.
- `./scripts/setup.sh`: 개발 환경 세팅 (.env가 없으면 예시 복사, `npm ci`)
- `./scripts/check.sh`: Rust 포맷·컴파일·테스트와 프론트엔드 테스트·빌드, Docker 이미지와 `rust-toolchain.toml`의 Rust 버전 일치 확인. 도구 누락이나 검사 실패 시 오류 종료
- `./scripts/check.sh --backend` / `--frontend`: 한쪽만 검증
- `./scripts/check.sh --docker`: 로컬 Rust·Node 설치 없이 Docker로 같은 검사 실행 (.env 불필요)
- `./scripts/build.sh`: Rust 컴파일과 프론트엔드 빌드만 검사 (테스트는 `check.sh`)
- `./scripts/check-template-modules.sh --docker`: 임시 프로젝트에서 기본형→common→rag+common→common→기본형 검사. 네이티브는 Python 3.11+·Rust 설치 후 --docker 생략
- `python3 scripts/template-module.py list`: 제공 모듈 목록. add/remove는 --project로 대상을 명시하고 --dry-run으로 변경 경로 검토
- 개별 테스트: `cd backend && cargo test --locked`, `cd frontend && npm test`
- `docker compose --env-file .env -f docker/docker-compose.dev.yml up`: 개발 환경 실행 (Vite HMR. Rust 변경은 `restart backend`로 재컴파일). PostgreSQL이 필요하면 `--profile postgres` 추가
- `docker compose --env-file .env -f docker/docker-compose.yml up --build`: 프로덕션 Docker 실행 (저장소 루트에서)
- 로컬 직접 실행:
  - 백엔드: `cd backend && cargo run`
  - 프론트엔드: `cd frontend && npm run dev`

## 규칙

- 이 저장소는 프로젝트별로 기능을 추가·제거하는 템플릿입니다. 제안한 AI 모듈·서버·콘솔을 모든 프로젝트의 필수 구조로 고정하지 않습니다. 선택한 모듈의 코드·의존성·설정·테스트·CI를 함께 관리합니다.

- `.env`와 비밀 값(토큰, 키, 비밀번호)은 읽거나 출력하거나 커밋하지 않습니다. 새 환경 변수는 이름만 `.env.example`에 추가합니다.
- 모듈 원본을 추가·수정하면 기본형 검사와 적용·제거 수명주기를 검증합니다. 기본형 backend에 직접 설치하지 말고 임시 프로젝트를 사용합니다. .env·개인 설정은 검증용 사본에 복사하지 않습니다.
- 개인 설정(`CLAUDE.local.md`, `.claude/settings.local.json`)과 로컬 메모리는 커밋하지 않습니다. 두 의존성 잠금 파일은 커밋하며 CI에서는 갱신하지 않습니다.
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
