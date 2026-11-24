# Tasks

## 0. Setup: Create Feature Branch (MANDATORY - FIRST STEP)

- [x] 0.1 Run `git checkout main` and `git pull --ff-only origin main`; verify `main` is at `origin/main`
- [x] 0.2 Create and switch to `feature/AUTK-8` from `main`
- [x] 0.3 Verify current branch is `feature/AUTK-8` and the working tree is clean

## 1. OpenSpec artifacts and validation

- [x] 1.1 Create the `fr-4-flashcard-generation` change with `proposal.md`, `design.md`, `specs/flashcard-generation/spec.md`, and this `tasks.md`; verify all files exist
- [x] 1.2 Run `openspec validate fr-4-flashcard-generation` and fix any validation errors
- [ ] 1.3 Create the companion `reconcile-text-input` change for the AUTK-6 cleanup and validate it

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

## 4. Infrastructure layer (TDD)

- [x] 4.1 Add failing tests in `backend/tests/unit/infrastructure/llm/test_openai_compatible_generator.py` for success, malformed JSON, empty fields, zero cards, HTTP errors, and timeouts using mocked `httpx`; verify they fail before implementation
- [x] 4.2 Extend `backend/src/config.py` with `LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`, `LLM_TIMEOUT_SECONDS`, and `MAX_INPUT_BYTES`; verify settings parse from env
- [x] 4.3 Implement the deterministic `StubGenerator` in `backend/src/infrastructure/llm/stub_generator.py`; verify it returns known cards without network
- [x] 4.4 Implement the OpenAI-compatible adapter in `backend/src/infrastructure/llm/openai_compatible_generator.py` with strict parsing and explicit errors; verify the adapter tests pass
- [x] 4.5 Add `httpx` to runtime dependencies in `backend/pyproject.toml` and run `uv sync`; verify installation succeeds
- [x] 4.6 Run `ruff check .`, `ruff format --check`, and `mypy src` on the infrastructure layer; verify no lint or type errors

## 5. Presentation layer (TDD)

- [x] 5.1 Update `backend/tests/integration/api/test_flashcards_generate.py`: valid input -> 200 + `data.cards`; empty/whitespace -> 400; provider limit -> 422; provider failure/invalid output -> 502; no `.apkg`; verify integration tests pass
- [x] 5.2 Update `backend/src/presentation/api/flashcards_router.py` to return `200` with `data.cards`; verify route contract
- [x] 5.3 Update `backend/src/presentation/api/exceptions.py` to map generation errors to `422/502` with the standard envelope; verify error mapping tests pass
- [x] 5.4 Update `backend/src/main.py` to wire the generator according to `LLM_PROVIDER`; verify app starts with stub provider
- [x] 5.5 Run `ruff check .`, `ruff format --check`, and `mypy src`; verify no lint or type errors

## 6. Companion cleanup change (separate artifacts)

- [ ] 6.1 Create `reconcile-text-input` with its own proposal/design/specs/tasks (FR-1 `SubmissionPolicy` port, removal of `src/autokards/`, root `tests/`, root `pyproject.toml`, `docs/api/submissions.md`, and `text-input` spec sync); verify all files exist
- [ ] 6.2 Run `openspec validate reconcile-text-input` and fix any validation errors
- [ ] 6.3 Execute the `reconcile-text-input` tasks after this change is verified

## 7. Review and Update Existing Unit Tests (MANDATORY)

- [ ] 7.1 Review existing unit tests for the touched modules and update expectations (notably the FR-3 integration test that expects `202`)
- [ ] 7.2 Add any missing edge cases discovered during implementation

## 8. Run Unit Tests and Verify Database State (MANDATORY)

- [ ] 8.1 Capture the pre-test baseline (no database in this change; document N/A)
- [ ] 8.2 Run targeted tests for the changed modules
- [ ] 8.3 Run the full suite: `pytest --cov=src`
- [ ] 8.4 Verify post-test state (no DB; document N/A) and restore anything mutated
- [ ] 8.5 Create `openspec/changes/fr-4-flashcard-generation/reports/YYYY-MM-DD-step-8-unit-test-and-db-verification.md`; verify the report exists

## 9. Manual Endpoint Testing with curl (MANDATORY - AGENT MUST EXECUTE)

- [ ] 9.1 Start the backend with `uvicorn src.main:app` and `LLM_PROVIDER=stub`
- [ ] 9.2 Test valid text -> 200 + `data.cards`
- [ ] 9.3 Test empty and whitespace-only text -> 400
- [ ] 9.4 Test oversized input -> 413 (after the companion change)
- [ ] 9.5 Test provider limit -> 422
- [ ] 9.6 Test provider failure / invalid output -> 502
- [ ] 9.7 Verify no `.apkg` or download link is present
- [ ] 9.8 Create `openspec/changes/fr-4-flashcard-generation/reports/YYYY-MM-DD-step-9-curl-verification.md`; document all curl commands and responses
- [ ] 9.9 Stop the server and confirm no state was left behind

## 10. E2E Testing with Playwright MCP (N/A - no frontend)

- [ ] 10.1 Document that Playwright E2E is not applicable because the MVP has no frontend in this change

## 11. Manual SM-05/06/07 Quality Validation (MANDATORY)

- [ ] 11.1 Prepare a text fixture with identifiable facts at the beginning, middle, and end
- [ ] 11.2 Generate cards with the stub and, if credentials exist, with the real provider
- [ ] 11.3 Review every card: non-empty Front/Back (SM-05), single retrieval target (SM-06), Back answers and is grounded (SM-07)
- [ ] 11.4 Record pass/fail per card in `openspec/changes/fr-4-flashcard-generation/reports/YYYY-MM-DD-sm-05-06-07-quality-validation.md`; verify the report exists

## 12. Update Technical Documentation (MANDATORY)

- [ ] 12.1 Add `docs/api/flashcards.md` with the request/response contract, error codes, and env vars; verify it renders
- [ ] 12.2 Update `README.md` with backend startup and LLM env configuration; verify it renders
- [ ] 12.3 Update `docs/backend-standards.md` if the dependency or env changes affect the documented stack; verify it renders
- [ ] 12.4 Sync the OpenSpec spec and archive the change after verification

## 13. Final verification and delivery

- [ ] 13.1 Run `ruff check .` and `ruff format --check` from `backend/`
- [ ] 13.2 Run `mypy src` from `backend/`
- [ ] 13.3 Run `pytest --cov=src` and verify >=90% coverage
- [ ] 13.4 Commit with conventional messages (`feat(AUTK-8): ...`, `refactor(AUTK-8): ...`, `docs(AUTK-8): ...`); verify commit is clean
- [ ] 13.5 Push `feature/AUTK-8` and open a PR to `main` referencing AUTK-8; verify PR exists
- [ ] 13.6 Move AUTK-8 to **En revisión** and comment the PR link; verify ticket status

## Workflow follow-up

- Run `openspec validate` on both changes before applying.
- Archive `fr-4-flashcard-generation` after PR review and merge.
- Archive `reconcile-text-input` after its tasks are complete.
