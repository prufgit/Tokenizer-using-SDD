# Contract: POST /api/bpe/train

Runs one BPE training operation. Thin route → delegates entirely to `bpe_service`
(validation + training algorithm), which updates the shared `BpeModelStore`. Implements
FR-033–FR-041, FR-051, FR-053, FR-054.

## Request

`application/json` (no file support — see research.md Decision 14)

| Field | Type | Required | Description |
|---|---|---|---|
| `training_text` | string | yes | Typed/pasted training text (FR-033) |
| `target_vocab_size` | integer | yes | Desired vocabulary size (FR-034) |

## Response — 200 OK

`application/json`, shape: `BpeModelResponse` (see [data-model.md](../data-model.md)),
with `trained: true`.

```json
{
  "trained": true,
  "vocabulary": [
    { "id": 0, "token": "a" },
    { "id": 1, "token": "b" },
    { "id": 2, "token": "ab" }
  ],
  "merge_rules": [
    { "order": 0, "left": "a", "right": "b", "merged": "ab", "merged_id": 2 }
  ],
  "training_steps": [
    { "step": 0, "pair_selected": ["a", "b"], "merged_into": "ab" }
  ],
  "target_vocab_size": 3,
  "achieved_vocab_size": 3
}
```

If the training text's distinct-character count is too small to ever reach
`target_vocab_size` through merges, training stops early (FR-040) and
`achieved_vocab_size < target_vocab_size` in an otherwise-normal 200 response — this is
not an error.

## Response — 400 Bad Request

`application/json`, shape: `ErrorResponse` (see [error-schema.md](./error-schema.md)).

| `error_code` | Trigger |
|---|---|
| `BPE_TRAINING_TEXT_EMPTY` | `training_text` is empty or whitespace-only (FR-038) |
| `BPE_TRAINING_TEXT_TOO_LONG` | `training_text` exceeds 5,000 characters (FR-038) |
| `BPE_TARGET_VOCAB_SIZE_INVALID` | `target_vocab_size` is non-positive, smaller than `training_text`'s distinct-character count, or exceeds 500 (FR-039) |

## Side effects

On success, **fully replaces** the current `BpeModelStore` contents (FR-041) — any
previously trained vocabulary, merge rules, and training steps are discarded. A
subsequent `GET /api/bpe/model` or `POST /api/tokenize` (`tokenizer_mode: "bpe"`)
immediately reflects the new model.
