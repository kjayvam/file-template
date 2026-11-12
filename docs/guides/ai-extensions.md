# 프로젝트별로 조합하는 RAG·Agent 템플릿 설계

상태: ai-common·rag 0.1.0의 원본·추가·제거 도구·임시 프로젝트 검증은 구현했습니다. 실제 사용은 [템플릿 카탈로그](../../templates/README.md)를 따릅니다. 아래 Agent·UI·별도 서비스·live 평가·영속 저장소는 후속 설계입니다.

## 1. 템플릿의 사용 원칙

이 저장소는 프로젝트를 시작하는 재료입니다. Rust·React 기본형에서 출발하되 필요한 기능만 추가하고, 사용하지 않는 기능은 코드·의존성·설정·테스트·CI까지 제거할 수 있어야 합니다. 모든 프로젝트에 동일한 AI 서비스·콘솔·배포 구성을 요구하지 않습니다.

기본 배치는 기존 backend 안의 기능 모듈과 기존 frontend 안의 선택 화면입니다. 별도 Rust workspace·AI 서버·독립 React 콘솔은 처리량·운영 경계·체험 목적에 따라 선택하는 배치 대안입니다. RAG·Agent·둘의 조합은 예시 조합이며 고정된 제품 모드 목록이 아닙니다.

템플릿에 있는 예제와 모듈 원본은 프로젝트 생성 후 삭제해도 제품 코드가 동작해야 합니다. 운영 코드는 templates/를 런타임 경로로 참조하지 않습니다. 현재는 모듈별 적용·해제 안내와 작은 파일 관리 도구를 제공합니다. Python 3.11 표준 라이브러리만 사용하며 전용 프로젝트 생성 프레임워크는 필요하지 않습니다. 변경된 파일의 강제 제거는 지원하지 않습니다.

## 2. 선택 가능한 모듈

| 모듈 | 의존 관계 | 선택하는 경우 | 제거할 때의 영향 |
| --- | --- | --- | --- |
| ai-common | 없음 | 모델 호출·신원 문맥·예산 인터페이스 필요 | rag·agent 등 사용 모듈이 없을 때 제거 가능 |
| rag | ai-common | 문서 검색과 근거 기반 답변 | 검색 라우트·수집·인덱스 설정·RAG 평가만 제거 |
| agent | ai-common | 제한된 도구 실행 | 실행 라우트·도구·메모리·Agent 평가만 제거 |
| rag-agent | rag + agent | Agent가 지식 검색도 사용 | 검색 도구 연결만 제거; RAG·Agent 단독 기능 유지 |
| ai-ui | rag 또는 agent 중 하나 이상 | 기존 React에 체험·업무 화면 필요 | 화면·API client·UI 테스트만 제거 |
| ai-service | rag 또는 agent 중 하나 이상 | 별도 서버·worker 배치 필요 | 서비스·통신·배포 설정 제거; 기능 모듈의 대체 배치를 먼저 결정 |

모델 공급자, 임베딩·검색 저장소, PDF 파서, 영속 메모리는 해당 모듈 안의 교체 가능한 어댑터입니다. 하나를 교체하기 위해 RAG·Agent 전체를 바꾸지 않습니다. Agent는 RAG를 직접 의존하지 않으며 rag-agent 연결 모듈이 검색 Tool을 등록합니다.

## 3. 템플릿 원본과 적용 후 구조

아래는 통합 배치의 전체 설계 예시입니다. ai-common·rag의 현재 정확한 파일 목록은 각 module.json을 참고하세요. 나머지 모듈·CLI·평가 디렉터리는 아직 구현하지 않았습니다.

