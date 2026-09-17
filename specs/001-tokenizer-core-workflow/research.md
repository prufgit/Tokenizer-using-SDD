# Phase 0 Research: Tokenizer Core Workflow

All explicit constraints (React+TS, FastAPI+Python, REST, tiktoken, PyMuPDF, Pydantic,
pytest, no DB, regex-based custom tokenizer) were given directly by the user and the
constitution, so no NEEDS CLARIFICATION markers remain in the Technical Context. The
items below are the technical *decisions* still needed to turn those constraints into an
implementable design.

## 1. Frontend test tooling

**Decision**: Vitest + React Testing Library.

**Rationale**: Vite-native (zero extra config/bundler for a Vite+React+TS app), fast,
and the de facto standard for component/hook testing in this stack. Satisfies
Constitution Principle VII ("frontend behavior MUST have appropriate automated tests")
without adding an unrelated framework.

**Alternatives considered**: Jest (works, but needs extra config to play well with
Vite's ESM/TS pipeline — redundant next to Vitest); Cypress/Playwright E2E (rejected —
constitution and user constraints call for no unnecessary infrastructure; end-to-end
smoke validation is instead covered manually via `quickstart.md`).

## 2. Custom Tokenizer splitting implementation

**Decision**: Single compiled regex `\w+|[^\w\s]`, applied with `re.finditer` over the
input text. Each match is one token: contiguous "word" characters (letters/digits/
underscore) form one token, and every other non-whitespace character (punctuation,
symbols) becomes its own single-character token. Whitespace is never emitted as a token.

