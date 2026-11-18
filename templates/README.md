# 모듈 카탈로그

앱 전체를 복제하는 대신 필요한 모듈을 조립합니다. 실행 원본은 `templates/<id>/files/`에 있고 경로는 생성 프로젝트 루트 기준입니다. 모듈 목록은 `python3 scripts/template-module.py list` 또는 [루트 안내](../README.md#모듈과-조립)를 확인하세요.

## 생성과 추가

Python 3.11 이상이 필요합니다. 프로젝트 이름은 소문자로 시작하는 영문·숫자·하이픈입니다. `init`은 새 경로 또는 빈 폴더만 허용하며 기본 `core`와 의존 모듈을 함께 설치합니다.

```bash
python3 scripts/template-module.py init --name sample --project ../sample --preset fullstack --modules rag llm-wiki --dry-run
python3 scripts/template-module.py init --name sample --project ../sample --preset fullstack --modules rag llm-wiki
python3 scripts/template-module.py add docker-web-api --project ../sample --with-dependencies
python3 scripts/template-module.py check --project ../sample
python3 scripts/template-module.py status --project ../sample
```

프리셋은 `minimal`(core), `api`(Rust), `web`(React), `fullstack`(앱+API 연결), `fullstack-docker`(앱+API 연결+Docker), `knowledge`(위키)입니다. 프리셋은 편의 목록일 뿐 필수 아키텍처가 아닙니다. `--modules`만으로 직접 조립할 수 있습니다.

`add`는 기본적으로 의존 모듈이 먼저 설치돼 있어야 합니다. `--with-dependencies`는 누락된 의존 모듈도 함께 조립합니다. 경로·의존 순환·연결 지점·소유 파일 충돌을 모든 쓰기 전에 확인합니다. `--dry-run`은 대상 폴더와 기록도 만들지 않습니다.

## 모듈 계약

- `schema_version`, `id`, `version`: 형식과 식별자·버전
- `requires`: 선행 모듈. 생성·일괄 추가 시 위상 정렬하고, 역의존 모듈이 있으면 제거 거부
- `owned_files`: 코드·설정·테스트 등 모듈 소유 파일. 기존 파일 덮어쓰기 금지, 설치 해시와 다르면 제거 거부
- `seed_files`: 프로젝트 소유로 전환되는 초기 자료. 기존 일반 파일 재사용, 제거 후에도 보존. 디렉터리·심볼릭 링크 충돌 거부
- `render_files`: 프로젝트 이름 자리표시자 `__PROJECT_NAME__`를 치환할 파일의 명시적 목록. 코드·잠금 파일에 무차별 치환하지 않음
- `integrations`: 공유 파일에 추가할 `path`·고유 `anchor`·`position`·이름 있는 `block`. 수정된 블록 자동 제거 금지
- `rust_package`: 소비하는 기존 crate 이름 또는 `null`. Rust 기반 원본을 제공하는 backend-rust 자체는 null, AI 모듈은 backend
- `existing_rust_dependencies`: 필요한 기존 버전 계열. 실제 feature 호환성은 컴파일로 확인
- `compose_files`: dev/prod별 Compose 조각. 설치 기록 순서대로 합치므로 기반 서비스 뒤에 연결 모듈 배치
- `checks`, `new_rust_dependencies`, `data_paths_to_preserve`: 사람을 위한 선언. 명령 자동 실행이나 새 패키지 자동 설치를 뜻하지 않음

모든 원본 파일은 owned 또는 seed 한 곳에 등록합니다. `.DS_Store`는 무시합니다. `core`는 제거하지 않습니다. 프로젝트 이름은 사용자 이름이고 `backend`·`frontend`는 기술 패키지 이름으로 유지합니다. 기존 crate·라우터를 변경한 프로젝트에는 AI 모듈의 integration과 import를 먼저 조정하세요.

`.template-modules.json`에 이름·설치 순서·버전·의존·해시·연결 블록·Compose 파일을 기록합니다. 커밋하고 임의로 지우지 않습니다. `status`는 기록 조회이고 `check`는 의존 관계·필수 파일·연결 블록의 구조 검사입니다. 일반 코드의 사용자 수정은 구조 검사에서 허용하며 빌드·테스트로 검증합니다. 임의의 모든 폴더 이름을 검사하거나 업무 설계를 자동 판단하지는 않습니다.

## 제거와 보존

```bash
python3 scripts/template-module.py remove rag --project ../sample --dry-run
python3 scripts/template-module.py remove rag --project ../sample
# 생성 프로젝트 안에서는 카탈로그가 없어도 제거 가능
python3 ../sample/scripts/modules.py remove ai-common --project ../sample
```

역의존 순서로 제거합니다. 예를 들어 docker-web-api → docker-react·docker-rust → web-api → frontend-react·backend-rust 순서에서 각 모듈의 의존을 해제합니다. 설치 기록에 저장한 연결 블록을 해제한 뒤 기본 앱을 제거합니다. 사용자 변경이 있으면 실패하며 강제 제거 옵션은 없습니다. 수동 병합과 기록 정리가 필요합니다.

위키·기존 자료·추가한 사용자 파일·DB 볼륨·빌드 산출물은 지우지 않습니다. 마지막 모듈 제거 후에도 사용자 파일이 있는 폴더는 남습니다. 설치형 앱의 seed 자료가 아닌 코드도 사용자 수정 시 자동 삭제하지 않습니다. 템플릿 업데이트 자동 병합·버전 업그레이드는 제공하지 않으며 새 모듈 버전 적용은 별도 검토가 필요합니다.

## 실행과 검증

생성 프로젝트의 `./scripts/check.sh [--docker]`는 core의 구조 검사와 설치한 앱의 테스트·빌드를 실행합니다. CI도 같은 명령을 사용하며 Python·Docker만 있으면 로컬 Rust·Node가 필요 없습니다. `./scripts/build.sh [--docker]`는 테스트 없이 컴파일·빌드합니다.

Docker는 `docker` 공통 도구에 `docker-rust`, `docker-react`, `docker-postgres`를 골라 붙입니다. `docker-web-api`는 프록시 연결까지 포함하는 조합입니다. `python3 scripts/compose.py dev up`, `prod up --build`로 선택한 서비스만 실행합니다. 프로젝트 이름으로 네트워크·볼륨을 구분합니다. postgres는 실행 환경·마이그레이션 양식이며 앱 드라이버를 설치하지 않습니다. config-yaml도 로더를 설치하지 않습니다.

카탈로그 자체는 `./scripts/check.sh --structure`, 전체 검사는 `./scripts/check.sh --docker`로 확인합니다. 위키만은 `python3 scripts/verify-template-modules.py --wiki-only`입니다. Rust 원본·잠금 파일과 기본 앱은 임시 프로젝트에만 조립합니다.

## 새 모듈 작성

1. `templates/<id>/files/`에 대상 프로젝트 기준으로 코드·설정·테스트·문서를 함께 배치합니다.
2. 인접한 module.json을 참고해 소유 파일·초기 자료·의존 관계·필요한 연결 블록을 선언합니다. 한 파일에 소유자를 중복 배치하지 않습니다.
3. 공유 파일 전체를 복사해 덮어쓰지 말고 고유한 연결 블록을 사용합니다. Rust 기능은 backend/src/features/<기능>/, React 기능은 frontend/src/features/<기능>/에 배치합니다.
4. Docker 조각은 JSON 문법의 YAML로 작성합니다. 경로는 프로젝트 루트 기준이며 compose_files에 등록합니다. 비밀 값은 넣지 않습니다.
5. scripts/verify-projects.py에 의미 있는 조합·실패·제거 검사를 추가하고 `./scripts/check.sh --docker`를 실행합니다.
6. 루트 README 모듈 표를 갱신합니다. 모듈 안에는 앱 실행 시 카탈로그를 참조하는 코드를 넣지 않습니다.
