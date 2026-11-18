# 테스트 배치와 검증

카탈로그 검사와 생성 프로젝트의 앱 검사를 구분합니다.

| 검사 | 위치·명령 |
| --- | --- |
| 계약·초기화·조합·충돌·앱 제거 | scripts/verify-projects.py |
| 위키 자료 보존·AI 모듈 수명주기 | scripts/verify-template-modules.py |
| 카탈로그 전체 | ./scripts/check.sh --docker |
| Python 구조·보존 검사 | ./scripts/check.sh --structure |
| 생성 프로젝트 구조·앱 테스트·빌드 | 생성 프로젝트에서 ./scripts/check.sh [--docker] |

조합은 최소형·Rust 단독·React 단독·풀스택·위키·Docker Rust·Docker React·Docker DB·전체 조립의 9가지입니다. Docker가 있으면 dev/prod Compose config도 확인합니다. 전체 검사에서는 Rust 단독·React 단독·전체 조립의 실제 테스트·빌드를 실행하고, Rust AI 모듈은 추가·제거 단계마다 포맷·테스트·라우트 상태를 확인합니다.

원본 테스트는 templates/<모듈>/files/ 아래에 있습니다. 생성 후 Rust 단위 테스트는 backend/src의 cfg(test), API 통합 테스트는 backend/tests, React 테스트는 frontend/src의 코드 옆, 공통 설정은 frontend/src/test/setup.ts입니다. 앞으로 E2E 러너를 도입하면 생성 프로젝트 tests/e2e, 공용 자료는 tests/fixtures를 사용합니다. 현재 E2E 러너는 제공하지 않습니다.

검증은 TemporaryDirectory에서 하고 종료하면 소스·빌드 산출물 사본을 지웁니다. Rust·Node 검사 캐시는 Docker 볼륨에 남습니다. 실제 .env·개인 설정·운영 자료를 검증 사본에 복사하지 않습니다. 소유 파일·연결 블록 충돌 시 프로젝트가 그대로인지, 위키 자료와 사용자 파일이 제거 후에도 보존되는지 검사합니다.