```text
templates/
  README.md                         # 조합 예시·적용 순서·불필요한 원본 정리 방법
  ai-common/
    README.md                       # 적용·해제 절차와 연결 변경
    module.json                     # 의존 모듈·소유 파일·공유 연결 지점·검사 목록
    files/backend/src/features/ai/common/
      mod.rs
      model.rs
      context.rs
      budget.rs
      error.rs
    files/backend/tests/ai_common.rs
  rag/
    README.md
    module.json
    files/backend/src/features/ai/rag/
      mod.rs
      document.rs
      chunk.rs
      store.rs
      mock.rs
      http.rs
      demo/corpus.json
      prompts/answer.v1.md
    files/backend/tests/ai_rag.rs
    files/evals/ai/rag/               # (후속) 해당 기능의 사례·fixture·rubric·기준값
  agent/
    README.md
    module.json
    files/backend/src/features/ai/agent/
      mod.rs
      runner.rs
      state.rs
      tool.rs
      policy.rs
      memory.rs
      prompts/planner.v1.md
    files/backend/tests/ai_agent.rs
    files/evals/ai/agent/
  rag-agent/
    README.md
    module.json
    files/backend/src/features/ai/tools/search_knowledge.rs
    files/backend/tests/ai_rag_agent.rs
  ai-ui/
    README.md
    module.json
    files/frontend/src/features/ai/
      api/client.ts
      rag/{QueryPage.tsx,QueryPage.test.tsx,Sources.tsx}
      agent/{RunPage.tsx,RunPage.test.tsx,RunTimeline.tsx}
  ai-service/
    README.md                       # 독립 배치 예시와 모듈 이동·연결 절차
    module.json
    files/services/ai/
      Cargo.toml
      src/{main.rs,lib.rs,routes.rs,identity.rs,config.rs}
    files/docker/docker-compose.ai.yml
```

ai-ui는 선택된 기능의 하위 파일만 적용합니다. Rag만 쓰는 프로젝트에 Agent 화면·타입·테스트를 복사하지 않습니다. 별도 모델 어댑터를 만들 때는 common 아래 providers/에 구현하고 실제 공유가 생겼을 때만 별도 crate로 추출합니다.

예를 들어 RAG만 선택한 소규모 프로젝트의 결과는 다음과 같습니다. 템플릿 원본 폴더는 결과물에 없어도 됩니다.

```text
backend/
  Cargo.toml, Cargo.lock            # 선택한 모듈의 의존성만 추가
  src/lib.rs                        # 선택한 기능의 라우터 연결
  src/features/ai/{common/,rag/}    # lib.rs에서 #[path]로 연결하므로 features/ai/mod.rs는 없음
  src/bin/ai_ingest.rs               # 수집 CLI가 필요한 경우만 추가
  tests/ai_rag.rs
evals/ai/
  manifest.json                     # 선택 모듈·지표·데이터 버전
  runner/                           # 해당 모듈용 평가 실행기
  rag/{datasets/,fixtures/,rubrics/,thresholds/,baselines/}
config/ai/rag.toml
scripts/{check-ai.sh,eval-ai.sh}
```

UI도 선택하면 frontend/src/features/ai/rag/를 추가하고, Agent를 선택하지 않으면 Agent 관련 파일·설정·테스트는 없습니다. 별도 서비스로 분리하는 프로젝트는 기능 코드를 services/ai/의 모듈 또는 crate에 배치하고 독립 Cargo.lock을 사용합니다. 통합 배치는 기존 backend/Cargo.lock을 사용합니다. 이미 수정한 코드를 배치 변경 과정에서 자동 덮어쓰거나 삭제하지 않습니다.

