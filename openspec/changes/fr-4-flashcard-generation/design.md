# Design

## Context

FR-3 already validates the generation entry point: `StudyText` rejects
empty/whitespace-only text, `GenerateFlashcardsUseCase` returns the validated
text, and `POST /api/v1/flashcards/generate` responds `202 accepted`. FR-4 must
turn that validated text into structured cards. The project follows the DDD
layered architecture in `docs/backend-standards.md`
(domain/application/presentation/infrastructure) and uses FastAPI + Pydantic v2
+ pytest + ruff + mypy. The companion AUTK-6 implementation in the repo root
(`src/autokards/input/policy.py`) defines a framework-free `SubmissionPolicy`
and a `GenerationPort` boundary whose error contract this design reuses. See
proposal.md for motivation and `specs/flashcard-generation/spec.md` for the
requirement contract.

## Goals / Non-Goals

**Goals:**
- Generate one or more front/back cards from validated text.
- Keep Fronts single-target and Backs answering + grounded through prompt
  engineering and strict structural validation.
- Keep generation provider-agnostic through a domain port; ship an
  OpenAI-compatible adapter and a deterministic stub.
- Return `200` with `data.cards`; map failures to explicit `422/502` envelopes.
- Keep the domain free of FastAPI/Pydantic/HTTP-client coupling.

**Non-Goals:**
- Persistence, `.apkg` generation, deck targeting (FR-7/FR-8, separate changes).
- Pre-export preview, in-app editing (FR-5/FR-6, out of scope).
- Automated semantic verification of single-target/grounding beyond prompt +
  structural checks; semantic quality is validated manually via SM-05/06/07.
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
- **Strict output parsing**: require a JSON array of `{front, back}`; reject
  malformed JSON, zero cards, empty fields, and non-string values with
  `InvalidGeneratorOutputError`. Rationale: prevents silent partial success and
  guarantees AC-1.
- **Prompt engineering**: system prompt requires one retrieval target per Front,
  a Back that answers it using only the source text, the source language, and
  JSON-only output. Rationale: semantic quality is model-driven; structural
  validation catches shape violations.
- **HTTP mapping**: `ValidationError` -> 400 (existing); `InputTooLargeError` ->
  413 (companion change); `ProviderLimitExceededError` -> 422;
  `GenerationError`/`InvalidGeneratorOutputError` -> 502. Rationale: consistent
  with the standard error envelope and no stack-trace leakage.
- **Success contract**: `200` with `{success, data:{cards}, message}`. Rationale:
  generation is synchronous and the MVP has no persistence; `202` no longer
  reflects completed work.

## Risks / Trade-offs

- [Risk] LLM output may violate single-target/grounding despite the prompt ->
  Mitigation: strict structural validation + manual SM-05/06/07 review on a
  fixture; a second verifier pass is deferred.
- [Risk] Provider outages or timeouts degrade UX -> Mitigation: explicit `502`
  with no partial cards; configurable timeout; stub for offline.
- [Risk] FastAPI/Pydantic buffers the body before the handler, weakening the
  pre-buffer byte-ceiling guarantee from AUTK-6 -> Mitigation: enforce the
  ceiling at the boundary and document the limitation; the companion
  `reconcile-text-input` change owns the final behavior.
- [Trade-off] No persistence means cards are only in the response ->
  Mitigation: intentional for this slice; FR-8/FR-10 add package/download.
- [Trade-off] No automated semantic verifier -> Mitigation: manual report per
  SM-05/06/07; revisit if quality fails.

## Migration Plan

- Add `httpx` as a runtime dependency in `backend/pyproject.toml` and run
  `uv sync`.
- Wire the generator in `backend/src/main.py` based on `LLM_PROVIDER`.
- No database migrations (stateless change).
- Rollback: revert `feature/AUTK-8`; `backend/` and `openspec/changes/`
  are self-contained.

## Open Questions

- Default provider/model values for local development (e.g., `gpt-4o-mini`
  versus a local model). Resolved at implementation via env config; no
  hardcoded secret.