**Rationale**: Directly implements the Clarifications decision ("split on whitespace and
punctuation — words and punctuation marks become separate tokens") and satisfies the
"use regex for custom tokenizer" constraint. `re.finditer` match objects expose
`.start()`/`.end()` directly, which gives exact character offsets for FR-007 with no
extra bookkeeping.

**Alternatives considered**: `str.split()` (loses punctuation-as-token behavior and
offsets); a hand-written character-scanning loop (more code, same result, no benefit
over regex given the explicit regex constraint).

## 3. Custom Tokenizer vocabulary ID assignment

**Decision**: A single in-memory `VocabularyStore` holding `token_to_id: dict[str, int]`,
`frequency: dict[str, int]`, and a monotonically increasing `next_id` counter starting at
0. On each token: if present in `token_to_id`, reuse its ID and increment frequency; if
absent, assign `next_id`, store it, increment `next_id`, set frequency to the count of
that token within the current operation, and record it in that operation's "newly
created" set.

**Rationale**: Satisfies FR-012–FR-016: reuse of existing IDs, creation of new entries,
deterministic ID assignment (same vocabulary state + same unseen token → same next ID),
frequency tracking, and correct "new" flagging even when a newly-seen token repeats
within one operation (Edge Case: created once, flagged once, frequency reflects all
occurrences).

**Alternatives considered**: Content-based hashing for IDs (rejected — determinism only
needs to hold for a given vocabulary state/sequence per FR-014 and the spec's acceptance
scenario, not across different vocabulary histories; hashing adds collision-handling
complexity with no requirement driving it).

## 4. Tiktoken character offsets

**Decision**: For each token ID returned by `encoding.encode(text)`, incrementally
decode using an incremental UTF-8 decoder (`codecs.getincrementaldecoder("utf-8")`) fed
one token's byte sequence (`encoding.decode_single_token_bytes(id)`) at a time. Track the
running decoded-character length before and after each token to derive its `start`/`end`
offsets in the original string.

**Rationale**: `tiktoken` operates on byte-pair merges over UTF-8 bytes, so individual
token boundaries do not always align with whole characters (a multi-byte character can
be split across two tokens). An incremental decoder correctly buffers partial multi-byte
sequences until enough bytes accumulate to form a full character, avoiding decode errors
and giving accurate offsets for FR-007 in Tiktoken mode.

**Alternatives considered**: Naive `token_bytes.decode("utf-8")` per token (raises
`UnicodeDecodeError` on tokens that end mid-character); approximate offsets by
byte-length ratio (would be inaccurate for multi-byte text, violating FR-007/SC-002's
"real token information" requirement).

## 5. Supported Tiktoken encodings source

**Decision**: Read the supported encoding list at startup from
`tiktoken.list_encoding_names()` rather than hardcoding a list, and validate any
user-selected encoding against that live list (FR-026).

**Rationale**: Keeps the "supported encodings" set automatically in sync with whichever
`tiktoken` version is installed, with zero risk of the app's list drifting out of step
with the library — consistent with Principle III's "Tiktoken behavior and vocabulary
MUST remain unchanged and externally authoritative."

**Alternatives considered**: A hardcoded list of encoding names (rejected — would need
manual updates and could silently reject encodings the installed library actually
supports, or accept ones it doesn't).

## 6. PDF extraction and failure classification

**Decision**: Open uploaded PDF bytes with PyMuPDF (`fitz.open(stream=..., filetype="pdf")`).
Treat `doc.needs_pass` (password-protected) and any `fitz` open/parse exception as
"invalid/corrupted PDF" (FR-024). If the document opens cleanly, concatenate
`page.get_text()` across all pages; if the stripped result is empty, classify as
"PDF with no extractable text" (FR-025) — a distinct error from a corrupted file.

**Rationale**: Matches the spec's Edge Case ("password-protected PDF MUST be treated as
invalid/corrupted") and keeps the two PDF failure messages (FR-024 vs FR-025) mutually
exclusive and testable.

**Alternatives considered**: OCR fallback for image-only PDFs (explicitly out of scope —
spec only requires extracting "normal text-based PDFs" and rejecting text-less ones with
a clear message, not making them extractable).

## 7. Vocabulary-view refresh strategy after a Custom Tokenizer operation

**Decision**: Keep `/api/tokenize` and `/api/vocabulary` as separate endpoints with one
shared response contract each. The frontend calls `GET /api/vocabulary` immediately after
any successful Custom Tokenizer `tokenize` call (chained in `useTokenize`), rather than
embedding a full vocabulary snapshot inside every `TokenizeResponse`.

**Rationale**: Keeps `TokenizeResponse` identical in shape regardless of tokenizer mode
(simpler contract, Principle III's "shared response contract"), and the vocabulary is
small enough (in-memory, single instance) that a follow-up GET has negligible cost while
still satisfying FR-019/SC-007's "immediately after... no manual refresh" requirement.

**Alternatives considered**: Embedding vocabulary state in the tokenize response
(rejected — couples an otherwise mode-agnostic response shape to Custom-mode-only data,
complicating the shared contract for no measurable benefit at this scale).

## 8. Frontend build tooling and state management

**Decision**: Vite for dev server/build; plain React `useState`/`useReducer` (lifted to
`App.tsx`, passed down via props/simple hooks) for state — no Redux/Zustand/React Query.

**Rationale**: The app has one shallow state tree (input, mode, request status, result,
vocabulary) with no cross-cutting async cache needs beyond two endpoints; a state library
would be pure overhead, violating the "no unnecessary frameworks or infrastructure"
constraint.

**Alternatives considered**: React Query/SWR for server-state caching (rejected — only
two read endpoints and one write-triggering endpoint, no caching/invalidation complexity
that justifies the dependency).

## 9. HTTP client

**Decision**: Native `fetch`, wrapped in `src/api/tokenizerClient.ts`.

**Rationale**: No auth headers, interceptors, or retry logic are required; `fetch` is
sufficient and avoids adding `axios` per the minimal-dependencies constraint.

**Alternatives considered**: `axios` (rejected — no feature gap `fetch` doesn't already
cover for this app's needs).

---

## BPE Amendment (User Stories 6-7, FR-032–FR-054)

The decisions below extend this research for the BPE enhancement to the Custom
Tokenizer. Nothing above this line changes: Tiktoken and the Simple strategy keep
their existing services, contracts, and behavior untouched.

## 10. BPE training algorithm

**Decision**: A plain iterative merge loop, matching well-known minimal/from-scratch
BPE implementations (e.g., the widely-referenced "minbpe" teaching approach), operating
at the character level per the Clarifications decision (whitespace is an ordinary
character, whole training text is one continuous stream — no word pre-tokenization):

1. Represent the training text as a list of single-character strings.
2. Repeat until the target vocabulary size is reached or no adjacent pair occurs more
   than once:
   a. Count the frequency of every adjacent pair of symbols in the current list.
   b. Pick the highest-frequency pair. **Tie-break**: the pair whose first occurrence
      appears earliest (leftmost) in the training text — achieved naturally by
      building the frequency count left-to-right into an insertion-ordered mapping
      and selecting the first maximal entry, since Python's `max()` returns the first
      element encountered among ties for insertion-ordered structures.
   c. Merge every non-overlapping occurrence of that pair (left-to-right) into one new
      symbol; assign it the next deterministic ID (see Decision 12); record the merge
      rule (Decision 13) and training step detail (pair selected, result).
3. Stop early (FR-040) once no pair occurs more than once — further merges would be
   arbitrary/non-useful — and report the vocabulary size actually achieved.

**Rationale**: With the now-clarified bounds (≤ 5,000-character training text, ≤ 500
target vocabulary size), this is at most ~500 merge steps over a ≤ 5,000-symbol list —
worst case on the order of a few million simple comparisons, comfortably fast in
Python with no need for a heap/priority-queue optimization. Keeping it simple also
keeps the "training step" log (FR-037) a direct byproduct of the loop rather than a
separately-reconstructed artifact. The leftmost tie-break makes training fully
deterministic (FR-036/SC-010) without needing a secondary sort key.

**Alternatives considered**: A frequency max-heap with lazy deletion (rejected —
meaningful only at far larger scale than this app's clarified limits allow; adds
complexity with no measurable benefit here). Byte-level BPE (rejected — the
Clarifications/Assumptions already settled on character-level for UI readability).

## 11. BPE vocabulary ID assignment

**Decision**: A monotonically increasing counter, exactly mirroring Decision 3's
approach for the Simple strategy's `VocabularyStore`. Base characters get IDs in the
order they first appear while scanning the training text left-to-right (0, 1, 2, …);
each subsequent merge step's resulting symbol gets the next ID, in training order.

**Rationale**: Directly satisfies FR-036 ("same training text + same target size →
same vocabulary, same merge rules, same IDs, in the same order") and stays consistent
with how the rest of the app already assigns deterministic IDs — no new ID scheme to
learn or justify.

**Alternatives considered**: Hashing token content (rejected for the same reason as
Decision 3 — no requirement needs cross-run/cross-vocabulary ID stability, only
same-input reproducibility).

## 12. BPE merge-rule application at tokenize time

**Decision**: Store merge rules as an ordered list, each with its learned rank (its
position in the list). To tokenize new text: first validate every character is in the
trained base-character set (else `BPE_UNKNOWN_CHARACTER`, FR-050); represent the text
as a list of single characters; repeatedly find the **lowest-rank** (earliest-learned)
merge rule whose pair still occurs adjacently anywhere in the current list, and apply
it (merge all its non-overlapping occurrences), until no learned rule's pair occurs
anywhere in the list. Then map the resulting symbol list to `Token`s with `id` from the
trained vocabulary, character-offset `start`/`end` from their position in the original
text (straightforward since the character stream has a direct 1:1 correspondence to
the source text — no filtering), and `is_new: false` for every token (nothing is ever
created at tokenize time, per FR-047).

**Rationale**: This is the standard BPE encode algorithm — applying learned merges in
learned order guarantees the same input always produces the same output (FR-047,
SC-011) and that tokenization can never invent a merge rule training didn't produce.

**Alternatives considered**: Greedy longest-match against the final vocabulary
(rejected — doesn't reproduce genuine BPE behavior and can disagree with the rule
order actually learned, breaking the "use those learned rules" requirement).

## 13. BPE model storage and retrain semantics

**Decision**: A single in-memory `BpeModelStore`, structurally parallel to the Simple
strategy's `VocabularyStore` (Decision 3) but fully independent from it: holds the
vocabulary (token → id), the ordered merge rules, the training step log, and the
achieved/target vocabulary sizes for the *current* trained model only. A successful
`POST /api/bpe/train` call atomically replaces the entire previous model (FR-041) — no
history/versioning of past training runs is kept, matching the Assumptions.

**Rationale**: Directly implements FR-032/FR-041 and the "independent of the Simple
strategy's vocabulary" Assumption; reusing the same in-memory-singleton pattern already
established for `VocabularyStore` keeps the codebase consistent (Principle VI: no
persistence, single source of truth per running instance).

**Alternatives considered**: Keeping a history of past trained models (rejected — not
requested, and the spec explicitly frames retraining as a full replacement).

## 14. API surface for BPE

**Decision**:
- Extend the existing `POST /api/tokenize` endpoint's `tokenizer_mode` to accept a
  third value, `"bpe"` (alongside `"tiktoken"` and `"custom"`), reusing the exact same
  request/response shape (`TokenizeResponse`) and the existing text/file input handling
  — directly implementing the Assumption that "tokenizing with a trained BPE model
  reuses the app's existing text/file input" and FR-048's "same tokenization result
  table."
- Add two new endpoints, since training has no equivalent in the existing contract:
  `POST /api/bpe/train` (JSON body: training text + target vocabulary size → the
  trained vocabulary, merge rules, and training steps) and `GET /api/bpe/model`
  (retrieve the current trained model, or an empty/untrained shape — FR-052).

**Rationale**: Keeps the tokenize contract's shape uniform across all three modes
(minimizes frontend branching) while giving training — which has a genuinely different
request/response shape and no file-upload need — its own small, focused contract.
`POST /api/bpe/train` uses a plain JSON body (not `multipart/form-data`) since, unlike
`/api/tokenize`, it never needs to accept a file.

**Alternatives considered**: A single combined `/api/bpe/*` sub-app mirroring
`/api/tokenize`'s multipart shape even for training (rejected — no file input for
training was requested, so multipart would add unused complexity to that request);
embedding training inside `/api/tokenize` via a special mode (rejected — training and
tokenizing have different inputs and different response shapes, which would force an
awkward union type onto one endpoint).

## 15. Frontend state modeling for the BPE strategy

**Decision**: Keep the top-level `tokenizerMode: "tiktoken" | "custom"` state exactly
as it is (FR-004 is unchanged). Add a second, independent piece of state,
`customStrategy: "simple" | "bpe"`, relevant only when `tokenizerMode === "custom"`
(FR-032). On the wire, `tokenizerClient.tokenize()` still sends one flat
`tokenizer_mode` form value — `"tiktoken"`, `"custom"`, or `"bpe"` — derived from these
two pieces of UI state, so the backend's `TokenizerMode` type/contract stays a simple
three-value enum despite the frontend visually nesting BPE under "Custom Tokenizer."

**Rationale**: Matches the spec's own framing (BPE is a strategy *within* Custom
Tokenizer mode, not a fourth top-level mode) while keeping the backend contract flat
and simple — UI grouping and wire representation are allowed to differ when, as here,
flattening the wire shape causes no ambiguity (the three modes are mutually exclusive
either way).

**Alternatives considered**: A compound wire value like `"custom:bpe"` (rejected —
unnecessary string-parsing on the backend for no benefit over a flat third enum value).

## 16. New frontend components and hooks

**Decision**:
- `components/bpe/BpeTrainingForm.tsx`: training-text textarea + target-vocab-size
  number input + "Start Training" button + its own loading/validation/error/success
  states — visually and functionally separate from the tokenize-input area (FR
  requirement to "clearly separate" the two flows).
- `components/bpe/BpeTrainingResult.tsx`: one combined table showing, per row, the
  order/step, the pair merged, the resulting token, and its ID — this single table
  satisfies both "show the learned vocabulary and merge rules" (FR-042/043) and "show
  training details: pair selected and merged at each step" (FR-044), since a merge
  rule *is* a training step's result; a separate raw vocabulary listing (id + token,
  including the base characters that were never merged) is shown alongside it to fully
  satisfy FR-042.
- `hooks/useBpeTraining.ts`: calls `POST /api/bpe/train`, manages that request's
  loading/error/success state.
- `hooks/useBpeModel.ts`: calls `GET /api/bpe/model` (mirrors `useVocabulary.ts`);
  refetched immediately after a successful training run (mirrors Decision 7's pattern)
  so the displayed model updates without a manual refresh (FR-045).
- BPE *tokenization* (User Story 7) reuses the existing `TextInput`/`FileUpload`/
  `TokenTable`/`StatsSummary`/`StateBanner` components and `useTokenize` hook
  unchanged, with `customStrategy === "bpe"` selecting `tokenizer_mode: "bpe"` on the
  request — no new components needed for that half of the flow.

**Rationale**: Reuses every existing, already-tested component wherever the shape
matches (tokenizing), and adds new components only where the flow is genuinely new
(training) — minimizing new frontend surface while satisfying the "clearly separate"
UI requirement.

**Alternatives considered**: Two separate tables for "vocabulary" and "merge
rules/training steps" (rejected — the merge-rule/training-step data is the same
information viewed two ways; one combined table plus the raw vocabulary list covers
FR-042–FR-044 without redundant UI).
