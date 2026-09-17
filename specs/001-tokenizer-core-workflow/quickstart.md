# Quickstart: Tokenizer Core Workflow

Manual/CLI validation guide proving the feature works end-to-end. Not a full test suite
(see `tasks.md`/`backend/tests`, `frontend/tests` for that) — this is the fast path to
confirm the pieces are wired together correctly.

## Prerequisites

- Python 3.11+
- Node.js 18+
- A short `.txt` file and a small text-based `.pdf` file for manual upload testing

## Setup

```bash
# Backend
cd backend
pip install -r requirements.txt   # fastapi, uvicorn, tiktoken, pymupdf, pydantic, pytest

# Frontend
cd ../frontend
npm install
```

## Run

```bash
# Backend (from backend/)
uvicorn app.main:app --reload --port 8000

# Frontend (from frontend/, separate terminal)
npm run dev
```

Open the frontend dev URL (Vite default: http://localhost:5173).

## Validation scenarios

Each scenario maps to an Acceptance Scenario in [spec.md](./spec.md). Use the UI, or the
equivalent `curl` against `http://localhost:8000/api/tokenize`.

### 1. Tiktoken tokenization (User Story 1)

1. Type `Hello, world!` into the text input.
2. Select tokenizer mode "Tiktoken" and encoding `cl100k_base` (from `GET /api/encodings`).
3. Run tokenization.
4. **Expect**: token list with real IDs/text for that encoding, plus stats
   (`character_count: 13`, `word_count: 2`, etc.) — see
   [contracts/tokenize-endpoint.md](./contracts/tokenize-endpoint.md).
5. Switch encoding (e.g., to `o200k_base`) and re-run. **Expect**: token IDs change to
   match the new encoding.

### 2. Custom Tokenizer + vocabulary growth (User Story 2)

1. Select tokenizer mode "Custom Tokenizer".
2. Tokenize `Hello, world!`. **Expect**: every token marked `is_new: true`; vocabulary
   grows from empty to 3 entries (`Hello`, `,`, `world`).
3. Tokenize `Hello, again!`. **Expect**: `Hello` and `,` reuse their existing IDs with
   `is_new: false` and incremented frequency; `again` and `!` are new.
4. Re-tokenize `Hello, world!` a second time (unchanged vocabulary). **Expect**: same
   token IDs as step 2's result — deterministic (SC-003).

### 3. File upload (User Story 3)

1. Upload the sample `.txt` file. **Expect**: same kind of result as typing its contents.
2. Upload the sample `.pdf` file. **Expect**: extracted text tokenized identically to
   typing that same text.

### 4. Vocabulary view and reset (User Story 4)

1. After step 2 above, open the vocabulary view. **Expect**: all entries listed with
   ID/token/frequency/status, `status: "new"` only for tokens from the *last* operation.
2. Click reset. **Expect**: `GET /api/vocabulary` returns `{ "entries": [], "total_entries": 0 }`.
3. Re-tokenize `Hello, world!`. **Expect**: `Hello`, `,`, `world` are `is_new: true` again
   (vocabulary was cleared).

### 5. Validation and states (User Story 5)

Trigger each and confirm a clear, specific error (`error_code` + `message`) and that the
UI shows the error state, not a blank screen or stack trace:

| Action | Expected `error_code` |
|---|---|
| Submit with no text and no file | `EMPTY_INPUT` |
| Upload a `.docx` or `.png` file | `UNSUPPORTED_FILE_TYPE` |
| Upload a file > 10 MB | `FILE_TOO_LARGE` |
| Upload a corrupted/password-protected PDF | `INVALID_PDF` |
| Upload a scanned/image-only PDF | `PDF_NO_TEXT` |
| Select an unsupported encoding string in Tiktoken mode | `UNSUPPORTED_ENCODING` |

Also confirm: a loading indicator appears while a request is in flight; the initial
screen (no input yet) shows the empty state; a successful run shows the success state
with results.

### 6. Train a BPE tokenizer (User Story 6)

1. Select tokenizer mode "Custom Tokenizer" → strategy "BPE".
2. Confirm the BPE vocabulary/merge-rule area shows the empty state (`GET /api/bpe/model`
   → `trained: false`) before any training has run.
3. Enter training text `aaabdaaabac` and target vocabulary size `10` (a small,
   hand-verifiable example), then start training.
4. **Expect**: `POST /api/bpe/train` returns `trained: true` with a vocabulary, ordered
   merge rules, and training steps; the first learned merge is `("a", "a")` (the most
   frequent adjacent pair), since it occurs more often than any other pair in that text.
5. Re-run training with the exact same text and target size. **Expect**: identical
   vocabulary, merge rules, and IDs (SC-010).
6. Start a new training run with different text. **Expect**: the previous model is
   fully replaced, not merged (FR-041).

### 7. Tokenize with the trained BPE tokenizer (User Story 7)

1. With a BPE model trained (see scenario 6), enter new text built only from characters
   that appeared in the training text (e.g., `aabc`) and tokenize with the "BPE"
   strategy.
2. **Expect**: tokens/IDs come from the trained vocabulary, in the existing
   tokenization result table, every `is_new: false` (FR-047, FR-048).
3. Tokenize the same text again. **Expect**: identical tokens/IDs (SC-011).
4. Tokenize text containing a character never seen during training (e.g., `z`).
   **Expect**: `BPE_UNKNOWN_CHARACTER` error, not a crash or silent drop (FR-050).
5. Reset the app state (or use a fresh backend process) and attempt to tokenize with
   "BPE" strategy before training. **Expect**: `BPE_MODEL_NOT_TRAINED` error (FR-049).

### 8. BPE validation (User Story 6/7 hardening)

| Action | Expected `error_code` |
|---|---|
| Start training with empty/whitespace-only training text | `BPE_TRAINING_TEXT_EMPTY` |
| Start training with text over 5,000 characters | `BPE_TRAINING_TEXT_TOO_LONG` |
| Start training with target vocab size ≤ 0, smaller than the training text's distinct-character count, or > 500 | `BPE_TARGET_VOCAB_SIZE_INVALID` |
| Tokenize with "BPE" strategy before training | `BPE_MODEL_NOT_TRAINED` |
| Tokenize BPE-mode text containing an unseen character | `BPE_UNKNOWN_CHARACTER` |

## Automated checks

```bash
# Backend
cd backend
pytest

# Frontend
cd ../frontend
npm run test
```
