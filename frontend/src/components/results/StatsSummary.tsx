import type { Statistics } from "../../types/api";

interface StatsSummaryProps {
  stats: Statistics;
}

const ROWS: Array<[label: string, key: keyof Statistics, format?: (v: number) => string]> = [
  ["Characters", "character_count"],
  ["Words", "word_count"],
  ["Tokens", "token_count"],
  ["Tokens / word", "tokens_per_word", (v) => v.toFixed(2)],
  ["Tokens / character", "tokens_per_character", (v) => v.toFixed(2)],
];

export function StatsSummary({ stats }: StatsSummaryProps) {
  return (
    <div
      className="panel neon-border"
      data-testid="stats-summary"
      style={{ display: "flex", gap: "1.5rem", flexWrap: "wrap" }}
    >
      {ROWS.map(([label, key, format]) => (
        <div key={key}>
          <div style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>{label}</div>
          <div className="neon-text" style={{ fontSize: "1.25rem", fontWeight: 700 }}>
            {format ? format(stats[key]) : stats[key]}
          </div>
        </div>
      ))}
    </div>
  );
}
