# autokards — MVP Product Requirements

> **Document:** Sections 4–5 of the autokards MVP PRD  
> **Related source:** `scope-mvp.md` (Sections 1–3; baseline dated 2026-11-21)  
> **Anki validation target:** Anki Desktop 26.09.4  
> **Status:** Requirements drafted; target deck binding uses deck name (including `::` subdeck hierarchy) per AUTK-2 spike findings. Numeric Deck ID is not the routing contract — Anki matches decks by name and remaps IDs on import.

This file contains only Sections 4 and 5. Read it together with `scope-mvp.md` for the product framing, target users, goals, and non-goals.

## Scope clarifications and amendments

The following decisions were made during PRD finalization. They refine or supersede corresponding statements in the 2026-11-21 `scope-mvp.md`. To keep the project documentation internally consistent, update that source file to reflect these decisions before treating the combined documents as the final locked baseline.

| Area | PRD decision | Effect on the earlier scope text |
|---|---|---|
| Input | MVP accepts raw text pasted or entered directly. | PDF file upload and in-product PDF extraction are excluded from MVP. The earlier text-and-PDF requirement is narrowed to text only. |
| PDF-derived material | A user may extract text from a PDF using another tool and then paste the resulting text into autokards. | This is not PDF support by autokards. OCR, PDF parsing, and PDF upload are deferred. |
| Input limits | No arbitrary product-defined maximum length is introduced. Real infrastructure and model-provider limits may still exist. | “Unbounded” does not mean infinite technical capacity. The product must never silently truncate accepted input. |
| Card quality | Minimum quality means one clear retrieval target on the Front, an answer that addresses it on the Back, and factual claims grounded in the submitted text. | No arbitrary character limit, fixed card count, or comprehensive-coverage guarantee is introduced. |
| Preview | No pre-export card preview in MVP. | Earlier Should Have item moves to the post-MVP backlog. |
| Import/duplicate guidance | No formal import-and-duplicate guidance feature in MVP. | Earlier Should Have item moves to the backlog. No custom or semantic duplicate detection is promised. |
| Anki version | Anki Desktop 26.09.4 is the initial validation target. | Compatibility with other versions is not implied. |

The MVP remains export-only: users manually import the generated `.apkg` into Anki Desktop. No account, Anki connection, automatic synchronization, live collection mutation, or mobile import flow is introduced by these requirements.

---

## 4. Product-Level Functional Requirements (`FR-X`)

The requirements below specify observable product behavior. “Must Have” requirements are release requirements unless explicitly identified as blocked by a technical dependency. A technical dependency is not considered satisfied merely because it is written into the package.

### Epic 1 — Raw Text Ingestion

#### FR-1 — Raw Text Input Submission

**Priority:** Must Have

The product must allow the user to enter or paste raw study text directly into autokards for flashcard generation.

- The MVP must not impose an arbitrary fixed character or word limit as a product rule.
- The product may be subject to finite infrastructure, processing, and AI-provider limits.
- If the complete submitted input cannot be processed, the product must report the failure explicitly. It must not silently truncate the input and present the result as complete.
- The product must not claim unlimited or infinite processing capacity.

#### FR-2 — PDF Upload and Extraction

**Priority:** Won't Have — explicitly out of scope

The MVP does not accept PDF files and does not extract text from PDFs, whether digital or scanned. A user who wants to use PDF-derived material must extract the text with a separate tool and paste that text into autokards.

OCR, PDF parsing, page/section extraction, and handling of PDF tables, mathematics, code, or diagrams are deferred capabilities. Their future inclusion is not implied by this PRD.

#### FR-3 — Empty Input Handling

**Priority:** Must Have

When the submitted text is empty or contains only whitespace, the product must stop the generation flow and inform the user that readable study text is required. It must not produce or offer an `.apkg` file for that submission.

### Epic 2 — Flashcard Content Generation

#### FR-4 — Front/Back Flashcard Generation

**Priority:** Must Have

For processable input text, the product must generate one or more flashcards, each represented by a Front and a Back.

Minimum card-level requirements:

1. **Front:** contains one identifiable question, prompt, or concept to retrieve. It must not combine multiple independent questions or retrieval targets into one card.
2. **Back:** is non-empty and answers the prompt on the Front.
3. **Source grounding:** factual claims on the Back must be supported by the submitted text. The Back must not introduce unsupported factual claims.
4. **Field separation:** the question/prompt and answer must occupy separate Front and Back fields.

