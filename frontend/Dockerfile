# 1. 빌드 스테이지
FROM node:22-alpine AS builder
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# 2. 런타임 스테이지 (Nginx)
# Dependabot이 갱신할 수 있도록 major.minor까지 고정합니다.
FROM nginx:1.31-alpine AS runtime
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
