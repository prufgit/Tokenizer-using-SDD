import type { Statistics } from "../../types/api";

interface StatsSummaryProps {
  stats: Statistics;
}

const CARDS: Array<[label: string, key: keyof Statistics, format?: (v: number) => string]> = [
  ["Characters", "character_count"],
  ["Words", "word_count"],
  ["Tokens", "token_count"],
  ["Tokens/Word", "tokens_per_word", (v) => v.toFixed(2)],
  ["Tokens/Char", "tokens_per_character", (v) => v.toFixed(2)],
];

export function StatsSummary({ stats }: StatsSummaryProps) {
  return (
    <section>
      <h3 className="section-label">Statistics</h3>
      <div className="panel stat-grid" data-testid="stats-summary">
        {CARDS.map(([label, key, format]) => (
          <div key={key} className="stat-card" data-testid={`stat-card-${key}`}>
            <div className="stat-card-label">{label}</div>
            <div className="stat-card-value">{format ? format(stats[key]) : stats[key]}</div>
          </div>
        ))}
      </div>
    </section>
  );
}
