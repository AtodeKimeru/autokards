# Proposal

## Why

Per AUTK-2 spike findings against Anki Desktop 26.09.4, Anki's importer matches imported decks by **deck name** (including `::` subdeck hierarchies) and **remaps numeric deck IDs on import**. The MVP's current assumption — routing generated cards by an isolated numeric Deck ID (FR-7) — is technically infeasible because an embedded numeric ID does not determine which local deck receives the cards. This change aligns autokards with native Anki import behavior by targeting decks via deck name instead of numeric ID, preserving manual Anki Desktop import and existing review history, while reducing database complexity (no name lookup or collection access required in autokards).

## What Changes

- Replace numeric target Deck ID binding with deck-name binding (including `::` subdeck hierarchy support) in target deck targeting (FR-7, FR-8); update FR-11 wording from Deck ID lookup to deck-name supply.
- Update success measures SM-11 and SM-12 to reflect name-based deck matching and numeric-ID reassignment on import. SM-15 (existing review-history preservation) is unchanged — it does not reference Deck ID.
- Update §5.4 acceptance gate to remove the ID-only feasibility blocker and reference deck-name targeting as the gate condition. §5.5 technical references are unchanged (already reference name-based import mapping and ID remapping).
- Label remaining assumptions and open questions: subdeck creation vs. existing-deck-only, `::` sanitization/naming rules, duplicate handling on import.
- Add `deck-targeting` capability spec capturing name-based deck binding behavior.

## Capabilities

### New Capabilities

- `deck-targeting`: Defines how generated flashcards are bound to a target Anki deck on import — by deck name including `::` subdeck hierarchy, matched by Anki's native importer; numeric deck ID is not the routing contract.

### Modified Capabilities

- (none)

## Gating

This change reverses a previously gated scope decision (numeric Deck ID → deck name) that was pending product-owner approval on AUTK-2. AUTK-2 remains "In Progress" with the acceptance criterion "Present findings to product owner for scope decision" not yet recorded. Until the product owner records the decision on AUTK-2 (comment + status move), the deck-name scope change is gated and must not be treated as approved. This PRD/spec documents the spike finding and labels SM-12 as open pending the §5.2 import test.

## Impact

- `docs/prd/autokards-mvp.md` — FR-7, FR-8, FR-11 wording, SM-11, SM-12, §5.4; SM-15 and §5.5 unchanged (do not reference numeric Deck ID)
- `docs/prd/scope-mvp.md` — scope/trade-off notes for deck-name targeting; cross-document coherence: PDF input, preview, and duplicate guidance align with autokards-mvp.md's Won't Have decisions
- `openspec/changes/deck-name-targeting/specs/deck-targeting/spec.md` — new capability spec (delta behavior)
