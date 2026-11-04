# 기여 가이드

기여해 주셔서 감사합니다.

## 작업 흐름

1. 저장소를 fork 하거나 새 브랜치를 만듭니다. (`feature/기능명`, `fix/버그명`)
2. 변경 사항을 작성하고 테스트를 추가합니다.
3. `./scripts/check.sh`로 포맷·컴파일·테스트·프론트엔드 빌드가 통과하는지 확인합니다. 로컬 도구가 없으면 `./scripts/check.sh --docker`를 사용합니다.
4. Pull Request를 열고 템플릿의 항목을 채웁니다.

## 커밋 메시지

`type: 요약` 형식을 권장합니다. (예: `feat: 로그인 API 추가`, `fix: 날짜 파싱 오류 수정`)

## 테스트와 의존성

- 테스트 위치와 실행 명령은 [테스트 안내](tests/README.md)를 따릅니다.
- 프론트엔드 의존성은 `cd frontend && npm ci`로 설치합니다.
- 의존성을 변경할 때는 `backend/Cargo.lock` 또는 `frontend/package-lock.json`도 함께 갱신합니다. CI는 `--locked`와 `npm ci`로 잠금 파일을 사용합니다.
- `./scripts/build.sh`는 컴파일·빌드만 수행하며 테스트를 대신하지 않습니다.

## 이슈 등록

버그와 기능 제안은 이슈 템플릿을 사용해 주세요.

## 행동 강령

[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)를 따릅니다.
