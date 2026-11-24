# Tasks

## 0. Setup: Create Feature Branch (MANDATORY - FIRST STEP)

- [x] 0.1 Create feature branch `AUTK-2-deck-name-targeting` via isolated worktree at `.worktrees/AUTK-2-deck-name-targeting`
- [x] 0.2 Verify branch creation and clean working tree status

## 1. PRD Docs: autokards-mvp.md — FR-7 deck-name binding

- [x] 1.1 Replace FR-7 "Numeric Target Deck ID" with deck-name binding (deck name including `::` subdeck hierarchy) and remove ID-only feasibility blocker language
- [x] 1.2 Update FR-8 to reflect the deck name (not numeric ID) bound into the `.apkg` for manual import
- [x] 1.3 Update FR-9 to confirm existing review history is preserved under name-targeted import

## 2. PRD Docs: autokards-mvp.md — Success measures SM-11, SM-12, SM-15

- [x] 2.1 Update SM-11 from numeric Deck ID input to deck-name input validation
- [x] 2.2 Update SM-12 from ID-only routing to name-based routing (remove SOURCE-LEVEL FAIL for ID-only assumption)
- [x] 2.3 Confirm SM-15 review-history preservation holds under name-targeted import

## 3. PRD Docs: autokards-mvp.md — §5.4 acceptance gate, §5.5 technical references

- [x] 3.1 Update §5.4 to remove ID-only feasibility blocker and reference deck-name targeting as the gate condition
- [x] 3.2 Update §5.5 technical references to reflect name-based import mapping and ID remapping on import

## 4. PRD Docs: scope-mvp.md — scope/trade-off notes

- [x] 4.1 Replace "targeting an existing numeric Deck ID" with deck-name targeting including `::` subdeck hierarchy
- [x] 4.2 Update duplicate-handling guidance note to reflect reliance on Anki's default import behavior

## 5. Label assumptions and open questions

- [x] 5.1 Label subdeck creation vs existing-deck-only decision (Anki auto-creates missing `::` subdecks on import)
- [x] 5.2 Label `::` sanitization/naming rules decision (boundary validation, pass-through verbatim)
- [x] 5.3 Label duplicate handling decision (Anki's default note-type update rules)

## 6. Update Technical Documentation (MANDATORY)

- [x] 6.1 Verify PRD edits are consistent between autokards-mvp.md and scope-mvp.md
- [x] 6.2 Verify no remaining numeric Deck ID references conflict with deck-name targeting in `docs/prd/` (backend-standards.md numeric Deck ID examples are out of scope for this docs-only change; tracked as a follow-up card)

## Workflow follow-up

- Run `openspec validate --changes deck-name-targeting --strict` to confirm artifact coherence
- Present the PRD diff to the user for review
- Archive the change once review requirements are satisfied

---

**Note on mandatory testing steps:** This change is documentation-only (PRD docs + OpenSpec planning artifacts). There is no implementation code, no API endpoints, and no database, so the unit-test, curl endpoint, E2E Playwright, and database-state steps from `openspec-tasks-mandatory-steps.md` are not applicable. The branch (Step 0) and documentation-update (Step 6) mandatory steps apply and are tracked above.
