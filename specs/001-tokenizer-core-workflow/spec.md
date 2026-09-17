# Feature Specification: Tokenizer Core Workflow

**Feature Branch**: `001-tokenizer-core-workflow`

**Created**: 2026-09-17

**Status**: Draft

**Input**: User description: "Define the functional requirements for the Tokenizer Application.

The application must:

- Allow users to enter text directly.
- Allow users to upload TXT files.
- Allow users to upload PDF files and extract text from normal text-based PDFs.
- Allow users to select between Tiktoken and Custom Tokenizer modes.
- Allow users to select a supported Tiktoken encoding.
- Tokenize input using the selected tokenizer.
- Display token index, token ID, token text, and relevant token details.
- Display character count, word count, token count, tokens per word, and tokens per character.
- For Tiktoken, use the actual selected encoding and return real token IDs and token information.
- For Custom Tokenizer, use a deterministic token-splitting strategy.
- Maintain an application-owned Custom Tokenizer vocabulary.
- Reuse existing custom vocabulary token IDs.
- Create new vocabulary entries for previously unseen tokens.
- Assign deterministic IDs to newly created custom tokens.
- Track token frequency.
- Identify tokens newly created during the current tokenization operation.
- Display the current Custom Tokenizer vocabulary with ID, token, frequency, and status.
- Visually distinguish newly created tokens from existing tokens.
- Update the vocabulary display immediately after successful custom tokenization.
- Allow users to reset the Custom Tokenizer vocabulary to its initial state.
- Validate empty input, unsupported files, oversized files, invalid/corrupted PDFs, PDFs with no extractable text, and unsupported encodings.
- Display clear and user-friendly validation and processing errors.
- Provide loading, empty, error, and success states."

**Amendment input** (adds Byte Pair Encoding to the Custom Tokenizer): "Update the
existing specification to enhance the Custom Tokenizer with Byte Pair Encoding (BPE).
Keep all existing functionality unchanged, especially Tiktoken and the current Custom
Tokenizer. The Custom Tokenizer should support BPE training using user-provided
training text. The user should be able to enter training text, set a target
vocabulary size, and start BPE training. After training, the UI should show the
learned vocabulary, merge rules, and training details such as the pair selected and
merged at each step. The user should then be able to enter new text and tokenize it
using the trained BPE tokenizer. Display the resulting tokens and token IDs in the
existing tokenization result table. The UI should clearly separate the BPE training
flow from the BPE tokenization flow and provide appropriate loading, empty,
validation, success, and error states. The BPE algorithm should learn frequent
adjacent pairs, merge them repeatedly, create a vocabulary and ordered merge rules,
and use those learned rules when tokenizing new text. It must not learn new merge
rules during tokenization. BPE vocabulary IDs must be deterministic. Keep all BPE
logic in the FastAPI backend; the React frontend handles user input, API calls, UI
state, results, and visualization only."

## Clarifications

### Session 2026-09-17

- Q: What deterministic rule should the Custom Tokenizer use to split input text into tokens? → A: Split on whitespace and punctuation — words and punctuation marks become separate tokens.
- Q: What is the maximum file size the application should accept for TXT/PDF uploads before rejecting it as too large? → A: 10 MB.
- Q: Besides index, ID, and token text, what other detail should be shown for each token in the results view? → A: Start/end character offset within the source text.

### Session 2026-09-17 (BPE amendment)

- Q: When learning BPE merges from the training text, should whitespace be treated as an ordinary mergeable character, or should the training text be pre-split on whitespace so merges only happen within each word? → A: Whitespace is an ordinary character; merges can span across it — the whole training text is one continuous character stream, with no pre-tokenization step.
- Q: What is the maximum length of BPE training text the application should accept before rejecting it as too large to train on? → A: 5,000 characters.
- Q: What is the maximum target vocabulary size a user should be allowed to request for BPE training? → A: 500.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Tokenize Typed Text with Tiktoken (Priority: P1)

