---

description: "Task list for Tokenizer Core Workflow"
---

# Tasks: Tokenizer Core Workflow

**Input**: Design documents from `/specs/001-tokenizer-core-workflow/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included and REQUIRED — Constitution Principle VII mandates pytest coverage
for every backend feature and automated tests for every frontend behavior.

**Organization**: Tasks are grouped by user story (from spec.md, in priority order) so
each story can be implemented, tested, and demoed independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: Maps the task to US1–US5 from spec.md
- File paths are exact, per plan.md's project structure

## Path Conventions

Web application layout per plan.md: `backend/app/...`, `backend/tests/...`,
`frontend/src/...`, `frontend/tests/...`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Scaffold both projects so later tasks have somewhere to land.

- [X] T001 [P] Create backend directory tree (`backend/app/api/routes/`,
      `backend/app/schemas/`, `backend/app/services/`, `backend/app/core/`,
      `backend/tests/unit/`, `backend/tests/contract/`, `backend/tests/integration/`,
      `backend/tests/fixtures/`) per plan.md's Project Structure
- [X] T002 [P] Create frontend directory tree (`frontend/src/api/`,
      `frontend/src/components/input/`, `frontend/src/components/results/`,
      `frontend/src/components/vocabulary/`, `frontend/src/hooks/`, `frontend/src/types/`,
      `frontend/src/styles/`, `frontend/tests/components/`, `frontend/tests/hooks/`)
      per plan.md's Project Structure
- [X] T003 [P] Create `backend/requirements.txt` (`fastapi`, `uvicorn`, `tiktoken`,
      `pymupdf`, `pydantic`, `pytest`, `httpx`) per research.md and install
- [X] T004 [P] Create `frontend/package.json` (`react`, `react-dom`, `typescript`,
      `vite`, `vitest`, `@testing-library/react`, `@testing-library/jest-dom`) and
      `vite.config.ts`/`tsconfig.json` per research.md decision 1 and 8, then install
- [X] T005 [P] Create `backend/app/core/config.py` `Settings` (Pydantic
      `BaseSettings`): `max_upload_size_bytes=10_485_760`, `allowed_cors_origins`
      (env-overridable) per data-model.md TokenizeRequest validation rules
- [X] T006 [P] Create `frontend/src/styles/theme.css` with dark/neon-gradient
      ("cyberpunk") design tokens: `--bg-primary`, `--bg-panel`, `--accent-cyan`,
      `--accent-magenta`, `--accent-violet`, `--text-primary`, `--text-muted`,
      `--border-neon`, `--new-token-glow`, monospace token font

**Checkpoint**: Both project skeletons exist and install cleanly.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared plumbing every user story's tokenize/vocabulary calls run through.

**⚠️ CRITICAL**: No user story task may start until this phase is complete.

- [X] T007 Create `backend/app/main.py`: FastAPI app factory + `CORSMiddleware`
      configured from `Settings.allowed_cors_origins` (depends on T005)
- [X] T008 [P] Create `backend/app/schemas/errors.py`: `ErrorCode` enum
      (`EMPTY_INPUT`, `UNSUPPORTED_FILE_TYPE`, `FILE_TOO_LARGE`, `INVALID_PDF`,
      `PDF_NO_TEXT`, `UNSUPPORTED_ENCODING`) and `ErrorResponse` per
      contracts/error-schema.md
- [X] T009 Create `backend/app/core/errors.py`: one domain exception class per
      `ErrorCode` and a FastAPI exception handler (registered in `main.py`, depends
      on T007, T008) translating each to the `ErrorResponse` shape — never leaking
      stack traces (FR-027)
- [X] T010 [P] Create `backend/app/schemas/tokenize.py`: `Token`, `Statistics`,
      `TokenizeResponse` Pydantic models per data-model.md
- [X] T011 [P] Create `backend/app/services/statistics.py`:
      `compute_statistics(text, token_count) -> Statistics` implementing the
      character/word/token-count and ratio formulas in data-model.md (shared by
      every tokenizer mode)
- [X] T012 Create `frontend/src/types/api.ts`: TypeScript interfaces mirroring
      `Token`, `Statistics`, `TokenizeResponse`, `ErrorResponse`,
      `CustomVocabularyEntry`, `VocabularyResponse`, `EncodingsResponse` from
      data-model.md
- [X] T013 [P] Create `frontend/src/api/tokenizerClient.ts`: generic `fetch`
      wrapper (base URL from `import.meta.env`, JSON/multipart handling, parses
      `ErrorResponse` on non-2xx) with stub exports `tokenize`, `getEncodings`,
      `getVocabulary`, `resetVocabulary` (depends on T012)
- [X] T014 [P] Create `frontend/src/components/results/StateBanner.tsx`: renders
      loading / empty / error / success sub-views based on a `requestState` prop
      (FR-028–FR-031), styled per T006's theme tokens

**Checkpoint**: Foundation ready — user story phases can now begin.

---

## Phase 3: User Story 1 - Tokenize Typed Text with Tiktoken (Priority: P1) 🎯 MVP

**Goal**: A user types text, picks Tiktoken + an encoding, and sees real tokens and
stats.

**Independent Test**: Type a short passage, select an encoding, tokenize, and confirm
returned tokens/IDs match that encoding's real output and stats are correct.

### Tests for User Story 1

- [X] T015 [P] [US1] Unit tests for `tiktoken_service` (encode, ID/text correctness
      for ≥2 encodings, offset correctness including a multi-byte-character input) in
      `backend/tests/unit/test_tiktoken_service.py`
- [X] T016 [P] [US1] Contract test for `GET /api/encodings` (response shape, non-empty
      list) in `backend/tests/contract/test_encodings_contract.py`
- [X] T017 [P] [US1] Contract test for `POST /api/tokenize` in Tiktoken mode (success
      shape, `EMPTY_INPUT`, `UNSUPPORTED_ENCODING`) in
      `backend/tests/contract/test_tokenize_contract.py`
- [X] T018 [P] [US1] Integration test: full typed-text → Tiktoken → response flow via
      `TestClient`, asserting stats match hand-computed values, in
      `backend/tests/integration/test_tokenize_tiktoken_flow.py`

### Implementation for User Story 1

- [X] T019 [US1] Implement `backend/app/services/tiktoken_service.py`: `list_encodings()`
      (from `tiktoken.list_encoding_names()`), `tokenize(text, encoding_name) -> list[Token]`
      using the incremental-UTF-8-decoder offset technique from research.md decision 4
      (depends on T010; make tests from T015 pass)
- [X] T020 [US1] Implement `backend/app/api/routes/encodings.py`:
      `GET /api/encodings` → `tiktoken_service.list_encodings()` (depends on T019;
      make T016 pass)
- [X] T021 [US1] Implement `backend/app/api/routes/tokenize.py`: `POST /api/tokenize`
      handling `text` input + `tokenizer_mode="tiktoken"` — validate non-empty text
      (raise `EMPTY_INPUT`), validate encoding via `tiktoken_service.list_encodings()`
      (raise `UNSUPPORTED_ENCODING`), call `tiktoken_service.tokenize`, call
      `statistics.compute_statistics`, return `TokenizeResponse` (depends on T009,
      T010, T011, T019; make T017, T018 pass)
- [X] T022 Register `tokenize` and `encodings` routers in `backend/app/main.py`
      (depends on T020, T021)
- [X] T023 [P] [US1] Create `frontend/src/components/input/TextInput.tsx`
- [X] T024 [P] [US1] Create `frontend/src/components/input/TokenizerModeToggle.tsx`
      (tiktoken/custom switch; only "tiktoken" wired end-to-end this phase)
- [X] T025 [P] [US1] Create `frontend/src/components/input/EncodingSelect.tsx`,
      populated via `tokenizerClient.getEncodings()` (depends on T013)
- [X] T026 [P] [US1] Create `frontend/src/components/results/StatsSummary.tsx`
      (renders `Statistics`)
- [X] T027 [US1] Create `frontend/src/components/results/TokenTable.tsx` (columns:
      index, id, text, start–end offset)
- [X] T028 [US1] Create `frontend/src/hooks/useTokenize.ts`: calls
      `tokenizerClient.tokenize`, manages `requestState`
      (`idle`/`loading`/`success`/`error`) and `result`/`errorMessage` (depends on
      T013)
- [X] T029 [US1] Wire `TextInput` + `TokenizerModeToggle` + `EncodingSelect` + submit
      action + `StateBanner` + `StatsSummary` + `TokenTable` together in
      `frontend/src/App.tsx` (depends on T014, T023–T028)
- [X] T030 [P] [US1] Component tests for `TextInput`, `EncodingSelect`,
      `StatsSummary`, `TokenTable` in `frontend/tests/components/`
- [X] T031 [P] [US1] Hook test for `useTokenize` (success + error paths, mocked
      `fetch`) in `frontend/tests/hooks/useTokenize.test.ts`

**Checkpoint**: User Story 1 is fully functional and independently testable (MVP).

---

## Phase 4: User Story 2 - Tokenize Typed Text with Custom Tokenizer (Priority: P2)

**Goal**: A user tokenizes with the Custom Tokenizer and sees its vocabulary grow
deterministically, with new tokens flagged.

**Independent Test**: Tokenize text with Custom Tokenizer mode; confirm IDs are reused
for repeat tokens, new tokens get new IDs and are flagged, and identical repeat input
yields identical output.

### Tests for User Story 2

- [X] T032 [P] [US2] Unit tests for `custom_tokenizer_service` (regex splitting
      `\w+|[^\w\s]`, exact offsets, ID reuse vs. creation, `is_new` correctness
      including a token repeated within one operation) in
      `backend/tests/unit/test_custom_tokenizer_service.py`
- [X] T033 [P] [US2] Unit tests for `vocabulary_store` (sequential deterministic ID
      assignment, frequency accumulation across multiple operations, `reset()`
      returns it to empty and restarts ID assignment) in
      `backend/tests/unit/test_vocabulary_store.py`
- [X] T034 [P] [US2] Extend `backend/tests/contract/test_tokenize_contract.py` with
      Custom Tokenizer mode cases (success shape, `is_new` present, `encoding: null`)
- [X] T035 [P] [US2] Integration test: tokenize same input twice against the same
      vocabulary state and assert identical tokens/IDs (SC-003); tokenize
      overlapping inputs and assert correct reuse/creation, in
      `backend/tests/integration/test_tokenize_custom_flow.py`

### Implementation for User Story 2

- [X] T036 [US2] Implement `backend/app/services/vocabulary_store.py`:
      `VocabularyStore` class (`token_to_id`, `frequency`, `next_id` counter, last-
      operation new-token set, a `threading.Lock` guarding mutations, `reset()`) per
      research.md decision 3 and data-model.md's state transitions (make T033 pass)
- [X] T037 [US2] Implement `backend/app/services/custom_tokenizer_service.py`:
      `tokenize(text, store: VocabularyStore) -> list[Token]` using
      `re.finditer(r"\w+|[^\w\s]", text)` for offsets, looking up/creating entries in
      `store` (depends on T036; make T032 pass)
- [X] T038 [US2] Extend `backend/app/api/routes/tokenize.py` to branch on
      `tokenizer_mode == "custom"`, calling `custom_tokenizer_service.tokenize` with
      the shared `VocabularyStore` instance instead of `tiktoken_service` (depends on
      T021, T037; make T034, T035 pass)
- [X] T039 [P] [US2] Extend `frontend/src/components/results/TokenTable.tsx` to
      render a neon-glow "new" badge/style when `token.is_new === true` (depends on
      T027)
- [X] T040 [US2] Wire the Custom Tokenizer branch of `TokenizerModeToggle` end-to-end
      in `App.tsx`/`useTokenize` (hide `EncodingSelect` when mode is "custom")
      (depends on T029)
- [X] T041 [P] [US2] Component test asserting new-token styling in
      `frontend/tests/components/TokenTable.test.tsx` (depends on T030, T039)

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Tokenize Uploaded TXT and PDF Files (Priority: P2)

**Goal**: A user uploads a TXT or text-based PDF instead of typing, and it tokenizes
identically to typing the same text.

**Independent Test**: Upload a valid `.txt` and a valid text-based `.pdf` separately;
confirm each produces the same kind of results as typing their contents.

### Tests for User Story 3

- [X] T042 [P] [US3] Unit tests for `file_processing` (TXT decode; valid PDF
      extraction via fixture; corrupted PDF → `INVALID_PDF`; password-protected PDF
      → `INVALID_PDF`; image-only PDF → `PDF_NO_TEXT`; >10MB → `FILE_TOO_LARGE`;
      wrong type → `UNSUPPORTED_FILE_TYPE`) in
      `backend/tests/unit/test_file_processing.py`
- [X] T043 [P] [US3] Extend `backend/tests/contract/test_tokenize_contract.py` with
      file-upload request cases (both `text` and `file` present → `400`; each file
      error code)
- [X] T044 [P] [US3] Integration test: upload TXT fixture and PDF fixture through
      `POST /api/tokenize`, assert extracted-text results match the equivalent typed
      -text results, in `backend/tests/integration/test_tokenize_file_upload_flow.py`

### Implementation for User Story 3

- [X] T045 [US3] Add fixtures to `backend/tests/fixtures/`: `sample.txt`,
      `sample_text.pdf` (text-based), `corrupted.pdf`, `password_protected.pdf`,
      `image_only.pdf` (no extractable text)
- [X] T046 [US3] Implement `backend/app/services/file_processing.py`: type/size
      validation, TXT decode (UTF-8), PDF extraction via
      `fitz.open(stream=..., filetype="pdf")` + `page.get_text()`, classification of
      `doc.needs_pass`/open errors as `INVALID_PDF` and empty extracted text as
      `PDF_NO_TEXT`, per research.md decision 6 (depends on T009, T045; make T042
      pass)
- [X] T047 [US3] Extend `backend/app/api/routes/tokenize.py` to accept an optional
      `file` field, enforce "exactly one of text/file" (else `400`), call
      `file_processing` when a file is present, then continue into the existing
      tiktoken/custom dispatch (depends on T038, T046; make T043, T044 pass)
- [X] T048 [P] [US3] Create `frontend/src/components/input/FileUpload.tsx` (file
      picker, mutually exclusive with `TextInput`, client-side filename/size hint
      only — authoritative validation stays server-side per Principle V)
- [X] T049 [US3] Wire `FileUpload` into `App.tsx`'s input flow and `useTokenize`'s
      multipart submission (depends on T028, T029, T048)
- [X] T050 [P] [US3] Component test for `FileUpload` in
      `frontend/tests/components/FileUpload.test.tsx`

**Checkpoint**: User Stories 1, 2, and 3 all work independently.

---

## Phase 6: User Story 4 - View and Reset Custom Tokenizer Vocabulary (Priority: P3)

**Goal**: A user views the full Custom Tokenizer vocabulary and can reset it to empty.

**Independent Test**: Populate the vocabulary via a Custom Tokenizer run, confirm the
vocabulary view lists every entry correctly, reset, and confirm it's empty.

### Tests for User Story 4

- [X] T051 [P] [US4] Contract tests for `GET /api/vocabulary` and
      `POST /api/vocabulary/reset` (shapes, empty-state shape) in
      `backend/tests/contract/test_vocabulary_contract.py`
- [X] T052 [P] [US4] Integration test: tokenize (custom mode) → `GET /api/vocabulary`
      shows correct entries/status → reset → `GET /api/vocabulary` is empty → re
      -tokenize same text → all tokens `is_new: true` again, in
      `backend/tests/integration/test_vocabulary_lifecycle.py`

### Implementation for User Story 4

- [X] T053 [P] [US4] Create `backend/app/schemas/vocabulary.py`:
      `CustomVocabularyEntry`, `VocabularyResponse` per data-model.md
- [X] T054 [US4] Create `backend/app/api/routes/vocabulary.py`:
      `GET /api/vocabulary` (entries with `status` computed from the store's last-
      operation new-token set) and `POST /api/vocabulary/reset` (calls
      `VocabularyStore.reset()`); register router in `main.py` (depends on T036,
      T053; make T051, T052 pass)
- [X] T055 [P] [US4] Create `frontend/src/components/vocabulary/VocabularyTable.tsx`
      (id, token, frequency, status badge)
- [X] T056 [P] [US4] Create
      `frontend/src/components/vocabulary/ResetVocabularyButton.tsx`
- [X] T057 [US4] Create `frontend/src/hooks/useVocabulary.ts`: `fetch`, `reset`, and
      auto-refetch immediately after every successful Custom Tokenizer `tokenize`
      call per research.md decision 7 (depends on T013, T028, T040)
- [X] T058 [US4] Wire `VocabularyTable` + `ResetVocabularyButton` +
      `useVocabulary` into `App.tsx` (depends on T055, T056, T057)
- [X] T059 [P] [US4] Component/hook tests for `VocabularyTable`,
      `ResetVocabularyButton`, and `useVocabulary` in `frontend/tests/`

**Checkpoint**: User Stories 1–4 all work independently.

---

## Phase 7: User Story 5 - Clear Feedback for Invalid Input and Processing States (Priority: P3)

**Goal**: Every specified invalid input produces a clear, specific error, and the UI
always shows the correct one of loading/empty/error/success.

**Independent Test**: Deliberately trigger each of the six invalid-input scenarios and
confirm a distinct, human-readable error each time; confirm loading/empty/success
states appear at the right moments.

### Tests for User Story 5

- [X] T060 [P] [US5] Integration test asserting each of the six `ErrorCode` values is
      reachable end-to-end with its expected `message`, in
      `backend/tests/integration/test_validation_errors.py`
- [X] T061 [P] [US5] Component tests asserting `StateBanner` renders the correct
      state (loading/empty/error/success) and surfaces each backend `message`
      verbatim, in `frontend/tests/components/StateBanner.test.tsx`

### Implementation for User Story 5

- [X] T062 [US5] Finalize clear, user-friendly `message` copy for every `ErrorCode`
      in `backend/app/core/errors.py` (FR-027; make T060 pass)
- [X] T063 [US5] Ensure every input surface (`TextInput`, `FileUpload`,
      `EncodingSelect`) and `App.tsx` route their `useTokenize`/`useVocabulary`
      errors through `StateBanner`, and that empty/loading/success are reachable
      from initial load through to a completed run (depends on T014, T029, T049,
      T058; make T061 pass)
- [X] T064 [P] [US5] Final pass applying `theme.css` neon-gradient/cyberpunk tokens
      consistently across all input/results/vocabulary components (depends on T006
      and all component tasks)

**Checkpoint**: All five user stories are independently functional, validated, and
visually consistent.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Whole-system verification against plan.md and the constitution.

- [X] T065 [P] Run `cd backend && pytest` and fix any failures across all suites
- [X] T066 [P] Run `cd frontend && npm run test` and fix any failures across all
      suites
- [X] T067 Execute every scenario in quickstart.md manually and confirm expected
      outcomes
- [X] T068 [P] Audit `backend/app/api/routes/*.py` for Constitution Principle IV
      (routes stay thin; no business logic outside `services/`)
- [X] T069 [P] Audit `frontend/src/**` for Constitution Principle II (no
      tokenization/statistics/vocabulary logic outside `tokenizerClient.ts`
      response handling)
- [X] T070 Add `README.md` with setup/run instructions referencing quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3–7)**: All depend on Foundational completion
  - US2, US3 build on the `tokenize` route US1 creates (same file, sequential edits)
    but are independently testable once their own tasks land
  - US4 depends on US2's `VocabularyStore` existing (T036)
  - US5 is a hardening pass over all prior stories' error/state paths
  - Recommended order given these realities: P1 → P2 (US2) → P2 (US3) → P3 (US4) →
    P3 (US5), i.e., priority order
- **Polish (Phase 8)**: Depends on all desired user stories being complete
- **Convergence (Phase 9)**: A later `/speckit-converge` pass; independent test-coverage
  additions with no dependency on Phases 10–12
- **BPE amendment (Phases 10–12)**: Added by a later `/speckit-plan` +
  `/speckit-tasks` pass covering User Stories 6–7 (FR-032–FR-054). Depends only on
  Foundational (Phase 2) — not on Phases 3–9 — since `bpe_service`/`bpe_model_store`
  are fully independent of `custom_tokenizer_service`/`VocabularyStore`. US7 (Phase 11)
  depends on US6 (Phase 10) completing first: there is nothing to tokenize with until a
  model has been trained.

### Within Each User Story

- Tests are written first and must fail before implementation
- Schemas/services before routes; routes before frontend wiring
- Story complete and independently checkpointed before moving to the next

### Parallel Opportunities

- T001–T006 (Setup) can all run in parallel
- T008, T010, T011, T013, T014 (Foundational, distinct files) can run in parallel
  after T007/T012 where noted
- Within each story, all `[P]`-marked test tasks can run together, and all `[P]`
  -marked component tasks can run together
- US1 and later stories cannot start in parallel with each other in practice (they
  share `tokenize.py`/`App.tsx`), but their test-writing tasks can be drafted ahead
- Within the BPE amendment, US6's test tasks (T074–T077) can all run in parallel with
  each other; T085/T086 (frontend API client + types) can run in parallel; T092/T093
  (US6 component/hook tests) can run in parallel with each other

---

## Parallel Example: User Story 1

```bash
# Backend tests together:
Task: "Unit tests for tiktoken_service in backend/tests/unit/test_tiktoken_service.py"
Task: "Contract test for GET /api/encodings in backend/tests/contract/test_encodings_contract.py"
Task: "Contract test for POST /api/tokenize in backend/tests/contract/test_tokenize_contract.py"

# Frontend components together:
Task: "Create TextInput.tsx"
Task: "Create TokenizerModeToggle.tsx"
Task: "Create EncodingSelect.tsx"
Task: "Create StatsSummary.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: run quickstart.md scenario 1 independently
5. Demo: real Tiktoken tokenization with stats — a working tokenizer inspector

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. + User Story 1 → validate → demo (MVP)
3. + User Story 2 → validate → demo (Custom Tokenizer + vocabulary growth)
4. + User Story 3 → validate → demo (file upload)
5. + User Story 4 → validate → demo (vocabulary view/reset)
6. + User Story 5 → validate → demo (full error/state hardening)
7. Phase 8 polish → final quickstart.md full run
8. Phase 9 convergence → close pre-BPE test-coverage gaps
9. + User Story 6 → validate → demo (train a BPE tokenizer, see vocabulary/merge
   rules/training steps)
10. + User Story 7 → validate → demo (tokenize with the trained BPE model)
11. Phase 12 polish → final quickstart.md full run, including BPE scenarios

## Notes

- `[P]` tasks touch different files and have no incomplete-task dependency
- `[Story]` label maps every user-story-phase task to US1–US7 for traceability
- Tests are required per the constitution (Principle VII) — write them first per
  story, confirm they fail, then implement
- Commit after each task or logical group
- Stop at any checkpoint to validate a story independently before continuing

---

## Phase 9: Convergence

**Purpose**: Close gaps found by `/speckit-converge` between the spec/plan/tasks and the
current code, after `/speckit-implement` completed all of Phases 1–8.

- [X] T071 [P] Add backend/tests/unit/test_statistics.py covering `compute_statistics`
      in backend/app/services/statistics.py, including its zero-division guard
      branches (`word_count == 0`, `character_count == 0`), which no existing test
      (direct or indirect) currently exercises per plan.md (missing)
- [X] T072 [P] Add an automated check verifying SC-001 ("users can tokenize typed
      text and see full results in under 2 seconds for inputs up to 5,000
      characters") — e.g. a timing assertion in
      backend/tests/integration/test_tokenize_tiktoken_flow.py — since no test or
      benchmark currently measures this per spec.md Success Criteria (missing)
- [X] T073 [P] Add a test case uploading a whitespace-only `.txt` file through
      `POST /api/tokenize` and asserting `EMPTY_INPUT`, in
      backend/tests/unit/test_file_processing.py or
      backend/tests/contract/test_tokenize_contract.py, to lock in the existing
      whitespace-only-file-content handling per spec.md Edge Cases / FR-021
      (partial)

---

## Phase 10: User Story 6 - Train a Custom BPE Tokenizer (Priority: P4)

**Goal**: A user enters training text and a target vocabulary size, starts training,
and sees the learned vocabulary, ordered merge rules, and per-step training detail.

**Independent Test**: Train on text, confirm vocabulary/merge rules/training steps are
displayed correctly — independent of ever tokenizing anything with the result.

**Depends on**: Foundational (Phase 2) only — fully independent of Phases 3–9 (see
Dependencies & Execution Order).

### Tests for User Story 6

- [X] T074 [P] [US6] Unit tests for the BPE training algorithm in
      `backend/app/services/bpe_service.py`: the classic `"aaabdaaabac"` example
      (first merge must be `("a","a")`), deterministic leftmost tie-break, determinism
      across two runs with identical input, and early stop when no pair repeats
      (FR-040), in `backend/tests/unit/test_bpe_service.py`
- [X] T075 [P] [US6] Unit tests for `bpe_model_store.py`: initial/untrained state,
      `trained: true` after a successful train, and full replacement (not merge) on a
      second training run, in `backend/tests/unit/test_bpe_model_store.py`
- [X] T076 [P] [US6] Contract test for `POST /api/bpe/train` and `GET /api/bpe/model`
      (success shapes per contracts/bpe-train-endpoint.md and
      contracts/bpe-model-endpoint.md; `BPE_TRAINING_TEXT_EMPTY`,
      `BPE_TRAINING_TEXT_TOO_LONG`, `BPE_TARGET_VOCAB_SIZE_INVALID` error cases) in
      `backend/tests/contract/test_bpe_contract.py`
- [X] T077 [P] [US6] Integration test: train → `GET /api/bpe/model` reflects it
      immediately → train again with different text → previous model fully replaced,
      in `backend/tests/integration/test_bpe_training_flow.py`

### Implementation for User Story 6

- [X] T078 [P] [US6] Create `backend/app/schemas/bpe.py`: `BpeTrainRequest`,
      `BpeVocabularyEntry`, `BpeMergeRule`, `BpeTrainingStep`, `BpeModelResponse` per
      data-model.md (make T076 pass)
- [X] T079 [P] [US6] Extend `backend/app/schemas/errors.py`: add
      `BPE_TRAINING_TEXT_EMPTY`, `BPE_TRAINING_TEXT_TOO_LONG`,
      `BPE_TARGET_VOCAB_SIZE_INVALID`, `BPE_MODEL_NOT_TRAINED`,
      `BPE_UNKNOWN_CHARACTER` to the `ErrorCode` enum (all five now, since US7 needs
      the last two)
- [X] T080 [US6] Extend `backend/app/core/errors.py`: add one domain exception class
      per new `ErrorCode` from T079 (depends on T079)
- [X] T081 [US6] Implement `backend/app/services/bpe_model_store.py`: `BpeModelStore`
      (vocabulary, ordered merge rules, training steps, target/achieved vocab size,
      `threading.Lock`, full-replace-on-train) per research.md Decision 13 (make T075
      pass)
- [X] T082 [US6] Implement `backend/app/services/bpe_service.py`:
      `validate_training_text()`, `validate_target_vocab_size()`, and
      `train(training_text, target_vocab_size, store)` implementing the iterative
      merge loop with leftmost tie-break and deterministic ID assignment per
      research.md Decisions 10–11 (depends on T080, T081; make T074 pass)
- [X] T083 [US6] Implement `backend/app/api/routes/bpe.py`:
      `POST /api/bpe/train` (parse JSON body → `bpe_service.train` → `BpeModelResponse`)
      and `GET /api/bpe/model` (read `bpe_model_store` → `BpeModelResponse`, with the
      `trained: false` empty shape when untrained) (depends on T078, T082; make T076,
      T077 pass)
- [X] T084 [US6] Register the `bpe` router in `backend/app/main.py` (depends on T083)
- [X] T085 [P] [US6] Add `trainBpe` and `getBpeModel` functions to
      `frontend/src/api/tokenizerClient.ts`
- [X] T086 [P] [US6] Extend `frontend/src/types/api.ts`: `BpeVocabularyEntry`,
      `BpeMergeRule`, `BpeTrainingStep`, `BpeModelResponse`, `BpeTrainRequest`
      per data-model.md
- [X] T087 [US6] Create `frontend/src/components/bpe/BpeTrainingForm.tsx`:
      training-text textarea + target-vocab-size number input + "Start Training"
      button + its own loading/validation/error/success states (depends on T085, T086)
- [X] T088 [US6] Create `frontend/src/components/bpe/BpeTrainingResult.tsx`: one
      combined vocabulary + ordered merge-rules/training-steps table per research.md
      Decision 16 (depends on T086)
- [X] T089 [US6] Create `frontend/src/hooks/useBpeTraining.ts`: calls
      `tokenizerClient.trainBpe`, manages loading/error/success state (depends on
      T085)
- [X] T090 [US6] Create `frontend/src/hooks/useBpeModel.ts`: calls
      `tokenizerClient.getBpeModel`, exposes a `refresh()` (mirrors
      `useVocabulary.ts`) (depends on T085)
- [X] T091 [US6] Add a `customStrategy: "simple" | "bpe"` selector (shown only when
      Custom Tokenizer mode is active, per FR-032) and wire `BpeTrainingForm` +
      `BpeTrainingResult` + `useBpeTraining` + `useBpeModel` into
      `frontend/src/App.tsx`, refreshing the model display immediately after a
      successful training run (FR-045, research.md Decision 15) (depends on T087,
      T088, T089, T090)
- [X] T092 [P] [US6] Component tests for `BpeTrainingForm` and `BpeTrainingResult` in
      `frontend/tests/components/`
- [X] T093 [P] [US6] Hook tests for `useBpeTraining` and `useBpeModel` in
      `frontend/tests/hooks/`

**Checkpoint**: User Story 6 is fully functional and independently testable — a user
can train a BPE tokenizer and see the results, with no tokenize step required.

---

## Phase 11: User Story 7 - Tokenize Text with the Trained BPE Tokenizer (Priority: P5)

**Goal**: A user tokenizes new text with the trained BPE model, seeing results in the
existing tokenization result table.

**Independent Test**: Train a model (US6), then tokenize new text and confirm the
returned tokens/IDs come from the learned vocabulary/merge rules.

**Depends on**: User Story 6 (Phase 10) — there is nothing to tokenize with until a
model has been trained.

### Tests for User Story 7

- [X] T094 [US7] Unit tests for BPE tokenize-time merge application in
      `backend/tests/unit/test_bpe_service.py` (extends T074's file): applies learned
      rules in rank order reproducing the training example's expected tokens,
      determinism across repeated calls, and rejects a character absent from the
      trained base vocabulary
- [X] T095 [P] [US7] Extend `backend/tests/contract/test_tokenize_contract.py` with
      `tokenizer_mode: "bpe"` cases: success shape (`encoding: null`, every
      `is_new: false`), `BPE_MODEL_NOT_TRAINED` before any training, and
      `BPE_UNKNOWN_CHARACTER` for an unseen character
- [X] T096 [P] [US7] Integration test: train then tokenize with BPE mode, assert
      determinism on repeated tokenize calls (SC-011), assert OOV rejection, and
      assert `BPE_MODEL_NOT_TRAINED` when attempted against a freshly-reset store, in
      `backend/tests/integration/test_bpe_tokenize_flow.py`

### Implementation for User Story 7

- [X] T097 [US7] Extend `backend/app/services/bpe_service.py`:
      `tokenize(text, store) -> list[Token]` (rank-based merge application per
      research.md Decision 12), `require_trained_model()` (raises
      `BpeModelNotTrainedError`), `require_known_characters()` (raises
      `BpeUnknownCharacterError`) (depends on T082; make T094 pass)
- [X] T098 [US7] Extend `backend/app/api/routes/tokenize.py`: add a `"bpe"` branch
      that calls the T097 functions against `bpe_model_store`, before falling through
      to the existing statistics computation (depends on T097 and the existing
      tokenize route from T038/T047; make T095, T096 pass)
- [X] T099 [P] [US7] Wire the `"bpe"` `customStrategy` in `frontend/src/App.tsx` to
      reuse the existing `TextInput`/`FileUpload`/`useTokenize` path for tokenizing
      (`tokenizer_mode: "bpe"`, no `EncodingSelect`), showing a "train a model first"
      prompt via `StateBanner` when `useBpeModel()`'s current model has
      `trained: false` (depends on T091, the existing `useTokenize`)
- [X] T100 [P] [US7] Component test verifying `TokenTable`/`StateBanner` correctly
      render BPE tokenize results and the "train first" validation state, in
      `frontend/tests/components/`

**Checkpoint**: All seven user stories are independently functional — the BPE
enhancement is complete.

---

## Phase 12: BPE Amendment Polish & Integration

**Purpose**: Whole-system verification of the BPE amendment against plan.md and the
constitution, mirroring Phase 8.

- [X] T101 [P] Run `cd backend && pytest` (full suite, including all BPE tests) and
      fix any failures
- [X] T102 [P] Run `cd frontend && npm run test` (full suite, including all BPE
      tests) and fix any failures
- [X] T103 Execute quickstart.md scenarios 6–8 (BPE training, BPE tokenization, BPE
      validation) manually and confirm expected outcomes
- [X] T104 [P] Audit `backend/app/api/routes/bpe.py` and the `"bpe"` branch of
      `tokenize.py` for Constitution Principle IV (routes stay thin; all BPE logic in
      `bpe_service.py`/`bpe_model_store.py`)
- [X] T105 [P] Audit `frontend/src/components/bpe/**` and the new hooks for
      Constitution Principle II (no training-algorithm or tokenization logic outside
      `tokenizerClient.ts` response handling)
- [X] T106 Update `README.md` to mention the BPE training/tokenization flow
