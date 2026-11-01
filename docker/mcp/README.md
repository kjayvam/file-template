# Docker MCP 가이드

## 개요

도커 컨테이너 내부에서 구동되는 AI 에이전트(샌드박스, 자동화 러너 등)를 위한 MCP(Model Context Protocol) 서버 구성 및 도구 설정 디렉토리입니다.

## 주요 역할

- **컨테이너 내부 에이전트 지원**: 에이전트가 격리된 컨테이너 환경에서 코드 빌드, 테스트 실행, DB 쿼리 등을 수행할 때 필요한 MCP 서버를 제공합니다.
- **도커 네트워크 연동**: 호스트(`localhost`)가 아닌 동일 도커 네트워크 상의 서비스(예: `db:5432`, `app:3000`)와 직접 통신할 수 있는 MCP 환경을 구성합니다.

## 컨테이너 환경 MCP 설정 예시

컨테이너 내부에서 실행되는 에이전트는 컨테이너 내부의 `.mcp.json`을 통해 도구를 호출합니다:

```json
{
  "mcpServers": {
    "postgres-internal": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://my_project:change-me@db:5432/my_project"
      ]
    }
  }
}
```

> **네트워크 참고**:
> - 같은 Compose 네트워크 내 서비스와 통신할 때는 컨테이너 서비스 이름(`db`, `app` 등)을 호스트명으로 사용합니다.
> - 호스트 머신의 서비스에 접근해야 하는 경우 `host.docker.internal`을 사용합니다.

## 디렉토리 관리 규칙

1. 에이전트 컨테이너 이미지 빌드 시 필요한 전용 Dockerfile이나 보조 스크립트는 이 디렉토리(`docker/mcp/`)에 함께 보관합니다.
2. 개발 중 MCP 도구 코드를 신속히 수정해야 할 경우, `docker-compose` 설정에서 이 디렉토리를 컨테이너 내부로 볼륨 마운트하여 사용합니다.
3. 데이터베이스 비밀번호나 API 키 등 민감한 정보는 환경 변수로 주입하며, 파일 내에 하드코딩하지 않습니다.
