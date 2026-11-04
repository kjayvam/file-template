# 선택형 템플릿 모듈

이 폴더는 프로젝트에 적용할 소스 원본입니다. 현재 기본형에는 AI가 설치돼 있지 않습니다. 원본에서 필요한 모듈만 추가하고, 적용한 프로젝트는 이 카탈로그 없이도 빌드·실행할 수 있습니다.

| 모듈 | 의존 관계 | 구현 범위 |
| --- | --- | --- |
| [ai-common](ai-common/README.md) | 없음 | 비동기 모델·임베딩 인터페이스, 신원 문맥·deadline, 호출 횟수 제한 |
| [rag](rag/README.md) | ai-common | 메모리 벡터 검색, 문서 revision·접근 범위, 인용, 오프라인 발췌 데모 |

Agent·UI·별도 서비스·실제 모델·영속 DB는 아직 제공하지 않습니다. 모듈은 기본 Rust 1.99.1, crate 이름 `backend`, 현재 `backend/src/lib.rs`의 라우터 구조를 기준으로 합니다. 그 구조를 변경한 프로젝트는 적용 전에 integration 블록과 테스트 import를 조정하세요.

## 정의와 소유권

각 `module.json`은 버전·의존 모듈·기존 Rust 의존성·소유 파일·공유 연결 블록·검증 명령을 기록합니다. JSON은 Python 표준 라이브러리로 검사하므로 YAML 파서나 pip 설치가 필요 없습니다. `files/` 아래 경로는 적용 대상 프로젝트 루트 기준입니다. `.DS_Store`는 원본 목록에서 제외합니다.

이번 두 모듈은 Cargo.toml·Cargo.lock에 새 의존성을 추가하지 않습니다. rag는 기본형의 Axum 0.7, Serde 1, serde_json 1, Tokio 1의 기존 설정을 재사용합니다. 관리 도구는 의존성 계열을 확인하며 필요한 feature·호환성은 실제 빌드가 확인합니다.

`backend/src/lib.rs`에 이름이 붙은 블록만 연결합니다. 물리 경로는 `src/features/ai/`이며 Rust 공개 경로는 `backend::ai_common`, `backend::rag`입니다. `#[path]`로 연결하므로 공유 `features/mod.rs`를 새로 덮어쓰지 않습니다.

## 추가

Python 3.11 이상이 필요합니다. 아래 명령은 이 템플릿 저장소 루트에서 실행하며 `/path/to/project`를 실제 대상 프로젝트 절대 경로로 바꿉니다. 대상은 이 템플릿에서 복제한 기존 프로젝트입니다. 기본형을 점검하려는 것이라면 추가 대신 아래 임시 프로젝트 검증을 사용하세요.

```bash
python3 scripts/template-module.py list
python3 scripts/template-module.py add ai-common --project /path/to/project --dry-run
python3 scripts/template-module.py add ai-common --project /path/to/project
python3 scripts/template-module.py add rag --project /path/to/project --dry-run
python3 scripts/template-module.py add rag --project /path/to/project
python3 scripts/template-module.py status --project /path/to/project
```

도구는 필요한 의존 모듈을 자동 설치하지 않습니다. rag 전에 ai-common을 명시적으로 추가합니다. 기존 대상 파일, 심볼릭 링크, 유일하지 않은 연결 지점, 지원하지 않는 의존성은 덮어쓰지 않고 실패합니다. `--dry-run`은 기록 파일도 만들지 않습니다.

적용 기록 `.template-modules.json`에는 모듈 버전·소유 파일 해시·연결 블록이 저장됩니다. 변경 이력에 함께 보관하세요. `status`는 적용 기록을 표시하며, 파일 변경 충돌 검사는 add/remove 시 수행합니다. 제거할 때까지 기록을 임의로 지우지 마세요.

## 적용 후 검증과 실행

대상 프로젝트에서 실행합니다.

