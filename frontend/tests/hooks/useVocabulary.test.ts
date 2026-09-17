import { act, renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";

import { useVocabulary } from "../../src/hooks/useVocabulary";
import * as tokenizerClient from "../../src/api/tokenizerClient";

describe("useVocabulary", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("refresh() loads the vocabulary from the API", async () => {
    const response = {
      entries: [{ id: 0, token: "hi", frequency: 1, status: "new" as const }],
      total_entries: 1,
    };
    vi.spyOn(tokenizerClient, "getVocabulary").mockResolvedValue(response);

    const { result } = renderHook(() => useVocabulary());
    await act(async () => {
      await result.current.refresh();
    });

    await waitFor(() => expect(result.current.vocabulary).toEqual(response));
  });

  it("reset() clears the vocabulary via the API and updates state", async () => {
    const empty = { entries: [], total_entries: 0 };
    vi.spyOn(tokenizerClient, "resetVocabulary").mockResolvedValue(empty);

    const { result } = renderHook(() => useVocabulary());
    await act(async () => {
      await result.current.reset();
    });

    expect(result.current.vocabulary).toEqual(empty);
  });
});