A user types or pastes text into the application, selects the Tiktoken tokenizer with a
supported encoding, and runs tokenization to see exactly how that encoding breaks the
text into tokens, along with summary statistics.

**Why this priority**: This is the core value of the application — giving users an
accurate, real view of tokenization using a real, unmodified encoding. Without this,
there is no product.

**Independent Test**: Can be fully tested by typing a short passage, selecting an
encoding, running tokenization, and confirming the returned tokens and statistics match
what that encoding actually produces. Delivers standalone value as a working tokenizer
inspector.

**Acceptance Scenarios**:

1. **Given** the application is loaded, **When** a user types text, selects Tiktoken
   mode and a supported encoding, and runs tokenization, **Then** the system displays
   each token's index, ID, text, and start/end character offset, plus character count,
   word count, token count, tokens-per-word, and tokens-per-character.
2. **Given** a user has typed text and selected a Tiktoken encoding, **When** tokenization
   completes, **Then** every returned token ID and token text matches what that specific
   encoding produces for that input (no substitution or approximation).
3. **Given** a user changes the selected Tiktoken encoding and re-runs tokenization on the
   same text, **When** the operation completes, **Then** the results reflect the newly
   selected encoding.

---

### User Story 2 - Tokenize Typed Text with Custom Tokenizer (Priority: P2)

A user types text and selects the Custom Tokenizer mode instead of Tiktoken, so they can
see the application's own deterministic tokenization, watch its vocabulary grow with new
tokens, and see token frequency accumulate across operations.

**Why this priority**: This is the application's distinguishing feature beyond a plain
Tiktoken viewer — it demonstrates vocabulary learning behavior, which depends on User
Story 1's display and statistics patterns but adds its own state.

**Independent Test**: Can be fully tested by tokenizing text with the Custom Tokenizer,
confirming token IDs are assigned deterministically, previously seen tokens reuse their
IDs, and newly seen tokens get new IDs and are flagged as new — independent of whether
Tiktoken mode is used at all.

**Acceptance Scenarios**:

1. **Given** the Custom Tokenizer vocabulary is empty, **When** a user tokenizes text for
   the first time, **Then** every resulting token is created as a new vocabulary entry
   and marked as newly created.
2. **Given** the Custom Tokenizer vocabulary already contains a token, **When** a user
   tokenizes text containing that same token again, **Then** the system reuses its
   existing ID and increases its recorded frequency, without marking it as new.
3. **Given** a user tokenizes text containing a mix of known and unseen tokens, **When**
   tokenization completes, **Then** the system clearly distinguishes which tokens in the
   result are newly created versus already existing.
4. **Given** the same exact input is tokenized twice against the same vocabulary state,
   **When** both operations complete, **Then** both runs produce identical tokens and IDs.

---

### User Story 3 - Tokenize Uploaded TXT and PDF Files (Priority: P2)

A user uploads a TXT file or a text-based PDF file instead of typing, and the application
extracts the text and tokenizes it the same way as directly typed text.

**Why this priority**: Extends the input method without changing tokenization behavior;
valuable on its own once typed-text tokenization works, since many users want to analyze
existing documents.

**Independent Test**: Can be fully tested by uploading a valid TXT file and a valid
text-based PDF file separately, and confirming each produces the same kind of
tokenization results and statistics as typing the equivalent text would.

**Acceptance Scenarios**:

1. **Given** a user has a plain TXT file, **When** they upload it and run tokenization,
   **Then** the system extracts its text content and tokenizes it using the selected
   tokenizer mode.
2. **Given** a user has a text-based (non-scanned) PDF file, **When** they upload it and
   run tokenization, **Then** the system extracts the embedded text and tokenizes it
   using the selected tokenizer mode.
3. **Given** a user uploads a file, **When** text extraction succeeds, **Then** the
   resulting statistics and token display match what would result from typing the
   extracted text directly.

---

### User Story 4 - View and Reset Custom Tokenizer Vocabulary (Priority: P3)

