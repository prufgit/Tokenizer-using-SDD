import { useState } from "react";

import { StateBanner, type RequestState } from "../results/StateBanner";

interface BpeTrainingFormProps {
  requestState: RequestState;
  errorMessage: string | null;
  onTrain: (trainingText: string, targetVocabSize: number) => void;
}

export function BpeTrainingForm({ requestState, errorMessage, onTrain }: BpeTrainingFormProps) {
  const [trainingText, setTrainingText] = useState("");
  const [targetVocabSize, setTargetVocabSize] = useState(50);

  const handleSubmit = () => {
    onTrain(trainingText, targetVocabSize);
  };

  return (
    <div className="panel neon-border" style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
      <h3 className="neon-text" style={{ margin: 0 }}>
        Train BPE Tokenizer
      </h3>
      <textarea
        aria-label="BPE training text"
        className="panel panel-raised"
        style={{
          width: "100%",
          minHeight: "100px",
          fontFamily: "var(--font-mono)",
          color: "var(--text-primary)",
          resize: "vertical",
        }}
        placeholder="Enter training text (up to 5,000 characters)…"
        value={trainingText}
        disabled={requestState === "loading"}
        onChange={(event) => setTrainingText(event.target.value)}
      />
      <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", flexWrap: "wrap" }}>
        <label style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          Target vocabulary size
          <input
            aria-label="Target vocabulary size"
            type="number"
            min={1}
            max={500}
            className="btn"
            style={{ width: "6rem" }}
            value={targetVocabSize}
            disabled={requestState === "loading"}
            onChange={(event) => setTargetVocabSize(Number(event.target.value))}
          />
        </label>
        <button
          type="button"
          className="btn btn-primary"
          disabled={requestState === "loading"}
          onClick={handleSubmit}
        >
          Start Training
        </button>
      </div>
      {requestState !== "idle" && requestState !== "success" && (
        <StateBanner state={requestState} errorMessage={errorMessage} />
      )}
    </div>
  );
}
