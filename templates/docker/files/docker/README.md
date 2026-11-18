# 선택형 Docker 실행

`python3 scripts/compose.py dev up` 또는 `python3 scripts/compose.py prod up --build`를 실행합니다.
설치한 `docker-rust`, `docker-react`, `docker-postgres`, `docker-web-api`의 Compose 조각만 사용합니다.
`python3 scripts/compose.py dev --dry-run up`으로 실행 명령을 확인합니다.
`down`은 볼륨을 보존합니다. `down -v`는 데이터를 삭제하므로 직접 판단해서 실행합니다.

- Rust 단독: 127.0.0.1:8080
- React 개발: 127.0.0.1:5173, 프로덕션: 127.0.0.1:8088
- 풀스택 연결: 개발 프록시와 프로덕션 Nginx가 backend:8080으로 전달합니다.
- PostgreSQL: dev에서는 127.0.0.1:5432, prod에서는 내부 네트워크만 사용합니다.

PostgreSQL 선택 시 DATABASE_NAME·DATABASE_USER·DATABASE_PASSWORD를 .env에 채우세요.
DB 실행 환경만 제공하며, 앱 드라이버·인증·TLS·실제 운영 배포는 프로젝트 요구에 맞게 구성합니다.
