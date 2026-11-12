# Changelog

[Keep a Changelog](https://keepachangelog.com/ko/1.1.0/) 형식을 따릅니다.

## [Unreleased]

### Added
- 프로젝트 초기 폴더 구조
- ai-common·rag 선택형 모듈 원본과 추가·제거 도구(`scripts/template-module.py`), 임시 프로젝트 수명주기 검증
- 빌드 컨텍스트별 `.dockerignore`(backend, frontend), Dependabot의 cargo·npm·docker 갱신, CodeQL의 Rust·Actions 분석

### Changed
- 서버형 DB(`db`)는 `--profile postgres`로만 실행하고, 앱 데이터(`app-data`)와 PostgreSQL 데이터(`pg-data`) 볼륨을 분리
- `check.sh --docker`와 개발 Compose의 Rust 빌드 산출물·`node_modules`를 Docker 볼륨으로 분리
- 백엔드 이미지를 root가 아닌 사용자로 실행하고 SIGTERM에 정상 종료
- 사용하지 않는 Rust 의존성(dotenvy, tower-http, chrono serde feature) 제거
- Release 워크플로가 CI를 재사용하고 쓰기 권한을 쓰지 않도록 변경

### Fixed
- Nginx가 `/api/` 접두사를 잘라 프로덕션에서 `/api/v1/health`가 404가 되던 문제
- rag 데모 API가 `top_k` 생략 시 설정과 무관한 고정값 5를 쓰던 문제, `set_readers`의 빈 reader 허용
