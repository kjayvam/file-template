# Changelog

[Keep a Changelog](https://keepachangelog.com/ko/1.1.0/) 형식을 따릅니다.

## [Unreleased]

### Added
- 프로젝트 초기 폴더 구조
- ai-common·rag 선택형 모듈 원본과 추가·제거 도구(`scripts/template-module.py`), 임시 프로젝트 수명주기 검증
- 빌드 컨텍스트별 `.dockerignore`(backend, frontend), Dependabot의 cargo·npm·docker·docker-compose 갱신, CodeQL의 Rust·Actions 분석
- `check.sh`의 Docker 이미지·`rust-toolchain.toml` Rust 버전 일치 검사, 새 프로젝트 시작 시 정리할 자리표시자 목록(`docs/getting-started.md`)

### Changed
- 서버형 DB(`db`)는 `--profile postgres`로만 실행하고, 앱 데이터(`app-data`)와 PostgreSQL 데이터(`pg-data`) 볼륨을 분리
- `check.sh --docker`와 개발 Compose의 Rust 빌드 산출물·`node_modules`를 Docker 볼륨으로 분리
- 백엔드 이미지를 root가 아닌 사용자로 실행하고 SIGTERM에 정상 종료
- 사용하지 않는 Rust 의존성(dotenvy, tower-http, chrono serde feature) 제거
- Release 워크플로가 CI를 재사용하고 쓰기 권한을 쓰지 않도록 변경
- 검사 스크립트의 Rust 이미지 버전을 `rust-toolchain.toml`에서 읽고 Docker 볼륨 접두사를 한 변수로 모음

### Fixed
- Nginx가 `/api/` 접두사를 잘라 프로덕션에서 `/api/v1/health`가 404가 되던 문제
- CI와 시작 안내가 툴체인을 설치하지 않는 `rustup show` 대신 `rustup toolchain install`을 사용
- rag 데모 API가 `top_k` 생략 시 설정과 무관한 고정값 5를 쓰던 문제, `set_readers`의 빈 reader 허용
