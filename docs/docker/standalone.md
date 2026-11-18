# 생성 프로젝트의 Docker 단독 실행

Python 3.11 이상, Docker Engine/Desktop, Compose v2가 필요합니다. 프로젝트에는 필요한 docker 실행 모듈이 설치돼 있어야 합니다. 루트 카탈로그에서 직접 앱을 실행하지 않습니다.

```bash
# 카탈로그에서 백엔드 단독 생성
python3 scripts/template-module.py init --name sample-api --project ../sample-api --modules docker-rust
cd ../sample-api
python3 scripts/compose.py dev --dry-run up
python3 scripts/compose.py dev up
```

React 단독은 --modules docker-react, 전체 연결은 --preset fullstack-docker로 생성합니다. 실행 파일은 설치 기록의 compose_files를 읽고 선행 서비스 뒤에 연결 조각을 합칩니다. config로 실제 설정을 확인할 수 있습니다.

```bash
python3 scripts/compose.py dev config
python3 scripts/compose.py dev restart backend
python3 scripts/compose.py prod up --build -d
python3 scripts/compose.py prod down
```

Rust 코드는 재시작하면 재컴파일합니다. React 개발 서버는 HMR을 사용합니다. 프로덕션 Rust는 cargo-chef 멀티스테이지, React는 Node 빌드→비특권 Nginx로 실행합니다. Nginx는 SPA fallback·정적 파일 캐시·기본 보안 헤더를 제공하고 docker-web-api 선택 시에만 API를 프록시합니다.

DB는 docker-postgres를 추가하고 .env에 DATABASE_NAME·DATABASE_USER·DATABASE_PASSWORD를 지정합니다. dev에서는 localhost:5432, prod에서는 내부 네트워크만 사용합니다. DB 드라이버·스키마 적용기는 프로젝트에서 선택합니다. .env 파일은 커밋하지 않습니다.

Rust 다운로드·target, Node 의존성, PostgreSQL 데이터는 목적별 볼륨으로 분리합니다. down은 볼륨을 보존합니다. down -v는 데이터를 삭제하므로 필요한 경우에만 직접 실행합니다. 호스트 포트는 고정 기본값이므로 여러 앱을 동시에 실행할 때 조정하세요.
