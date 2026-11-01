# 1. Base 스테이지: cargo-chef 준비
FROM rust:1.80-alpine AS chef
RUN apk add --no-cache musl-dev
RUN cargo install cargo-chef
WORKDIR /app

# 2. Planner 스테이지: 의존성 레시피 생성
FROM chef AS planner
COPY . .
RUN cargo chef prepare --recipe-path recipe.json

# 3. Builder 스테이지: 의존성 캐싱 및 소스 빌드
FROM chef AS builder
COPY --from=planner /app/recipe.json recipe.json
# 의존성만 먼저 빌드 (소스 코드가 바뀌어도 Cargo.lock이 동일하면 캐시 재사용)
RUN cargo chef cook --release --recipe-path recipe.json

COPY . .
RUN cargo build --release --bin backend

# 4. Runtime 스테이지: 초경량 실행 이미지
FROM alpine:3.20 AS runtime
RUN apk add --no-cache ca-certificates tzdata

WORKDIR /app
COPY --from=builder /app/target/release/backend /app/backend

ENV PORT=8080
EXPOSE 8080

CMD ["/app/backend"]
