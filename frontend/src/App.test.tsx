import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { App } from "./App";

describe("백엔드 상태 표시", () => {
  it("응답을 기다리는 동안 연결 확인 메시지를 표시한다", () => {
    vi.stubGlobal("fetch", vi.fn(() => new Promise<Response>(() => {})));
    render(<App />);
    expect(screen.getByText("백엔드 연결 확인 중...")).toBeInTheDocument();
  });

  it("정상 응답의 서비스 상태를 표시한다", async () => {
    const health = { status: "ok", service: "backend", timestamp: "2026-11-04T00:00:00Z" };
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(health)));
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);

    expect(await screen.findByText(/"service": "backend"/)).toHaveTextContent('"status": "ok"');
    expect(fetchMock).toHaveBeenCalledWith("/api/v1/health");
    expect(screen.queryByText("백엔드 연결 확인 중...")).not.toBeInTheDocument();
  });

  it("HTTP 오류를 정상 상태로 표시하지 않는다", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response('{"status":"ok"}', { status: 503 })));
    render(<App />);
    expect(await screen.findByRole("alert")).toHaveTextContent("백엔드에 연결할 수 없습니다.");
    expect(screen.queryByText(/"status": "ok"/)).not.toBeInTheDocument();
  });

  it("네트워크 오류가 나면 연결 확인 대신 오류를 표시한다", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Network error")));
    render(<App />);
    expect(await screen.findByRole("alert")).toHaveTextContent("백엔드에 연결할 수 없습니다.");
    expect(screen.queryByText("백엔드 연결 확인 중...")).not.toBeInTheDocument();
  });

  it("JSON이 아닌 응답을 받으면 오류를 표시한다", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("not json")));
    render(<App />);
    expect(await screen.findByRole("alert")).toHaveTextContent("백엔드에 연결할 수 없습니다.");
  });
});
