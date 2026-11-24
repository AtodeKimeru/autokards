# Design

## Context

See proposal.md - Why for motivation. The current state: autokards targets generated cards via an isolated numeric Deck ID (FR-7), which AUTK-2 spike findings showed is technically infeasible against Anki Desktop 26.09.4 — Anki's importer matches decks by name (including `::` subdeck hierarchies) and remaps numeric IDs on import. The export-only MVP imports `.apkg` files manually via Anki Desktop and does not access the user's collection.

## Goals / Non-Goals

**Goals:**
- Bind generated flashcards to a target deck by name (including `::` subdeck hierarchy) rather than numeric Deck ID.
- Preserve manual Anki Desktop import workflow.
- Preserve existing review history of cards already in the target deck.
- Keep autokards free of collection access / deck-name lookup (export-only).

**Non-Goals:**
- Implementing deck-name lookup or partial collection access in autokards.
- Modifying Anki's import behavior or duplicate-handling rules.
- Automated sync, cloud, mobile, or in-place deck mutation.

## Decisions

### Deck-name binding (replaces numeric Deck ID)
**Decision:** Target deck is specified by name including `::` subdeck path; autokards writes the name into the `.apkg` and Anki resolves it on import.
**Rationale:** Matches Anki's native import behavior (name-based matching, ID remapping on import); no collection access needed; reduces DB complexity.
**Alternatives considered:**
- Numeric Deck ID binding — rejected: AUTK-2 spike showed ID-only routing infeasible (Anki remaps IDs on import).
- Deck name + numeric ID — rejected: numeric ID adds no routing value and reintroduces the infeasible assumption.
- Deck-name binding via AnkiConnect lookup (collection access) — rejected for MVP: requires autokards to access/query the user's Anki collection, adds auth/state complexity and coupling to a running Anki instance, contradicting the export-only MVP constraint. Revisit post-MVP if collection access becomes a requirement.

### Subdeck creation vs. existing-deck-only
**Decision:** Allow Anki to auto-create missing decks/subdecks on import (native behavior); do not require the target deck to pre-exist.
**Rationale:** Lower user friction for first-time setup; avoids autokards needing collection access to check existence. The spec labels this as relying on Anki's native behavior rather than an autokards guarantee.

### `::` sanitization at autokards boundary
**Decision:** autokards validates/sanitizes deck names at the boundary — reject empty names, reject empty `::` segments (e.g. `"Spanish::"`, `"::Verbs"`, `"Spanish:::Verbs"`), strip leading/trailing whitespace — then writes the resulting normalized name into the `.apkg`. The normalization contract is: strip leading/trailing whitespace from the whole name, split on `::`, strip each segment, reject if any segment is empty, rejoin segments with `::`. The resulting normalized name is what autokards writes into the package; Anki resolves and may further normalize per component on import.
**Rationale:** Prevents malformed packages while preserving full fidelity with the user's existing Anki structure. Comparison in SM-12 must be against the *normalized* deck name (post-stripping), not the raw user input, because Anki normalizes per component itself on import. Exact sanitization rules beyond empty segments/whitespace are an open question labeled in the PRD.

### Duplicate handling via Anki's defaults
**Decision:** Rely on Anki's default note-type update rules on re-import; autokards specifies no duplicate-handling behavior.
**Rationale:** Duplicate handling is Anki's responsibility; autokards cannot control it without collection access.

## Risks / Trade-offs

[Risk] Auto-creating missing `::` subdecks may surprise users who expected existing-deck-only → Mitigation: clearly document that import follows Anki's native behavior and that missing decks are created by Anki, not autokards.

[Risk] Verbatim `::` names with typos could create unintended subdecks → Mitigation: boundary sanitization (reject empty segments, strip whitespace) reduces malformed input; user is responsible for name accuracy.

[Risk] Import behavior varies by Anki version → Mitigation: validation target is Anki Desktop 26.09.4 only (per PRD §5.2); no compatibility claims for other versions.

[Risk] Deck-name binding alone does not guarantee cards land in a *specific pre-existing* deck if naming collides → Mitigation: Anki's kind-conflict renaming governs collisions; out of autokards scope.

## Open Questions

- Exact `::` sanitization rules (which characters are disallowed beyond empty segments / whitespace) — to be finalized at implementation.
- Whether to add explicit existing-deck-only mode as a future option — currently out of scope.
