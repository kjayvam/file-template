import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import { App } from "./App";

it("앱의 시작 화면을 표시한다", () => {
  render(<App />);
  expect(screen.getByText("React 앱이 준비되었습니다.")).toBeInTheDocument();
});
