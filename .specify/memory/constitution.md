<!--
Sync Impact Report
- Version change: (none, template unfilled) → 1.0.0
- Modified principles: n/a (initial ratification)
- Added sections:
  - Core Principles: I. Modular Full-Stack Separation, II. Backend-Authoritative Tokenization
    (NON-NEGOTIABLE), III. Dual Independent Tokenizer Services, IV. Thin API Layer /
    Service-Delegated Logic, V. Validated File Input (TXT & PDF Only), VI. Stateless Simplicity
    (No Database), VII. Testable & Traceable Requirements
  - Technology Stack & Architecture Constraints
  - Development Workflow & Quality Gates
  - Governance
- Removed sections: none (initial creation from template scaffold)
- Templates requiring updates:
  - .specify/templates/plan-template.md: ⚠ pending manual check (verify Constitution Check
    gates reference these principles)
  - .specify/templates/spec-template.md: ✅ no changes required (no hard-coded principle refs)
  - .specify/templates/tasks-template.md: ⚠ pending manual check (verify pytest/frontend test
    task categories align with Principle VII)
- Follow-up TODOs: none — all placeholders resolved from user input.
-->

# Tokenizer Application Constitution

## Core Principles

### I. Modular Full-Stack Separation
The system MUST be built as a simple, modular React + FastAPI application with clear
separation of responsibilities between frontend and backend.
- React owns: UI rendering, user interactions, calling backend APIs, loading states,
  error display, and visualization of results.
- FastAPI owns: request validation, file processing, text extraction, tokenization,
  statistics computation, vocabulary management, and shaping API responses.
- Neither layer may absorb the other's responsibilities (e.g., React MUST NOT perform
  text extraction or statistics computation; FastAPI MUST NOT own presentation concerns).

Rationale: A strict UI/logic boundary keeps each layer independently understandable,
testable, and replaceable, and prevents business logic from leaking into the client.

### II. Backend-Authoritative Tokenization (NON-NEGOTIABLE)
All authoritative tokenization MUST happen in the backend. React MUST NOT duplicate
tokenizer logic, re-implement token counting, or embed vocabulary/token tables
client-side. The frontend only displays results returned by the backend API.

Rationale: A single source of truth for tokenization prevents drift between displayed
results and actual computation, and avoids two implementations silently disagreeing.

### III. Dual Independent Tokenizer Services
The system MUST maintain two independent tokenizer services behind a common interface:
Tiktoken and Custom Tokenizer.
- Tiktoken behavior and vocabulary MUST remain unchanged and externally authoritative;
  its encoding/decoding behavior MUST NOT be patched, wrapped in ways that alter
  results, or reimplemented.
- Custom Tokenizer MUST maintain its own in-memory vocabulary with deterministic token
  IDs (same input token MUST always map to the same ID within a server run) and MUST
  support dynamic creation of new tokens as unseen text is encountered.
- Both services MUST be independently replaceable or extendable without requiring
  major changes to the frontend (i.e., they conform to a shared response contract).

Rationale: Isolating a third-party-correct implementation (Tiktoken) from an evolving
in-house one (Custom Tokenizer) lets each evolve safely without risking the other's
correctness guarantees.

### IV. Thin API Layer, Service-Delegated Logic
API routes MUST remain thin: they parse and validate the request, invoke the
appropriate service(s), and format the response. Business logic — extraction,
tokenization, statistics, vocabulary management — MUST live in dedicated service
modules, not in route handlers.

Rationale: Keeping routes thin makes business logic reusable and unit-testable without
spinning up HTTP infrastructure, and keeps route files easy to audit.

### V. Validated File Input (TXT & PDF Only)
The application MUST support TXT and PDF input files. The backend MUST validate file
type, size, and structure before processing, and MUST perform text extraction
server-side. Unsupported formats or malformed files MUST be rejected with clear,
actionable error responses; the frontend only surfaces these errors, it does not
attempt its own extraction or validation of file contents.

Rationale: Centralizing validation and extraction in the backend guarantees consistent,
safe handling of user-supplied files regardless of client.

### VI. Stateless Simplicity (No Database)
No database is required or permitted for core functionality. The Custom Tokenizer's
vocabulary is maintained in memory, scoped to the running backend process, and is
expected to reset on restart.

Rationale: The application's scope does not warrant persistent storage; in-memory state
keeps the system simple to run, test, and reason about.

### VII. Testable & Traceable Requirements
All requirements and behavior MUST be stated clearly enough to be testable and MUST be
traceable to both implementation and tests.
- Backend tests MUST use pytest.
- Frontend behavior MUST have appropriate automated tests (e.g., component/unit tests
  for interactions, loading states, and error handling).
- Vague or unverifiable requirements MUST be rewritten as concrete, testable statements
  before implementation begins.

Rationale: Traceability from spec to code to test is what makes the spec-driven
workflow (and future changes) safe and verifiable.

## Technology Stack & Architecture Constraints

- Frontend: React, responsible only for UI, API calls, loading/error states, and
  visualization (Principle I).
- Backend: FastAPI (Python), responsible for validation, extraction, tokenization,
  statistics, and vocabulary management (Principle I, IV).
- Tokenization: exactly two services — Tiktoken (unchanged, authoritative) and Custom
  Tokenizer (in-memory, deterministic, dynamic) — exposed through a shared contract so
  either can be swapped or extended independently (Principle III).
- Persistence: none; no database. Custom vocabulary lives in backend process memory
  only (Principle VI).
- Supported input formats: TXT and PDF only, validated and extracted server-side
  (Principle V).

## Development Workflow & Quality Gates

- Any change touching tokenizer behavior MUST specify which service (Tiktoken, Custom
  Tokenizer, or both) it affects and MUST NOT alter Tiktoken's behavior or vocabulary.
- Any change adding or modifying an API route MUST keep the route thin and place new
  logic in a service module (Principle IV).
- Any change to the frontend MUST NOT introduce tokenization, statistics, or vocabulary
  logic; such logic belongs in the backend and is only ever consumed via API responses.
- Every backend feature MUST ship with pytest coverage; every frontend feature MUST
  ship with corresponding automated tests, before it is considered complete.
- Reviews (self- or peer-review) MUST verify compliance with the separation of
  responsibilities in Principle I and the backend-authoritative rule in Principle II
  before merging.

## Governance

This constitution supersedes other informal practices for this project. Amendments are
made by editing `.specify/memory/constitution.md` via the constitution workflow, and
MUST include an updated Sync Impact Report and version bump.

- **Amendment procedure**: propose the change, update affected principles/sections,
  regenerate the Sync Impact Report, and bump the version per the policy below.
- **Versioning policy** (semantic versioning for governance):
  - MAJOR: backward-incompatible removal or redefinition of a principle (e.g.,
    allowing frontend-side tokenization, or introducing a database).
  - MINOR: a new principle or materially expanded guidance is added.
  - PATCH: wording, clarification, or non-semantic fixes.
- **Compliance review**: all plans and PRs MUST verify alignment with these principles;
  any deviation MUST be explicitly justified in the relevant plan's Complexity Tracking
  (or equivalent) section, or rejected.

**Version**: 1.0.0 | **Ratified**: 2026-09-17 | **Last Amended**: 2026-09-17