모듈 원본의 경로는 통합 배치를 기준으로 설명합니다. 별도 서비스 전환은 파일 이동·import·신원 전달·API 프록시를 검토하는 별도 작업이며 설정 한 줄만으로 자동 이관된다고 약속하지 않습니다. Cargo workspace가 필요해질 때는 [공식 문서](https://doc.rust-lang.org/cargo/reference/workspaces.html)의 잠금 파일·빌드 범위를 따릅니다.

## 4. 추가·제거·교체 규칙

module.json은 검토 가능한 의존·파일·연결 목록입니다. 현재 template-module.py가 이 중 소유 파일·연결 블록·의존 관계를 사용하고 적용 당시 해시를 기록합니다. checks·data_paths_to_preserve·new_rust_dependencies 필드는 현재 선언 전용이며 도구가 실행·검사하지 않습니다. 확장 시 목표 스키마는 다음 정보를 기록합니다.

- 모듈 ID·버전·필수 의존·함께 사용하는 선택 모듈.
- 모듈이 전적으로 소유하는 경로와 Cargo·라우터·설정·CI 같은 공유 파일의 연결 지점.
- 추가하는 dependency·feature·환경 변수 이름·라우트·마이그레이션·검사.
- 적용 후 검사, 제거 후 검사, 사용자 데이터 보존·정리 항목.

추가할 때는 필요한 모듈과 전이 의존만 적용하고 변경 목록을 확인한 뒤 검증합니다. 제거할 때는 의존하는 모듈을 먼저 확인하고, 라우트·UI 연결·설정·검사 등록을 해제한 다음 모듈 소유 파일과 더 이상 쓰지 않는 의존성을 정리합니다. 공유 파일 전체나 다른 모듈이 사용하는 ai-common을 삭제하지 않습니다.

프로젝트에서 수정한 파일은 적용·제거 시 diff로 확인하고 자동 덮어쓰기·자동 삭제 대상에서 제외합니다. 현재 도구는 원본 버전·적용 당시 해시를 기록하고 변경된 파일은 자동 제거하지 않고 수동 병합 대상으로 남깁니다. 실제 문서·대화·인덱스·DB 데이터 삭제는 코드 제거와 별개입니다. 적용된 마이그레이션은 지우거나 수정하지 않고 필요한 경우 새 마이그레이션으로 변경합니다.

런타임 비활성화와 템플릿 제거는 다릅니다. 전자는 코드·의존성을 남기고 등록만 끄는 것이고, 후자는 관련 파일·의존성·설정·테스트·CI 참조를 함께 정리하는 것입니다. Cargo feature는 필요할 때의 빌드 선택 수단이며 제거 기능을 대신하지 않습니다.

공급자·저장소 교체 시에는 인터페이스 계약·fixture 테스트를 먼저 확인하고 새 어댑터를 연결합니다. 새 임베딩 모델·차원·chunker는 기존 인덱스를 재사용하지 않고 새 세대로 재색인합니다. 실제 선택하지 않은 공급자 SDK·DB는 의존성이나 Docker 서비스에 넣지 않습니다.

## 5. 배치와 설정

| 프로젝트 상황 | 권장 출발 배치 | 추가하지 않아도 되는 것 |
| --- | --- | --- |
| AI 없는 웹 앱 | 현재 Rust·React | AI 파일·모델 키·AI 평가·서비스 전체 |
| 작은 문서 검색 앱 | backend의 common+rag, 필요하면 기존 React 화면 | Agent·독립 콘솔·별도 AI 서버 |
| 도구 자동화 API | backend의 common+agent | RAG·임베딩·벡터 DB·AI 화면 |
| 검색을 쓰는 Agent | common+rag+agent+연결 도구 | 별도 서비스·독립 콘솔은 여전히 선택 |
| AI 처리량·격리 요구가 큰 앱 | services/ai/로 기능 분리 | 기존 backend에 AI 구현을 중복 보관하지 않음 |

Mock·live는 모듈의 실행 구성입니다. Mock은 가상 모델·문서·도구로 기능을 검사하고, live는 프로젝트가 선택한 실제 어댑터를 사용합니다. Live 설정이 없을 때 mock으로 몰래 대체하지 않습니다. 환경 변수에는 키를 주입하고 정책·모델 ID·실행 제한은 검토 가능한 설정에 둡니다.

실제 모듈만 라우터·UI·평가기에서 등록합니다. UI가 있으면 capabilities API로 활성 기능을 확인할 수 있고, UI가 없으면 capabilities나 체험 화면 자체를 필수로 만들지 않습니다. API 접두사와 공통 응답 형식은 프로젝트 규칙에 맞춰 조정하되 신원·근거·실행 상태 계약은 유지합니다.

아래 기능별 계약은 모듈을 선택한 경우에만 적용합니다. 수집 CLI·장기 메모리·독립 콘솔처럼 필요하지 않은 세부 기능은 적용 목록에서 제외하고 평가 항목도 그 범위에 맞게 명시합니다.

## 6. RAG 동작과 데이터 계약

6~9절은 확장할 때의 목표 계약입니다. 현재 0.1.0은 메모리 검색·revision·접근 범위·인용·호출 횟수·deadline과 가상 HTTP 데모를 구현했습니다. 수집 CLI·영속 인덱스·운영 인증·live 공급자·토큰/금액 정산·Agent는 아직 없습니다. 현재 지원 범위는 [rag 안내](../../templates/rag/README.md)를 기준으로 확인하세요.

초기 입력 형식은 UTF-8 Markdown·텍스트와 가상 corpus JSON 배열(`demo/corpus.json`)로 제한합니다. PDF·웹 크롤러·OCR은 후속 어댑터입니다. 처음부터 파일 업로드·작업 큐까지 만들지 않고 `ai_ingest` CLI로 검증된 입력을 색인합니다.

메모리 저장소를 쓰는 첫 버전에서 CLI는 정규화된 corpus snapshot과 manifest를 `var/ai/corpus/`에 작성합니다. 서버가 이 snapshot을 읽어 **자기 프로세스 안에서** 임베딩·인덱스를 구성합니다. CLI 프로세스의 메모리 인덱스를 서버가 공유한다고 가정하지 않습니다. 문서 변경은 snapshot 갱신 후 서버 재시작으로 반영하고, 온라인 갱신 API는 후속 범위로 남깁니다. Lifecycle 테스트는 같은 프로세스에서 변경·삭제·권한 회수 계약을 검사합니다.

수집 흐름은 `입력 검증 → 정규화 → 내용 해시 → 분할 → 임베딩 → 새 인덱스 세대 생성 → 교체`입니다. 조회 흐름은 `검증된 신원 → 접근 가능한 문서 집합 → top-k 검색 → 근거 선택 → 답변 → 인용 유효성 확인`입니다.

| 타입 | 필수 필드 |
| --- | --- |
| `RequestContext` | 서버가 검증한 `principal_id`, `tenant_id`, 접근 범위, `request_id`, 예산·deadline |
| `Document` | `tenant_id`, `document_id`, `revision`, `content_hash`, `source_uri`, 접근 메타데이터, 정규화된 본문 |
| `Chunk` | 위 문서 식별자, `chunk_id`, 정규화 본문의 문자 범위, 본문, 임베딩 버전 |
| `Citation` | `document_id`, `revision`, `chunk_id`, 인용 문자 범위·텍스트 |
| `Answer` | `status = answered/insufficient_evidence`, 답변·인용 목록, `trace_id`, 사용량 |

동일 내용 재수집은 중복을 만들지 않습니다. 수정 시 새 revision을 만들고, 인덱스 전체에 chunker·임베딩 모델·벡터 차원·정규화 버전을 기록합니다. 이 값이 달라지면 새 세대를 완성한 후 교체합니다. 조회는 하나의 세대에 고정해 구버전과 신버전 근거가 섞이지 않게 합니다.

삭제와 접근 권한 회수는 조회용 필터에 먼저 반영하고, 진행 중인 응답도 반환 직전에 다시 권한·삭제 상태를 확인합니다. 검색 전에 tenant·접근 범위를 제한하며 top-k 이후 필터링으로 대신하지 않습니다. 답변·캐시 키에도 tenant·접근 범위 버전·인덱스 세대가 필요합니다. 초기 버전에는 답변 캐시를 넣지 않습니다.

단순 코사인 유사도 `MemoryIndex`를 기본 예제로 두되, 운영 규모의 저장 성능을 보장하는 구현으로 설명하지 않습니다. 검색 점수 기준은 모델마다 달라 설정·평가로 보정합니다. 사용할 수 있는 근거가 없으면 `insufficient_evidence`를 반환하며, 주장이 참임을 인용 ID 존재 여부만으로 판단하지 않습니다.

## 7. Agent 실행 계약

첫 버전은 단일 Agent의 제한된 루프입니다. `planner.v1.md`가 구조화된 다음 행동을 제안하고, 코드가 스키마·권한·잔여 예산을 검사한 후 도구를 실행합니다. 멀티 Agent, 범용 브라우저·셸·파일 쓰기는 첫 범위에 넣지 않습니다.

상태는 `queued → running → succeeded/failed/cancelled/timed_out/budget_exceeded`입니다. 대기 중 취소는 `queued → cancelled`로 전환합니다. 실패·취소·제한 초과를 성공으로 기록하지 않습니다. 모델이 완료했다고 말해도 필수 도구 결과가 없으면 성공으로 전환하지 않습니다. 최종 목표 달성 여부는 평가기의 독립 검증으로 다시 판정합니다.

| 초기 도구 | 동작 | 필요한 모듈 |
| --- | --- | --- |
| `calculator` | 허용 연산만 파싱하는 계산기; 코드 eval 금지 | agent |
| `lookup_fixture` | 가상 데이터에서 식별자로 조회 | mock 체험과 격리된 live 평가 |
| `search_knowledge` | 현재 신원의 접근 범위로 RAG 검색 | rag-agent |

도구는 이름·입출력 스키마·효과 종류·호출 timeout을 선언합니다. 최초 정책은 읽기 전용만 허용합니다. 모델이 제안한 미등록·쓰기 도구는 실행 전에 거부합니다. 문서와 도구 응답 속 지시는 사용자 권한을 변경하지 못합니다.

메모리는 기본적으로 `tenant + principal + run_id` 단위의 단기 상태입니다. 장기 메모리·사용자 간 공유는 추후 별도 저장·동의·삭제 정책이 필요한 선택 기능으로 남깁니다. `.claude/agent-memory/`에는 제품의 사용자 데이터나 실행 상태를 저장하지 않습니다.

시작 제한 제안은 run당 모델 결정 6회, 도구 호출 4회, 전체 30초, 도구당 5초입니다. 재시도도 카운트·시간·비용에 포함하며 읽기 전용의 일시 오류에만 1회 허용합니다. 취소 토큰·deadline을 모델과 도구 호출까지 전달합니다. 클라이언트가 연결을 끊는 것과 명시적 취소는 구분하고, 상태 조회·취소 API를 제공합니다.

## 8. API·콘솔 계약

모든 경로는 AI 호스트의 `/api/ai/v1` 아래에 둡니다. 제안한 최소 API는 다음과 같습니다.

| 메서드·경로 | 기능 | 결과 |
| --- | --- | --- |
| `GET /health` | 서버 생존 | 모델을 호출하지 않고 200 |
| `GET /api/ai/v1/capabilities` | 활성 기능·mock 여부 | enabled 목록과 API 계약 버전 |
| `POST /api/ai/v1/query` | RAG 질의 | 200; answered 또는 insufficient_evidence |
| `POST /api/ai/v1/runs` | Agent 실행 생성 | 202와 run_id; Idempotency-Key 지원 |
| `GET /api/ai/v1/runs/{id}` | 실행 상태·허용된 도구 요약 | 200; 다른 신원의 실행은 노출하지 않음 |
| `POST /api/ai/v1/runs/{id}/cancel` | 취소 요청 | 202; 이후 상태 조회로 종료 확인 |

query 입력은 질문과 허용된 검색 옵션, runs 입력은 목표와 허용된 업무 입력입니다. `tenant_id`, 도구 목록, 모델 공급자 URL, 시스템 프롬프트를 클라이언트가 임의로 주입할 수 없게 합니다. 생성 API의 idempotency 저장 범위는 신원+키+요청 해시이며, 첫 버전에는 프로세스 생존 기간에만 유효합니다.

초기 데모에서는 `POST /runs`가 in-process task를 생성하고 실행 저장소도 메모리입니다. 서버 재시작 시 실행·idempotency 기록은 사라집니다. 영속 큐·재시작 복구를 지원한다고 약속하지 않습니다. Live 평가에서 `lookup_fixture`는 실제 모델의 도구 사용 능력을 측정하기 위한 고정 도구이며, 외부 업무 API 연동의 정확성까지 검증한 것으로 보고하지 않습니다.

업무 응답은 `{success:true,data:{...},meta:{trace_id,usage}}`, 오류는 `{success:false,error:{code,message},meta:{trace_id}}`로 통일합니다. 입력 오류 400, 신원 없음 401, 권한 없음 403, 없는 기능·리소스 404, 같은 idempotency 키의 다른 요청 409, 호출 예산·동시 실행 제한 429, 공급자 장애 502, deadline 초과 504를 구분합니다. 이미 202로 생성된 run의 실행 중 오류는 상태 조회의 종료 상태로 표현합니다.

UI를 선택했다면 첫 화면은 polling으로 구현하고 SSE는 필요할 때 추가합니다. RAG 화면은 질문·답변·열람 가능한 출처와 근거 부족 상태, Agent 화면은 목표·진행 상태·도구 결과 요약·취소를 보여줍니다. 내부 추론 원문을 타임라인에 노출하지 않습니다. mock 배지와 재시작 시 데이터 초기화 안내는 표시합니다.

통합 배치에서는 기존 UI 5173/API 8080을 사용하므로 별도 AI 포트가 필요하지 않습니다. 독립 서비스나 체험 콘솔을 선택한 프로젝트에서만 AI API 8090·콘솔 5174 같은 추가 포트와 docker-compose.ai.yml을 둡니다. 기존 앱에 붙이는 화면과 독립 콘솔을 모두 만들 필요는 없습니다.

독립 배치를 선택한 경우에만 Vite/Nginx가 `/api/ai/`를 별도 AI 서버로 프록시합니다. Nginx의 `proxy_pass http://ai-api:8090;`처럼 후행 URI를 붙이지 않아 경로를 보존합니다. 프로덕션 콘솔은 별도 host 포트 8081, AI API는 내부 네트워크만 사용합니다. 통합 배치에서는 기존 프록시 경로를 재사용하되 API 접두사가 보존되는지 확인합니다.

## 9. 신원·사용량·실행 기록

현재 rag 0.1.0의 mock 데모 라우트(`POST /api/ai/v1/query`)는 기존 `app()`에 합쳐지므로, 백엔드가 열린 모든 곳(프로덕션 Compose의 8080 포트와 Nginx `/api/` 프록시 포함)에서 접근됩니다. 고정 demo 신원과 가상 corpus만 쓰지만, 공개 배포 전에는 이 라우트를 제거하거나 실제 인증 뒤로 옮깁니다. 실제 프로젝트에서는 기존 인증 체계의 검증된 문맥을 주입합니다. 요청의 임의 tenant 헤더를 신뢰하지 않습니다. 테스트에서는 주입된 IdentityResolver로 여러 신원을 검증합니다. 공유·외부 공개 전에 실제 인증 어댑터와 문서 권한 저장소가 필요하며, 아직 기본 템플릿에 인증이 구현돼 있다고 가정하지 않습니다.

Live 사용량은 입력·출력 토큰, 임베딩량, 모델·가격표 버전으로 계산합니다. 모델 호출 전에 최대 출력과 입력을 포함한 예상 상한을 예약하고, 실제 사용량으로 정산합니다. 가격표나 사용량을 얻지 못하면 비용 0으로 취급하지 않고 `unknown`·예약액 유지로 기록합니다. 예산을 집행할 수 없는 live 설정은 거부합니다.

로그에는 request/run ID, 종료 상태, 소요 시간, 호출 수, 토큰·비용, 문서 식별자, 설정·프롬프트 버전을 남깁니다. 키·원문 문서·질문·내부 추론은 기본 로그에 넣지 않습니다. 오류 응답에는 내부 공급자 오류 원문 대신 정규화한 오류를 반환합니다.

## 10. 구현 순서와 평가 범위

첫 구현으로 ai-common·rag 원본·가상 corpus·통합 테스트와 소유권 기반 추가·제거 도구를 제공합니다. 현재 실제 명령은 ./scripts/check-template-modules.sh --docker이며 base부터 두 모듈 적용·역순 제거까지 검사합니다. 아래 check-ai.sh·eval-ai.sh는 향후 품질 평가 CLI 제안입니다. Agent·연결 도구·UI·독립 서비스는 필요한 순서에 추가합니다. 모든 모듈의 빈 폴더를 제품 기본형에 미리 만들지 않습니다.

프로젝트별 manifest는 선택 모듈·배치·제공 API·검사 목록·평가 기준 버전을 기록합니다. 예시 조합에는 base, rag-only, agent-only, rag-with-agent가 있지만 사용자는 인증·배치 작업·기존 검색기 등과 새 조합을 만들 수 있습니다.

템플릿 자체의 검증은 아래를 확인합니다.

1. 기본형은 AI 키·의존성·서비스 없이 검사된다.
2. 각 모듈을 최소 의존만으로 적용하면 관련 테스트·빌드가 통과한다.
3. 해당 모듈을 제거하면 라우터·import·설정·CI에 끊어진 참조가 없고 남은 기능이 통과한다.
4. rag-agent 연결만 제거해도 RAG·Agent 단독 기능이 유지된다.
5. 모듈 원본인 templates/를 제거해도 적용된 프로젝트가 동작한다.
6. 어댑터를 교체해도 계약 테스트를 통과하고 품질 기준선은 새 구성으로 평가된다.

선택형 검사 스크립트를 도입한다면 아래와 같은 명령을 제공할 수 있습니다. 현재 존재하는 명령이 아니며 생성기를 먼저 만들 필요는 없습니다.

```bash
./scripts/check-ai.sh --modules rag
./scripts/check-ai.sh --modules agent
./scripts/check-ai.sh --modules rag,agent,rag-agent
./scripts/eval-ai.sh --suite rag --profile project-rag --budget-usd 5
```

기존 기본형의 ./scripts/check.sh는 그대로 둡니다. 템플릿을 복제한 프로젝트가 기본 frontend·Docker 등까지 제거하는 경우에는 그 프로젝트가 선택한 구성에 맞게 README·검사·CI도 함께 조정합니다. 검사 대상을 조용히 건너뛰어 성공으로 보고하는 방식은 사용하지 않습니다.

세부 지표는 [AI 평가 기준](ai-evaluation.md)의 카탈로그를 참고하고 프로젝트별 데이터·시간·비용·품질 기준을 설정합니다. 선택하지 않은 모듈은 평가 대상 밖이라고 기록하며 선택한 모듈의 필수 검사를 누락한 것과 구분합니다. 구조 선택 이유는 [ADR-0001](../adr/0001-optional-ai-extensions.md)에 기록합니다.
