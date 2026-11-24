# Proposal

## Why

FR-4 requires autokards to turn readable study text into structured front/back flashcards. FR-3 already validates the generation entry point (`StudyText`, `POST /api/v1/flashcards/generate`) but stops at returning the validated text, so the product cannot yet produce any review material. Without this change, valid submissions never generate cards, and the MVP cannot satisfy SM-05/SM-06/SM-07 or the AC-1..AC-4 acceptance criteria.

## What Changes

- Add a `Flashcard` domain value object with non-empty, separate `front` and `back` fields.
- Add a `FlashcardSet` aggregate that guarantees at least one generated card.
- Add a `FlashcardGenerator` domain port (Protocol) for provider-agnostic generation.
- Add an OpenAI-compatible LLM adapter configured through environment variables, plus a deterministic `stub` adapter for tests and offline verification.
- Extend `GenerateFlashcardsUseCase` to call the generator and return generated cards, preserving FR-3 input validation.
- Change the success response of `POST /api/v1/flashcards/generate` from `202 accepted` to `200` with `data.cards`.
- Map generation failures to explicit HTTP errors (`422`, `502`) with the standard error envelope; never return partial cards or a `.apkg` link.
- Add unit, adapter, and integration tests covering success, invalid output, provider errors, and input failures.
- Companion change `reconcile-text-input` handles the AUTK-6 duplicate cleanup and the `text-input` spec sync; tracked under the same AUTK-8 ticket.

## Capabilities

### New Capabilities

- `flashcard-generation`: Generation of one or more front/back flashcards from validated study text, including single-target Fronts, answering and grounded Backs, strict output validation, and explicit failure behavior.

### Modified Capabilities

- None. The existing `input-validation` capability (FR-3) keeps its behavior; this change only adds the downstream generation step.

## Impact

- New and modified code under `backend/` following the DDD layered architecture in `docs/backend-standards.md`.
- New runtime dependency: `httpx` (currently dev-only).
- New environment variables: `LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`, `LLM_TIMEOUT_SECONDS`, `MAX_INPUT_BYTES`.
- New API contract for `POST /api/v1/flashcards/generate` (success changes from `202` to `200` with cards).
- New tests under `backend/tests/` with >=90% coverage.
- No persistence, no `.apkg`, no deck targeting, no frontend.
