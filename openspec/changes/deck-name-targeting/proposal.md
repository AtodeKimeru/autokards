# Proposal

## Why

Per AUTK-2 spike findings against Anki Desktop 26.09.4, Anki's importer matches imported decks by **deck name** (including `::` subdeck hierarchies) and **remaps numeric deck IDs on import**. The MVP's current assumption — routing generated cards by an isolated numeric Deck ID (FR-7) — is technically infeasible because an embedded numeric ID does not determine which local deck receives the cards. This change aligns autokards with native Anki import behavior by targeting decks via deck name instead of numeric ID, preserving manual Anki Desktop import and existing review history, while reducing database complexity (no name lookup or collection access required in autokards).

## What Changes

- Replace numeric target Deck ID binding with deck-name binding (including `::` subdeck hierarchy support) in target deck targeting (FR-7, FR-8, FR-9).
- Update success measures SM-11, SM-12, SM-15 to reflect name-based deck matching and numeric-ID reassignment on import.
- Update §5.4 acceptance gate and §5.5 technical references to remove numeric-ID lookup assumptions.
- Label remaining assumptions and open questions: subdeck creation vs. existing-deck-only, `::` sanitization/naming rules, duplicate handling on import.
- Add `deck-targeting` capability spec capturing name-based deck binding behavior.

## Capabilities

### New Capabilities

- `deck-targeting`: Defines how generated flashcards are bound to a target Anki deck on import — by deck name including `::` subdeck hierarchy, matched by Anki's native importer; numeric deck ID is not the routing contract.

### Modified Capabilities

- (none)

## Impact

- `docs/prd/autokards-mvp.md` — FR-7, FR-8, FR-9, SM-11, SM-12, SM-15, §5.4, §5.5
- `docs/prd/scope-mvp.md` — scope/trade-off notes for deck-name targeting; cross-document coherence: PDF input, preview, and duplicate guidance align with autokards-mvp.md's Won't Have decisions
- `openspec/specs/deck-targeting/spec.md` — new capability spec (delta behavior)
