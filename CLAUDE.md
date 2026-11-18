# 모듈형 프로젝트 템플릿 카탈로그

이 저장소는 필요한 모듈을 선택해 별도 프로젝트를 조립하는 카탈로그입니다. 루트에 실행 앱을 설치하지 않습니다.

## 폴더 구조

- `templates/<모듈>/module.json`: 버전·의존·소유 파일·초기 자료·공유 연결 블록·Compose 연결 계약
- `templates/<모듈>/files/`: 생성 프로젝트 루트 기준 원본. backend-rust·frontend-react·web-api·config-yaml·postgres·docker 계열·AI·위키 제공
- `templates/core/files/`: 기술 중립 공통부와 생성 프로젝트의 실행·검사·CI
- `scripts/`: 조립 도구, 구조·조합·수명주기 검증
- `docs/`: 카탈로그 및 생성 프로젝트의 개발 가이드
- `tests/`: 검사 배치 안내, 공용 fixture·향후 E2E 자리
- `external/`: 외부 자료 목록
- `.github/`, `.claude/`: 카탈로그 자체의 CI·협업·에이전트 설정

## 명령어

- `python3 scripts/template-module.py list`: 제공 모듈 목록
- `python3 scripts/template-module.py init --name 이름 --project 대상 --preset fullstack`: 새 경로·빈 폴더에 생성, 의존 모듈 자동 포함
- `python3 scripts/template-module.py add 모듈 --project 대상 --with-dependencies --dry-run`: 의존 모듈을 포함한 적용 미리보기
- `python3 scripts/template-module.py check --project 대상`: 설치 기록의 의존·표준 파일·연결 블록 확인
- `./scripts/check.sh --structure`: Python 3.11+로 카탈로그 계약·9개 조합·충돌·위키 보존 검사
- `./scripts/check.sh --docker`: Docker로 위 검사와 AI 수명주기·Rust/React 테스트·빌드 실행
- `./scripts/check.sh`: 같은 전체 검사. 로컬 Rust 1.99.1·rustfmt·Node 22.22.2 이상(22 계열)·npm 필요
- `./scripts/check-template-modules.sh --docker`: AI 모듈 추가·제거·기본형 복원 검사
- 생성 프로젝트에서는 `./scripts/setup.sh`, `./scripts/check.sh [--docker]`, `./scripts/build.sh [--docker]` 사용

## 규칙

- 모든 앱·DB·Docker·AI·위키는 선택 사항입니다. 공통부는 문서·에이전트 지침·조립 기록·검사·CI입니다.
- 원본은 `templates/` 한 곳에 둡니다. 루트 backend·frontend 등에 모듈을 설치하지 않습니다.
- `.env`와 비밀 값(토큰, 키, 비밀번호)은 읽거나 출력하거나 커밋하지 않습니다. 새 환경 변수는 이름만 `.env.example`에 추가합니다.
- 모듈 변경 후 임시 프로젝트에서 구조·조합·적용·제거·자료 보존과 해당 앱 테스트를 검사합니다. 비밀 값·개인 설정·로컬 빌드 산출물을 사본에 복사하지 않습니다.
- `scripts/template-module.py`를 변경하면 배포 사본 `templates/core/files/scripts/modules.py`도 동기화합니다. 검증에서 일치 여부를 확인합니다.
- 일반 코드 수정은 구조 검사에서 허용합니다. 소유 파일 해시와 연결 블록은 자동 제거 시 사용자 변경 보호에 사용합니다. 수정한 연결 블록은 구조 검사도 실패하므로 계약 변경을 검토합니다.
- 개인 설정(`CLAUDE.local.md`, `.claude/settings.local.json`)과 로컬 메모리는 커밋하지 않습니다. Cargo.lock·package-lock.json은 모듈 원본에 커밋하고 CI에서는 갱신하지 않습니다.
- 이미 적용된 마이그레이션은 수정하지 않습니다. 새 번호의 up/down 파일 쌍을 추가합니다.
- 커밋 메시지는 `type: 요약` 형식입니다. 새 폴더·명령은 README 표를 갱신합니다.
- GitHub 저장소와 외부 자료는 `external/`에 이름·URL·용도를 기록합니다.

## 서브에이전트

`.claude/agents/`에는 코드·보안 검토, 조사, 테스트 역할의 정의가 있습니다. 위임 시 필요한 규칙과 맥락을 전달합니다.
