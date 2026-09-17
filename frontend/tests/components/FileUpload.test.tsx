import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { FileUpload } from "../../src/components/input/FileUpload";

describe("FileUpload", () => {
  it("calls onChange with the selected file", async () => {
    const onChange = vi.fn();
    render(<FileUpload file={null} onChange={onChange} />);

    const file = new File(["hello"], "sample.txt", { type: "text/plain" });
    const input = screen.getByLabelText("Upload a TXT or PDF file");

    await userEvent.upload(input, file);

    expect(onChange).toHaveBeenCalledWith(file);
  });

  it("shows the selected file name and clears it on remove", async () => {
    const onChange = vi.fn();
    const file = new File(["hello"], "sample.txt", { type: "text/plain" });
    render(<FileUpload file={file} onChange={onChange} />);

    expect(screen.getByText("sample.txt")).toBeInTheDocument();

    await userEvent.click(screen.getByLabelText("Remove uploaded file"));
    expect(onChange).toHaveBeenCalledWith(null);
  });
});
