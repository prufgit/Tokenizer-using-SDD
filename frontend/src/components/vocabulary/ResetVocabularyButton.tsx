interface ResetVocabularyButtonProps {
  onReset: () => void;
  disabled?: boolean;
}

export function ResetVocabularyButton({ onReset, disabled }: ResetVocabularyButtonProps) {
  const handleClick = () => {
    if (window.confirm("Reset the Custom Tokenizer vocabulary? This clears all learned tokens.")) {
      onReset();
    }
  };

  return (
    <button type="button" className="btn" disabled={disabled} onClick={handleClick}>
      Reset vocabulary
    </button>
  );
}
