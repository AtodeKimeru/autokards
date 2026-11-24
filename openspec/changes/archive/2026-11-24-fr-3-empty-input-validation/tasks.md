# Tasks

## 1. Project scaffolding

- [x] 1.1 Create backend project structure under `backend/src/` (domain, application, presentation, infrastructure directories) and `backend/tests/` (unit, integration) and verify expected directories exist
- [x] 1.2 Configure `backend/pyproject.toml` with Python 3.11+, FastAPI, Pydantic v2, pytest, ruff, mypy and verify `uv sync` installs dependencies

## 2. Domain layer

- [x] 2.1 Implement `ValidationError` domain exception in `backend/src/domain/exceptions.py` and verify it is importable with a `.message` attribute
- [x] 2.2 Implement `StudyText` value object in `backend/src/domain/models/study_text.py` that rejects empty or whitespace-only text on construction and verify `""` and `"   "` raise `ValidationError`

## 3. Application layer

- [x] 3.1 Implement `GenerateFlashcardsRequest` Pydantic v2 schema in `backend/src/application/schemas/generate_flashcards.py` with a `text: str` field and verify it parses valid JSON input
- [x] 3.2 Implement `GenerateFlashcardsUseCase` in `backend/src/application/services/generate_flashcards_use_case.py` that constructs `StudyText`, stops the flow without invoking generation on invalid input, and verify invalid input returns a validation result while valid input proceeds

## 4. Presentation layer

- [x] 4.1 Implement `POST /api/v1/flashcards/generate` route in `backend/src/presentation/api/flashcards_router.py` that returns HTTP 400 with the standard error envelope (`VALIDATION_ERROR`, "Readable study text is required") on invalid input and verify no `.apkg` download link is present on failure
- [x] 4.2 Implement centralized exception handler mapping `ValidationError` → HTTP 400 and verify raw stack traces are not leaked in API responses

## 5. Tests

- [x] 5.1 Add domain unit tests in `backend/tests/unit/domain/test_study_text.py` covering empty text, whitespace-only text, and valid text (AAA pattern, `test_<behavior>_when_<condition>` naming) and verify they pass
- [x] 5.2 Add application unit tests in `backend/tests/unit/application/test_generate_flashcards_use_case.py` covering flow stop on invalid input and proceed on valid input and verify they pass
- [x] 5.3 Add API integration tests in `backend/tests/integration/api/test_flashcards_generate.py` covering 400 on empty/whitespace input and 2xx proceed on valid input and verify they pass

## 6. Verification

- [x] 6.1 Run `ruff check .` and `ruff format --check` from `backend/` and verify no lint or formatting errors
- [x] 6.2 Run `mypy src` from `backend/` and verify type checking passes with no `Any` leakage
- [x] 6.3 Run `pytest --cov=src` from `backend/` and verify ≥90% coverage across branches, lines, and statements

## Workflow follow-up

- Run `openspec validate` on the change before applying.
- Start the `openspec-apply-change` workflow to implement the tasks.
- After implementation and PR creation, move AUTK-7 to `En revisión` and comment on the ticket with the PR link.
