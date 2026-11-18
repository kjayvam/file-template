# 1. 빌드 스테이지
FROM node:22-alpine AS builder
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# 2. 런타임 스테이지 (Nginx)
# root가 아닌 nginx 사용자로 실행하는 이미지입니다. 1024 미만 포트를 열 수 없어 컨테이너 안에서는 8080을 씁니다.
# Dependabot이 갱신할 수 있도록 major.minor까지 고정합니다.
FROM nginxinc/nginx-unprivileged:1.31-alpine AS runtime
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
