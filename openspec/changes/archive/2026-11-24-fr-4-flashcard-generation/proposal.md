# Proposal

## Why

FR-4 requires autokards to turn readable study text into structured front/back flashcards. FR-3 already validates the generation entry point (`StudyText`, `POST /api/v1/flashcards/generate`) but stops at returning the validated text, so the product cannot yet produce any review material. Without this change, valid submissions never generate cards, and the MVP cannot satisfy SM-05/SM-06/SM-07 or the AC-1..AC-4 acceptance criteria.

## What Changes

- Add a `Flashcard` domain value object with non-empty, separate `front` and `back` fields.
- Add a `FlashcardSet` aggregate that guarantees at least one generated card.
- Add a `FlashcardGenerator` domain port (Protocol) for provider-agnostic generation.
- Add an OpenAI-compatible LLM adapter configured through environment variables, plus a deterministic `stub` adapter for local development and offline verification. The stub stays the local default but the application refuses to start when `APP_ENV=production`; an unrecognized `LLM_PROVIDER` value fails at startup instead of silently selecting a provider.
- Extend `GenerateFlashcardsUseCase` to call the generator and return generated cards, preserving FR-3 input validation.
- Enforce a UTF-8 byte ceiling (`MAX_INPUT_BYTES`, default 10 MiB) before the text reaches the provider, returning `413` with code `INPUT_TOO_LARGE`.
- Change the success response of `POST /api/v1/flashcards/generate` from `202 accepted` to `200` with `data.cards`, described by a typed response model so the card schema is present in OpenAPI.
- Map failures to explicit HTTP errors (`413`, `422`, `502`) with the standard error envelope, including request-schema validation failures; never return partial cards or a `.apkg` link.
- Add unit, adapter, and integration tests covering success, invalid output, provider errors, input failures, the byte ceiling, and the configuration guards.

## Capabilities

### New Capabilities

- `flashcard-generation`: Generation of one or more front/back flashcards from validated study text, including single-target Fronts, answering and grounded Backs, strict output validation, a configurable byte ceiling, a typed success contract, and explicit failure behavior.

### Modified Capabilities

- None. The existing `input-validation` capability (FR-3) keeps its behavior; this change only adds the downstream generation step.

## Impact

- New and modified code under `backend/` following the DDD layered architecture in `docs/backend-standards.md`.
- New runtime dependency: `httpx` (currently dev-only).
- New environment variables: `APP_ENV`, `LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`, `LLM_TIMEOUT_SECONDS`, and `MAX_INPUT_BYTES` (byte ceiling, default 10 MiB).
- New API contract for `POST /api/v1/flashcards/generate` (success changes from `202` to `200` with cards; new `413` and `422 INVALID_REQUEST` error cases).
- New tests under `backend/tests/` with >=90% coverage.
- No persistence, no `.apkg`, no deck targeting, no frontend.
- Provider auth/rate-limit distinction, output size caps, adapter retry/fence repair, and structured logging are explicitly deferred to follow-up AUTK tickets (see `tasks.md` -> Workflow follow-up).
