import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi, afterEach } from "vitest";

import { ResetVocabularyButton } from "../../src/components/vocabulary/ResetVocabularyButton";

describe("ResetVocabularyButton", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("calls onReset when the user confirms", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(true);
    const onReset = vi.fn();

    render(<ResetVocabularyButton onReset={onReset} />);
    await userEvent.click(screen.getByRole("button", { name: /reset vocabulary/i }));

    expect(onReset).toHaveBeenCalledTimes(1);
  });

  it("does not call onReset when the user cancels the confirmation", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(false);
    const onReset = vi.fn();

    render(<ResetVocabularyButton onReset={onReset} />);
    await userEvent.click(screen.getByRole("button", { name: /reset vocabulary/i }));

    expect(onReset).not.toHaveBeenCalled();
  });
});
