# Contract: Error Response Shape

Shared by every endpoint. Implements FR-027 (clear, user-friendly errors, no raw
internal output) via FastAPI exception handlers that translate internal/domain
exceptions into this shape — never letting a stack trace or framework default error
body reach the client.

## Shape

`application/json`

| Field | Type | Notes |
|---|---|---|
| `error_code` | enum | One of `EMPTY_INPUT`, `UNSUPPORTED_FILE_TYPE`, `FILE_TOO_LARGE`, `INVALID_PDF`, `PDF_NO_TEXT`, `UNSUPPORTED_ENCODING`, `BPE_TRAINING_TEXT_EMPTY`, `BPE_TRAINING_TEXT_TOO_LONG`, `BPE_TARGET_VOCAB_SIZE_INVALID`, `BPE_MODEL_NOT_TRAINED`, `BPE_UNKNOWN_CHARACTER` |
| `message` | string | Human-readable; safe to render directly in the UI |

The five `BPE_*` codes are used by `POST /api/bpe/train` (the first three) and
`POST /api/tokenize` when `tokenizer_mode == "bpe"` (the last two) — see
[bpe-train-endpoint.md](./bpe-train-endpoint.md) and
[tokenize-endpoint.md](./tokenize-endpoint.md).

## Status codes

All eleven `error_code` values are returned with HTTP `400`. FastAPI's own request-shape
validation errors (e.g., a missing required form field) return HTTP `422` with FastAPI's
standard validation error body — the frontend treats any non-2xx response as the error
state (FR-030) and prefers `message` when present, falling back to a generic message
otherwise.

## Example

```json
{
  "error_code": "PDF_NO_TEXT",
  "message": "This PDF doesn't contain any extractable text (it may be a scanned image). Try a text-based PDF or a TXT file instead."
}
```
