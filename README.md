# 모듈형 프로젝트 템플릿

필요한 모듈만 선택해 표준 폴더 구조의 프로젝트를 생성하는 카탈로그입니다. 이 저장소 자체는 앱이 아니며, Rust·React·DB·Docker·AI·위키를 모든 프로젝트에 강제하지 않습니다.

## 프로젝트 생성

Python 3.11 이상이 필요합니다. 저장소 루트에서 실행하며 대상은 새 경로 또는 빈 디렉터리여야 합니다.

```bash
# 최소 공통 구조만 생성
python3 scripts/template-module.py init --name my-app --project ../my-app

# 백엔드 단독 / 프론트엔드 단독 / 풀스택
python3 scripts/template-module.py init --name my-api --project ../my-api --preset api
python3 scripts/template-module.py init --name my-web --project ../my-web --preset web
python3 scripts/template-module.py init --name my-fullstack --project ../my-fullstack --preset fullstack

# Docker 풀스택 + PostgreSQL 실행 환경 + RAG + 위키
python3 scripts/template-module.py init --name my-service --project ../my-service \
  --preset fullstack-docker --modules docker-postgres rag llm-wiki --dry-run
# 미리보기 확인 후 같은 명령에서 --dry-run을 빼고 생성합니다.
```

프로젝트 이름·페이지 제목·Docker 프로젝트 이름과 검사 볼륨 이름은 자동 적용됩니다. 기술 패키지 이름 `backend`, `frontend`는 모듈 연결 계약으로 유지합니다. 생성된 프로젝트는 이 카탈로그 없이 실행·검증할 수 있습니다. 모듈 추가 시에만 카탈로그가 필요합니다.

## 모듈과 조립

| 모듈 | 용도 | 직접 의존 |
| --- | --- | --- |
| `core` | 문서·에이전트 지침·검사·CI·환경 변수 양식 | 없음, init에서 항상 포함 |
| `backend-rust` | Axum API와 테스트, Rust 버전 고정 | core |
| `frontend-react` | 독립 React 앱과 테스트, Node 의존성 고정 | core |
| `web-api` | React에서 Rust health API 조회 | backend-rust, frontend-react |
| `config-yaml` | 환경별 설정 양식, 로더는 프로젝트에서 구현 | core |
| `postgres` | PostgreSQL 마이그레이션 양식, 드라이버는 프로젝트에서 구현 | core |
| `docker` | 선택한 Compose 조각을 합치는 실행 도구 | core |
| `docker-rust` / `docker-react` | 각 앱의 Dockerfile과 dev/prod Compose | docker, 해당 앱 |
| `docker-postgres` | PostgreSQL 컨테이너와 영속 볼륨 | docker, postgres |
| `docker-web-api` | Docker 내 API 프록시 연결 | web-api, docker-rust, docker-react |
| `ai-common` | 모델·임베딩 인터페이스, 요청 문맥·호출 제한 | backend-rust |
| `rag` | 오프라인 검색·인용 데모, 실제 LLM·영속 DB 제외 | ai-common |
| `llm-wiki` | Obsidian용 자료·정리 문서·공통 에이전트 지침 | 없음 |

`init`은 의존 모듈을 함께 조립합니다. 기존 프로젝트의 `add`는 `--with-dependencies`를 지정할 때 의존 모듈을 자동으로 추가합니다. 모든 변경을 미리 검사한 뒤 한 번에 적용하며 충돌하면 일부 모듈만 설치하지 않습니다.

```bash
python3 scripts/template-module.py list
python3 scripts/template-module.py add rag --project ../my-app --with-dependencies --dry-run
python3 scripts/template-module.py add rag --project ../my-app --with-dependencies
python3 scripts/template-module.py check --project ../my-app
python3 scripts/template-module.py status --project ../my-app
python3 scripts/template-module.py remove rag --project ../my-app --dry-run
```

설치 기록 `.template-modules.json`은 커밋합니다. 기존 파일을 덮어쓰지 않으며, 수정한 소유 파일은 자동 제거하지 않습니다. 역의존 모듈을 먼저 제거하고 `core`는 유지합니다. 위키 초기 자료와 사용자 파일·실행 데이터는 보존합니다. 상세 규약은 [카탈로그 안내](templates/README.md)를 참고하세요.

## 폴더 구조

| 경로 | 용도 |
| --- | --- |
| `templates/<모듈>/module.json` | 버전·의존 관계·소유권·연결 지점·검사·Compose 파일 계약 |
| `templates/<모듈>/files/` | 생성 대상 프로젝트의 루트 기준 파일 원본 |
| `scripts/template-module.py` | 프로젝트 생성·모듈 추가·제거·상태·구조 검사 |
| `scripts/check.sh` | 카탈로그 계약, 조합, 모듈 수명주기와 앱 검사 |
| `scripts/verify-projects.py` | 임시 프로젝트의 독립 앱·풀스택·Docker 조합 검사 |
| `scripts/verify-template-modules.py` | 위키 보존 및 AI 모듈 추가·제거 회귀 검사 |
| `scripts/check-template-modules.sh`, `scripts/docker-common.sh` | Rust 수명주기 검증과 Docker 검사 캐시 |
| `docs/` | 카탈로그 사용법, 생성 프로젝트의 개발·아키텍처 가이드 |
| `tests/` | 검증 배치 안내와 향후 공용 fixture·E2E 자리 |
| `external/` | 외부 자료의 이름·URL·용도 |
| `.github/` | 카탈로그 자체의 CI·의존성 관리·협업 설정 |
| `.claude/` | 카탈로그 작업용 에이전트 설정·스킬·규칙 |

실행할 `backend/`, `frontend/`, `docker/`, `config/`, `migrations/`는 생성 프로젝트에 선택적으로 만들어집니다. 카탈로그 원본은 `templates/`에만 둡니다. 과거 체크아웃의 무시된 빌드 산출물·개인 파일은 자동 삭제하지 않습니다.

## 검증

```bash
# Python + Docker로 소스 계약·9가지 조합·Rust/React 테스트·빌드 검증
./scripts/check.sh --docker

# Python만으로 구조·충돌·자료 보존 검사 (Docker가 있으면 Compose 설정도 검사)
./scripts/check.sh --structure

# Rust 모듈 추가·제거만 검사
./scripts/check-template-modules.sh --docker
```

생성 프로젝트에서는 `./scripts/setup.sh`, `./scripts/check.sh [--docker]`, `./scripts/build.sh [--docker]`를 사용합니다. `check.sh`는 설치 기록에 있는 앱만 검사합니다. Docker 검증은 비밀 값을 읽지 않으며 Rust·Node를 로컬에 설치할 필요가 없습니다. 프론트엔드 빌드 산출물은 임시 생성 프로젝트 안에 생성되고 검사 캐시는 Docker 볼륨에 남습니다.

[시작하기](docs/getting-started.md) · [구조와 계약](docs/architecture.md) · [모듈 작성](templates/README.md#새-모듈-작성) · [테스트](tests/README.md)
