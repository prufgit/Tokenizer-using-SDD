# Implementation Plan: Tokenizer Core Workflow

**Branch**: `001-tokenizer-core-workflow` | **Date**: 2026-09-17 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-tokenizer-core-workflow/spec.md`

## Summary

Build a React + TypeScript / FastAPI + Python tokenizer inspector. Users type text or
upload a TXT/text-based PDF, choose between two independent, backend-only tokenizer
services (Tiktoken — unmodified, real encodings; Custom Tokenizer — regex-based,
deterministic, with a growing in-memory vocabulary), and see a per-token breakdown
(index, ID, text, offsets, new-token flag) plus summary statistics. The Custom
Tokenizer's vocabulary is viewable and resettable. All computation (extraction,
tokenization, stats, vocabulary) lives in FastAPI services behind a single thin REST
contract; React only renders state returned by the API, styled with a dark, neon-gradient
("cyberpunk") visual theme.

**BPE Amendment**: The Custom Tokenizer gains a second, independent strategy — a
from-scratch, character-level Byte Pair Encoding (BPE) tokenizer that users train on
their own text (learning a vocabulary and ordered merge rules, with per-step training
detail shown) and then tokenize new text with, using only what was learned. This is
purely additive: Tiktoken and the existing ("Simple") Custom Tokenizer strategy are
unchanged, in code and in behavior.

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript 5.x with React 18 (frontend)

**Primary Dependencies**: FastAPI, uvicorn, `tiktoken`, PyMuPDF (`pymupdf`/`fitz`),
Pydantic v2 (backend); React 18, Vite (build/dev server), native `fetch` (frontend) —
no additional state-management, HTTP-client, or UI-component libraries

**Storage**: N/A — no database; Custom Tokenizer vocabulary lives in a single in-memory
store inside the FastAPI process (Principle VI)

**Testing**: pytest + FastAPI `TestClient` (backend unit/contract/integration); Vitest +
React Testing Library (frontend component/hook tests)

**Target Platform**: Web — FastAPI served via uvicorn (any Linux/Windows host), React
app served via Vite dev server in development / static build in production

**Project Type**: Web application (frontend + backend, per Constitution Principle I)

**Performance Goals**: Full tokenize-and-display round trip in under 2 seconds for
inputs up to 5,000 characters (SC-001); file extraction for a 10 MB PDF should not block
the UI beyond the loading state

**Constraints**: No database/persistent storage; no unnecessary frameworks (no Redux/
Zustand/axios/ORM); Tiktoken behavior/vocabulary MUST NOT be modified; Custom Tokenizer
(Simple strategy) MUST use regex-based splitting; API routes thin, logic in services;
max upload size 10 MB (per Clarifications); React MUST NOT contain tokenization logic;
BPE training text ≤ 5,000 characters and target vocabulary size ≤ 500 (per
Clarifications); BPE MUST NOT learn new merge rules during tokenization (FR-047)

**Scale/Scope**: Single backend instance, single shared in-memory vocabulary/BPE model,
single concurrent-use tool (not a multi-tenant SaaS) — 7 user stories, ~10 REST-facing
operations, 3 tokenizer strategies (Tiktoken, Custom Tokenizer Simple, Custom Tokenizer
BPE) across 2 top-level tokenizer modes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Status |
|---|---|---|
| I. Modular Full-Stack Separation | React limited to UI/API calls/states/visualization; FastAPI owns validation, extraction, tokenization, stats, vocabulary — including all BPE training/tokenization logic | PASS |
| II. Backend-Authoritative Tokenization | All three tokenizer strategies run only in FastAPI services; React renders `TokenizeResponse`/`BpeModelResponse` as received, no client-side token or merge logic | PASS |
| III. Dual Independent Tokenizer Services | `tiktoken_service` and "Custom Tokenizer" (now `custom_tokenizer_service` for the Simple strategy + `bpe_service` for BPE) remain the two independent top-level tokenizer modes required by FR-004 and Principle III; `bpe_service` is a second, fully independent *implementation module* of the Custom Tokenizer service, not a new top-level mode — it shares no state with `custom_tokenizer_service`/`VocabularyStore`, and Tiktoken is untouched | PASS |
| IV. Thin API Layer, Service-Delegated Logic | Routes (`api/routes/*.py`) only parse/validate/format; all logic — including BPE training/validation — in `services/*.py` | PASS |
| V. Validated File Input (TXT & PDF Only) | Unchanged; BPE training text is JSON (no file input, per Assumptions), BPE tokenization reuses the existing file-validated path | PASS |
| VI. Stateless Simplicity (No Database) | Vocabulary and the BPE model each held in one in-memory store; no DB/ORM introduced | PASS |
| VII. Testable & Traceable Requirements | Every FR (including FR-032–FR-054) mapped to a service/route + pytest test; new frontend states/interactions covered by Vitest + RTL | PASS |

No violations identified. Complexity Tracking table intentionally left empty.

*Re-checked after Phase 1 design (data-model.md, contracts/, quickstart.md): still PASS
on all seven principles — the two tokenizer services remain fully separate modules
behind one shared `TokenizeResponse` contract, all routes stay thin per
`contracts/*.md`, and no persistence was introduced.*

*Re-checked again after the BPE amendment's Phase 0/1 design: still PASS. `bpe_service`
and `BpeModelStore` are new, fully independent modules that touch neither
`tiktoken_service` nor `custom_tokenizer_service`/`VocabularyStore`; `POST /api/bpe/train`
and `GET /api/bpe/model` are as thin as the existing routes; no new frontend component
performs tokenization, training-algorithm, or statistics logic — they only call the API
and render its response.*

## Project Structure

### Documentation (this feature)

```text
specs/001-tokenizer-core-workflow/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md         # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   ├── tokenize-endpoint.md
│   ├── vocabulary-endpoints.md
│   ├── encodings-endpoint.md
│   ├── error-schema.md
│   ├── bpe-train-endpoint.md    # BPE amendment
│   └── bpe-model-endpoint.md    # BPE amendment
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── main.py                        # FastAPI app factory, router mounting, CORS setup
│   ├── api/
│   │   └── routes/
│   │       ├── tokenize.py            # POST /api/tokenize (thin: parse -> service -> response)
│   │       ├── vocabulary.py          # GET /api/vocabulary, POST /api/vocabulary/reset
│   │       ├── encodings.py           # GET /api/encodings
│   │       └── bpe.py                 # POST /api/bpe/train, GET /api/bpe/model (BPE amendment)
│   ├── schemas/                       # Pydantic request/response contracts
│   │   ├── tokenize.py                # TokenizeRequest/Response, Token, Statistics
│   │   ├── vocabulary.py              # VocabularyEntry, VocabularyResponse
│   │   ├── errors.py                  # ErrorResponse, ErrorCode enum (+ 5 BPE codes)
│   │   └── bpe.py                     # BpeTrainRequest, BpeVocabularyEntry, BpeMergeRule, BpeTrainingStep, BpeModelResponse (BPE amendment)
│   ├── services/
│   │   ├── file_processing.py         # TXT/PDF validation + extraction (PyMuPDF)
│   │   ├── tiktoken_service.py        # Wraps `tiktoken`: encode, list encodings, offsets
│   │   ├── custom_tokenizer_service.py# Regex splitting + vocabulary lookup/create (Simple strategy)
│   │   ├── vocabulary_store.py        # In-memory Simple-strategy vocabulary state, reset, thread-safety
│   │   ├── bpe_service.py             # BPE amendment: training algorithm + tokenize-time merge application + validation
│   │   ├── bpe_model_store.py         # BPE amendment: in-memory trained-model state, replace-on-retrain, thread-safety
│   │   └── statistics.py              # char/word/token count + ratio calculations
│   └── core/
│       ├── config.py                  # Settings: max upload size, CORS origins, BPE limits, etc.
│       └── errors.py                  # Domain exceptions + FastAPI exception handlers
└── tests/
    ├── unit/
    │   ├── test_custom_tokenizer_service.py
    │   ├── test_tiktoken_service.py
    │   ├── test_file_processing.py
    │   ├── test_statistics.py
    │   ├── test_vocabulary_store.py
    │   ├── test_bpe_service.py            # BPE amendment
    │   └── test_bpe_model_store.py        # BPE amendment
    ├── contract/
    │   ├── test_tokenize_contract.py      # extended with "bpe" mode cases
    │   ├── test_vocabulary_contract.py
    │   ├── test_encodings_contract.py
    │   └── test_bpe_contract.py           # BPE amendment
    └── integration/
        ├── test_tokenize_tiktoken_flow.py
        ├── test_tokenize_custom_flow.py
        ├── test_tokenize_file_upload_flow.py
        ├── test_vocabulary_lifecycle.py
        ├── test_bpe_training_flow.py      # BPE amendment
        └── test_bpe_tokenize_flow.py      # BPE amendment

frontend/
├── src/
│   ├── main.tsx
│   ├── App.tsx                        # Top-level state (input, mode, customStrategy, request status, results)
│   ├── api/
│   │   └── tokenizerClient.ts         # fetch wrappers: tokenize, getVocabulary, resetVocabulary, getEncodings, trainBpe, getBpeModel
│   ├── components/
│   │   ├── input/
│   │   │   ├── TextInput.tsx
│   │   │   ├── FileUpload.tsx
│   │   │   ├── TokenizerModeToggle.tsx
│   │   │   └── EncodingSelect.tsx
│   │   ├── results/
│   │   │   ├── StateBanner.tsx        # loading / empty / error / success switch
│   │   │   ├── StatsSummary.tsx
│   │   │   └── TokenTable.tsx         # highlights newly-created tokens
│   │   ├── vocabulary/
│   │   │   ├── VocabularyTable.tsx
│   │   │   └── ResetVocabularyButton.tsx
│   │   └── bpe/                       # BPE amendment
│   │       ├── BpeTrainingForm.tsx    # training text + target vocab size + start-training
│   │       └── BpeTrainingResult.tsx  # learned vocabulary + merge rules/training steps
│   ├── hooks/
│   │   ├── useTokenize.ts
│   │   ├── useVocabulary.ts
│   │   ├── useBpeTraining.ts          # BPE amendment
│   │   └── useBpeModel.ts             # BPE amendment
│   ├── types/
│   │   └── api.ts                     # TS interfaces mirroring backend Pydantic schemas
│   └── styles/
│       └── theme.css                  # neon-gradient / dark cyberpunk design tokens
└── tests/
    ├── components/
    └── hooks/
```

**Structure Decision**: Web application layout (`backend/` + `frontend/`), matching
Constitution Principle I's React/FastAPI split. Backend follows
routes → schemas → services → core layering so routes stay thin (Principle IV) and the
two tokenizer services stay fully independent modules (Principle III). Frontend follows a
components/hooks/api split so no component reaches past `tokenizerClient.ts` into
tokenization logic (Principle II). The BPE amendment adds `bpe_service.py`/
`bpe_model_store.py` and `api/routes/bpe.py` as new, fully independent modules following
the same layering — nothing in the existing structure was moved or renamed.

## Complexity Tracking

*No entries — Constitution Check reported no violations.*
