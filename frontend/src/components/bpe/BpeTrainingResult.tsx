import type { BpeModelResponse } from "../../types/api";

interface BpeTrainingResultProps {
  model: BpeModelResponse | null;
}

export function BpeTrainingResult({ model }: BpeTrainingResultProps) {
  if (!model || !model.trained) {
    return (
      <div className="panel" data-testid="bpe-model-empty">
        No BPE model has been trained yet. Enter training text above and start
        training to see the learned vocabulary and merge rules here.
      </div>
    );
  }

  return (
    <div className="panel" style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <div style={{ color: "var(--text-muted)" }}>
        Achieved vocabulary size: {model.achieved_vocab_size} / target{" "}
        {model.target_vocab_size}
      </div>

      <div>
        <h4 className="neon-text">Vocabulary</h4>
        <table data-testid="bpe-vocabulary-table" style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th style={{ textAlign: "left" }}>ID</th>
              <th style={{ textAlign: "left" }}>Token</th>
            </tr>
          </thead>
          <tbody>
            {model.vocabulary.map((entry) => (
              <tr key={entry.id} data-testid={`bpe-vocab-row-${entry.id}`}>
                <td>{entry.id}</td>
                <td style={{ fontFamily: "var(--font-mono)" }}>
                  <span className="token-chip">{JSON.stringify(entry.token)}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div>
        <h4 className="neon-text">Merge Rules &amp; Training Steps</h4>
        <table data-testid="bpe-merge-rules-table" style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th style={{ textAlign: "left" }}>Step</th>
              <th style={{ textAlign: "left" }}>Pair Selected</th>
              <th style={{ textAlign: "left" }}>Merged Into</th>
              <th style={{ textAlign: "left" }}>Token ID</th>
            </tr>
          </thead>
          <tbody>
            {model.merge_rules.map((rule) => (
              <tr key={rule.order} data-testid={`bpe-merge-row-${rule.order}`}>
                <td>{rule.order}</td>
                <td style={{ fontFamily: "var(--font-mono)" }}>
                  {JSON.stringify(rule.left)} + {JSON.stringify(rule.right)}
                </td>
                <td style={{ fontFamily: "var(--font-mono)" }}>
                  <span className="token-chip is-new">{JSON.stringify(rule.merged)}</span>
                </td>
                <td>{rule.merged_id}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