These criteria define the minimum acceptance standard; they do not guarantee that every important concept in the source will be covered. “Concise”, “high quality”, and “comprehensive” are not independent acceptance requirements unless separately defined and approved.

The MVP is limited to a basic front/back card layout. Cloze deletions, image occlusion, audio, images, custom templates, and multi-field card schemas remain out of scope.

#### FR-5 — Pre-Export Card Preview

**Priority:** Won't Have — post-MVP backlog

The MVP does not need to display generated cards in a preview or review interface before export. The `.apkg` download is the output of the generation flow.

#### FR-6 — In-App Card Editing

**Priority:** Won't Have

The MVP does not provide in-app editing, deletion, or reordering of generated cards before export.

### Epic 3 — Anki Package Generation and Target Deck Binding

#### FR-7 — Target Deck Binding by Name

**Priority:** Must Have

The product must accept a user-provided target deck name (including `::` subdeck hierarchy, e.g. `Spanish::Verbs`) and the intended behavior is that all imported generated cards are added to the deck matching that name in the Anki collection into which the user imports the package.

- Target deck binding is by **deck name**, not by a standalone numeric Deck ID. The user provides the deck name; autokards does not perform deck-name lookup or connect to the user's Anki collection.
- Anki's native importer matches imported decks by name (including `::` subdeck hierarchy) and remaps the imported package's numeric deck ID to the local deck's ID during import. The numeric ID embedded in the package is not, by itself, the routing contract.
- The package binds cards to the local deck whose name matches the target deck name (including `::` subdeck hierarchy) per Anki's native import behavior. When a same-name, same-kind deck exists, Anki maps the imported deck to that local deck. If no matching deck exists, Anki's native import behavior creates the deck (including intermediate `::` subdecks) on import. If a same-named deck of a different kind exists, Anki may rename the imported deck to avoid a conflicting deck kind.
- autokards performs boundary validation/sanitization on the deck name (e.g., rejecting empty `::` segments, stripping whitespace) and then writes the name into the `.apkg`; Anki resolves it on import.

**Rationale:** AUTK-2 spike findings against Anki Desktop 26.09.4 confirmed that ID-only routing is technically infeasible: Anki matches decks by name and reassigns numeric IDs on import. Deck-name targeting aligns with native Anki import behavior, avoids collection access, and reduces database complexity. See the technical references at the end of this document.

**Assumptions and open questions (labeled):**
- Subdeck creation vs. existing-deck-only: autokards relies on Anki's native behavior — missing `::` subdecks may be created on import; autokards does not verify deck existence.
- `::` sanitization rules: exact disallowed characters beyond empty segments and leading/trailing whitespace are to be finalized at implementation.
- Duplicate handling on import: relies on Anki's default note-type update rules; autokards specifies no duplicate-handling behavior.

#### FR-8 — Valid `.apkg` Package Generation

**Priority:** Must Have

The product must generate a valid Anki deck package (`.apkg`) from the generated Front/Back card data represented in a Python data structure.

The package must:

- be accepted through the standard Anki Desktop import workflow in the target version;
- bind the generated cards to the target deck by name (including `::` subdeck hierarchy) per FR-7;
- contain the generated Front/Back notes and their corresponding basic cards;
- render the Front as the question/prompt side and the Back as the answer side; and
- contain no unintended card types or rich-media fields outside the MVP schema.

A file merely having an `.apkg` extension is not sufficient evidence of package validity.

#### FR-9 — Preservation of Existing Review Progress

**Priority:** Must Have

After the user manually imports the generated package into the intended existing deck, all pre-existing cards in that target deck must remain present and retain their pre-import review and scheduling state.

For this PRD, “historical review progress” includes, at minimum:

- recorded review-history entries;
- due date / due state;
- interval;
- review count;
- lapse count; and
- scheduling state (including new, learning, review, or relearning state, as applicable).

The generated package must not carry review history or scheduling information for the newly generated cards. New cards must enter Anki as new cards, not with inherited review history or intervals.

This requirement protects pre-existing cards; it does not promise custom duplicate detection, semantic card matching, card merging, or automatic reconciliation of independently regenerated content.

#### FR-10 — `.apkg` Download

**Priority:** Must Have

Once generation succeeds, the product must make the resulting `.apkg` file available for the user to download locally.

