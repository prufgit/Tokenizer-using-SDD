import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { VocabularyTable } from "../../src/components/vocabulary/VocabularyTable";

describe("VocabularyTable", () => {
  it("shows an empty-state message when there are no entries", () => {
    render(<VocabularyTable entries={[]} />);
    expect(screen.getByTestId("vocabulary-empty")).toBeInTheDocument();
  });

  it("renders one row per entry with id, token, frequency, and status", () => {
    render(
      <VocabularyTable
        entries={[
          { id: 0, token: "Hello", frequency: 3, status: "existing" },
          { id: 1, token: "world", frequency: 1, status: "new" },
        ]}
      />
    );

    expect(screen.getByTestId("vocabulary-row-0")).toHaveTextContent("Hello");
    expect(screen.getByTestId("vocabulary-row-0")).toHaveTextContent("3");
    expect(screen.getByTestId("vocabulary-row-1")).toHaveTextContent("NEW");
  });
});