A user reviews the full current Custom Tokenizer vocabulary — every token, its ID,
frequency, and status — and can reset it back to an empty starting state when they want
to start fresh.

**Why this priority**: A supporting/management capability that depends on the vocabulary
already being populated by User Story 2; not required for a first tokenization, but
needed to fully use and control the Custom Tokenizer over time.

**Independent Test**: Can be fully tested by tokenizing enough text to populate the
vocabulary, confirming the vocabulary view lists every entry with ID/token/frequency/
status, then resetting and confirming the view returns to empty.

**Acceptance Scenarios**:

1. **Given** the Custom Tokenizer vocabulary contains entries, **When** a user opens the
   vocabulary view, **Then** every entry is listed with its ID, token, frequency, and
   status.
2. **Given** a user has just run a successful Custom Tokenizer operation, **When** the
   operation completes, **Then** the vocabulary view updates to reflect the new state
   without the user needing to manually refresh.
3. **Given** the Custom Tokenizer vocabulary contains entries, **When** a user resets the
   vocabulary, **Then** all entries are cleared and the vocabulary returns to its initial
   empty state.

---

### User Story 5 - Clear Feedback for Invalid Input and Processing States (Priority: P3)

A user who submits empty input, an unsupported or oversized file, a corrupted or
image-only PDF, or an unsupported encoding is told clearly what went wrong, and at every
stage of an operation the user can tell whether the app is idle, working, has failed, or
has succeeded.

**Why this priority**: Robustness and trust-building layer over the core flows; it
matters most once there is a working tokenization flow to protect from bad input.

**Independent Test**: Can be fully tested by deliberately submitting each of the invalid
input types (empty input, unsupported file, oversized file, corrupted PDF, text-less
PDF, unsupported encoding) and confirming each produces a clear, specific, user-friendly
error rather than a silent failure or technical error dump; and by observing loading,
empty, error, and success states appear at the correct points in a flow.

**Acceptance Scenarios**:

1. **Given** no text has been entered and no file uploaded, **When** a user attempts to
   tokenize, **Then** the system rejects the request with a clear "no input provided"
   message.
2. **Given** a user uploads a file that is not TXT or PDF, **When** they attempt to
   tokenize, **Then** the system rejects the file with a clear "unsupported file type"
   message.
3. **Given** a user uploads a file larger than the allowed maximum size, **When** they
   attempt to tokenize, **Then** the system rejects the file with a clear "file too
   large" message.
4. **Given** a user uploads a corrupted or unreadable PDF, **When** they attempt to
   tokenize, **Then** the system rejects it with a clear "invalid/corrupted PDF" message.
5. **Given** a user uploads a PDF with no extractable text (e.g., scanned images only),
   **When** they attempt to tokenize, **Then** the system rejects it with a clear
   "no extractable text found" message, distinct from the corrupted-file message.
6. **Given** a user selects an encoding that is not supported, **When** they attempt to
   tokenize in Tiktoken mode, **Then** the system rejects the request with a clear
   "unsupported encoding" message.
7. **Given** any tokenization or file-processing operation is running, **When** the user
   is waiting for it to complete, **Then** the system shows a loading indicator.
8. **Given** no input has been provided yet and no prior results exist, **When** the user
   views the application, **Then** the system shows an empty state rather than a blank or
   broken screen.
9. **Given** a tokenization operation completes successfully, **When** results are ready,
   **Then** the system shows the success state with the results.

---

### User Story 6 - Train a Custom BPE Tokenizer (Priority: P4)

A user enters training text and a target vocabulary size, starts training, and watches
the Custom Tokenizer learn a Byte Pair Encoding (BPE) vocabulary and an ordered list of
merge rules from that text — including which pair was selected and merged at each step.

**Why this priority**: This is a self-contained enhancement to the Custom Tokenizer that
does not change any existing flow; it's valuable once the core app (User Stories 1-5)
works, but nothing else depends on it.

