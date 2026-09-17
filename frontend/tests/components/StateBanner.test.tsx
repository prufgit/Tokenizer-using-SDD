import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { StateBanner } from "../../src/components/results/StateBanner";

describe("StateBanner", () => {
  it("shows the empty state when idle", () => {
    render(<StateBanner state="idle" />);
    expect(screen.getByTestId("state-empty")).toBeInTheDocument();
  });

  it("shows a loading indicator while loading", () => {
    render(<StateBanner state="loading" />);
    expect(screen.getByTestId("state-loading")).toBeInTheDocument();
  });

  it("surfaces the backend error message verbatim in the error state", () => {
    render(<StateBanner state="error" errorMessage="This PDF is invalid or corrupted." />);
    const banner = screen.getByTestId("state-error");
    expect(banner).toHaveTextContent("This PDF is invalid or corrupted.");
  });

  it("falls back to a generic message when no error message is provided", () => {
    render(<StateBanner state="error" />);
    expect(screen.getByTestId("state-error")).toHaveTextContent(/something went wrong/i);
  });

  it("renders children in the success state", () => {
    render(
      <StateBanner state="success">
        <div>Results here</div>
      </StateBanner>
    );
    expect(screen.getByTestId("state-success")).toHaveTextContent("Results here");
  });
});
