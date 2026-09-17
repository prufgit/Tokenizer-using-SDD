import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { TokenTable } from "../../src/components/results/TokenTable";

describe("TokenTable", () => {
  it("renders one row per token with index, id, text, and offset", () => {
    render(
      <TokenTable
        tokens={[
          { index: 0, id: 9906, text: "Hello", start: 0, end: 5, is_new: null },
          { index: 1, id: 11, text: ",", start: 5, end: 6, is_new: null },
        ]}
      />
    );

    expect(screen.getByTestId("token-row-0")).toHaveTextContent("Hello");
    expect(screen.getByTestId("token-row-0")).toHaveTextContent("9906");
    expect(screen.getByTestId("token-row-0")).toHaveTextContent("0–5");
    expect(screen.getByTestId("token-row-1")).toHaveTextContent(",");
  });

  it("does not show a NEW badge for tokens with is_new null or false", () => {
    render(
      <TokenTable
        tokens={[{ index: 0, id: 1, text: "hi", start: 0, end: 2, is_new: null }]}
      />
    );
    expect(screen.queryByText("NEW")).not.toBeInTheDocument();
  });

  it("shows a NEW badge and is-new styling for newly created tokens", () => {
    render(
      <TokenTable
        tokens={[{ index: 0, id: 1, text: "hi", start: 0, end: 2, is_new: true }]}
      />
    );
    expect(screen.getByText("NEW")).toBeInTheDocument();
    expect(screen.getByTestId("token-chip-0")).toHaveClass("is-new");
  });
});