**Independent Test**: Can be fully tested by entering training text and a target
vocabulary size, starting training, and confirming the resulting vocabulary, ordered
merge rules, and per-step training details (pair selected, pair merged) are displayed —
independent of whether anything is ever tokenized with the result.

**Acceptance Scenarios**:

1. **Given** a user enters training text and a target vocabulary size, **When** they
   start BPE training, **Then** the system learns frequent adjacent pairs, merges them
   repeatedly, and produces a vocabulary and an ordered list of merge rules.
2. **Given** BPE training has completed, **When** the user views the result, **Then**
   the system displays the learned vocabulary, the ordered merge rules, and, for each
   training step, which pair was selected and merged.
3. **Given** a user starts a new BPE training run, **When** it completes, **Then** the
   newly learned vocabulary and merge rules replace any previously trained BPE model.
4. **Given** the same training text and target vocabulary size are used twice, **When**
   both training runs complete, **Then** both runs produce the same vocabulary and the
   same ordered merge rules (deterministic).

---

### User Story 7 - Tokenize Text with the Trained BPE Tokenizer (Priority: P5)

A user who has already trained a BPE tokenizer (User Story 6) enters new text and
tokenizes it using the learned vocabulary and merge rules, seeing the resulting tokens
and token IDs in the same results table used by Tiktoken and the existing Custom
Tokenizer.

**Why this priority**: Delivers the payoff of training; it necessarily follows User
Story 6 (there is nothing to tokenize with until a model has been trained), so it is
sequenced right after it.

**Independent Test**: Can be fully tested by training a BPE tokenizer, then entering new
text and tokenizing it, and confirming the returned tokens/IDs come from the learned
vocabulary and merge rules — without needing to touch Tiktoken or the Simple Custom
Tokenizer strategy at all.

**Acceptance Scenarios**:

1. **Given** a BPE tokenizer has been trained, **When** a user enters new text and
   tokenizes it with BPE, **Then** the system applies the learned merge rules (and only
   those rules — no new merge rules are learned during tokenization) and returns tokens
   and token IDs in the existing tokenization result table.
2. **Given** the same trained BPE model, **When** the same text is tokenized twice,
   **Then** both runs return identical tokens and token IDs (deterministic).
3. **Given** no BPE tokenizer has been trained yet, **When** a user attempts to tokenize
   with the BPE strategy, **Then** the system clearly indicates that training is
   required first, rather than silently failing or fabricating results.

### Edge Cases

- What happens when a user submits only whitespace as text (no visible characters)? It
  MUST be treated as empty input.
- What happens when a user switches tokenizer mode (Tiktoken ↔ Custom Tokenizer) after
  already viewing results? The system should tokenize fresh under the newly selected
  mode when the user runs it again, without mixing results from both modes.
- What happens when a single tokenization operation contains the same previously-unseen
  token more than once? The token MUST be created once, marked as new once, and its
  frequency MUST reflect all occurrences within that operation.
- What happens when a user resets the vocabulary and then immediately re-tokenizes
  previously-seen text? Every token MUST be treated as newly created again, since the
  vocabulary was cleared.
- What happens when a very large TXT/PDF file (within the allowed size limit) is
  uploaded? The system MUST still process it and report accurate statistics, using the
  loading state while processing.
- What happens when a PDF is password-protected? It MUST be treated as an
  invalid/corrupted PDF for the purposes of the error shown to the user.
- What happens when a user submits empty or whitespace-only BPE training text? It
  MUST be rejected as invalid input before training starts.
- What happens when a user submits BPE training text longer than 5,000 characters? It
  MUST be rejected with a clear "training text too long" message before training
  starts.
- What happens when the requested target vocabulary size is invalid (not a positive
  number, smaller than the number of distinct characters in the training text, or
  greater than 500)? It MUST be rejected with a clear validation error before
  training starts.
- What happens when the training text contains fewer distinct characters than needed
  to reach the requested target vocabulary size through merges? Training MUST stop
  once no further useful merges are possible and MUST report the achieved vocabulary
  size, rather than erroring out.
