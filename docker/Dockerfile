# 빌드 컨텍스트는 저장소 루트입니다: docker build -f docker/Dockerfile .
FROM node:22-alpine

WORKDIR /app

# package.json을 추가하면 아래에 의존성 설치 단계(npm ci --omit=dev)를 넣으세요.
COPY src ./src

ENV NODE_ENV=production
EXPOSE 3000

USER node
CMD ["node", "src/index.js"]
