import React, { useEffect, useState } from "react";

interface HealthResponse {
  status: string;
  service: string;
  timestamp: string;
}

export const App: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetch("/api/v1/health")
      .then((res) => {
        if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
        return res.json();
      })
      .then((data: HealthResponse) => {
        if (!cancelled) setHealth(data);
      })
      .catch(() => {
        if (!cancelled) setError(true);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <main style={{ fontFamily: "sans-serif", padding: "2rem" }}>
      <h1>Rust + React Template</h1>
      <p>초기 템플릿 환경이 성공적으로 설정되었습니다.</p>
      <section style={{ marginTop: "1rem", padding: "1rem", background: "#f4f4f5", borderRadius: "8px" }}>
        <h2>Backend Health Check</h2>
        {error ? (
          <p role="alert">백엔드에 연결할 수 없습니다. 서버 상태를 확인해 주세요.</p>
        ) : health ? (
          <pre>{JSON.stringify(health, null, 2)}</pre>
        ) : (
          <p>백엔드 연결 확인 중...</p>
        )}
      </section>
    </main>
  );
};
