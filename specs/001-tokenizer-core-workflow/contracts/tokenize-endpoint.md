# Contract: POST /api/tokenize

Runs one tokenize operation. Thin route → delegates to `file_processing` (if a file was
sent), then to `tiktoken_service`, `custom_tokenizer_service`, or `bpe_service` per
`tokenizer_mode`, then to `statistics`. Implements FR-001–FR-010, FR-021–FR-031, and
(for `"bpe"` mode) FR-046–FR-050.

## Request

`multipart/form-data`

| Field | Type | Required | Description |
|---|---|---|---|
| `text` | string | one of `text`/`file` | Directly entered text (FR-001) |
| `file` | file (TXT or PDF) | one of `text`/`file` | Uploaded document (FR-002, FR-003) |
| `tokenizer_mode` | `"tiktoken"` \| `"custom"` \| `"bpe"` | yes | FR-004, FR-032 |
| `encoding` | string | required iff `tokenizer_mode == "tiktoken"` | Must be in `GET /api/encodings` result (FR-005) |

Exactly one of `text` / `file` must be present. `"bpe"` mode reuses the same text/file
input as `"tiktoken"`/`"custom"` (research.md Decision 14) and requires no `encoding`.

## Response — 200 OK

`application/json`, shape: `TokenizeResponse` (see [data-model.md](../data-model.md)).

```json
{
  "tokenizer_mode": "custom",
  "encoding": null,
  "tokens": [
    { "index": 0, "id": 0, "text": "Hello", "start": 0, "end": 5, "is_new": true },
    { "index": 1, "id": 1, "text": ",", "start": 5, "end": 6, "is_new": true },
    { "index": 2, "id": 2, "text": "world", "start": 7, "end": 12, "is_new": true }
  ],
  "stats": {
    "character_count": 12,
    "word_count": 2,
    "token_count": 3,
    "tokens_per_word": 1.5,
    "tokens_per_character": 0.25
  }
}
```

For `tokenizer_mode: "tiktoken"`, `encoding` echoes the request's encoding, every
`is_new` is `null`, and `id`/`text` are exactly what that encoding produces (FR-009).

For `tokenizer_mode: "bpe"`, `encoding` is `null`, every `is_new` is `false` (nothing
is created at tokenize time, FR-047), and `id`/`text` come from applying the current
trained BPE model's merge rules in learned order (research.md Decision 12):

```json
{
  "tokenizer_mode": "bpe",
  "encoding": null,
  "tokens": [
    { "index": 0, "id": 27, "text": "Hello", "start": 0, "end": 5, "is_new": false },
    { "index": 1, "id": 3, "text": ",", "start": 5, "end": 6, "is_new": false }
  ],
  "stats": { "character_count": 6, "word_count": 1, "token_count": 2, "tokens_per_word": 2.0, "tokens_per_character": 0.33 }
}
```

## Response — 400 Bad Request

`application/json`, shape: `ErrorResponse` (see [error-schema.md](./error-schema.md)).
Returned for any of: `EMPTY_INPUT`, `UNSUPPORTED_FILE_TYPE`, `FILE_TOO_LARGE`,
`INVALID_PDF`, `PDF_NO_TEXT`, `UNSUPPORTED_ENCODING` (FR-021–FR-027, SC-005), or, for
`"bpe"` mode, `BPE_MODEL_NOT_TRAINED` / `BPE_UNKNOWN_CHARACTER` (FR-049, FR-050).

## Side effects

When `tokenizer_mode == "custom"` and the request succeeds, the shared
`VocabularyStore` is updated (new entries created, frequencies incremented, `status`
recomputed for this operation) before the response is returned — so a subsequent
`GET /api/vocabulary` immediately reflects it (FR-019, SC-007).

`tokenizer_mode == "bpe"` has **no side effects** — it only reads the current
`BpeModelStore` (FR-047, "must not learn ... during tokenization"); `GET /api/bpe/model`
is unaffected by tokenize calls.
