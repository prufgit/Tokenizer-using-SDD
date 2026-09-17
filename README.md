# Tokenizer Application

A React + TypeScript / FastAPI + Python tokenizer inspector. Type text or upload a
TXT/text-based PDF, tokenize it with the real **Tiktoken** library, the in-house
**Custom Tokenizer**, or a **BPE** tokenizer you train yourself, and see a per-token
breakdown plus summary statistics.

The Custom Tokenizer offers two strategies:
- **Simple**: deterministic, whitespace/punctuation splitting with a vocabulary that
  grows as you tokenize.
- **BPE**: enter training text and a target vocabulary size to train a from-scratch
  Byte Pair Encoding tokenizer — see the learned vocabulary, ordered merge rules, and
  per-step training detail, then tokenize new text with the trained model (it never
  learns new merges at tokenize time).

See [specs/001-tokenizer-core-workflow/](specs/001-tokenizer-core-workflow/) for the
full specification, plan, and task breakdown, and
[specs/001-tokenizer-core-workflow/quickstart.md](specs/001-tokenizer-core-workflow/quickstart.md)
for a scenario-by-scenario manual validation guide.

## Prerequisites

- Python 3.11+
- Node.js 18+

## Setup

```bash
# Backend
cd backend
python -m venv .venv
./.venv/Scripts/pip install -r requirements.txt   # Windows
# source .venv/bin/activate && pip install -r requirements.txt   # macOS/Linux

# Frontend
cd ../frontend
npm install
cp .env.example .env   # adjust VITE_API_BASE_URL if the backend runs elsewhere
```

## Run

```bash
# Backend (from backend/)
./.venv/Scripts/python -m uvicorn app.main:app --reload --port 8000

# Frontend (from frontend/, separate terminal)
npm run dev
```

Open the frontend dev URL (Vite default: http://localhost:5173).

## Test

```bash
# Backend
cd backend
./.venv/Scripts/python -m pytest

# Frontend
cd frontend
npm run test
```

## Project layout

- `backend/app/api/routes/` — thin FastAPI routes (parse → delegate to services → respond)
- `backend/app/services/` — Tiktoken service, Custom Tokenizer (Simple) service,
  BPE training/tokenize service, vocabulary/BPE-model stores, file processing
  (TXT/PDF), statistics
- `backend/app/schemas/` — Pydantic request/response contracts
- `frontend/src/components/` — input, results, vocabulary, and BPE training UI components
- `frontend/src/hooks/` — `useTokenize`, `useVocabulary`, `useBpeTraining`, `useBpeModel`
- `frontend/src/api/tokenizerClient.ts` — the only place the frontend talks to the backend

All tokenization (including BPE training and merge application), extraction,
statistics, and vocabulary logic lives in the backend; the frontend only renders what
the API returns (see [.specify/memory/constitution.md](.specify/memory/constitution.md)).
