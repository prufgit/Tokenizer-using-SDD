import type { TokenizerMode } from "../../types/api";

interface TokenizerModeToggleProps {
  mode: TokenizerMode;
  onChange: (mode: TokenizerMode) => void;
  disabled?: boolean;
}

export function TokenizerModeToggle({
  mode,
  onChange,
  disabled,
}: TokenizerModeToggleProps) {
  return (
    <div role="radiogroup" aria-label="Tokenizer mode" className="tab-strip">
      <button
        type="button"
        role="radio"
        aria-checked={mode === "tiktoken"}
        className="tab"
        disabled={disabled}
        onClick={() => onChange("tiktoken")}
      >
        Tiktoken
      </button>
      <button
        type="button"
        role="radio"
        aria-checked={mode === "custom"}
        className="tab"
        disabled={disabled}
        onClick={() => onChange("custom")}
      >
        Custom Tokenizer
      </button>
    </div>
  );
}
