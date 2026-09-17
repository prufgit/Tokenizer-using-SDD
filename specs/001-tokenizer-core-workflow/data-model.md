# Phase 1 Data Model: Tokenizer Core Workflow

Entities below are logical (spec-level) shapes; they map directly to Pydantic schemas in
`backend/app/schemas/` and TypeScript interfaces in `frontend/src/types/api.ts`. No
entity is persisted — all are constructed per-request or held in the single in-memory
`VocabularyStore` (Principle VI).

## TokenizeRequest

Represents one tokenize operation submitted by the client (`multipart/form-data`, since
it must support an optional file part).

| Field | Type | Required | Rules |
|---|---|---|---|
| `text` | string | one of `text`/`file` | Ignored/rejected if `file` also present; trimmed before validation |
| `file` | binary (TXT or PDF) | one of `text`/`file` | ≤ 10 MB (FR-023); type validated by content, not just extension |
| `tokenizer_mode` | enum: `"tiktoken"` \| `"custom"` | yes | FR-004 |
| `encoding` | string | required iff `tokenizer_mode == "tiktoken"` | Must be a member of the live `tiktoken.list_encoding_names()` set (FR-005, FR-026) |

**Validation rules** (FR-021–FR-026, in order applied):
1. Exactly one of `text` / `file` must be present → else `EMPTY_INPUT` if neither, or a
   `400` "provide either text or a file, not both" if both.
2. If `file`: type must be TXT or PDF (by sniffed content, not just filename) → else
   `UNSUPPORTED_FILE_TYPE`; size ≤ 10 MB → else `FILE_TOO_LARGE`.
3. If `file` is a PDF: must open and must not be password-protected → else `INVALID_PDF`;
   extracted text must be non-empty after stripping → else `PDF_NO_TEXT`.
4. Resulting text (typed or extracted), after trimming, must be non-empty → else
   `EMPTY_INPUT`.
5. If `tokenizer_mode == "tiktoken"`: `encoding` must be supported → else
   `UNSUPPORTED_ENCODING`.

## Token

One unit produced by a tokenize operation (Key Entity: Token).

