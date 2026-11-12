# 빌드 및 이미지 최적화 가이드 (Build Optimization)

Rust와 React(TypeScript)는 개발 생산성과 성능이 뛰어난 조합이지만, 컴파일 언어와 정적 번들러 특성상 올바른 도커 빌드 파이프라인을 구축하지 않으면 이미지 용량이 수 GB에 달하거나 빌드 속도가 크게 느려질 수 있습니다.

본 템플릿에 적용된 멀티스테이지 빌드 및 최적화 전략을 안내합니다.

---

## 1. Rust 백엔드 빌드 최적화 (`cargo-chef`)

Rust는 소스 코드 한 줄만 바뀌어도 모든 의존성을 다시 컴파일하는 문제가 발생하기 쉽습니다. 이를 방지하기 위해 `cargo-chef`를 사용해 의존성 레이어와 소스 코드 레이어를 분리합니다.

```mermaid
flowchart TD
    Base["1. base 스테이지<br/>(rust:1.99.1-alpine / chef 설치)"]
    Planner["2. planner 스테이지<br/>(cargo chef prepare --recipe-path recipe.json)"]
    Builder["3. builder 스테이지<br/>(cargo chef cook --release --recipe-path recipe.json)<br/>★ 의존성만 미리 컴파일하여 캐싱!"]
    CodeBuild["4. 소스 복사 및 최종 빌드<br/>(cargo build --release)"]
    Runtime["5. runtime 스테이지<br/>(alpine, root가 아닌 app 사용자)<br/>★ 바이너리만 복사 (용량 < 30MB)"]

    Base --> Planner --> Builder --> CodeBuild --> Runtime
```

### Dockerfile 핵심 설계
* **의존성 캐시 유효**: `Cargo.toml`, `Cargo.lock`이 변경되지 않았다면 의존성 빌드(`cargo chef cook`) 단계는 완전히 캐시되어 수 초 만에 빌드가 완료됩니다.
* **초경량 런타임**: 빌드 도구(Rustc, Cargo, GCC 등)가 포함되지 않고 정적 링크된 단일 바이너리와 CA 인증서·tzdata만 포함되므로 최종 이미지 용량이 30MB 안팎으로 유지됩니다.

---

## 2. React (TypeScript) 프론트엔드 빌드 최적화

React 웹 애플리케이션은 브라우저에서 실행되는 정적 에셋(HTML, JS, CSS)입니다. 프로덕션 환경에 무거운 Node.js 런타임을 둘 필요가 없습니다.

```mermaid
flowchart TD
    DevDeps["1. 의존성 설치 스테이지<br/>(node:22-alpine, package.json / lockfile)"]
    Bundler["2. 정적 번들 빌드 스테이지<br/>(Vite build -> /app/dist 생성)"]
    Nginx["3. 런타임 스테이지<br/>(nginx:alpine, 정적 파일 복사 & 리버스 프록시)<br/>★ 크기는 nginx:alpine 기반 이미지가 대부분 차지"]

    DevDeps --> Bundler --> Nginx
```

### Nginx 리버스 프록시 역할
* **단일 오리진 제공**: 클라이언트(브라우저)는 Nginx 포트(예: `:80`)로만 접속합니다.
* **정적 서빙 & 프록시 분기**:
  * `/` 및 정적 리소스 요청: Nginx가 gzip 압축을 적용하고, 해시가 붙은 `/assets/`는 1년 캐시, `index.html`은 매번 재검증하도록 응답 (`docker/nginx/default.conf`)
  * `/api/*` 요청: Nginx가 경로를 그대로 유지한 채 동일 도커 네트워크의 Rust 백엔드(`http://backend:8080`)로 프록시하여 CORS 문제를 원천 제거

---

## 3. 요약: 프로덕션 이미지 크기 비교

| 컴포넌트 | 비최적화 이미지 (단일 스테이지) | 최적화 이미지 (멀티스테이지 적용) |
|---|---|---|
| **Backend (Rust)** | 약 1.8 GB ~ 2.2 GB (Rust 툴체인 포함) | **약 20 MB ~ 35 MB** (단일 바이너리, 실측 약 21 MB) |
| **Frontend (React)** | 약 800 MB ~ 1.2 GB (Node/npm 포함) | **약 50 MB ~ 100 MB** (nginx:alpine + 정적 에셋, 2026-11 기준 실측 약 93 MB) |
| **보안 이점** | 쉘, 패키지 매니저, 개발 도구 노출 | 공격 표면(Attack Surface) 최소화 |
