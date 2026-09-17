import { useEffect, useState } from "react";

import { getEncodings } from "../../api/tokenizerClient";

interface EncodingSelectProps {
  value: string | null;
  onChange: (encoding: string) => void;
  disabled?: boolean;
}

export function EncodingSelect({ value, onChange, disabled }: EncodingSelectProps) {
  const [encodings, setEncodings] = useState<string[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getEncodings()
      .then((res) => {
        if (cancelled) return;
        setEncodings(res.encodings);
        if (!value && res.encodings.length > 0) {
          onChange(res.encodings[0]);
        }
      })
      .catch(() => {
        if (!cancelled) setLoadError("Couldn't load supported encodings.");
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (loadError) {
    return <span className="state-error">{loadError}</span>;
  }

  return (
    <select
      aria-label="Tiktoken encoding"
      className="btn"
      value={value ?? ""}
      disabled={disabled || encodings.length === 0}
      onChange={(event) => onChange(event.target.value)}
    >
      {encodings.map((encoding) => (
        <option key={encoding} value={encoding}>
          {encoding}
        </option>
      ))}
    </select>
  );
}
