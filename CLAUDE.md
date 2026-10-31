# my-project

언어와 프레임워크는 아직 정하지 않았습니다. 현재는 Node 기준 뼈대(`src/index.js`)만 있습니다. 언어가 정해지면 이 문서를 갱신하세요.

## 폴더 구조

- `src/`: 소스 코드 (`components/`, `services/`, `utils/`, `config/`, `types/`, `assets/`)
- `tests/`: `unit/`, `integration/`, `e2e/`, `fixtures/`
- `config/`: 환경별 설정 YAML (비밀 값 없음). 이를 읽는 코드는 `src/config/`
- `migrations/`: DB 마이그레이션 SQL (`NNNN_설명.up.sql` / `NNNN_설명.down.sql`)
- `docker/`: Dockerfile, docker-compose
- `external/`: GitHub 저장소와 기타 외부 자료 목록 (`external/README.md`)
- `docs/`, `scripts/`, `examples/`, `.github/`

## 명령어

- `./scripts/setup.sh`: 개발 환경 세팅 (현재는 틀만 있음)
- `./scripts/build.sh`: 빌드와 테스트 (현재는 틀만 있음)
- `node src/index.js`: 실행
- `docker compose --env-file .env -f docker/docker-compose.yml up --build`: Docker 실행 (저장소 루트에서)

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
