# Design

## Context

FR-3 already validates the generation entry point: `StudyText` rejects
empty/whitespace-only text, `GenerateFlashcardsUseCase` returns the validated
text, and `POST /api/v1/flashcards/generate` responds `202 accepted`. FR-4 must
turn that validated text into structured cards. The project follows the DDD
layered architecture in `docs/backend-standards.md`
(domain/application/presentation/infrastructure) and uses FastAPI + Pydantic v2
+ pytest + ruff + mypy.

FR-1 established the byte-ceiling contract for this product: a single
infrastructure-derived limit (not a product-defined character/word rule) that
rejects oversized input explicitly rather than truncating it. This change adopts
that contract for the generation entry point instead of deferring it to a
separate change, so `MAX_INPUT_BYTES` is enforced here.

See proposal.md for motivation and `specs/flashcard-generation/spec.md` for the
requirement contract.

## Goals / Non-Goals

**Goals:**
- Generate one or more front/back cards from validated text.
- Keep Fronts single-target and Backs answering + grounded through prompt
  engineering and strict structural validation.
- Keep generation provider-agnostic through a domain port; ship an
  OpenAI-compatible adapter and a deterministic stub.
- Enforce the `MAX_INPUT_BYTES` ceiling in this change, before the provider call.
- Return `200` with `data.cards`; map failures to explicit `413/422/502`
  envelopes with a typed success schema.
- Keep the domain free of FastAPI/Pydantic/HTTP-client coupling.

**Non-Goals:**
- Persistence, `.apkg` generation, deck targeting (FR-7/FR-8, separate changes).
- Pre-export preview, in-app editing (FR-5/FR-6, out of scope).
- Automated semantic verification of single-target/grounding beyond prompt +
  structural checks; semantic quality is validated manually via SM-05/06/07.
- Automated grading of model output quality, retry/backoff policies, and
  structured logging (deferred follow-ups, see Risks).
- Frontend.

## Decisions

- **`Flashcard` value object + `FlashcardSet` aggregate**: `Flashcard` is a
  frozen dataclass validating non-empty `front`/`back`; `FlashcardSet` enforces
  >=1 card. Rationale: keeps the AC-1/field-separation invariants in the domain,
  framework-free.
- **`FlashcardGenerator` Protocol**: async `generate(StudyText) -> list[Flashcard]`.
  Rationale: DIP; the use case depends on an abstraction and tests inject a fake.
- **OpenAI-compatible adapter via `httpx`**: configurable
  `base_url`/`api_key`/`model`/timeout; JSON structured output. Rationale: works
  with OpenAI, OpenRouter, Ollama, LM Studio without vendor lock-in.
- **Deterministic `stub` adapter**: selected with `LLM_PROVIDER=stub`.
  Rationale: tests and curl verification run offline without credentials; the
  real-provider path is covered with mocked `httpx`.
- **Provider selection and fail-fast**: `LLM_PROVIDER` defaults to `stub` for
  local development and offline verification. Startup MUST fail when
  `APP_ENV=production` and the resolved provider is `stub`. An unrecognized
  `LLM_PROVIDER` value MUST fail at startup rather than falling through to the
  real adapter. A warning is logged whenever the stub is active outside
  production. Rationale: the stub returns input-agnostic cards, so serving it as
  a production success would fabricate ungrounded material; a silent fallback on
  a typo would ship an unconfigured provider.
- **Byte ceiling enforcement**: validate `len(text.encode("utf-8"))` against
  `MAX_INPUT_BYTES` (default 10 MiB, aligned with FR-1) and reject with `413`
  `INPUT_TOO_LARGE` before the provider call; also pre-check `Content-Length` so
  oversized bodies are not buffered. Rationale: bounds both provider cost and
  worker memory. Residual limitation: FastAPI buffers the body before validation
  runs, so the ceiling is enforced at the handler boundary, not at the socket.
