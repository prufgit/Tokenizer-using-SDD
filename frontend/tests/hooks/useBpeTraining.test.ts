import { act, renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";

import { useBpeTraining } from "../../src/hooks/useBpeTraining";
import * as tokenizerClient from "../../src/api/tokenizerClient";
import { ApiError } from "../../src/api/tokenizerClient";

describe("useBpeTraining", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("transitions idle -> loading -> success and calls onTrainingSuccess", async () => {
    const response = {
      trained: true,
      vocabulary: [{ id: 0, token: "a" }],
      merge_rules: [],
      training_steps: [],
      target_vocab_size: 1,
      achieved_vocab_size: 1,
    };
    vi.spyOn(tokenizerClient, "trainBpe").mockResolvedValue(response);
    const onSuccess = vi.fn();

    const { result } = renderHook(() => useBpeTraining(onSuccess));
    expect(result.current.requestState).toBe("idle");

    await act(async () => {
      await result.current.train({ training_text: "a", target_vocab_size: 1 });
    });

    await waitFor(() => expect(result.current.requestState).toBe("success"));
    expect(result.current.result).toEqual(response);
    expect(onSuccess).toHaveBeenCalledTimes(1);
  });

  it("transitions to error state and stores the message on failure", async () => {
    vi.spyOn(tokenizerClient, "trainBpe").mockRejectedValue(
      new ApiError(
        { error_code: "BPE_TRAINING_TEXT_EMPTY", message: "Please enter training text." },
        "fallback"
      )
    );

    const { result } = renderHook(() => useBpeTraining());

    await act(async () => {
      await result.current.train({ training_text: "", target_vocab_size: 1 });
    });

    await waitFor(() => expect(result.current.requestState).toBe("error"));
    expect(result.current.errorMessage).toBe("Please enter training text.");
  });
});
