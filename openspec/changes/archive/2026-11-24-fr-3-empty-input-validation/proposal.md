# Proposal

## Why

The autokards MVP requires input validation at the start of the flashcard generation flow (FR-3). When a user submits empty or whitespace-only study text, the system must stop the generation flow immediately, inform the user that readable study text is required, and must not produce or offer a `.apkg` download. Without this validation, invalid input could proceed through generation and produce an empty or meaningless package, wasting the user's time and violating the MVP's empty-input acceptance criteria (AC-1, AC-2).

## What Changes

- Add a `StudyText` domain value object that self-validates on construction and rejects empty or whitespace-only text.
- Add a `ValidationError` domain exception raised by `StudyText` when input is invalid.
- Add a `GenerateFlashcardsRequest` Pydantic v2 schema carrying the submitted `text`.
- Add a `GenerateFlashcardsUseCase` application service that validates the input and stops the flow without invoking generation when invalid.
- Add a `POST /api/v1/flashcards/generate` presentation route returning HTTP 400 with a standard error envelope on invalid input, and proceeding on valid input.
- Add unit and integration tests covering empty, whitespace-only, and valid input paths.

## Capabilities

### New Capabilities

- `input-validation`: Validation of submitted study text at generation entry. Rejects empty or whitespace-only input with a clear message ("Readable study text is required"), stops the generation flow, and ensures no `.apkg` is produced or offered for invalid submissions. Valid input proceeds to flashcard generation (FR-4, separate change).

### Modified Capabilities

- None. This is a greenfield capability; no existing specs exist in `openspec/specs/`.

## Impact

- New code under `backend/src/` (domain, application, presentation layers) following the DDD layered architecture in `docs/backend-standards.md`.
- New tests under `backend/tests/` targeting ≥90% coverage.
- New API endpoint `POST /api/v1/flashcards/generate`.
- No existing files are modified; no dependencies added beyond the configured backend stack (Python 3.11+, FastAPI, Pydantic v2, pytest, ruff, mypy).