- What happens when a user attempts to tokenize with the BPE strategy before any BPE
  training has completed? The system MUST clearly indicate that training is required
  first (see User Story 7, Scenario 3), not attempt to tokenize with an empty model.
- What happens when text submitted for BPE tokenization contains a character that
  never appeared in the training text? It MUST be rejected with a clear validation
  error identifying that the text contains characters unknown to the trained model,
  rather than silently dropping or guessing at those characters.
- What happens when a user starts BPE training while the BPE strategy is not the
  currently selected tokenizer mode? Starting training MUST NOT affect the Tiktoken
  or Simple Custom Tokenizer flows in any way.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to enter text directly into an input area for
  tokenization.
- **FR-002**: System MUST allow users to upload a TXT file as an alternative to typing
  text.
- **FR-003**: System MUST allow users to upload a PDF file and extract its text content
  when the PDF contains extractable (non-scanned) text.
- **FR-004**: System MUST allow users to choose between two tokenization modes: Tiktoken
  and Custom Tokenizer.
- **FR-005**: System MUST allow users to select a supported Tiktoken encoding whenever
  Tiktoken mode is active.
- **FR-006**: System MUST tokenize the provided input (typed text, or text extracted from
  an uploaded file) using the currently selected tokenizer mode.
- **FR-007**: System MUST display, for every token produced, its index, ID, token text,
  and its start/end character offset within the source text.
- **FR-008**: System MUST display character count, word count, token count,
  tokens-per-word, and tokens-per-character for the tokenized input.
- **FR-009**: When Tiktoken mode is used, System MUST tokenize using exactly the selected
  encoding and return the real token IDs and token details that encoding produces.
- **FR-010**: When Custom Tokenizer mode is used with the **Simple strategy** (the
  default, and the only Custom Tokenizer behavior prior to this amendment), System MUST
  split input into tokens by whitespace and punctuation — each word and each
  punctuation mark becomes its own token — such that the same input always yields the
  same tokens.
- **FR-011**: System MUST maintain an application-owned Custom Tokenizer **Simple
  strategy** vocabulary that persists across tokenization operations during the
  application's runtime, independent of the BPE strategy's vocabulary (FR-034).
- **FR-012**: System MUST reuse the existing ID of any token already present in the
  Custom Tokenizer **Simple strategy** vocabulary rather than creating a duplicate
  entry.
- **FR-013**: System MUST create a new **Simple strategy** vocabulary entry for any
  token the Simple strategy has not previously seen.
- **FR-014**: System MUST assign a deterministic ID to each newly created **Simple
  strategy** token, such that a given unseen token always receives the same next ID for
  a given vocabulary state.
- **FR-015**: System MUST track how many times each token in the **Simple strategy**
  vocabulary has been encountered (its frequency).
- **FR-016**: System MUST identify, among the tokens produced by the current **Simple
  strategy** tokenization operation, which were newly created versus which already
  existed in the vocabulary.
- **FR-017**: System MUST display the current Custom Tokenizer **Simple strategy**
  vocabulary, showing each entry's ID, token, frequency, and status.
- **FR-018**: System MUST visually distinguish newly created tokens from pre-existing
  tokens, both in the **Simple strategy** tokenization results and in its vocabulary
  display.
- **FR-019**: System MUST update the **Simple strategy** vocabulary display immediately
  after a successful Simple-strategy tokenization operation, without requiring a manual
  refresh.
- **FR-020**: System MUST allow users to reset the Custom Tokenizer **Simple strategy**
  vocabulary back to its initial, empty state on request, independent of the BPE
  strategy's trained model.
- **FR-021**: System MUST validate input before tokenizing and reject empty (or
  whitespace-only) input with a clear message.
- **FR-022**: System MUST validate uploaded files and reject unsupported file types with
  a clear message.
- **FR-023**: System MUST validate uploaded files and reject files exceeding 10 MB with a
  clear message.
- **FR-024**: System MUST detect invalid or corrupted PDF files and reject them with a
  clear message.
