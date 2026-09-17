import type { Token } from "../../types/api";

interface TokenTableProps {
  tokens: Token[];
}

export function TokenTable({ tokens }: TokenTableProps) {
  return (
    <table className="panel" data-testid="token-table" style={{ width: "100%", borderCollapse: "collapse" }}>
      <thead>
        <tr>
          <th style={{ textAlign: "left" }}>Index</th>
          <th style={{ textAlign: "left" }}>ID</th>
          <th style={{ textAlign: "left" }}>Token</th>
          <th style={{ textAlign: "left" }}>Offset</th>
        </tr>
      </thead>
      <tbody>
        {tokens.map((token) => (
          <tr key={token.index} data-testid={`token-row-${token.index}`}>
            <td>{token.index}</td>
            <td>{token.id}</td>
            <td>
              <span
                className={`token-chip${token.is_new ? " is-new" : ""}`}
                data-testid={`token-chip-${token.index}`}
              >
                {token.text}
                {token.is_new ? <span className="badge-new">NEW</span> : null}
              </span>
            </td>
            <td>
              {token.start}–{token.end}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
