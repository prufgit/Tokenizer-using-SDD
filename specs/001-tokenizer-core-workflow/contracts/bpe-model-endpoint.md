# Contract: GET /api/bpe/model

Returns the currently trained BPE model (vocabulary, merge rules, training steps), or
an empty/untrained shape if no training has completed yet in this application run.
Implements FR-042–FR-045, FR-052.

## Request

No parameters.

## Response — 200 OK

`application/json`, shape: `BpeModelResponse` (see [data-model.md](../data-model.md)) —
identical shape to `POST /api/bpe/train`'s success response (see
[bpe-train-endpoint.md](./bpe-train-endpoint.md)).

**Untrained** (FR-052's empty state — no training has completed yet, or the app
restarted since):

```json
{
  "trained": false,
  "vocabulary": [],
  "merge_rules": [],
  "training_steps": [],
  "target_vocab_size": null,
  "achieved_vocab_size": null
}
```

**Trained**: same shape as the `POST /api/bpe/train` example, reflecting the most
recently completed training run.

## Notes

This endpoint never errors under normal use (always 200, `trained` distinguishes the
two states) — it only reads `BpeModelStore`, never mutates it. The frontend calls it on
initial load (to restore the display if a model was already trained) and immediately
after every successful `POST /api/bpe/train` (FR-045, mirroring research.md Decision 7's
pattern for the Simple strategy's vocabulary).
