interface TextInputProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export function TextInput({ value, onChange, disabled }: TextInputProps) {
  return (
    <textarea
      aria-label="Text to tokenize"
      className="panel panel-raised"
      style={{
        width: "100%",
        minHeight: "140px",
        fontFamily: "var(--font-mono)",
        color: "var(--text-primary)",
        resize: "vertical",
      }}
      placeholder="Type or paste text to tokenize…"
      value={value}
      disabled={disabled}
      onChange={(event) => onChange(event.target.value)}
    />
  );
}
