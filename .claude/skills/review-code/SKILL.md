---
name: review-code
description: 지정한 파일이나 폴더를 code-reviewer 서브에이전트에서 검토한다.
context: fork
agent: code-reviewer
disable-model-invocation: true
background: false
argument-hint: "[파일 또는 폴더]"
---

다음 대상의 코드를 검토하세요: $ARGUMENTS

버그, 빠진 예외 처리, 하드코딩된 비밀 값, CLAUDE.md의 규칙 위반, 빠진 테스트를 확인하고 심각도가 높은 순서로 `파일경로:줄번호`와 함께 정리하세요.
대상이 비어 있으면 `src/` 폴더를 검토하세요.
