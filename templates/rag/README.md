# rag 0.1.0

ai-common에 의존하는 작은 오프라인 RAG 모듈입니다. [module.json](module.json)은 기존 Axum 0.7·Tokio 1·Serde 1·serde_json 1 사용과 전체 소유 파일·라우트 연결을 기록합니다. 추가 Cargo 패키지·모델 키·DB·독립 AI 서버는 없습니다.

## 구성

| 파일 | 역할 |
| --- | --- |
| `files/backend/src/features/ai/rag/mod.rs` | 설정 검증, 수집·검색·답변 흐름, timeout·호출 제한·인용 검사 |
| `files/backend/src/features/ai/rag/document.rs` | 문서·revision·reader 목록, Unicode 문자 범위와 인용 타입 |
| `files/backend/src/features/ai/rag/chunk.rs` | Unicode scalar 기준 분할·겹침, 입력·청크 수 상한 |
| `files/backend/src/features/ai/rag/store.rs` | tenant·reader 후보 제한 후 코사인 top-k, revision 교체·삭제·권한 재검증 |
| `files/backend/src/features/ai/rag/mock.rs` | 네트워크 없는 문자 해시 임베딩·원문 발췌 모델 |
| `files/backend/src/features/ai/rag/http.rs` | 기존 app에 합치는 고정 demo 신원의 POST query 라우터 |
| `files/backend/src/features/ai/rag/demo/corpus.json` | 공개 demo 2건과 격리 확인용 다른 tenant 가상 문서 |
| `files/backend/src/features/ai/rag/prompts/answer.v1.md` | 근거만 사용하도록 모델에 전달하는 지시; 권한 검사는 코드가 담당 |
| `files/backend/tests/ai_rag.rs` | 검색·revision·인용·접근·timeout·HTTP 회귀 검사 |

## 추가와 제거

[카탈로그 안내](../README.md)의 명령으로 ai-common → rag 순서로 추가합니다. 공유 파일에는 `template:rag:module`, `template:rag:routes` 블록만 추가됩니다. 기존 `app()`이 mock 라우터를 merge하므로 main.rs·frontend·Docker·Cargo 파일은 수정하지 않습니다.

적용 후 대상 backend에서 `cargo test --locked --test ai_rag`를 실행하고 프로젝트 루트의 `./scripts/check.sh --docker`로 기본형까지 확인합니다. API 요청 예시도 카탈로그에 있습니다.

제거는 rag부터 진행합니다. 모듈 소유 파일·두 연결 블록을 제거하면 query 라우트는 404이고 common과 기존 health 라우트는 유지됩니다. 기존 데이터를 삭제하거나 common을 함께 제거하지 않습니다. 변경된 파일은 자동 제거되지 않으므로 프로젝트 변경을 검토해야 합니다.

## 현재 지원과 교체 경계

`Rag::ingest`는 호스트가 검증하고 정규화한 Document를 받아 메모리 인덱스에 넣습니다. HTTP에는 수집·수정·권한 관리 API가 없으며 호스트 관리 코드가 호출하는 계약입니다. 동일 문서·revision·내용은 중복 저장하지 않고, 내용 변경에는 더 큰 revision이 필요합니다. tenant가 다르면 같은 document ID도 분리됩니다.

문서 reader 목록이 비어 있으면 아무도 조회할 수 없습니다. 검색 전에 tenant·reader를 제한하고 답변 생성 후 삭제·revision·권한을 재검증합니다. 인용이 존재한다는 사실만으로 실제 모델 답변의 의미적 근거 충실도가 입증되지는 않습니다.

모델은 ChatModel, 임베딩은 Embedder 구현으로 바꿀 수 있습니다. 변경한 임베딩 버전·차원을 기존 Rag 인스턴스에 혼합하지 않으며 새 인스턴스에 재색인합니다. 영속 검색 저장소는 아직 MemoryIndex를 대신하는 구현 작업이 필요합니다. 별도 IndexStore trait·수집 CLI·운영 인증·live 공급자·화폐 예산·품질 평가기는 후속 범위입니다.

데모 API의 `meta.mock=true`와 가상 corpus를 실제 사용자 인증·실제 LLM로 오해하지 마세요. 데모 라우트는 기존 `app()`에 합쳐져 백엔드가 열린 모든 곳에서 접근되므로, 공개 배포 전에는 `template:rag:routes` 블록을 지우거나 인증 뒤로 옮기세요. 초기 인덱스는 Tokio OnceCell로 한 번 구성되고 서버 재시작 시 초기화됩니다. 기본 설정은 800자 청크·100자 겹침·top-k 최대 5·코사인 최소 0.2·질문 4000자·출력 2000자이며 문자 해시 예시용 값입니다. 실제 검색·모델 품질 목표는 [평가 설계](../../docs/guides/ai-evaluation.md)에 따라 별도로 설정해야 합니다.
