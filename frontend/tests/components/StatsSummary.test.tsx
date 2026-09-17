import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { StatsSummary } from "../../src/components/results/StatsSummary";

describe("StatsSummary", () => {
  it("renders all five statistics", () => {
    render(
      <StatsSummary
        stats={{
          character_count: 13,
          word_count: 2,
          token_count: 4,
          tokens_per_word: 2,
          tokens_per_character: 0.31,
        }}
      />
    );

    expect(screen.getByText("13")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("4")).toBeInTheDocument();
    expect(screen.getByText("2.00")).toBeInTheDocument();
    expect(screen.getByText("0.31")).toBeInTheDocument();
  });
});
