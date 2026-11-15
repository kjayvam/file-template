---
name: security-checklist
description: 이 프로젝트의 보안 검토 체크리스트. 코드, 설정, Docker, 워크플로, 마이그레이션을 보안 관점에서 검토할 때 참고한다.
---

# 보안 체크리스트

## 비밀 값
- 토큰, 키, 비밀번호가 코드, 설정 파일, 워크플로, 예시 파일에 직접 적혀 있지 않은가
- `.env`와 비밀 값이 `.gitignore`와 `.dockerignore`에 들어 있는가
- 새로 쓰는 `.env.<이름>` 파일이 `.claude/settings.json`의 Read 거부 목록에 있는가
- `.env.example`에는 가짜 값만 있는가

## 입력과 데이터베이스
- 사용자 입력을 검증하는가
- SQL을 문자열로 이어 붙이지 않고 매개변수로 넘기는가
- 마이그레이션이 데이터를 의도치 않게 지우지 않는가

## Docker
- 컨테이너가 root가 아닌 사용자로 실행되는가
- Nginx 응답에 기본 보안 헤더가 빠진 location이 없는가 (location의 `add_header`는 server 값을 상속하지 않음)
- 이미지에 `.env`나 개발용 파일이 들어가지 않는가
- DB 포트나 비밀번호가 필요 이상으로 노출되지 않는가

## GitHub Actions
- 워크플로 `permissions`가 필요한 만큼만 열려 있는가
- 외부 액션이 커밋 SHA와 버전 주석(`@<sha> # vX.Y.Z`)으로 고정되어 있는가
