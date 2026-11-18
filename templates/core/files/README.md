# __PROJECT_NAME__

선택한 모듈로 조립한 프로젝트입니다. 설치 목록과 버전은 `.template-modules.json`에서 확인합니다.

- `./scripts/setup.sh`: 선택한 도구의 개발 환경 준비
- `./scripts/check.sh`: 구조 검사와 선택한 앱의 테스트·빌드
- `./scripts/check.sh --docker`: 로컬 Rust·Node 없이 검사 (Python 3.11+·Docker 필요)
- `./scripts/build.sh [--docker]`: 구조 검사와 컴파일·빌드
- `python3 scripts/modules.py status --project .`: 설치 목록
- `python3 scripts/modules.py check --project .`: 구조 검사만 실행

## 표준 폴더

| 경로 | 용도 |
| --- | --- |
| `docs/` | 공통 개발 규칙 |
| `scripts/` | 선택한 모듈의 환경 준비·검증 |
| `backend/` (선택) | Rust API, 기능은 `src/features/<기능>/`, 통합 테스트는 `tests/` |
| `frontend/` (선택) | React 앱, 기능은 `src/features/<기능>/`, 테스트는 코드 옆 |
| `config/` (선택) | 비밀이 아닌 YAML 설정 양식 |
| `migrations/` (선택) | PostgreSQL 마이그레이션 양식 |
| `docker/` (선택) | 모듈별 개발·프로덕션 Compose 조각 |
| `knowledge/` (선택) | 원본과 AI 정리 위키 |

## 실행

Rust 모듈은 `cd backend && cargo run --locked`, React 모듈은 `cd frontend && npm run dev`로 실행합니다.
Docker 실행 모듈을 선택했다면 `python3 scripts/compose.py dev up` 또는 `python3 scripts/compose.py prod up --build`를 사용합니다.

추가 모듈은 카탈로그의 `scripts/template-module.py add 모듈 --project 이프로젝트경로 --with-dependencies`로 적용합니다.
프로젝트에 포함된 `scripts/modules.py`는 카탈로그 없이 구조 검사·상태 조회·제거를 지원합니다. 추가에는 카탈로그가 필요합니다.
DB 실행 모듈은 드라이버·업무 스키마를 자동 구현하지 않습니다. 각 선택 모듈의 README를 확인하세요.
