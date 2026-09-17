import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";

import { EncodingSelect } from "../../src/components/input/EncodingSelect";
import * as tokenizerClient from "../../src/api/tokenizerClient";

describe("EncodingSelect", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("loads encodings and defaults to the first one", async () => {
    vi.spyOn(tokenizerClient, "getEncodings").mockResolvedValue({
      encodings: ["cl100k_base", "o200k_base"],
    });
    const onChange = vi.fn();

    render(<EncodingSelect value={null} onChange={onChange} />);

    await waitFor(() => expect(onChange).toHaveBeenCalledWith("cl100k_base"));
    expect(screen.getByText("o200k_base")).toBeInTheDocument();
  });

  it("shows an error message when loading fails", async () => {
    vi.spyOn(tokenizerClient, "getEncodings").mockRejectedValue(new Error("boom"));

    render(<EncodingSelect value={null} onChange={vi.fn()} />);

    expect(await screen.findByText(/couldn't load supported encodings/i)).toBeInTheDocument();
  });
});