The requirement does not define a download-speed or generation-time service level. The product must not present a download link when generation has failed or no valid package has been produced.

### Epic 4 — Deferred Import Guidance and Duplicate Handling

#### FR-11 — Import and Duplicate Guidance

**Priority:** Won't Have — post-MVP backlog

The MVP does not require a dedicated guidance feature explaining how to supply a target deck name (including `::` subdeck hierarchy), how to import packages, or how Anki handles duplicates.

The MVP does not implement custom duplicate detection or card-merge logic. It must not claim that semantically equivalent cards will be detected, merged, or prevented from appearing more than once. Anki's documented handling of notes previously imported from a package must not be generalized into a promise of semantic deduplication.

---

## 5. Success Metrics & Validation

### 5.1 Purpose and terminology

This section defines binary, verifiable MVP success measures. The identifiers use `SM-X` (`SM` = **Success Measure**). In this document, an SM is a pass/fail validation outcome, not a business KPI such as conversion rate, retention, or user satisfaction.

The MVP is successful only when the complete workflow is demonstrated: raw text submission → Front/Back generation → valid `.apkg` generation → manual import into the intended existing deck → preservation of pre-existing review progress.

A successful file-generation step alone does not prove that the MVP works.

### 5.2 Validation environment

The initial validation target is **Anki Desktop 26.09.4**. Record the operating system and exact Anki version used in the test report. Passing on this version does not establish compatibility with other Anki versions.

Use an isolated Anki test profile containing:

- an existing intended target deck with a known deck name (including `::` subdeck hierarchy);
- pre-existing cards in that target deck with recorded review history and non-default scheduling states;
- at least one unrelated control deck with existing cards; and
- a baseline record of the target and control decks before import.

The generated test package must contain new test notes that do not intentionally match the pre-existing test notes. This isolates the preservation test from duplicate/update behavior, which is not an MVP feature.

Before importing, record the target deck name/path, the existing card/note identities, scheduling values, and review-history records needed for comparison. After import, compare the same records. Do not infer preservation solely from the fact that the target deck remains visible.

### 5.3 Success measures

| ID | Area | Pass condition | Validation method |
|---|---|---|---|
| **SM-01** | Raw text submission | The user can submit non-empty raw text and the generation flow receives it. | Submit a text fixture and confirm the flow proceeds to generation. |
| **SM-02** | Input integrity | Input is either processed in full or rejected with an explicit error. No accepted submission is silently truncated. No arbitrary product-defined fixed length cap is applied. | Test fixtures with identifiable content at the beginning, middle, and end; verify full input reaches the generation step or the request fails explicitly. Inspect the user-visible result for silent partial-success behavior. |
| **SM-03** | Empty input | Empty or whitespace-only input produces an explicit validation message and no `.apkg` download. | Submit empty text and whitespace-only text. |
| **SM-04** | Text-only boundary | The MVP does not accept or process PDF files. Text extracted elsewhere from a PDF can be pasted and processed as raw text. | Verify that no PDF upload/extraction flow is included; paste extracted text and submit it through the raw-text path. |
| **SM-05** | Structured card data | Each generated record contains a non-empty Front and a non-empty Back. | Inspect every record in the generated Python data structure for the validation fixture. |
| **SM-06** | Front validity | Every Front presents exactly one identifiable retrieval target; a card with multiple independent questions or prompts fails. | Review every generated card against the stated Front rule. Record each failure; do not use a subjective “looks good” rating. |
| **SM-07** | Back validity and grounding | Every Back answers its Front, and every factual claim on the Back is supported by the submitted source text. | Review every card against the source. A non-answer or unsupported factual claim is a failure. |
| **SM-08** | Data-to-package integrity | The package contains all generated card records; no record is silently omitted. For the basic one-card-per-note layout, the imported card count matches the generated record count. | Compare generated record count, packaged note/card count, and imported card count in a clean test collection. |
| **SM-09** | Package validity | Anki Desktop 26.09.4 accepts the generated `.apkg` through its standard import workflow without a corrupt/unsupported-package error. | Import the package into the isolated Anki test profile. |
| **SM-10** | Front/Back rendering | Each imported card displays the generated Front on the question side and the corresponding Back on the answer side, using the basic front/back layout. | Open every imported test card in Anki Desktop and inspect both sides. |
| **SM-11** | Deck-name input | The product accepts a non-empty target deck name (including `::` subdeck hierarchy) and rejects empty names and names with invalid `::` segments. | Submit valid and invalid deck-name test values. |
| **SM-12** | Existing target-deck routing | With only the target deck name supplied (including `::` subdeck hierarchy), every imported card appears in the deck matching that name; no other deck receives the cards. If no matching deck exists, Anki's native import behavior creates the deck (including intermediate `::` subdecks) on import. If a same-named deck of a different kind exists, Anki may rename the imported deck to avoid a conflicting deck kind. | Import into the controlled profile; verify the resulting local deck name/path and card membership against the supplied `::`-qualified deck name. |
| **SM-13** | Target isolation | The unrelated control deck and its cards remain present and unchanged; no generated cards are placed there. | Compare target and control deck card membership before and after import. |
| **SM-14** | No scheduling payload for new cards | The generated package does not include review-history entries or inherited scheduling values for its newly generated cards. | Inspect the package/import result and verify new generated cards enter as new cards without imported review history or inherited intervals. |
| **SM-15** | Existing review-history preservation | Every pre-existing target-deck card remains present and retains its pre-import review-history records and scheduling state. | Compare pre-import and post-import records for existing cards, including review history, due state/date, interval, review count, lapse count, and queue/state. Any unexplained change is a failure. |
| **SM-16** | Download availability | After successful generation, the user can download the generated `.apkg`; when generation fails, no download is offered. | Complete one successful generation and one failing generation; verify the corresponding download behavior. |

