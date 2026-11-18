# 시작하기

이 저장소는 카탈로그입니다. 앱은 별도 경로에 생성합니다. Python 3.11 이상이 필요합니다.

## 템플릿으로 새 프로젝트 시작하기

```bash
python3 scripts/template-module.py list
python3 scripts/template-module.py init --name my-app --project ../my-app --preset fullstack --dry-run
python3 scripts/template-module.py init --name my-app --project ../my-app --preset fullstack
```

프리셋: minimal·api·web·fullstack·fullstack-docker·knowledge. `--modules`로 모듈을 더하거나 프리셋 없이 직접 선택할 수 있습니다. 의존 모듈은 함께 조립합니다. 대상은 새 경로 또는 빈 디렉터리이고 상위 디렉터리는 있어야 합니다. 경로에 공백이 있으면 셸에서 따옴표로 감쌉니다.

프로젝트 이름·페이지 제목·Docker 프로젝트 이름·검사 볼륨은 자동 적용됩니다. 소유자·라이선스·배포 계정 같은 프로젝트별 정보는 프로젝트 요구에 맞게 추가합니다. 카탈로그의 Git 이력·개인 설정·.env·문서 전체를 복사하지 않습니다.

## 생성 프로젝트에서 실행

```bash
cd ../my-app
./scripts/setup.sh
./scripts/check.sh --docker
```

구조 검사·스크립트에는 Python 3.11 이상이 필요합니다. 로컬 앱 실행에는 선택한 Rust 1.99.1(rustfmt 포함) 또는 Node 22.22.2 이상(22 계열)·npm이 필요합니다. Rust는 `rust-toolchain.toml`로 고정하고 두 앱의 잠금 파일을 버전 관리합니다. Docker 검사에는 로컬 Rust·Node가 필요 없습니다.

- Rust: `cd backend && cargo run --locked`. 기본 8080, `PORT`로 변경. .env 자동 로드 없음
- React: `cd frontend && npm run dev`. 기본 localhost:5173. 백엔드 없이 실행 가능
- web-api를 선택하면 /api/v1/health를 조회하고 Vite가 localhost:8080으로 전달
- Docker 실행 모듈을 선택하면 `python3 scripts/compose.py dev up` 또는 `prod up --build`
- docker-web-api가 컨테이너 간 프록시 연결을 설정
- docker-postgres를 선택하면 .env에 DATABASE_NAME·DATABASE_USER·DATABASE_PASSWORD를 지정. 앱 드라이버·스키마·접속 코드 별도 구현

`setup.sh`는 .env가 없을 때만 .env.example을 복사합니다. 프론트엔드가 있을 때만 npm ci를 실행합니다.

## 추가·제거·검사

카탈로그 루트에서:

```bash
python3 scripts/template-module.py add rag --project ../my-app --with-dependencies --dry-run
python3 scripts/template-module.py add rag --project ../my-app --with-dependencies
python3 scripts/template-module.py check --project ../my-app
python3 scripts/template-module.py remove rag --project ../my-app --dry-run
```

적용 후 생성 프로젝트에서 `./scripts/check.sh [--docker]`를 실행합니다. 빌드만은 `./scripts/build.sh [--docker]`, 앱 하나만은 `./scripts/check.sh --backend` 또는 `--frontend`입니다. 선택하지 않은 앱에 대한 검사는 실패합니다. core만 있으면 구조 검사만 합니다.

추가에는 카탈로그가 필요합니다. 생성된 scripts/modules.py는 카탈로그 없이 check·status·remove를 지원합니다. 역의존 모듈을 먼저 제거하며 사용자 변경·데이터를 자동 삭제하지 않습니다. [모듈 계약](../templates/README.md)을 확인하세요.

## 버전 변경

Rust는 templates/backend-rust/files/rust-toolchain.toml과 templates/docker-rust의 Dockerfile·dev Compose를 함께 변경합니다. Node는 frontend-react의 package.json·package-lock.json·@types/node와 docker-react의 이미지, core의 project-check.py 이미지를 함께 검토합니다. 변경 후 `./scripts/check.sh --docker`를 실행합니다. 실행 환경 버전은 최신이라고 가정하지 않고 잠금 파일과 기존 검증 기준을 유지합니다.
