# MCP (Model Context Protocol) 가이드

## 개요

Model Context Protocol(MCP)은 AI 에이전트(Antigravity, Claude 등)가 외부 도구, 데이터베이스, API 및 파일 시스템과 안전하게 통신할 수 있도록 지원하는 개방형 프로토콜입니다.

이 가이드는 프로젝트의 MCP 서버 설정 파일([`.mcp.json`](../../.mcp.json)) 구성 방법과 보안 지침을 다룹니다.

## 설정 파일 구조 (`.mcp.json`)

저장소 루트의 `.mcp.json`에 사용할 MCP 서버 목록을 정의합니다.

```json
{
  "mcpServers": {
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/mydb"]
    }
  }
}
```

## 보안 및 비밀 값 관리 수칙

> [!CAUTION]
> `.mcp.json`은 버전 관리 시스템(Git)에 커밋될 수 있는 파일입니다. 비밀번호, API 키, 인증 토큰 등 민감한 정보를 직접 하드코딩해서는 안 됩니다.

1. **환경 변수 참조**: 민감한 키 값은 `.env` 또는 시스템 환경 변수로 주입합니다.
2. **최소 권한 원칙**: DB 연동 시 가급적 읽기 전용 계정을 연결하거나, 개발/테스트용 로컬 데이터베이스를 사용합니다.
3. **로컬 전용 설정 분리**: 개인 개발용 MCP 서버가 필요하다면 `.gitignore`에 등록된 로컬 전용 설정 파일을 활용합니다.

## 권장 MCP 도구 유형

- **코드베이스 탐색**: 대용량 저장소 검색 및 문서 인덱싱
- **데이터베이스 조회**: 읽기 전용 스키마 및 쿼리 테스트용 DB MCP
- **외부 문서 조회**: 프레임워크나 라이브러리 공식 문서 검색용 MCP

## 도커 컨테이너 환경에서의 MCP (`docker/mcp/`)

에이전트를 로컬 호스트가 아닌 격리된 도커 컨테이너(샌드박스) 내부에서 실행할 경우:

- **설정 디렉토리**: [`docker/mcp/`](../../docker/mcp/README.md)에 컨테이너 내부 에이전트용 MCP 설정 및 스크립트를 관리합니다.
- **네트워크 주소 주의**: 호스트 기준의 `localhost` 대신 도커 네트워크 상의 서비스 이름(예: `db`, `app`)이나 `host.docker.internal`을 사용해야 합니다.
- **볼륨 마운트**: 개발 중인 커스텀 MCP 도구는 컨테이너 재빌드 없이 테스트할 수 있도록 볼륨 마운트하여 연동합니다.
