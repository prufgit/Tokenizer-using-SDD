export type RequestState = "idle" | "loading" | "success" | "error";

interface StateBannerProps {
  state: RequestState;
  errorMessage?: string | null;
  children?: React.ReactNode;
}

export function StateBanner({ state, errorMessage, children }: StateBannerProps) {
  if (state === "loading") {
    return (
      <div className="panel" role="status" data-testid="state-loading">
        Tokenizing…
      </div>
    );
  }

  if (state === "error") {
    return (
      <div className="panel state-error" role="alert" data-testid="state-error">
        {errorMessage ?? "Something went wrong. Please try again."}
      </div>
    );
  }

  if (state === "idle") {
    return (
      <div className="panel" data-testid="state-empty">
        Enter text or upload a TXT/PDF file, then run tokenization to see results.
      </div>
    );
  }

  return (
    <div className="state-success" data-testid="state-success">
      {children}
    </div>
  );
}
