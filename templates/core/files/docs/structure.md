# 모듈 프로젝트 표준

공통부는 문서·에이전트 지침·검사 스크립트·CI·설치 기록입니다. 앱·DB·Docker는 선택 사항입니다.

- 백엔드 기능: `backend/src/features/<기능>/mod.rs`, 외부 API 연결은 `backend/src/lib.rs`에서 합니다.
- 프론트엔드 기능: `frontend/src/features/<기능>/`, 화면 조립은 `frontend/src/App.tsx`에서 합니다.
- 모든 기능을 미리 만들지 않습니다. 공용 코드는 실제 공유 시에만 분리합니다.
- 모듈은 의존 관계·소유 파일·프로젝트에 보존할 초기 파일·명시된 연결 블록을 선언합니다.
- 사용자 코드와 자료를 덮어쓰거나 수정한 소유 파일을 자동 삭제하지 않습니다.
- `scripts/modules.py check --project .`는 의존 관계·필수 파일·연결 블록을 검사합니다.
- 테스트·빌드는 `scripts/check.sh`에서 설치 기록에 있는 앱만 검사합니다.
- `config-yaml`은 설정 양식, `postgres`는 마이그레이션 양식입니다. 로더·DB 드라이버는 앱 요구에 맞게 구현합니다.
- Docker Compose는 선택한 실행 모듈의 파일만 합칩니다. 볼륨은 프로젝트 이름으로 분리합니다.
- 생성 시 기술별 패키지 이름 `backend`·`frontend`는 유지합니다. 사용자 프로젝트 이름과 별개입니다.
