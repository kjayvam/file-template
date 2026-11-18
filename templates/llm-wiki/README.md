# LLM Wiki 모듈 0.1.0

카파시의 [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 패턴을 바탕으로 한 최소 Markdown 보관함입니다. 원본은 다른 모듈과 같은 `module.json`·`files/` 구조로 관리하며, 적용하면 프로젝트 루트에 `knowledge/`를 만듭니다. Claude Code·Codex가 같은 문서를 관리하고 Obsidian에서 태그·링크·그래프로 탐색할 수 있습니다.

`.claude/`는 Claude 전용 설정·메모리 위치입니다. 여러 도구가 공유할 위키 본문은 `knowledge/`에 둡니다. Rust·ai-common·rag·커뮤니티 플러그인 의존성이 없는 독립 모듈입니다. 문서 전용 프로젝트에서도 Python 3.11 이상과 이 템플릿의 루트 지침 파일만 있으면 사용할 수 있습니다.

## 프로젝트에 추가

카탈로그 저장소 루트에서 실행하며 `/path/to/project`는 실제 대상 프로젝트 절대 경로로 바꿉니다. 기본형 저장소에는 미리 적용하지 않습니다.

```bash
python3 scripts/template-module.py list
python3 scripts/template-module.py add llm-wiki --project /path/to/project --dry-run
python3 scripts/template-module.py add llm-wiki --project /path/to/project
python3 scripts/template-module.py status --project /path/to/project
```

관리 도구는 `knowledge/`의 초기 파일을 만들고 루트 `CLAUDE.md`의 `## 규칙` 앞에 이름이 붙은 위키 지침 블록을 연결합니다. 이 템플릿의 루트 `AGENTS.md`는 `CLAUDE.md`를 읽도록 연결되어 있어 Codex와 Claude Code가 같은 규칙을 사용합니다. 루트 지침 구조를 바꾼 프로젝트는 해당 진입점과 연결 지점을 먼저 맞추세요. 연결 지점을 찾지 못하거나 여러 개면 파일을 쓰지 않고 실패합니다.

위키 파일은 `seed_files`로 정의합니다. 처음에는 원본으로 생성하고, 같은 경로의 일반 파일이 이미 있으면 내용을 덮어쓰지 않고 재사용합니다. 디렉터리·심볼릭 링크 충돌은 거부합니다. `--dry-run`에서는 추가·재사용·지침 연결 경로를 표시하고 어떤 파일도 쓰지 않습니다. 적용 기록은 다른 모듈과 같은 `.template-modules.json`에 저장합니다.

기존 폴더 복사 방식으로 `knowledge/`를 만든 프로젝트도 같은 add 명령으로 등록할 수 있습니다. 기존 자료는 재사용하며, 예전에 직접 적은 위키 지침이 있다면 중복된 문장만 정리하세요.

## Obsidian에서 시작

1. Obsidian에서 기존 폴더를 보관함으로 열고 대상 프로젝트의 `knowledge/`를 선택합니다. 이 카탈로그의 `files/knowledge/`를 직접 작업용으로 쓰지 않습니다.
2. 기본 플러그인인 Templates를 켜고 템플릿 폴더 위치를 `templates`로 지정합니다. 설정 경로는 [공식 Templates 안내](https://help.obsidian.md/plugins/templates)를 참고하세요.
3. `raw/`에 글·논문·직접 작성한 메모를 넣습니다. 첨부 자료가 필요하면 `raw/assets/`를 만듭니다.
4. 프로젝트에서 실행 중인 에이전트에게 아래 수집 요청을 합니다. `knowledge/`만 별도로 열어 작업할 때도 내부의 `AGENTS.md`·`CLAUDE.md`가 공통 규칙을 안내합니다.
5. `wiki/index.md`, 태그 보기, 백링크·그래프에서 결과를 확인합니다. 태그를 붙이는 것만으로 문서 사이의 링크가 생기지는 않으므로 에이전트가 관련 문서 링크도 함께 작성합니다.

태그는 [공식 태그 안내](https://help.obsidian.md/tags)에 따라 YAML의 `tags` 목록으로 작성합니다. 역할은 `wiki/source`·`wiki/topic`, 주제는 `topic/rust` 같은 형태로 구분합니다. 본문에서 `#topic/rust`로도 사용할 수 있습니다. 상태는 태그와 중복 관리하지 않고 `status` 속성에 기록합니다.

## 요청 예시

**수집**

> knowledge/README.md를 읽고 raw에 새로 넣은 자료를 정리해 줘. 원본은 유지하고 원본별 요약, 관련 주제 문서, 태그, 출처 링크, 색인, 로그를 갱신해 줘.

**질의**

> 이 프로젝트에서 검색 방식을 비교해 줘. knowledge/wiki/index.md에서 관련 문서를 찾고 출처를 붙여 답해 줘. 근거가 부족한 부분은 구분해 줘.

**점검**

> 위키의 끊어진 링크, 출처 누락, 오래된 주장, 충돌, 고립 문서를 점검해 줘. 확인 가능한 것은 수정하고 확인이 필요한 주장은 표시해 줘.

폴더 감시·자동 수집·모델 학습은 포함하지 않습니다. 자료를 넣은 뒤 에이전트에게 수집 작업을 요청합니다. Obsidian은 편집·탐색 도구이며 사용하지 않아도 일반 Markdown과 Git으로 관리할 수 있습니다.

## 검증

이 카탈로그 저장소에서 Rust 없이 위키 수명주기만 검사할 수 있습니다.

```bash
python3 scripts/verify-template-modules.py --wiki-only
```

임시 프로젝트에서 설치·상태 확인·미리보기·충돌 거부·자료 수정 후 제거·재추가를 검사합니다. 전체 모듈 검사는 아래 명령으로 실행합니다.

```bash
./scripts/check-template-modules.sh --docker
```

처음에는 자료가 없는 빈 색인이 정상입니다. 수집한 뒤에는 색인에서 실제 노트로, 노트에서 출처·관련 문서로 이동하는지 확인합니다. 앱 코드·Cargo·npm 의존성은 변경하지 않으며, 적용된 보관함은 이 카탈로그 없이 사용할 수 있습니다.

## 제거와 재추가

```bash
python3 scripts/template-module.py remove llm-wiki --project /path/to/project --dry-run
python3 scripts/template-module.py remove llm-wiki --project /path/to/project
```

제거는 루트 지침의 등록 블록과 모듈 적용 기록을 해제합니다. **`knowledge/`의 원본·요약·색인·로그·노트 양식·관리 규칙·Obsidian 설정은 수정 여부와 관계없이 모두 보존합니다.** `seed_files`는 설치 후 프로젝트 자료이므로 자동 삭제하지 않습니다. 폴더 자체를 없애려면 사용자가 축적한 내용을 먼저 확인해야 합니다.

등록 블록을 직접 수정한 경우에는 기존 모듈처럼 제거를 거부하고 경로를 알려줍니다. 위키 문서나 색인·로그를 수정한 것은 제거를 막지 않습니다. 카탈로그가 없어도 관리 도구 사본과 적용 기록만 있으면 remove를 실행할 수 있습니다.

다시 add하면 기존 위키를 그대로 사용하고, 빠진 초기 파일만 생성하며 지침 블록을 다시 연결합니다. 다른 모듈의 설치 상태와 소유 파일은 유지합니다. 제거 후에도 `knowledge/`를 별도로 열면 보관된 문서와 내부 작업 지침을 사용할 수 있습니다.
