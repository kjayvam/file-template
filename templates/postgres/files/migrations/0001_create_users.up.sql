-- PostgreSQL 예시입니다. SQLite를 쓰면 문법을 바꿔 사용하세요.
CREATE TABLE users (
  id         BIGSERIAL PRIMARY KEY,
  email      VARCHAR(255) NOT NULL UNIQUE,
  name       VARCHAR(100) NOT NULL,
  created_at TIMESTAMPTZ  NOT NULL DEFAULT now()
);
