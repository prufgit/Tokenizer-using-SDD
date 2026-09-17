import type { CustomVocabularyEntry } from "../../types/api";

interface VocabularyTableProps {
  entries: CustomVocabularyEntry[];
}

export function VocabularyTable({ entries }: VocabularyTableProps) {
  if (entries.length === 0) {
    return (
      <div className="panel" data-testid="vocabulary-empty">
        The Custom Tokenizer vocabulary is empty.
      </div>
    );
  }

  return (
    <table className="panel" data-testid="vocabulary-table" style={{ width: "100%", borderCollapse: "collapse" }}>
      <thead>
        <tr>
          <th style={{ textAlign: "left" }}>ID</th>
          <th style={{ textAlign: "left" }}>Token</th>
          <th style={{ textAlign: "left" }}>Frequency</th>
          <th style={{ textAlign: "left" }}>Status</th>
        </tr>
      </thead>
      <tbody>
        {entries.map((entry) => (
          <tr key={entry.id} data-testid={`vocabulary-row-${entry.id}`}>
            <td>{entry.id}</td>
            <td style={{ fontFamily: "var(--font-mono)" }}>{entry.token}</td>
            <td>{entry.frequency}</td>
            <td>
              {entry.status === "new" ? (
                <span className="badge-new">NEW</span>
              ) : (
                <span style={{ color: "var(--text-muted)" }}>—</span>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
