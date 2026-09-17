# Contract: Custom Tokenizer Vocabulary Endpoints

Both routes are thin wrappers over `vocabulary_store`. Implements FR-011, FR-017,
FR-020.

## GET /api/vocabulary

Returns the current Custom Tokenizer vocabulary, `status` per entry computed relative to
the most recently completed Custom Tokenizer operation (FR-016, FR-017).

### Response — 200 OK

`application/json`, shape: `VocabularyResponse` (see [data-model.md](../data-model.md)).

```json
{
  "entries": [
    { "id": 0, "token": "Hello", "frequency": 3, "status": "existing" },
    { "id": 1, "token": ",", "frequency": 3, "status": "existing" },
    { "id": 2, "token": "world", "frequency": 1, "status": "new" }
  ],
  "total_entries": 3
}
```

An empty vocabulary (initial state, or immediately after reset) returns
`{ "entries": [], "total_entries": 0 }`.

## POST /api/vocabulary/reset

Clears the vocabulary back to its initial empty state (FR-020). Idempotent — resetting
an already-empty vocabulary succeeds and returns the same empty shape.

### Response — 200 OK

`application/json`, shape: `VocabularyResponse`, always `{ "entries": [], "total_entries": 0 }`.

No request body required.