### 5.4 Overall MVP acceptance gate

The MVP passes technical validation only when **all Must Have requirements and all applicable Success Measures pass**, including SM-12, SM-13, and SM-15.

SM-12 is supported by a source-level finding from the AUTK-2 spike: Anki 26.09.4 matches an imported deck to an existing local deck by name (including `::` subdeck hierarchy) and remaps the imported numeric ID to the local deck ID during import (see technical references). SM-12 **remains open pending the §5.2 import test**; a GUI reproduction in Anki Desktop 26.09.4 is required before the MVP can be declared fully accepted against deck-name targeting. Until the product owner approves the deck-name scope decision on AUTK-2 (currently In Progress), this scope change is gated and must not be treated as approved.

Any decision to add deck-name lookup, collection access, AnkiConnect, an add-on, or another integration beyond name-based targeting is a scope change. It must be approved and reflected in `scope-mvp.md` before implementation proceeds on that alternative.

### 5.5 What this section does not claim

The MVP acceptance gate does not establish:

- unlimited input capacity beyond actual infrastructure or model-provider limits;
- complete coverage of every important concept in a source;
- a fixed number of cards per page, paragraph, or source;
- a numeric or user-research-backed card-quality score;
- semantic duplicate detection across separate generations;
- compatibility with Anki versions other than 26.09.4; or
- generation-time, latency, conversion, adoption, or retention targets.

No benchmark values or user-research results are invented in this PRD.

---

## Technical references

These references support the Anki-specific constraints recorded above. They do not replace the required integration test.

1. [Anki Desktop downloads](https://apps.ankiweb.net/) — lists 26.09.4 as the current Desktop version at the time of this PRD review.
2. [Anki Manual — Packaged Decks](https://github.com/ankitects/anki/blob/26.09.4/docs-site/manual/importing/packaged-decks.mdx) — describes `.apkg` contents and package-import options.
3. [Anki 26.09.4 source — APKG deck import mapping](https://github.com/ankitects/anki/blob/26.09.4/rslib/src/import_export/package/apkg/import/decks.rs#L57-L67) — shows that the importer looks up an existing deck by name, updates a same-kind match, or adds a deck when no match exists. [Name lookup](https://github.com/ankitects/anki/blob/26.09.4/rslib/src/import_export/package/apkg/import/decks.rs#L103-L107) and [ID remapping](https://github.com/ankitects/anki/blob/26.09.4/rslib/src/import_export/package/apkg/import/decks.rs#L115-L133) are also explicit in the version-pinned source.
4. [Anki 26.09.4 source — APKG card import](https://github.com/ankitects/anki/blob/26.09.4/rslib/src/import_export/package/apkg/import/cards.rs#L145-L151) — shows imported cards receiving the locally remapped deck ID.
5. [Anki FAQ — note type changes and package updates](https://github.com/ankitects/anki/blob/26.09.4/docs-site/faqs/some-updates-were-ignored-because-the-note-type-has-changed.mdx) — explains conditions that affect updates of previously imported notes.
