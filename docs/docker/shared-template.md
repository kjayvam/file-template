# 도커 공유 템플릿 연계 가이드 (Shared Template Integration)

본 템플릿은 `도커 공유 템플릿`(`agent-kit`, `p-tools`, `creative-toolkit` 등)이 구축된 호스트 서버에서 손쉽게 연계하여 사용할 수 있도록 설계되었습니다.

이 가이드는 `도커 공유 템플릿`의 핵심 철학인 **자원 공유(`sync_*`)와 프로젝트 격리(`p_*`), 볼륨 보존(Keeper 패턴), AI 에이전트 연동**을 본 템플릿에 적용하는 방법을 설명합니다.

---

## 1. 연계 개요 및 원칙

1. **무조건적인 강제가 아닌 선택적 적용**:
   * 모든 볼륨을 `sync_`로 둘 필요는 없습니다.
   * Crate 캐시처럼 호스트 전체에서 공유할 가치가 큰 자원만 `sync_`로 승격하고, DB 데이터나 앱 설정은 반드시 `p_*`로 프로젝트 단위를 격리합니다.
2. **에이전트 러너와의 분리**:
   * 본 템플릿의 앱 서비스(Frontend, Backend, DB)와 에이전트 실행 환경(`agent-kit`)은 명확히 분리됩니다.
   * 에이전트는 컨테이너 내부에서 [docker/mcp](../../docker/mcp/README.md)를 통해 격리된 네트워크 상의 앱이나 DB와 안전하게 상호작용합니다.

---

## 2. agent-kit 설치 및 에이전트 연동

`도커 공유 템플릿`이 있는 서버에서 본 프로젝트로 에이전트 환경을 이식하는 절차입니다.

```bash
# 1. 도커 공유 템플릿의 agent-kit을 현재 프로젝트 루트로 설치
<도커-공유-템플릿-경로>/agent-kit/scripts/install.sh .

# 2. 프로젝트 초기화 (공용 인증 볼륨 및 프로젝트 전용 상태 볼륨 준비)
./agent-kit/scripts/bootstrap.sh

# 3. 에이전트 실행 (컨테이너 내에서 안전하게 프로젝트 코드 작업 수행)
./agent-kit/scripts/agent.sh --instance main run claude
```

* **공용 인증 재사용**: 서버에서 이미 로그인한 자격 증명(`sync_agent_auth`)을 그대로 사용하여 별도 재인증이 불필요합니다.
* **프로젝트 상태 격리**: 대화 및 메모리는 `p_agent_state_<PROJECT_ID>_<INSTANCE>` 볼륨으로 완전히 분리됩니다.

---

## 3. 볼륨 보존을 위한 Keeper 패턴 (`x-keeper`) 적용

`도커 공유 템플릿`의 Keeper 패턴을 적용하면, Docker Desktop이나 시스템 정리(`docker system prune`) 시에도 볼륨과 고정 이미지가 삭제되지 않습니다.

공유 템플릿 환경에서 사용할 별도 `docker/compose.keeper.yml` 예시:

```yaml
name: my-project-keeper

x-keeper: &keeper
  image: sync_tools:template
  pull_policy: never
  command: ["true"]
  restart: "no"
  network_mode: none
  labels:
    agent-kit.role: volume-keeper

services:
  # 프로젝트 전용 데이터 보호 컨테이너 (정지 상태 보관)
  project-keeper:
    <<: *keeper
    container_name: p-myproject-keeper
    volumes:
      - p_db_data:/volumes/p_db_data:ro
      - p_agent_state:/volumes/p_agent_state:ro

volumes:
  p_db_data:
    external: true
    name: p_db_data_myproject
  p_agent_state:
    external: true
    name: p_agent_state_myproject_main
```

> [!TIP]
> 생성 명령: `docker compose -f docker/compose.keeper.yml create`
> * 컨테이너를 실행(`start`/`up`)할 필요 없이 생성(`create`)만 해두면 볼륨 참조가 유지되어 안전하게 보호됩니다.

---

## 4. 선택적 빌드 캐시 공유 (`sync_cargo_cache`)

팀/서버 단위로 여러 Rust 프로젝트를 진행할 때, Crate 레지스트리 캐시를 호스트 단위로 공유하여 빌드 시간을 단축할 수 있습니다.

```yaml
# docker-compose.dev.yml 또는 override 설정 예시
services:
  backend:
    volumes:
      - sync_cargo_cache:/usr/local/cargo/registry

volumes:
  sync_cargo_cache:
    external: true
    name: sync_cargo_cache
```

* 호스트에 `sync_cargo_cache` 볼륨이 이미 존재하면 이를 재사용하고, 없을 때는 로컬 `cargo-cache` 볼륨을 사용하는 방식으로 유연하게 전환합니다.

---

## 5. 컨테이너 내부 MCP 에이전트 연동

에이전트가 컨테이너 내부에서 개발을 진행할 때, 프로젝트의 데이터베이스나 API 엔드포인트에 안전하게 접근할 수 있습니다.

* 상세 설정 및 보안 지침: [`docker/mcp/README.md`](../../docker/mcp/README.md) 및 [`docs/guides/mcp.md`](../guides/mcp.md)
* 컨테이너 네트워크 통신: `db:5432` 및 `backend:8080`을 통해 동일 도커 브리지 네트워크 상에서 직접 질의합니다.
