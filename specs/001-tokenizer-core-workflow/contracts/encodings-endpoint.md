# Contract: GET /api/encodings

Supports FR-005 (selecting a supported Tiktoken encoding) by giving the frontend a live
list to populate the encoding selector, sourced from `tiktoken.list_encoding_names()`
(see [research.md](../research.md), decision 5) — never hardcoded, so it can't drift from
what the installed `tiktoken` library actually supports (Principle III).

## Request

No parameters.

## Response — 200 OK

`application/json`, shape: `EncodingsResponse` (see [data-model.md](../data-model.md)).

```json
{ "encodings": ["cl100k_base", "o200k_base", "p50k_base", "r50k_base"] }
```

The exact list depends on the installed `tiktoken` version; the frontend must not
hardcode or assume specific values from it.
