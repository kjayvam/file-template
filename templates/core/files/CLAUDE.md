# __PROJECT_NAME__

이 프로젝트는 선택형 모듈로 조립했습니다. `.template-modules.json`의 모듈만 사용합니다.
기능 폴더와 검증 규칙은 `docs/structure.md`, 실행 방법은 `README.md`를 확인하세요.

## 규칙

- 요청 범위의 구현·검증을 완료합니다. 선택하지 않은 앱·DB·AI를 임의로 추가하지 않습니다.
- `.env`와 비밀 값을 읽거나 출력하거나 커밋하지 않습니다. 환경 변수의 이름은 `.env.example`에 기록합니다.
- 기능은 `backend/src/features/<기능>/`, `frontend/src/features/<기능>/`에 배치합니다.
- Rust API 통합 테스트는 `backend/tests/`, React 테스트는 대상 코드 옆에 둡니다.
- 변경 후 `./scripts/check.sh`를 실행합니다. 모듈 추가·제거 후에도 구조·테스트·빌드를 확인합니다.
- 적용한 마이그레이션은 수정하지 않습니다. 새 up/down 파일 쌍을 추가합니다.
- 설치 기록은 커밋합니다. 소유 파일을 수정한 모듈은 자동 제거하지 않으므로 수동 병합합니다.
