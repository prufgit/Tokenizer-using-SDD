interface FileUploadProps {
  file: File | null;
  onChange: (file: File | null) => void;
  disabled?: boolean;
}

export function FileUpload({ file, onChange, disabled }: FileUploadProps) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
      <label className="btn" style={{ cursor: disabled ? "not-allowed" : "pointer" }}>
        Upload TXT or PDF
        <input
          type="file"
          accept=".txt,.pdf,text/plain,application/pdf"
          aria-label="Upload a TXT or PDF file"
          disabled={disabled}
          style={{ display: "none" }}
          onChange={(event) => onChange(event.target.files?.[0] ?? null)}
        />
      </label>
      {file && (
        <span style={{ color: "var(--text-muted)" }}>
          {file.name}
          <button
            type="button"
            className="btn"
            aria-label="Remove uploaded file"
            style={{ marginLeft: "0.5rem", padding: "0.1rem 0.5rem" }}
            onClick={() => onChange(null)}
          >
            ×
          </button>
        </span>
      )}
    </div>
  );
}
