# 아키텍처

## 1. 시스템 개요

본 프로젝트는 고성능 안정성을 보장하는 **Rust 백엔드 API**와 반응형 사용자 인터페이스를 제공하는 **React (TypeScript) 프론트엔드**, 그리고 **PostgreSQL** 데이터베이스로 구성된 풀스택 템플릿 아키텍처입니다.

```mermaid
flowchart TD
    subgraph ClientLayer["클라이언트 계층"]
        Browser["사용자 브라우저 (Web)"]
    end

    subgraph ContainerNetwork["도커 네트워크 (app-network)"]
        subgraph WebLayer["웹 / 프론트엔드"]
            Frontend["React + TypeScript (Vite/Nginx)<br/>Port: 5173 / 80"]
        end

        subgraph APILayer["백엔드 API"]
            Backend["Rust API 서버 (Axum / Tokio)<br/>Port: 8080"]
        end

        subgraph DataLayer["영속성 / 데이터베이스"]
            Database[("PostgreSQL 16")<br/>Port: 5432]
        end

        subgraph AgentLayer["에이전트 인프라"]
            MCPRunner["컨테이너 내부 에이전트 / MCP<br/>(docker/mcp)"]
        end
    end

    Browser -->|HTTP/HTTPS| Frontend
    Frontend -->|/api/* 리버스 프록시| Backend
    Backend -->|SQL / Connection Pool| Database
    MCPRunner -.->|내부 진단 및 쿼리| Backend & Database
```

---

## 2. 주요 구성 요소

| 모듈 | 디렉터리 경로 | 기술 스택 | 주요 역할 |
|---|---|---|---|
| **Frontend** | [`frontend/`](../../frontend) | React, TypeScript, Vite, Tailwind/CSS | 클라이언트 UI, 사용자 인터랙션, 상태 관리 |
| **Backend** | [`backend/`](../../backend) | Rust, Axum, Tokio, SQLx/Serde | 비즈니스 로직 처리, RESTful API 제공, DB 연결 풀 관리 |
| **Database** | [`migrations/`](../../migrations) | PostgreSQL 16 | 정규화된 데이터 저장, 마이그레이션 관리 |
| **Docker** | [`docker/`](../../docker) | Docker, Docker Compose, Nginx | 컨테이너화, 멀티스테이지 빌드 파이프라인, MCP 연계 |
| **에이전트 연동** | [`docker/mcp/`](../../docker/mcp) | MCP (Model Context Protocol) | 격리된 컨테이너 환경 내 에이전트 도구 제공 |

---

## 3. 통신 및 데이터 흐름

1. **클라이언트 요청**:
   * 브라우저에서 정적 웹 리소스(HTML/JS/CSS)를 프론트엔드 컨테이너(개발: Vite, 상용: Nginx)로부터 수신합니다.
2. **API 호출**:
   * 브라우저의 `/api/*` 요청은 프론트엔드 Nginx를 통해 백엔드 컨테이너(`backend:8080`)로 프록시되어 CORS 제약 없이 안전하게 전달됩니다.
3. **비즈니스 로직 및 DB 연동**:
   * Rust 백엔드는 요청을 역직렬화하고, 비즈니스 규칙을 수행한 뒤 PostgreSQL 커넥션 풀을 통해 트랜잭션을 처리합니다.
4. **결과 반환**:
   * 표준 JSON 규격([API 설계 가이드](api/overview.md) 참조)에 맞춰 클라이언트로 응답을 전송합니다.

---

## 4. 인프라 및 배포 아키텍처

자세한 도커 컨테이너 구성 및 환경별 운용 방법은 [Docker 활용 가이드](docker/README.md)를 참고하세요.
* [단독 실행 가이드 (Standalone)](docker/standalone.md)
* [도커 공유 템플릿 연계 가이드 (Shared Template)](docker/shared-template.md)
* [빌드 최적화 가이드](docker/build-optimization.md)
