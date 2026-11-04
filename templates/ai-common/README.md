# ai-common 0.1.0

의존 모듈·추가 Rust 패키지·환경 변수·HTTP 라우트가 없는 공통 계약입니다. [module.json](module.json)에 소유 파일과 연결 블록을 기록합니다.

| 파일 | 역할 |
| --- | --- |
| `files/backend/src/features/ai/common/model.rs` | Send Future 기반 ChatModel·Embedder, context 인덱스를 포함한 모델 응답 |
| `files/backend/src/features/ai/common/context.rs` | 호스트가 검증한 tenant·principal·요청 ID, 남은 deadline |
| `files/backend/src/features/ai/common/budget.rs` | 모델·임베딩 호출 전 횟수 예약; 실패해도 환급하지 않음 |
| `files/backend/src/features/ai/common/error.rs` | 입력·시간·예산·revision·근거 변경·공급자 오류의 정규화 코드 |
| `files/backend/tests/ai_common.rs` | 신원 입력, deadline, 호출 제한 검사 |

추가·제거의 실제 명령은 [카탈로그 안내](../README.md)를 따릅니다. ai-common부터 추가하고, 의존 모듈을 모두 제거한 다음 해제합니다. 공유 파일의 연결은 `template:ai-common:module` 블록 하나입니다. 기본 app의 라우트는 바뀌지 않습니다.

추가 후 대상 backend에서 `cargo test --locked --test ai_common`와 기존 `cargo test --locked --test health`를 실행합니다. 제거 후에는 전체 `cargo test --locked`로 남은 기능을 확인합니다.

현재 Budget은 호출 횟수 제한만 구현합니다. 토큰·금액 정산, 실제 공급자 인증, 에이전트 메모리는 구현하지 않았습니다. RequestContext 생성은 인증 성공을 뜻하지 않으며 실제 호스트가 검증한 신원만 넣어야 합니다. deadline은 남은 시간 계약이고, 이를 실제 공급자 Future에 집행하는 것은 rag와 같은 호출 측의 책임입니다.
