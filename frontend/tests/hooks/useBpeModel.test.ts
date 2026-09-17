import { act, renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";

import { useBpeModel } from "../../src/hooks/useBpeModel";
import * as tokenizerClient from "../../src/api/tokenizerClient";

describe("useBpeModel", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("refresh() loads the current BPE model from the API", async () => {
    const response = {
      trained: true,
      vocabulary: [{ id: 0, token: "a" }],
      merge_rules: [],
      training_steps: [],
      target_vocab_size: 1,
      achieved_vocab_size: 1,
    };
    vi.spyOn(tokenizerClient, "getBpeModel").mockResolvedValue(response);

    const { result } = renderHook(() => useBpeModel());
    await act(async () => {
      await result.current.refresh();
    });

    await waitFor(() => expect(result.current.model).toEqual(response));
  });
});