```bash
./scripts/check.sh --docker
```

Rust·Node가 설치되어 있으면 `./scripts/check.sh`도 같습니다. Rust 테스트는 복사된 `backend/tests/ai_common.rs`, `backend/tests/ai_rag.rs`를 자동 발견합니다. 기존 CI가 check.sh를 실행하면 적용한 모듈 테스트도 함께 실행하므로 별도 공급자 키·AI 서비스가 필요하지 않습니다.

대상 프로젝트의 백엔드를 실행하면 rag 적용 시에만 아래 API가 추가됩니다. 데모 데이터·고정 demo 신원만 사용합니다.

```bash
cd backend
cargo run --locked
```

```bash
curl -X POST http://localhost:8080/api/ai/v1/query \
  -H 'content-type: application/json' \
  -d '{"question":"로그 보관 기간은 7일입니다.","top_k":1}'
```

응답의 `meta.mock`은 true입니다. 이 데모는 문자 해시 임베딩과 원문 발췌이며 실제 의미 검색·LLM 품질을 검증한 것이 아닙니다. 질문 본문의 tenant·principal 지정은 거부합니다. 실제 문서에는 호스트의 인증 경계에서 만든 RequestContext와 실제 어댑터를 연결해야 합니다.

## 제거

카탈로그 저장소에서 대상 프로젝트를 지정합니다. 반대 의존 순서로 제거합니다.

```bash
python3 scripts/template-module.py remove rag --project /path/to/project --dry-run
python3 scripts/template-module.py remove rag --project /path/to/project
python3 scripts/template-module.py remove ai-common --project /path/to/project
```

rag가 남아 있으면 ai-common 제거는 거부됩니다. 소유 파일이나 등록 블록을 프로젝트에서 수정했으면 자동 제거는 실패하며 어떤 경로인지 알려줍니다. 강제 덮어쓰기·강제 제거 옵션은 없습니다. 이 경우 프로젝트 변경을 별도 기능으로 옮길지 검토하고 소유 파일·연결 지점을 수동으로 정리한 뒤 적용 기록도 실제 상태에 맞춰 갱신하세요.

정상 제거는 해당 모듈 파일과 등록 블록만 지우고 공유 파일의 다른 변경·다른 파일·`var/ai/` 데이터는 보존합니다. 빈 디렉터리만 정리하며 마지막 모듈을 제거하면 적용 기록도 제거합니다. 이번 두 모듈은 Cargo 파일을 변경하지 않으므로 lock 갱신도 필요 없습니다.

대상 프로젝트에서 `./scripts/check.sh --docker`를 다시 실행합니다. rag만 제거했다면 common 테스트는 남고 query API는 404여야 합니다. 둘 다 제거하면 health API와 기존 React만 남습니다. 실제로 공급자·DB를 추가한 프로젝트는 별도 의존성·설정·마이그레이션·데이터 정리도 검토해야 합니다.

## 템플릿 원본의 전체 검증

```bash
./scripts/check-template-modules.sh --docker
```

현재 체크아웃에 모듈을 적용하지 않고 임시 프로젝트에서 base → common → rag+common → common → base 순서로 Rust 포맷·컴파일·테스트와 라우트 상태를 확인합니다. 제거는 카탈로그가 없는 독립 도구 사본으로도 검사합니다. 의존 순서·덮어쓰기·심볼릭 링크·사용자 변경·dry-run 거부 검사와 데이터·기존 Cargo 파일 보존도 확인합니다.

Docker는 임시 프로젝트와 전용 `file-template-modules-target` 빌드 캐시, 기존 Cargo 다운로드 캐시를 사용합니다. 원본 backend·templates·scripts는 읽기 전용으로 마운트하고 `.env`·개인 설정은 복사하지 않습니다. 네이티브 검증은 Python 3.11+, Rust·rustfmt 설치 후 같은 명령에서 `--docker`를 빼면 됩니다.
