import React, { useEffect, useState } from "react";

interface HealthResponse {
  status: string;
  service: string;
  timestamp: string;
}

export const App: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    fetch("/api/v1/health")
      .then((res) => res.json())
      .then((data: HealthResponse) => setHealth(data))
      .catch((err) => console.error("Health check error:", err));
  }, []);

  return (
    <main style={{ fontFamily: "sans-serif", padding: "2rem" }}>
      <h1>Rust + React Template</h1>
      <p>초기 템플릿 환경이 성공적으로 설정되었습니다.</p>
      <section style={{ marginTop: "1rem", padding: "1rem", background: "#f4f4f5", borderRadius: "8px" }}>
        <h3>Backend Health Check</h3>
        {health ? (
          <pre>{JSON.stringify(health, null, 2)}</pre>
        ) : (
          <p>백엔드 연결 확인 중...</p>
        )}
      </section>
    </main>
  );
};
