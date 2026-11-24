# Design

## Context

The project is at scaffolding stage: `openspec/` config exists (`schema: spec-driven`), `docs/backend-standards.md` defines a Python DDD layered architecture (domain/application/presentation/infrastructure), and `docs/prd/` contains the MVP requirements including FR-3 (empty input handling) and its acceptance criteria AC-1/AC-2/AC-3. No backend source code exists yet, so this change establishes the initial layer structure under `backend/src/` and tests under `backend/tests/`. See proposal.md for motivation; see `specs/input-validation/spec.md` for the requirement contract.

## Goals / Non-Goals

**Goals:**
- Validate empty or whitespace-only study text at the API boundary before any generation infrastructure is invoked.
- Return HTTP 400 with a standard error envelope and message "Readable study text is required" for invalid input; never offer a `.apkg` download on failure.
- Proceed to flashcard generation (FR-4, separate change) when input contains at least one non-whitespace character.
- Keep domain models free of FastAPI/Pydantic/SQLAlchemy coupling per DDD standards.

**Non-Goals:**
- Flashcard generation itself (FR-4) — out of scope for this change.
- PDF upload/extraction (FR-2, out of scope per PRD).
- Pre-export card preview, in-app editing, deck ID routing, `.apkg` generation (FR-5 through FR-10, separate changes).

## Decisions

- **Validation at the API boundary via `StudyText` value object**: construction rejects empty/whitespace-only text, raising `ValidationError`. Rationale: encapsulates the business invariant (readable text required) in the domain layer, self-validating and framework-free. Alternative considered — validating inside the use case or route — rejected because it scatters the same rule across layers and makes the domain model anemic.
- **DDD layered architecture**: domain value object/exception → application use case + Pydantic schema → presentation route + centralized exception handler. Rationale: matches `docs/backend-standards.md`, keeps services free of ORM/HTTP concerns, and makes each layer independently testable.
- **Centralized exception handler mapping `ValidationError` → HTTP 400**: Rationale: avoids repeating try/except HTTP mapping in every route, consistent with the standardized error envelope in the standards.
- **No database/repository for this change**: validation is stateless and in-memory; no persistence is required. Rationale: adding SQLAlchemy/Alembic would be premature for a stateless validation entry point.

## Risks / Trade-offs

- [Risk] Frontend/UI client not yet defined, so the exact consumer of the endpoint is unknown → Mitigation: design the request/response as plain JSON per the API design standards so any client can consume it.
- [Risk] Empty-validation business rule duplicated elsewhere later → Mitigation: keep the rule solely in `StudyText`; all entry points construct `StudyText` rather than re-implementing the strip/length check.
- [Trade-off] No repository/protocol introduced yet → Mitigation: none needed; add repositories only when persistence is required by a later change (FR-7/FR-8).

## Open Questions

None.