- **FR-025**: System MUST detect PDFs with no extractable text (e.g., scanned/image-only
  PDFs) and reject them with a clear message distinct from the corrupted-file message.
- **FR-026**: System MUST validate the selected Tiktoken encoding and reject unsupported
  encodings with a clear message.
- **FR-027**: System MUST present all validation and processing errors in clear,
  user-friendly language, without exposing raw internal/technical error output.
- **FR-028**: System MUST present a loading state while a tokenization or file-processing
  operation is in progress.
- **FR-029**: System MUST present an empty state when no input has been provided and no
  results exist yet.
- **FR-030**: System MUST present an error state when validation or processing fails,
  describing what went wrong.
- **FR-031**: System MUST present a success state showing the tokenization results once
  an operation completes successfully.

#### BPE Strategy Selection

- **FR-032**: System MUST allow users, whenever Custom Tokenizer mode is selected, to
  choose between two strategies: the existing **Simple** strategy (FR-010-FR-020,
  unchanged) and the new **BPE** strategy (FR-033-FR-054). Switching strategies MUST
  NOT alter or reset the other strategy's vocabulary/model.

#### BPE Training

- **FR-033**: System MUST allow users to enter BPE training text directly (typed or
  pasted); training text is entered separately from the text tokenized in User Story 7.
- **FR-034**: System MUST allow users to set a target vocabulary size and, on request,
  start a BPE training run using the entered training text and that target size.
- **FR-035**: System MUST learn a BPE vocabulary and an ordered list of merge rules by
  repeatedly finding the most frequent adjacent pair of symbols in the training text
  and merging it into a new symbol, until the target vocabulary size is reached or no
  further useful merge exists. The training text MUST be treated as one continuous
  character stream — including whitespace — with no whitespace-based pre-tokenization,
  so a merge may span across a space or newline (e.g., a merged token may include a
  trailing space).
- **FR-036**: System MUST assign a deterministic ID to every vocabulary entry (base
  characters and every merged token), such that training the same training text with
  the same target vocabulary size always produces the same vocabulary, the same merge
  rules, and the same IDs, in the same order.
- **FR-037**: System MUST record, for each training step, which pair was selected and
  what it was merged into, in the order the merges were learned.
- **FR-038**: System MUST validate BPE training text before training starts and reject
  empty or whitespace-only training text, and text exceeding 5,000 characters, each
  with a clear, distinct message.
- **FR-039**: System MUST validate the target vocabulary size before training starts
  and reject a value that is not a positive number, is smaller than the number of
  distinct characters in the training text (whitespace characters included, per
  FR-035), or exceeds 500, each with a clear, distinct message.
- **FR-040**: If the training text cannot reach the requested target vocabulary size
  (no further useful merges exist), System MUST stop training and report the
  vocabulary size actually achieved, rather than treating this as an error.
- **FR-041**: A new successful BPE training run MUST replace any previously trained BPE
  vocabulary and merge rules for the application instance.

#### BPE Vocabulary, Merge Rules, and Training Detail Display

- **FR-042**: After a successful BPE training run, System MUST display the learned BPE
  vocabulary (at minimum: ID and token for each entry).
- **FR-043**: After a successful BPE training run, System MUST display the ordered list
  of merge rules learned (at minimum: the order/step, the pair merged, and the
  resulting token).
- **FR-044**: After a successful BPE training run, System MUST display, for each
  training step, which pair was selected and merged (satisfying FR-037's data with a
  corresponding UI view).
- **FR-045**: System MUST update the displayed BPE vocabulary, merge rules, and
  training details immediately after a successful training run, without requiring a
  manual refresh.

#### BPE Tokenization

- **FR-046**: System MUST allow users to enter new text and tokenize it using the most
  recently trained BPE vocabulary and merge rules.
- **FR-047**: When tokenizing with the BPE strategy, System MUST apply only the merge
  rules learned during the most recent training run, in the order they were learned,
  and MUST NOT learn, create, or apply any new merge rule during tokenization.
