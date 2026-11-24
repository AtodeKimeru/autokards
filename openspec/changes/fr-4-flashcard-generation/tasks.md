# Tasks

## 0. Setup: Create Feature Branch (MANDATORY - FIRST STEP)

- [x] 0.1 Run `git checkout main` and `git pull --ff-only origin main`; verify `main` is at `origin/main`
- [x] 0.2 Create and switch to `feature/AUTK-8` from `main`
- [x] 0.3 Verify current branch is `feature/AUTK-8` and the working tree is clean

## 1. OpenSpec artifacts and validation

- [x] 1.1 Create the `fr-4-flashcard-generation` change with `proposal.md`, `design.md`, `specs/flashcard-generation/spec.md`, and this `tasks.md`; verify all files exist
- [x] 1.2 Run `openspec validate fr-4-flashcard-generation` and fix any validation errors
- [x] 1.3 Revise the artifacts to make the byte ceiling, provider fail-fast, typed success contract, and error envelope explicit; verify `openspec validate fr-4-flashcard-generation` reports the change is valid

## 2. Domain layer (TDD)

- [x] 2.1 Add failing unit tests in `backend/tests/unit/domain/test_flashcard.py` for non-empty Front/Back, field separation, immutability, and >=1 card in `FlashcardSet`; verify they fail before implementation
- [x] 2.2 Implement `Flashcard` in `backend/src/domain/models/flashcard.py` and `FlashcardSet` in `backend/src/domain/models/flashcard_set.py`; verify the domain tests pass
- [x] 2.3 Add `GenerationError`, `ProviderLimitExceededError`, and `InvalidGeneratorOutputError` to `backend/src/domain/exceptions.py`; verify they are importable
- [x] 2.4 Add the `FlashcardGenerator` Protocol in `backend/src/domain/ports/flashcard_generator.py`; verify it is importable
- [x] 2.5 Run `ruff check .` and `mypy src` on the domain layer; verify no lint or type errors

## 3. Application layer (TDD)

- [x] 3.1 Add failing unit tests in `backend/tests/unit/application/test_generate_flashcards_use_case.py` for success, zero cards, invalid output, and provider errors using a fake generator; verify they fail before implementation
- [x] 3.2 Extend `GenerateFlashcardsUseCase` to inject `FlashcardGenerator`, keep FR-3 validation, and return `list[Flashcard]`; verify the application tests pass
- [x] 3.3 Update dependency wiring/factories; verify the use case resolves the generator per env
- [x] 3.4 Run `ruff check .`, `ruff format --check`, and `mypy src`; verify no lint or type errors
- [x] 3.5 Add a failing unit test asserting that an unexpected generator exception (for example `httpx.InvalidURL`) surfaces as `GenerationError` and that constructing the use case without a generator is rejected; verify the test fails before implementation
- [x] 3.6 Make `generator` a required `GenerateFlashcardsUseCase` constructor argument, translate unexpected generator exceptions into `GenerationError`, and remove the default-generator `NotImplementedError` path; verify 3.5 and the existing application tests pass
- [x] 3.7 Run `ruff check .`, `ruff format --check`, and `mypy src`; verify no lint or type errors

## 4. Infrastructure layer (TDD)

- [x] 4.1 Add failing tests in `backend/tests/unit/infrastructure/llm/test_openai_compatible_generator.py` for success, malformed JSON, empty fields, zero cards, HTTP errors, and timeouts using mocked `httpx`; verify they fail before implementation
- [x] 4.2 Extend `backend/src/config.py` with `LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`, `LLM_TIMEOUT_SECONDS`, and `MAX_INPUT_BYTES`; verify settings parse from env
- [x] 4.3 Implement the deterministic `StubGenerator` in `backend/src/infrastructure/llm/stub_generator.py`; verify it returns known cards without network
- [x] 4.4 Implement the OpenAI-compatible adapter in `backend/src/infrastructure/llm/openai_compatible_generator.py` with strict parsing and explicit errors; verify the adapter tests pass
- [x] 4.5 Add `httpx` to runtime dependencies in `backend/pyproject.toml` and run `uv sync`; verify installation succeeds
- [x] 4.6 Run `ruff check .`, `ruff format --check`, and `mypy src` on the infrastructure layer; verify no lint or type errors
- [x] 4.7 Add failing unit tests for settings validation: `APP_ENV=production` with `LLM_PROVIDER=stub` raises at startup, an unrecognized `LLM_PROVIDER` raises at startup, and `MAX_INPUT_BYTES` defaults to 10 MiB; verify they fail before implementation
- [x] 4.8 Implement the settings guards plus the `APP_ENV` and `MAX_INPUT_BYTES` defaults, and log a warning when the stub is active outside production; verify 4.7 passes
- [x] 4.9 Add failing adapter tests for context-limit detection: provider HTTP 422 maps to `ProviderLimitExceededError`, and provider HTTP 400 carrying a context-length-overflow error maps to `ProviderLimitExceededError`; verify they fail before implementation
- [x] 4.10 Implement context-limit detection and include `max_tokens` in the request payload; verify 4.9 and the existing adapter tests pass
- [x] 4.11 Run `ruff check .`, `ruff format --check`, and `mypy src`; verify no lint or type errors

