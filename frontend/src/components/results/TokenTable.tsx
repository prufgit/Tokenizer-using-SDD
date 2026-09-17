import type { Token } from "../../types/api";

interface TokenTableProps {
  tokens: Token[];
}

export function TokenTable({ tokens }: TokenTableProps) {
  return (
    <section style={{ marginTop: "1.5rem" }}>
      <h3 className="section-label">Tokenized Output</h3>
      <div className="panel token-grid" data-testid="token-table">
        {tokens.map((token) => (
          <div
            key={token.index}
            className={`token-card${token.is_new ? " is-new" : ""}`}
            data-testid={`token-row-${token.index}`}
          >
            <div className="token-card-index">
              #{token.index}
              {token.is_new ? <span className="badge-new" style={{ marginLeft: "0.4rem" }}>NEW</span> : null}
            </div>
            <div className="token-card-text" data-testid={`token-chip-${token.index}`}>
              {token.text}
            </div>
            <div className="token-card-meta">ID: {token.id}</div>
            <div className="token-card-meta">Bytes: [{token.bytes.join(", ")}]</div>
          </div>
        ))}
      </div>
    </section>
  );
}
