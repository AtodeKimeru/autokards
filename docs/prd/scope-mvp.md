# autokards — MVP Scope
> Agreed scope, locked on 2026-11-21. This is the baseline on which the PRD will be written.
> Supersedes any prior version discussed in conversation. If something is not here, it is not agreed.

---

## 1. Problem Framing

### Core User Pain Point
Time-constrained learners—specifically university students working full-time—have minimal off-work hours to convert dense study materials (text and PDFs) into structured flashcards before starting spaced-repetition review. Manual authoring delays study sessions and drains limited energy, while importing new material into an existing deck carries the risk of disrupting historical review progress or creating messy duplicates.

### Current Workarounds & Limitations
* **Manual Card Authoring in Desktop Flashcard Software:** Copying and pasting excerpts into front/back fields one card at a time. *Limitation:* High time cost and fatigue on long texts or PDFs, delaying study sessions.
* **Spreadsheets, CSVs, or Plain-Text Imports:** Drafting Q&A pairs manually and importing files. *Limitation:* Extra formatting/mapping steps, poor handling of dense PDF text, and risk of import errors or misrouted cards.
* **Ad-Hoc Chat or Note-Taking Apps:** Generating questions in separate tools without a direct deck output. *Limitation:* Forces manual transfer, cleanup, and import into the target deck.
* **Passive Re-Reading or Memory:** Reviewing highlights or skipping card creation when time runs out. *Limitation:* Lower retention efficiency than consistent spaced repetition.

---

## 2. Target Users & Current State

### Primary Target Users
* **University Students Working Full-Time (Desktop Users):** Degree students balancing full-time employment who rely on Anki Desktop for spaced repetition, face severe time scarcity, and need to append new front/back cards to an existing deck without losing prior review history.
* **Concise-Workflow Learners *(Assumption)*:** Users who want to submit source content in a streamlined flow, receive a ready-to-import deck file, and bring it into Anki Desktop via standard import with minimal setup.

### Current State (Without This Product)
* Users spend scarce non-work hours manually authoring front/back cards, staging drafts in notes/spreadsheets, or falling back to passive reading when prep time runs out.
* New cards are added via manual entry or standard desktop file imports, relying on Anki Desktop's default import behavior to merge cards while preserving historical review intervals.

### Explicit Non-Target Users (MVP Scope)
* **Mobile-Only Learners:** Users who study exclusively on mobile devices without access to Anki Desktop for manual deck file import.
* **Users Expecting Automated Sync or In-Place Deck Editing:** Users seeking automatic cloud/AnkiWeb synchronization, continuous background updates, or direct modification of existing deck cards without manual import.
* **Users Requiring Complex Card Types or Rich Media *(Assumption)*:** Learners relying on cloze deletions, audio, image occlusion, custom templates, or multi-field schemas beyond clean front/back cards.
* **Non-Anki Learners:** Users studying in flashcard platforms outside Anki.

### Overlooked Segments & Edge Cases
* **Overworked Students Abandoning Prep or Review:** High-burnout full-time workers who drop off if generated cards feel bloated, inaccurate, or require heavy editing before studying. *(Deferred to post-MVP versions.)*
* **Duplicate & Target-Deck Edge Cases:** Relying on Anki's default import behavior can produce duplicates or misdirected cards if users re-submit overlapping source material or supply an unintended target deck name. *(Addressed in MVP via careful Anki import alignment and a concise guidance note.)*
* **Complex or Non-Standard PDFs *(Assumption)*:** Scanned PDFs, multi-column layouts, tables, dense math/code, or diagrams may extract poorly and yield low-utility cards. *(Explicitly out of scope for MVP.)*
* **Full-Time Professionals / Certification Studiers:** Non-university full-time workers share the same time scarcity and desktop review habits; excluded as primary persona but acceptable as secondary testers during MVP validation.

---

## 3. MVP Scope, Out-of-Scope & MoSCoW Prioritization

Aligned with **Sections 1–2**, this release is an **export-only Anki Desktop MVP**: users submit text input, receive a valid `.apkg` generated via a Python data structure with a clean front/back layout targeting an existing deck by name (including `::` subdeck hierarchy), and import it manually into Anki Desktop without breaking historical review progress *(structured with SOLID principles and hexagonal architecture in mind for future scale)*[cite: 1]. PDF upload/extraction is deferred to post-MVP.

### IN SCOPE (Must Have + Should Have)
* **[Must Have] Text Input to Front/Back Cards:** Accept raw text study material (unbounded input length for MVP) and generate concise front/back flashcard content *(assumption: text input is the primary baseline; PDF extraction is deferred to post-MVP)*[cite: 1].
* **[Must Have] Valid `.apkg` Generation Targeting a Deck by Name:** Produce a valid `.apkg` via a Python data structure using a clean front/back card layout bound to a user-provided target deck name (including `::` subdeck hierarchy), aligned cleanly with Anki's name-based import mechanics[cite: 1].
* **[Must Have] Safe Manual Anki Desktop Import:** Support standard manual import into Anki Desktop to add new cards to the target deck without breaking historical review progress[cite: 1].
* **[Should Have] Concise Import & Duplicate Guidance Note:** Provide brief instructions on deck-name (`::` hierarchy) usage and a note that duplicate handling relies on Anki's default import behavior *(assumption: sufficient for MVP without custom deduplication logic)*[cite: 1].

### OUT SCOPE (Could Have + Won't Have)
* **[Won't Have] Quick Pre-Import Card Preview:** Pre-export card preview moves to the post-MVP backlog; the `.apkg` download is the output of the generation flow[cite: 1].
* **[Could Have — Scope-Creep Pushback] Granular Prompt, Difficulty, or Card-Count Controls:** *Pushback:* Adds extra knobs and tuning overhead that conflict with "skip the setup and start studying now" for time-pressed working students. Excluded from MVP unless trivial and risk-free[cite: 1].
* **[Could Have — Scope-Creep Pushback] Source Page or Section Citations on Card Back:** *Pushback:* Adds PDF parsing/layout complexity and risks cluttering clean front/back cards for limited MVP value. Excluded from MVP unless trivial[cite: 1].
* **[Won't Have] Complex or Non-Standard PDF Handling (Scanned/Image-Heavy PDFs, Tables, Math/Code, Diagrams):** Excluded from MVP to keep initial scope focused and achievable *(assumption: future extensibility is supported cleanly via hexagonal architecture without bloating MVP)*[cite: 1].
* **[Won't Have] Card-Quality / Low-Edit Polish Beyond Baseline Front/Back Generation:** Deep fixes for bloated or inaccurate cards that cause burnout/drop-off are deferred to post-MVP iterations[cite: 1].
* **[Won't Have] Custom Deduplication or Card-Merge Logic:** Excluded for MVP; relies on Anki's default import behavior accompanied by a brief guidance note[cite: 1].
* **[Won't Have] Automated Cloud / AnkiWeb Sync or Live Deck Mutations:** Excluded because the MVP is export-only via manual Anki Desktop import; syncing or editing decks in place adds state, auth, and data-loss risks out of scope for MVP[cite: 1].
* **[Won't Have] Mobile App or Mobile-Only Import Flow:** Excluded because manual import targets Anki Desktop and mobile adds separate platform and UX overhead[cite: 1].
* **[Won't Have] Specialized Card Types & Rich Media (Cloze, Audio, Image Occlusion, Custom Templates):** Excluded to keep the card schema to a single clean front/back layout and avoid media/template complexity[cite: 1].
* **[Won't Have] User Accounts, Billing, or Multi-User/Team Features:** Excluded as premature before validating core text-to-`.apkg` value for university students working full-time[cite: 1].