- **FR-048**: System MUST display BPE tokenization results — token index, token ID,
  token text — in the same tokenization result table used for Tiktoken and Simple
  Custom Tokenizer results.
- **FR-049**: System MUST reject a request to tokenize with the BPE strategy when no
  BPE model has been trained yet, with a clear message indicating training is required
  first, rather than attempting to tokenize with an empty vocabulary.
- **FR-050**: System MUST reject BPE tokenization input that contains a character not
  present in the trained model's base vocabulary, with a clear message, rather than
  silently dropping, replacing, or guessing at that character.

#### BPE States

- **FR-051**: System MUST present a loading state while a BPE training run or a BPE
  tokenization request is in progress.
- **FR-052**: System MUST present an empty state for the BPE vocabulary/merge-rule
  display when no BPE model has been trained yet in the current application run.
- **FR-053**: System MUST present clear validation and error states for BPE training
  and BPE tokenization failures (FR-038, FR-039, FR-049, FR-050), distinct from
  Tiktoken's and the Simple strategy's error messages.
- **FR-054**: System MUST present a success state for a completed BPE training run and,
  separately, for a completed BPE tokenization request.

### Key Entities

- **Tokenization Result**: The outcome of one tokenize operation — source input, which
  tokenizer mode and (if applicable) encoding was used, the ordered list of tokens
  produced, and the summary statistics (character count, word count, token count,
  tokens-per-word, tokens-per-character).
- **Token**: A single unit produced by tokenization — its index within the result, its
  ID, its text, its start/end character offset within the source text, and (for Custom
  Tokenizer results) whether it was newly created during this operation.
- **Custom Vocabulary Entry (Simple strategy)**: A single token known to the Simple
  strategy — its deterministic ID, its token text, its accumulated frequency across
  operations, and its status (e.g., newly created vs. pre-existing) relative to the
  most recent operation. Independent of the BPE strategy's vocabulary.
- **Uploaded File**: A user-supplied TXT or PDF file — its name, type, size, and either
  its successfully extracted text or the reason extraction/validation failed.
- **BPE Vocabulary Entry**: A single token known to the trained BPE model — its
  deterministic ID and its token text (a base character or a merged sequence of
  symbols). Replaced in full whenever a new training run completes.
- **BPE Merge Rule**: One learned merge, in the order it was learned — its step/order
  number, the pair of symbols merged, and the resulting merged token.
- **BPE Training Run**: The outcome of one training operation — the training text used,
  the requested target vocabulary size, the vocabulary size actually achieved, the
  resulting BPE Vocabulary Entries, and the ordered list of BPE Merge Rules.
- **BPE Training Step**: One step within a BPE Training Run — the step number, the pair
  of symbols selected as most frequent, and what that pair was merged into.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can tokenize typed text and see full results (tokens + statistics)
  in under 2 seconds for typical inputs (up to 5,000 characters).
- **SC-002**: 100% of tokens and IDs produced in Tiktoken mode match the real output of
  the selected encoding for the given input, with zero substituted or approximated
  values.
- **SC-003**: Repeating the same input against the same Custom Tokenizer vocabulary
  state always produces identical tokens and IDs, with zero variance across repeated
  runs.
- **SC-004**: Users can tell which tokens were newly created in a given operation
  directly from the results view, without cross-referencing another screen.
- **SC-005**: Each of the six specified invalid-input scenarios (empty input,
  unsupported file, oversized file, corrupted PDF, PDF with no extractable text,
  unsupported encoding) produces a clear, human-readable error message rather than a
  silent failure or a raw technical error.
- **SC-006**: Users can reset the Custom Tokenizer vocabulary and see the vocabulary
  view reflect the empty state in a single action.
- **SC-007**: The vocabulary view reflects new tokens and updated frequencies
  immediately after every successful Custom Tokenizer operation, with no manual refresh
  step needed.
- **SC-008**: Users can successfully tokenize content from an uploaded TXT or text-based
  PDF file without needing to retype or copy-paste the content themselves.
