import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { BpeTrainingForm } from "../../src/components/bpe/BpeTrainingForm";

describe("BpeTrainingForm", () => {
  it("calls onTrain with the entered training text and target vocab size", async () => {
    const onTrain = vi.fn();
    render(<BpeTrainingForm requestState="idle" errorMessage={null} onTrain={onTrain} />);

    await userEvent.type(screen.getByLabelText("BPE training text"), "hi");
    await userEvent.click(screen.getByRole("button", { name: /start training/i }));

    expect(onTrain).toHaveBeenCalledWith("hi", 50);
  });

  it("disables inputs while loading and shows the loading state", () => {
    render(<BpeTrainingForm requestState="loading" errorMessage={null} onTrain={vi.fn()} />);

    expect(screen.getByLabelText("BPE training text")).toBeDisabled();
    expect(screen.getByRole("button", { name: /start training/i })).toBeDisabled();
    expect(screen.getByTestId("state-loading")).toBeInTheDocument();
  });

  it("shows the error message when training fails", () => {
    render(
      <BpeTrainingForm
        requestState="error"
        errorMessage="Please enter some training text."
        onTrain={vi.fn()}
      />
    );

    expect(screen.getByTestId("state-error")).toHaveTextContent(
      "Please enter some training text."
    );
  });
});