- **Provider context-limit detection**: map provider HTTP 422 and HTTP 400
  responses whose error payload indicates a context-length overflow to
  `ProviderLimitExceededError`. Rationale: OpenAI, OpenRouter, Ollama, and LM
  Studio report overflow as HTTP 400, so a literal-422-only check would make the
  scenario unreachable.
- **Strict output parsing**: require a JSON array of `{front, back}`; reject
  malformed JSON, zero cards, empty fields, and non-string values with
  `InvalidGeneratorOutputError`. Rationale: prevents silent partial success and
  guarantees AC-1.
- **Prompt engineering**: system prompt requires one retrieval target per Front,
  a Back that answers it using only the source text, the source language, and
  JSON-only output. Rationale: semantic quality is model-driven; structural
  validation catches shape violations.
- **HTTP mapping**: `ValidationError` -> 400 `VALIDATION_ERROR`;
  `InputTooLargeError` -> 413 `INPUT_TOO_LARGE` with `limit_bytes`/`received_bytes`
  in `details`; request-schema violations -> 422 `INVALID_REQUEST`;
  `ProviderLimitExceededError` -> 422 `INPUT_EXCEEDS_PROVIDER_LIMIT`;
  `GenerationError`/`InvalidGeneratorOutputError` -> 502 `GENERATION_ERROR`.
  Rationale: consistent with the standard error envelope and no stack-trace
  leakage.
- **Typed response and envelope**: Pydantic response models describe
  `data.cards` and drive the OpenAPI schema; a `RequestValidationError` handler
  emits `422 INVALID_REQUEST` in the standard envelope without echoing submitted
  input. Rationale: a documented contract clients can bind to, and one envelope
  for every failure path.
- **Composition root and test seam**: the generator is resolved by a provider
  function consumed through `Depends`, not by mutating `app.dependency_overrides`
  in production wiring; tests remove only the override they added. Rationale:
  `create_app()` currently installs its wiring in that same dict, so a test-wide
  `clear()` leaves the running app un-wired.
- **Success contract**: `200` with `{success, data:{cards}, message}`. Rationale:
  generation is synchronous and the MVP has no persistence; `202` no longer
  reflects completed work.

## Risks / Trade-offs

- [Risk] LLM output may violate single-target/grounding despite the prompt ->
  Mitigation: strict structural validation + manual SM-05/06/07 review on a
  fixture; a second verifier pass is deferred.
- [Risk] The stub returns input-agnostic cards, so SM-07 grounding cannot be
  verified offline -> Mitigation: production startup refuses the stub; SM-07
  requires a recorded real-provider run before the ticket is closed.
- [Risk] FastAPI buffers the request body before the handler validates it, so a
  hostile client can still force an oversized buffer -> Mitigation:
  `Content-Length` pre-check plus handler-level byte validation; the residual
  socket-level gap is accepted for this slice.
- [Risk] Provider outages or timeouts degrade UX -> Mitigation: explicit `502`
  with no partial cards; configurable timeout; stub for offline.
- [Trade-off] No persistence means cards are only in the response ->
  Mitigation: intentional for this slice; FR-8/FR-10 add package/download.
- [Trade-off] No automated semantic verifier -> Mitigation: manual report per
  SM-05/06/07; revisit if quality fails.
- [Trade-off] All provider failures (including 401/403/429) collapse to `502` in
  this slice -> Mitigation: deferred to a follow-up AUTK ticket that splits auth
  failures from rate limits and honours `Retry-After`.

## Migration Plan

- Add `httpx` as a runtime dependency in `backend/pyproject.toml` and run
  `uv sync`.
- Wire the generator in `backend/src/main.py` based on `LLM_PROVIDER`, guarded by
  the `APP_ENV` fail-fast checks.
- No database migrations (stateless change).
- Rollback: revert `feature/AUTK-8`; `backend/` and `openspec/changes/`
  are self-contained.

## Open Questions

- None. Resolved: the stub is the local default and is refused in production; a
  real provider must be selected explicitly.
