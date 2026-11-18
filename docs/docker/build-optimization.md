# 모듈별 빌드와 캐시

- docker-rust 원본: templates/docker-rust/files/backend/Dockerfile
- docker-react 원본: templates/docker-react/files/frontend/Dockerfile
- 앱 잠금 파일: backend-rust의 Cargo.lock, frontend-react의 package-lock.json

Rust 프로덕션 이미지는 고정한 cargo-chef로 의존 레시피를 만든 뒤 release 바이너리를 빌드합니다. React는 npm ci와 Vite 빌드 후 비특권 Nginx에 정적 파일을 복사합니다. 빌드 컨텍스트의 .dockerignore는 비밀 값과 호스트 산출물을 제외합니다.

개발 Compose는 Cargo 다운로드·Rust target·Node 의존성을 각각 볼륨에 둡니다. 생성 프로젝트의 check.sh --docker도 프로젝트 이름으로 분리한 검사 볼륨을 사용합니다. 검사 도구 이미지는 기본 이미지와 설치 명령의 해시로 재사용합니다. 이미지 자체는 공용이지만 프로젝트의 빌드 산출물·의존성 볼륨은 분리됩니다.

Rust 버전은 backend-rust의 rust-toolchain.toml과 docker-rust의 Dockerfile·dev Compose를 함께 바꿉니다. 생성 프로젝트 검사에서 일치를 확인합니다. Node는 frontend-react의 engines·잠금 파일·타입 패키지와 docker-react 이미지·core 검사 이미지를 함께 검토합니다.

카탈로그 Rust 수명주기 검사 캐시는 file-template-check-cargo와 file-template-modules-target입니다. 생성 프로젝트 검사 캐시는 <프로젝트이름>-check-cargo·-check-target·-check-node-modules입니다. 캐시 정리는 다른 프로젝트에서 사용 중인지 확인한 뒤 직접 수행합니다.
