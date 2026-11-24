# Proposal

## Why

Learners currently have no way to submit study text into autokards. FR-1 (AUTK-6) requires accepting raw text input with no product-defined length limit, while still failing explicitly rather than silently truncating when real infrastructure or provider limits are hit. This is the foundation for every downstream generation capability (FR-3, FR-4, FR-7+).

## What Changes

- Introduce a `POST /api/v1/submissions` endpoint that accepts raw text and forwards the complete, unmodified text toward flashcard generation.
- Enforce a single infrastructure-derived byte ceiling (not a product-defined character/word rule) and reject oversized input with an explicit `413 INPUT_TOO_LARGE` error carrying the limit and received size.
- Surface provider/model-level rejection as an explicit `422 INPUT_EXCEEDS_PROVIDER_LIMIT` error, never a silent truncation or partial result.
- Add a minimal non-empty guard on the input (full empty/whitespace UX is **out of scope**, owned by AUTK-7/FR-3).
- Scaffold the application with Python 3.14 + FastAPI + pytest. This stack is a reversible choice for this slice only; it does not supersede `docs/backend-standards.md`'s Node/TS prescription. A follow-up chore will track the durable stack decision.

## Capabilities

### New Capabilities
- `text-input`: Accepting raw study text for flashcard generation, including integrity (no truncation), infrastructure-limit rejection, and explicit failure reporting. Owns FR-1 only; does not own empty/whitespace validation (FR-3) or generation itself (FR-4).

### Modified Capabilities
- None — this is a greenfield capability.

## Impact

- **New code**: `src/autokards/input/` (framework-free policy + models), `src/autokards/api/` (FastAPI shell, in-memory store), `tests/`.
- **No persistence layer yet**: submissions are held in memory; restart loses data. Acceptable for AC-1..AC-3, flagged as a known limitation in `design.md`.
- **No real model/provider integration**: a fake `GenerationPort` stands in for the real provider, which will be wired in FR-4/FR-7+.
- **Docs**: new `docs/api/submissions.md` contract; `docs/backend-standards.md` is not amended by this change — the stack deviation is tracked separately.
- **Dependencies**: adds Python/FastAPI/pytest tooling (no dependency exists in the repo today).
