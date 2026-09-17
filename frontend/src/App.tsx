import { useEffect, useState } from "react";

import { BpeTrainingForm } from "./components/bpe/BpeTrainingForm";
import { BpeTrainingResult } from "./components/bpe/BpeTrainingResult";
import { EncodingSelect } from "./components/input/EncodingSelect";
import { FileUpload } from "./components/input/FileUpload";
import { TextInput } from "./components/input/TextInput";
import { TokenizerModeToggle } from "./components/input/TokenizerModeToggle";
import { StateBanner } from "./components/results/StateBanner";
import { StatsSummary } from "./components/results/StatsSummary";
import { TokenTable } from "./components/results/TokenTable";
import { ResetVocabularyButton } from "./components/vocabulary/ResetVocabularyButton";
import { VocabularyTable } from "./components/vocabulary/VocabularyTable";
import { useBpeModel } from "./hooks/useBpeModel";
import { useBpeTraining } from "./hooks/useBpeTraining";
import { useTokenize } from "./hooks/useTokenize";
import { useVocabulary } from "./hooks/useVocabulary";
import type { CustomStrategy, TokenizerMode } from "./types/api";

export default function App() {
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [tokenizerMode, setTokenizerMode] = useState<TokenizerMode>("tiktoken");
  const [customStrategy, setCustomStrategy] = useState<CustomStrategy>("simple");
  const [encoding, setEncoding] = useState<string | null>(null);

  const { vocabulary, refresh: refreshVocabulary, reset: resetVocabularyState } = useVocabulary();
  const { model: bpeModel, refresh: refreshBpeModel } = useBpeModel();

  // Immediately after any successful Custom Tokenizer (Simple strategy) operation,
  // refetch the vocabulary so the view updates with no manual refresh (FR-019, SC-007).
  const { requestState, result, errorMessage, run } = useTokenize(refreshVocabulary);
  // Immediately after a successful BPE training run, refetch the model (FR-045).
  const {
    requestState: trainingState,
    errorMessage: trainingErrorMessage,
    train,
  } = useBpeTraining(refreshBpeModel);

  useEffect(() => {
    void refreshBpeModel();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const isBpeStrategy = tokenizerMode === "custom" && customStrategy === "bpe";
  // On the wire, the three modes are flat: "tiktoken" | "custom" | "bpe" — the UI
  // nests BPE under "Custom Tokenizer" (research.md decision 15).
  const wireTokenizerMode = isBpeStrategy ? "bpe" : tokenizerMode;

  const handleTextChange = (value: string) => {
    setText(value);
    if (value) setFile(null);
  };

  const handleFileChange = (nextFile: File | null) => {
    setFile(nextFile);
    if (nextFile) setText("");
  };

  const handleSubmit = () => {
    void run({
      text: file ? undefined : text,
      file: file ?? undefined,
      tokenizerMode: wireTokenizerMode,
      encoding: tokenizerMode === "tiktoken" ? encoding ?? undefined : undefined,
    });
  };

  return (
    <div style={{ maxWidth: "960px", margin: "0 auto", padding: "2rem 1rem" }}>
      <h1 className="neon-text">Tokenizer</h1>

      <TokenizerModeToggle
        mode={tokenizerMode}
        onChange={setTokenizerMode}
        disabled={requestState === "loading"}
      />

      {tokenizerMode === "custom" && (
        <div
          style={{ display: "flex", alignItems: "center", gap: "0.75rem", margin: "0.9rem 0" }}
        >
          <span style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>Strategy:</span>
          <div role="radiogroup" aria-label="Custom Tokenizer strategy" className="tab-strip-sub">
            <button
              type="button"
              role="radio"
              aria-checked={customStrategy === "simple"}
              className="tab-sub"
              disabled={requestState === "loading"}
              onClick={() => setCustomStrategy("simple")}
            >
              Simple
            </button>
            <button
              type="button"
              role="radio"
              aria-checked={customStrategy === "bpe"}
              className="tab-sub"
              disabled={requestState === "loading"}
              onClick={() => setCustomStrategy("bpe")}
            >
              BPE
            </button>
          </div>
        </div>
      )}

      {isBpeStrategy && (
        <div style={{ marginTop: "1rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
          <BpeTrainingForm
            requestState={trainingState}
            errorMessage={trainingErrorMessage}
            onTrain={(trainingText, targetVocabSize) =>
              void train({ training_text: trainingText, target_vocab_size: targetVocabSize })
            }
          />
          <BpeTrainingResult model={bpeModel} />
        </div>
      )}

      <div className="panel" style={{ marginTop: "1rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
        <TextInput
          value={text}
          onChange={handleTextChange}
          disabled={requestState === "loading" || !!file}
        />
        <FileUpload file={file} onChange={handleFileChange} disabled={requestState === "loading"} />

        <div style={{ display: "flex", gap: "1rem", alignItems: "center", flexWrap: "wrap" }}>
          {tokenizerMode === "tiktoken" && (
            <EncodingSelect
              value={encoding}
              onChange={setEncoding}
              disabled={requestState === "loading"}
            />
          )}
          <button
            type="button"
            className="btn btn-primary"
            disabled={requestState === "loading"}
            onClick={handleSubmit}
          >
            Tokenize
          </button>
        </div>
        {isBpeStrategy && bpeModel && !bpeModel.trained && (
          <div className="state-error" data-testid="bpe-train-first-hint">
            Train a BPE tokenizer above before tokenizing with it.
          </div>
        )}
      </div>

      <div style={{ marginTop: "1.5rem" }}>
        <StateBanner state={requestState} errorMessage={errorMessage}>
          {result && (
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              <StatsSummary stats={result.stats} />
              <TokenTable tokens={result.tokens} />
            </div>
          )}
        </StateBanner>
      </div>

      {tokenizerMode === "custom" && customStrategy === "simple" && (
        <div className="panel" style={{ marginTop: "1.5rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h2 className="neon-text" style={{ margin: 0 }}>
              Custom Tokenizer Vocabulary
            </h2>
            <div style={{ display: "flex", gap: "0.5rem" }}>
              <button type="button" className="btn" onClick={() => void refreshVocabulary()}>
                Refresh
              </button>
              <ResetVocabularyButton onReset={() => void resetVocabularyState()} />
            </div>
          </div>
          <div style={{ marginTop: "1rem" }}>
            <VocabularyTable entries={vocabulary?.entries ?? []} />
          </div>
        </div>
      )}
    </div>
  );
}
