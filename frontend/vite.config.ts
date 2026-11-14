import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    // 로컬 `npm run dev`는 Vite 기본값(localhost)만 엽니다. 컨테이너는 개발 Compose가 --host 0.0.0.0을 넘깁니다.
    port: 5173,
    proxy: {
      "/api": {
        target: process.env.VITE_API_BACKEND_URL || "http://localhost:8080",
        changeOrigin: true,
      },
    },
  },
});