## 5. Presentation layer (TDD)

- [x] 5.1 Update `backend/tests/integration/api/test_flashcards_generate.py`: valid input -> 200 + `data.cards`; empty/whitespace -> 400; provider limit -> 422; provider failure/invalid output -> 502; no `.apkg`; verify integration tests pass
- [x] 5.2 Update `backend/src/presentation/api/flashcards_router.py` to return `200` with `data.cards`; verify route contract
- [x] 5.3 Update `backend/src/presentation/api/exceptions.py` to map generation errors to `422/502` with the standard envelope; verify error mapping tests pass
- [x] 5.4 Update `backend/src/main.py` to wire the generator according to `LLM_PROVIDER`; verify app starts with stub provider
- [x] 5.5 Run `ruff check .`, `ruff format --check`, and `mypy src`; verify no lint or type errors
- [ ] 5.6 Add failing integration tests for the byte ceiling: text above `MAX_INPUT_BYTES` returns 413 `INPUT_TOO_LARGE` with `limit_bytes`/`received_bytes`, text at the ceiling returns 200, and no provider call occurs on rejection; verify they fail before implementation
- [ ] 5.7 Enforce the ceiling with a UTF-8 byte-length validator plus a `Content-Length` pre-check, and map `InputTooLargeError` to 413 in the error envelope; verify 5.6 passes
- [ ] 5.8 Add a failing test asserting the OpenAPI 200 response references a typed `data.cards[].front`/`data.cards[].back` schema rather than an untyped object; verify it fails before implementation
- [ ] 5.9 Add Pydantic response models for the success payload and use them as the route `response_model`; verify 5.8 passes
- [ ] 5.10 Add failing tests asserting that a missing or unknown request field returns 422 `INVALID_REQUEST` in the standard envelope without echoing the submitted input; verify they fail before implementation
- [ ] 5.11 Register a `RequestValidationError` handler that emits the standard envelope and strips submitted input from the response; verify 5.10 passes
- [ ] 5.12 Move generator wiring out of `app.dependency_overrides` into a provider function consumed by `Depends`, and update the integration tests to remove only their own override; verify the full integration suite passes regardless of test order
- [ ] 5.13 Run `ruff check .`, `ruff format --check`, and `mypy src`; verify no lint or type errors

## 6. Companion change (NOT part of this change)

The original plan deferred the AUTK-6 duplicate cleanup and the `text-input` spec
sync to a companion `reconcile-text-input` change. That change was never created,
and this change now owns its own byte ceiling, so nothing here depends on it. If
the duplicate cleanup is still wanted it must be raised as its own change (see
Workflow follow-up). No tracked tasks live in this section; the numbering is kept
so the existing step reports stay aligned with their sections.

## 7. Review and Update Existing Unit Tests (MANDATORY)

- [x] 7.1 Review existing unit tests for the touched modules and update expectations (notably the FR-3 integration test that expects `202`)
- [x] 7.2 Add any missing edge cases discovered during implementation
- [ ] 7.3 Add `backend/tests/conftest.py` with a fixture that pins environment configuration (`LLM_PROVIDER=stub`) per test; verify `LLM_PROVIDER=openai pytest` produces the same result as an unmodified shell
- [ ] 7.4 Rewrite assertions that prove nothing: the stub-guard test that raises inside `StudyText`, the `front != back` tautology, the `"stack" not in body` check, and the adapter mocks that discard `url`/`kwargs` (assert the `Authorization` header, `model`, and the `/chat/completions` path); verify each rewritten test fails when the behavior it covers is deliberately broken
- [ ] 7.5 Replace `app.dependency_overrides.clear()` with a targeted `del` in a `try/finally` fixture; verify the integration module passes with tests run in reverse order

## 8. Run Unit Tests and Verify Database State (MANDATORY)

- [x] 8.1 Capture the pre-test baseline (no database in this change; document N/A)
- [x] 8.2 Run targeted tests for the changed modules
- [x] 8.3 Run the full suite: `pytest --cov=src`
- [x] 8.4 Verify post-test state (no DB; document N/A) and restore anything mutated
- [x] 8.5 Create `openspec/changes/fr-4-flashcard-generation/reports/2026-11-24-step-8-unit-test-and-db-verification.md`; verify the report exists
- [ ] 8.6 Re-run the full suite after the revisions in sections 3-5 and 7 and update the step-8 report with the new counts and coverage; verify the report matches the command output