| Field | Type | Notes |
|---|---|---|
| `index` | int | 0-based position within the result's token list |
| `id` | int | Tiktoken's real token ID, or the Custom Tokenizer's vocabulary ID |
| `text` | string | The token's literal text |
| `start` | int | Start character offset in the source text (inclusive) |
| `end` | int | End character offset in the source text (exclusive) |
| `is_new` | bool \| null | Custom mode: `true`/`false`. Tiktoken mode: `null` (concept doesn't apply — Tiktoken has no vocabulary growth) |

## Statistics

Summary metrics for one tokenize operation (FR-008).

| Field | Type | Formula |
|---|---|---|
| `character_count` | int | `len(text)` |
| `word_count` | int | count of whitespace-delimited words in `text` |
| `token_count` | int | `len(tokens)` |
| `tokens_per_word` | float | `token_count / word_count` (0 if `word_count == 0`) |
| `tokens_per_character` | float | `token_count / character_count` (0 if `character_count == 0`) |

## TokenizeResponse

| Field | Type | Notes |
|---|---|---|
| `tokenizer_mode` | enum: `"tiktoken"` \| `"custom"` | Echoes the request |
| `encoding` | string \| null | The encoding used (Tiktoken mode) or `null` (Custom mode) |
| `tokens` | `Token[]` | Ordered by `index` |
| `stats` | `Statistics` | See above |

## CustomVocabularyEntry

One row of the Custom Tokenizer's vocabulary (Key Entity: Custom Vocabulary Entry).

| Field | Type | Notes |
|---|---|---|
| `id` | int | Deterministic, assigned once at first sighting (monotonic counter) |
| `token` | string | The vocabulary token text — unique key |
| `frequency` | int | Total occurrences across the vocabulary's lifetime (since last reset) |
| `status` | enum: `"new"` \| `"existing"` | `"new"` iff this token was created during the *most recent* Custom Tokenizer operation (FR-016); recalculated on each operation, not historical |

**State transitions** (the vocabulary as a whole):
- `empty` (initial / post-reset) → `populated` on the first successful Custom Tokenizer
  operation that yields ≥1 token.
- `populated` → `populated` on subsequent operations (entries added and/or frequencies
  incremented; every entry's `status` is recomputed relative to the just-completed
  operation).
- `populated` or `empty` → `empty` on an explicit reset request (FR-020); this clears
  `token_to_id`, `frequency`, and resets the ID counter — the very next unseen token after
  a reset gets the same starting ID a freshly-started application would assign.
- Implicit `populated`/`empty` → `empty` on backend process restart (in-memory only,
  Principle VI).

## VocabularyResponse

| Field | Type | Notes |
|---|---|---|
| `entries` | `CustomVocabularyEntry[]` | All entries, ordered by `id` ascending |
| `total_entries` | int | `len(entries)` |

## UploadedFileMeta (internal — not returned to client)

| Field | Type | Notes |
|---|---|---|
| `filename` | string | As supplied by the client |
| `content_type` | string | Sniffed/validated server-side |
| `size_bytes` | int | Enforced against the 10 MB limit |
| `extracted_text` | string \| null | Populated on success; `null` if extraction failed (in which case an `ErrorResponse` is returned instead) |

## ErrorResponse

| Field | Type | Notes |
|---|---|---|
| `error_code` | enum: `EMPTY_INPUT` \| `UNSUPPORTED_FILE_TYPE` \| `FILE_TOO_LARGE` \| `INVALID_PDF` \| `PDF_NO_TEXT` \| `UNSUPPORTED_ENCODING` | Machine-readable, one per FR-021/022/023/024/025/026 |
| `message` | string | Clear, user-friendly text (FR-027) — what the frontend renders as-is |

## EncodingsResponse

| Field | Type | Notes |
|---|---|---|
| `encodings` | string[] | Live list from `tiktoken.list_encoding_names()`, used to populate the encoding selector (FR-005) |

---

## BPE Amendment Entities (User Stories 6-7, FR-032–FR-054)

Held in a single in-memory `BpeModelStore`, fully independent of `VocabularyStore`
(research.md Decision 13). `TokenizeRequest.tokenizer_mode` and `TokenizeResponse` gain
a third value, `"bpe"` (see updated tables below), reusing `Token`/`Statistics`
unchanged.

### BpeTrainRequest

`application/json` (no file support — training text is typed/pasted only, per
Assumptions).

| Field | Type | Required | Rules |
|---|---|---|---|
| `training_text` | string | yes | Trimmed before validation; non-empty after trim (else `BPE_TRAINING_TEXT_EMPTY`); ≤ 5,000 characters (else `BPE_TRAINING_TEXT_TOO_LONG`) — FR-038 |
| `target_vocab_size` | int | yes | Must be a positive integer, ≥ the number of distinct characters in `training_text` (whitespace included), and ≤ 500 — else `BPE_TARGET_VOCAB_SIZE_INVALID` — FR-039 |

### BpeVocabularyEntry

| Field | Type | Notes |
|---|---|---|
| `id` | int | Deterministic (research.md Decision 11) |
| `token` | string | A base character or a merged sequence |

### BpeMergeRule

| Field | Type | Notes |
|---|---|---|
| `order` | int | 0-based rank — the order this merge was learned in (also its application priority at tokenize time, Decision 12) |
| `left` | string | Left symbol of the merged pair |
| `right` | string | Right symbol of the merged pair |
| `merged` | string | The resulting token (`left + right`) |
| `merged_id` | int | The resulting token's `BpeVocabularyEntry.id` |

### BpeTrainingStep

| Field | Type | Notes |
|---|---|---|
| `step` | int | 0-based step number — identical to the corresponding `BpeMergeRule.order` (FR-037/FR-044 are two views of the same underlying data, per research.md Decision 16) |
| `pair_selected` | [string, string] | The `(left, right)` pair chosen as most frequent this step |
| `merged_into` | string | What it was merged into |

### BpeModelResponse

Returned by both `POST /api/bpe/train` (the newly trained model) and
`GET /api/bpe/model` (the current model, or the empty shape below).

| Field | Type | Notes |
|---|---|---|
| `trained` | bool | `false` with empty arrays below = no model trained yet this run (FR-052's empty state) |
| `vocabulary` | `BpeVocabularyEntry[]` | Ordered by `id` ascending |
| `merge_rules` | `BpeMergeRule[]` | Ordered by `order` ascending |
| `training_steps` | `BpeTrainingStep[]` | Ordered by `step` ascending (mirrors `merge_rules`) |
| `target_vocab_size` | int \| null | The size requested at training time |
| `achieved_vocab_size` | int \| null | The size actually reached (may be < `target_vocab_size` per FR-040) |

**State transitions** (the BPE model as a whole):
- `untrained` (initial) → `trained` on the first successful `POST /api/bpe/train`.
- `trained` → `trained` on every subsequent successful training run — the entire
  previous model is replaced (FR-041), never merged with it.
- `trained`/`untrained` → `untrained` on backend process restart (in-memory only,
  Principle VI, same as `VocabularyStore`).

### TokenizeRequest / TokenizeResponse (updated)

`tokenizer_mode` now accepts `"tiktoken"` \| `"custom"` \| `"bpe"` (FR-032). When
`"bpe"`: no `encoding` is used (`null` in the response, same as `"custom"`); the
resolved text is validated against the trained model's base character set before
tokenizing (else `BPE_UNKNOWN_CHARACTER`, FR-050); if no model has been trained yet,
the request is rejected with `BPE_MODEL_NOT_TRAINED` (FR-049) instead of being
processed against an empty vocabulary; every resulting `Token.is_new` is `false`
(nothing is created at tokenize time, FR-047).

### ErrorResponse (updated `error_code` set)

Adds five BPE-specific codes to the existing six (FR-053, "distinct from Tiktoken's
and the Simple strategy's error messages"):

| Code | Trigger |
|---|---|
| `BPE_TRAINING_TEXT_EMPTY` | Empty/whitespace-only training text (FR-038) |
| `BPE_TRAINING_TEXT_TOO_LONG` | Training text over 5,000 characters (FR-038) |
| `BPE_TARGET_VOCAB_SIZE_INVALID` | Non-positive, smaller than the training text's distinct-character count, or over 500 (FR-039) |
| `BPE_MODEL_NOT_TRAINED` | Tokenizing with `"bpe"` mode before any training run has completed (FR-049) |
| `BPE_UNKNOWN_CHARACTER` | Tokenize-time text contains a character absent from the trained base vocabulary (FR-050) |
