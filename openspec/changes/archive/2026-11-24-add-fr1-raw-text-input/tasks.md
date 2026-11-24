# Tasks

## 0. Setup: Feature Branch (MANDATORY - FIRST STEP)

- [x] 0.1 Create feature branch `feature/AUTK-6` from `main` and verify `git status --branch` shows it as current
- [x] 0.2 Verify branch is up to date with `origin/main`

## 1. Project Scaffold

- [x] 1.1 Create `pyproject.toml` (or `requirements.txt` + `requirements-dev.txt`) declaring `fastapi`, `uvicorn`, `pytest`, `httpx` and verify `pip install -e .` (or equivalent) succeeds
- [x] 1.2 Create package layout `src/autokards/__init__.py`, `src/autokards/input/__init__.py`, `src/autokards/api/__init__.py`, `tests/input/`, `tests/api/` and verify `pytest --collect-only` runs without import errors

## 2. Core Policy: Integrity and Limits (TDD)

- [x] 2.1 Write failing tests in `tests/input/test_policy.py` for AC-1 (byte-for-byte identical large/unicode/mixed-line-ending text accepted) and verify they fail (`pytest tests/input/test_policy.py -v` shows red)
- [x] 2.2 Implement `src/autokards/input/policy.py` acceptance path to make AC-1 tests pass and verify `pytest tests/input/test_policy.py -v` is green
- [x] 2.3 Write failing tests for AC-2 (oversized input rejected with explicit error carrying limit/received bytes, nothing persisted) and verify they fail
- [x] 2.4 Implement the byte-ceiling rejection path (`AUTOKARDS_MAX_INPUT_BYTES`, `INPUT_TOO_LARGE`) to make AC-2 tests pass and verify green run
- [x] 2.5 Write failing tests for AC-3 (boundary sweep just under the limit is accepted; no character/word cap exists) and verify they fail, then confirm they pass with no additional code changes (the byte-only design already satisfies this) and document that confirmation in the test file's docstring
- [x] 2.6 Write failing test asserting no response/error message contains unlimited-capacity language, then verify it passes against the implemented messages

## 3. Core Policy: Provider Failure Path (TDD)

- [x] 3.1 Define `GenerationPort` interface and a `FakeGenerationPort` test double in `src/autokards/input/models.py` / `policy.py`
- [x] 3.2 Write failing test asserting a provider-side rejection surfaces as an explicit `INPUT_EXCEEDS_PROVIDER_LIMIT` error, not a truncated/partial result, and verify it fails
- [x] 3.3 Implement the provider-error mapping to make the test pass and verify `pytest tests/input/ -v` is fully green

## 4. API Shell (TDD)

- [x] 4.1 Write failing integration tests in `tests/api/test_submissions.py` for `POST /api/v1/submissions`: 202 on valid text, 413 on oversized body (with `limit_bytes`/`received_bytes` in the response), 422 on simulated provider rejection, and empty-input rejection
- [x] 4.2 Implement `src/autokards/api/app.py` (FastAPI app, streaming size check before buffering) and `src/autokards/api/store.py` (in-memory submission store) to make the tests pass and verify `pytest tests/api/ -v` is green
- [x] 4.3 Wire the fake `GenerationPort` into the app for this slice and verify the 422 integration test still passes end-to-end through the HTTP layer

## 5. Review and Update Existing Unit Tests (MANDATORY)

- [x] 5.1 Review `tests/input/` and `tests/api/` for overlap/duplication introduced across tasks 2-4 and consolidate any redundant cases, verifying the full suite still passes after consolidation

## 6. Run Unit Tests and Verify State (MANDATORY)

- [x] 6.1 Capture pre-test state baseline (no persistent datastore in this slice; record that the in-memory store starts empty per process)
- [x] 6.2 Run targeted tests: `pytest tests/input/ tests/api/ -v` and record passed/failed/skipped counts
- [x] 6.3 Run full suite: `pytest -v --cov=src/autokards` and record total counts, coverage, and runtime
- [x] 6.4 Verify no unintended state leaks between tests (in-memory store is re-instantiated per test via fixture); confirm via a test asserting store isolation
- [x] 6.5 Create report `openspec/changes/add-fr1-raw-text-input/reports/<date>-step-6-unit-test-and-state-verification.md` with commands, results, and state verification
- [x] 6.6 Mark this step complete only after the report exists and the suite is green

## 7. Manual Endpoint Testing with curl (MANDATORY - AGENT MUST EXECUTE)

- [x] 7.1 Start the API locally (e.g. `uvicorn autokards.api.app:app --port 8000`) and verify it is reachable
- [x] 7.2 `curl -X POST http://localhost:8000/api/v1/submissions -H "Content-Type: application/json" -d '{"text":"<non-empty study text>"}'` and verify `202` with a submission id in the body
- [x] 7.3 `curl` a payload exceeding `AUTOKARDS_MAX_INPUT_BYTES` and verify `413 INPUT_TOO_LARGE` with `limit_bytes`/`received_bytes` in the body
- [x] 7.4 `curl` an empty `"text"` value and verify an explicit rejection (not a 202)
- [x] 7.5 `curl` a payload crafted to trigger the fake provider's limit and verify `422 INPUT_EXCEEDS_PROVIDER_LIMIT`
- [x] 7.6 Document all commands and responses in `openspec/changes/add-fr1-raw-text-input/reports/<date>-step-7-curl-verification.md`; stop the local server afterward

## 8. Documentation (MANDATORY)

- [x] 8.1 Write `docs/api/submissions.md` documenting the endpoint contract, the byte-based limit rationale, and the three response shapes (202/413/422), and verify it matches the actual curl output from Step 7
- [x] 8.2 Review `docs/documentation-standards.md` checklist and confirm no other doc requires updates for this change (record the confirmation in the PR description)

## Workflow follow-up

- Open a PR referencing AUTK-6 once all tasks above are complete and the suite is green.
- Comment the PR link on AUTK-6 and move the ticket to "En revisión".
- File a follow-up Jira chore to decide the durable application stack (Node/TS per `docs/backend-standards.md` vs. Python for `.apkg` generation), since this slice uses Python as a reversible choice only.
- Archive this OpenSpec change after the PR is merged and verified, per `openspec-archive-change`.
