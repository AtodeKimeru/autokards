# Step 11 — Manual SM-05/06/07 Quality Validation

Date: 2026-11-24
Change: `fr-4-flashcard-generation` (AUTK-8 / FR-4)
Provider: `LLM_PROVIDER=stub` (offline, no credentials)

## 11.1 Fixture

Text with identifiable facts at the beginning, middle, and end:

> The mitochondria is the powerhouse of the cell, producing ATP through cellular
> respiration. Photosynthesis occurs in chloroplasts, converting light energy into
> chemical energy stored in glucose. The nucleus contains DNA and controls cellular
> activities.

## 11.2 Cards generated (stub)

The deterministic `StubGenerator` returns fixed, input-agnostic cards for offline
verification (no network, no credentials):

| Card | Front | Back |
|------|-------|------|
| 1 | What is the main topic of the text? | The text covers the submitted study content. |
| 2 | Name one key detail from the text. | A key detail is present in the submitted study content. |

## 11.3 Review per card

SM-05 — non-empty Front/Back: **PASS** on both cards.

SM-06 — single retrieval target per Front: **PASS** on both cards (each Front asks exactly one thing).

SM-07 — Back answers Front and is grounded in source text: **STRUCTURAL PASS** on both cards (Backs are non-empty answers); **SEMANTIC NOT VERIFIED** — the stub returns generic, input-agnostic text rather than fixture-specific facts, so grounding against the submitted text cannot be confirmed with the stub.

## 11.4 Pass/fail summary

| Criterion | Card 1 | Card 2 | Overall |
|-----------|--------|--------|---------|
| SM-05 non-empty Front/Back | PASS | PASS | PASS |
| SM-06 single retrieval target | PASS | PASS | PASS |
| SM-07 Back answers + grounded | STRUCTURAL PASS | STRUCTURAL PASS | STRUCTURAL PASS / SEMANTIC PENDING |

## Notes

- The `StubGenerator` is an offline fallback; semantic quality (SM-07 grounding,
  SM-06 single-target precision) depends on the real provider path via
  `OpenAICompatibleGenerator` + prompt engineering, which requires configured
  `LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` credentials not
  present in this environment.
- Real-provider validation is documented as pending and should be executed when
  credentials are available.
- No `.apkg`, no persistence, no frontend — out of scope for this change.
