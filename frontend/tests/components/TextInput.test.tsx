import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { TextInput } from "../../src/components/input/TextInput";

describe("TextInput", () => {
  it("calls onChange with the typed value", async () => {
    const onChange = vi.fn();
    render(<TextInput value="" onChange={onChange} />);

    await userEvent.type(screen.getByLabelText("Text to tokenize"), "Hi");

    expect(onChange).toHaveBeenCalledWith("H");
    expect(onChange).toHaveBeenCalledWith("i");
  });

  it("disables the textarea when disabled is true", () => {
    render(<TextInput value="" onChange={vi.fn()} disabled />);
    expect(screen.getByLabelText("Text to tokenize")).toBeDisabled();
  });
});
