import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { BpeTrainingResult } from "../../src/components/bpe/BpeTrainingResult";

describe("BpeTrainingResult", () => {
  it("shows the empty state when no model has been trained", () => {
    render(<BpeTrainingResult model={null} />);
    expect(screen.getByTestId("bpe-model-empty")).toBeInTheDocument();
  });

  it("shows the empty state when the model response says trained: false", () => {
    render(
      <BpeTrainingResult
        model={{
          trained: false,
          vocabulary: [],
          merge_rules: [],
          training_steps: [],
          target_vocab_size: null,
          achieved_vocab_size: null,
        }}
      />
    );
    expect(screen.getByTestId("bpe-model-empty")).toBeInTheDocument();
  });

  it("renders vocabulary and merge rules when trained", () => {
    render(
      <BpeTrainingResult
        model={{
          trained: true,
          vocabulary: [
            { id: 0, token: "a" },
            { id: 1, token: "b" },
            { id: 2, token: "ab" },
          ],
          merge_rules: [
            { order: 0, left: "a", right: "b", merged: "ab", merged_id: 2 },
          ],
          training_steps: [
            { step: 0, pair_selected: ["a", "b"], merged_into: "ab" },
          ],
          target_vocab_size: 3,
          achieved_vocab_size: 3,
        }}
      />
    );

    expect(screen.getByTestId("bpe-vocab-row-2")).toHaveTextContent('"ab"');
    expect(screen.getByTestId("bpe-merge-row-0")).toHaveTextContent('"a"');
    expect(screen.getByTestId("bpe-merge-row-0")).toHaveTextContent('"b"');
    expect(screen.getByTestId("bpe-merge-row-0")).toHaveTextContent("2");
  });
});