- **SC-009**: Users can train a BPE tokenizer and see its resulting vocabulary, ordered
  merge rules, and per-step training details displayed within a few seconds for typical
  training text (up to 2,000 characters), without leaving the training view.
- **SC-010**: Training the same text with the same target vocabulary size always
  produces the same vocabulary and the same ordered merge rules, with zero variance
  across repeated runs.
- **SC-011**: Tokenizing the same text twice against the same trained BPE model always
  produces identical tokens and token IDs, with zero variance across repeated runs.
- **SC-012**: Users can tell directly from the UI, without attempting to tokenize,
  whether a BPE model has been trained yet in the current session.
- **SC-013**: Each of the BPE-specific invalid-input scenarios (empty training text,
  training text over 5,000 characters, target vocabulary size that is non-positive,
  too small for the training text, or over 500, tokenizing before training, and
  tokenizing text with an unknown character) produces a clear, human-readable error
  rather than a silent failure or a raw technical error.

## Assumptions

- The Custom Tokenizer vocabulary is a single, application-wide store shared by all
  users of a running instance (no per-user or per-session isolation), consistent with
  there being no database and no authentication in scope.
- "Supported Tiktoken encodings" means the standard set of encodings exposed by the
  underlying Tiktoken library (e.g., common encodings used by current model families);
  the exact list is a configuration detail decided during planning, not a scope
  decision.
- The maximum upload file size is 10 MB (see Clarifications); this applies to both TXT
  and PDF uploads.
- The Custom Tokenizer's whitespace-and-punctuation splitting rule (see Clarifications)
  determines what counts as one token; exact character classes treated as punctuation
  (e.g., handling of contractions, hyphens, Unicode punctuation) are a planning-level
  detail, as long as the rule stays deterministic.
- The Custom Tokenizer vocabulary resets only when the user explicitly requests a reset,
  or when the application/server restarts (since it is in-memory); it does not expire or
  shrink on its own otherwise.
- "Newly created" status for a token is scoped to the current tokenization operation —
  the vocabulary display's status reflects the most recent operation, not full history.

**BPE design defaults** (resolved without a formal clarification question, consistent
with how earlier ambiguity in this spec was handled — see Clarifications):

- BPE operates at the **character level** (individual text characters), not raw bytes —
  consistent with how the existing Simple strategy already treats tokens as character
  sequences. This keeps the learned vocabulary and merge rules human-readable in the UI
  (e.g., showing `"th"` merged from `"t"` + `"h"`), which directly serves the
  requirement to display "the pair selected and merged at each step." Tiktoken already
  covers the production-grade, byte-level BPE use case elsewhere in this app: this
  Custom BPE strategy's value is being transparent and readable, not duplicating
  Tiktoken.
- Because BPE is character-level, a character never seen during training cannot be
  represented by the trained model. Per FR-050, this is treated as a validation error
  at tokenize time (consistent with how every other invalid-input case in this app is
  handled: explicit rejection with a clear message, not silent degradation).
- The BPE strategy's vocabulary and merge rules are a single, application-wide,
  in-memory model — independent of the Simple strategy's vocabulary — consistent with
  there being no database (Constitution Principle VI) and with "keep all existing
  functionality unchanged."
- BPE training text is entered as typed/pasted text only in this iteration (no
  TXT/PDF upload for training text), since only "enter training text" was requested;
  file-based training input can be added later without contradicting this spec.
  Tokenizing *with* a trained BPE model still reuses the app's existing text/file input
  (User Story 7 shares the same input surface as User Stories 1-3).
- The maximum BPE training-text length is 5,000 characters (see Clarifications),
  mirroring the existing 10 MB upload limit's purpose of bounding worst-case
  processing time.
- Starting a new BPE training run fully replaces the previous BPE vocabulary and merge
  rules (no versioning/history of past training runs is kept) — this doubles as the
  BPE strategy's reset mechanism, so no separate "reset BPE model" action is required
  beyond retraining.
