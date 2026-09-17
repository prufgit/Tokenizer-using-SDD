import { act, renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";

import { useTokenize } from "../../src/hooks/useTokenize";
import * as tokenizerClient from "../../src/api/tokenizerClient";
import { ApiError } from "../../src/api/tokenizerClient";

describe("useTokenize", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("transitions idle -> loading -> success and stores the result", async () => {
    const response = {
      tokenizer_mode: "tiktoken" as const,
      encoding: "cl100k_base",
      tokens: [],
      stats: {
        character_count: 0,
        word_count: 0,
        token_count: 0,
        tokens_per_word: 0,
        tokens_per_character: 0,
      },
    };
    vi.spyOn(tokenizerClient, "tokenize").mockResolvedValue(response);

    const { result } = renderHook(() => useTokenize());
    expect(result.current.requestState).toBe("idle");

    await act(async () => {
      await result.current.run({ text: "hi", tokenizerMode: "tiktoken", encoding: "cl100k_base" });
    });

    await waitFor(() => expect(result.current.requestState).toBe("success"));
    expect(result.current.result).toEqual(response);
  });

  it("transitions to error state and stores the message on failure", async () => {
    vi.spyOn(tokenizerClient, "tokenize").mockRejectedValue(
      new ApiError({ error_code: "EMPTY_INPUT", message: "Please enter text." }, "fallback")
    );

    const { result } = renderHook(() => useTokenize());

    await act(async () => {
      await result.current.run({ text: "", tokenizerMode: "tiktoken" });
    });

    await waitFor(() => expect(result.current.requestState).toBe("error"));
    expect(result.current.errorMessage).toBe("Please enter text.");
  });

  it("calls onCustomTokenizeSuccess only for custom mode", async () => {
    const response = {
      tokenizer_mode: "custom" as const,
      encoding: null,
      tokens: [],
      stats: {
        character_count: 0,
        word_count: 0,
        token_count: 0,
        tokens_per_word: 0,
        tokens_per_character: 0,
      },
    };
    vi.spyOn(tokenizerClient, "tokenize").mockResolvedValue(response);
    const onCustomSuccess = vi.fn();

    const { result } = renderHook(() => useTokenize(onCustomSuccess));

    await act(async () => {
      await result.current.run({ text: "hi", tokenizerMode: "custom" });
    });

    expect(onCustomSuccess).toHaveBeenCalledTimes(1);
  });
});