## 9. Manual Endpoint Testing with curl (MANDATORY - AGENT MUST EXECUTE)

- [x] 9.1 Start the backend with `uvicorn src.main:app` and `LLM_PROVIDER=stub`
- [x] 9.2 Test valid text -> 200 + `data.cards`
- [x] 9.3 Test empty text -> 400
- [x] 9.4 Test whitespace-only text -> 400
- [ ] 9.5 Test oversized input -> 413 `INPUT_TOO_LARGE` with `limit_bytes`/`received_bytes`
- [ ] 9.6 Test a missing or unknown request field -> 422 `INVALID_REQUEST` in the standard envelope
- [ ] 9.7 Test provider limit -> 422 `INPUT_EXCEEDS_PROVIDER_LIMIT` using real curl against the app pointed at a local stub HTTP provider that returns 422 (not TestClient)
- [ ] 9.8 Test provider failure -> 502 `GENERATION_ERROR` with the same local stub provider returning 500
- [ ] 9.9 Verify no `.apkg` or download link is present in any response
- [ ] 9.10 Rewrite `openspec/changes/fr-4-flashcard-generation/reports/2026-11-24-step-9-curl-verification.md` with the actual curl commands and responses, explicitly noting which cases previously used TestClient instead of curl
- [ ] 9.11 Stop the server and confirm no state was left behind

## 10. E2E Testing with Playwright MCP (N/A - no frontend)

- [x] 10.1 Document that Playwright E2E is not applicable because the MVP has no frontend in this change

## 11. Manual SM-05/06/07 Quality Validation (MANDATORY)

- [x] 11.1 Prepare a text fixture with identifiable facts at the beginning, middle, and end
- [x] 11.2 Generate cards with the stub and, if credentials exist, with the real provider
- [x] 11.3 Review every card: non-empty Front/Back (SM-05), single retrieval target (SM-06), Back answers and is grounded (SM-07)
- [x] 11.4 Record pass/fail per card in `openspec/changes/fr-4-flashcard-generation/reports/2026-11-24-sm-05-06-07-quality-validation.md`; verify the report exists
- [ ] 11.5 Re-run SM-05/06/07 against a configured real provider and record pass/fail per card; verify the report no longer reports SM-07 as SEMANTIC PENDING before AUTK-8 is closed

## 12. Update Technical Documentation (MANDATORY)

- [x] 12.1 Add `docs/api/flashcards.md` with the request/response contract, error codes, and env vars; verify it renders
- [x] 12.2 Update `README.md` with backend startup and LLM env configuration; verify it renders
- [ ] 12.3 Update `docs/backend-standards.md` to list `httpx` in the stack and the `domain/ports/` package; verify it renders and matches the implemented structure
- [ ] 12.4 Update `docs/api/flashcards.md` to document 413, 422 `INVALID_REQUEST`, context-limit detection, the `APP_ENV` production guard, and the 10 MiB default; verify each example matches a real curl response
- [ ] 12.5 Update the README environment table for `APP_ENV` and the new `MAX_INPUT_BYTES` default; verify it matches `backend/src/config.py`
- [ ] 12.6 Sync the `flashcard-generation` spec delta into `openspec/specs/` and verify `openspec validate` passes

## 13. Final verification and delivery

- [x] 13.1 Run `ruff check .` and `ruff format --check` from `backend/`
- [x] 13.2 Run `mypy src` from `backend/`
- [x] 13.3 Run `pytest --cov=src` and verify >=90% coverage
- [x] 13.4 Commit with conventional messages (`feat(AUTK-8): ...`, `refactor(AUTK-8): ...`, `docs(AUTK-8): ...`); verify commit is clean
- [x] 13.5 Push `feature/AUTK-8` and open a PR to `main` referencing AUTK-8; verify PR exists
- [ ] 13.6 Move AUTK-8 to **In Review** and comment the PR link; verify ticket status
- [ ] 13.7 File follow-up AUTK tickets for the deferred items listed under Workflow follow-up and link them from this file; verify each ticket exists

## Workflow follow-up

- Archive `fr-4-flashcard-generation` after PR review and merge.
- Raise the `reconcile-text-input` change separately if the AUTK-6 duplicate cleanup is still wanted; it was never created and is not a dependency of this change.
- Deferred follow-ups to file as AUTK tickets:
  - Adapter retry and code-fence repair (JSON wrapped in code fences currently returns 502).
  - Provider 401/403/429 distinction with `Retry-After` and retry/backoff.
  - Output size caps: card count, Front/Back length, and deduplication.
  - Structured logging for provider failures.
  - `FlashcardSet` accepts lists and is unhashable despite `frozen=True`.
  - Config parse errors should name the offending variable; add bounds checks for timeouts.
  - Reuse a long-lived `httpx.AsyncClient` instead of creating one per request.
