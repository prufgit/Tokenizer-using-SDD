import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi, beforeEach } from "vitest";

import App from "../../src/App";
import * as tokenizerClient from "../../src/api/tokenizerClient";

describe("App - BPE strategy", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.spyOn(tokenizerClient, "getEncodings").mockResolvedValue({
      encodings: ["cl100k_base"],
    });
  });

  it("shows a train-first hint when the BPE strategy is selected but untrained", async () => {
    vi.spyOn(tokenizerClient, "getBpeModel").mockResolvedValue({
      trained: false,
      vocabulary: [],
      merge_rules: [],
      training_steps: [],
      target_vocab_size: null,
      achieved_vocab_size: null,
    });

    render(<App />);

    await userEvent.click(screen.getByRole("radio", { name: "Custom Tokenizer" }));
    await userEvent.click(screen.getByRole("radio", { name: "BPE" }));

    await waitFor(() =>
      expect(screen.getByTestId("bpe-train-first-hint")).toBeInTheDocument()
    );
    expect(screen.getByTestId("bpe-model-empty")).toBeInTheDocument();
  });

  it("renders BPE tokenize results in the shared token table", async () => {
    vi.spyOn(tokenizerClient, "getBpeModel").mockResolvedValue({
      trained: true,
      vocabulary: [{ id: 0, token: "a" }],
      merge_rules: [],
      training_steps: [],
      target_vocab_size: 1,
      achieved_vocab_size: 1,
    });
    vi.spyOn(tokenizerClient, "tokenize").mockResolvedValue({
      tokenizer_mode: "bpe",
      encoding: null,
      tokens: [{ index: 0, id: 0, text: "a", start: 0, end: 1, is_new: false, bytes: [97] }],
      stats: {
        character_count: 1,
        word_count: 1,
        token_count: 1,
        tokens_per_word: 1,
        tokens_per_character: 1,
      },
    });

    render(<App />);

    await userEvent.click(screen.getByRole("radio", { name: "Custom Tokenizer" }));
    await userEvent.click(screen.getByRole("radio", { name: "BPE" }));
    await userEvent.type(screen.getByLabelText("Text to tokenize"), "a");
    await userEvent.click(screen.getByRole("button", { name: "Tokenize" }));

    await waitFor(() => expect(screen.getByTestId("state-success")).toBeInTheDocument());
    expect(screen.getByTestId("token-table")).toHaveTextContent("a");
  });
});
