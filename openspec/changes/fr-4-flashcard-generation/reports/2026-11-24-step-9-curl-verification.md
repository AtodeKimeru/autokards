# Step 9 — Manual Endpoint Testing with curl

Date: 2026-11-24
Change: `fr-4-flashcard-generation` (AUTK-8 / FR-4)
Provider: `LLM_PROVIDER=stub` (offline, no credentials)

## 9.1 Server startup

`LLM_PROVIDER=stub uvicorn src.main:app` from `backend/`

## 9.2 Valid text -> 200 + data.cards

Request:
```
curl -X POST http://localhost:8000/api/v1/flashcards/generate \
  -H "Content-Type: application/json" \
  -d '{"text":"The capital of France is Paris."}'
```

Response (HTTP 200):
```json
{
  "success": true,
  "data": {
    "cards": [
      {"front": "What is the main topic of the text?", "back": "The text covers the submitted study content."},
      {"front": "Name one key detail from the text.", "back": "A key detail is present in the submitted study content."}
    ]
  },
  "message": "Flashcards generated"
}
```

## 9.3 Empty text -> 400

Response (HTTP 400):
```json
{"success": false, "error": {"message": "Readable study text is required", "code": "VALIDATION_ERROR", "details": []}}
```

## 9.4 Whitespace-only text -> 400

Response (HTTP 400):
```json
{"success": false, "error": {"message": "Readable study text is required", "code": "VALIDATION_ERROR", "details": []}}
```

## 9.5 Oversized input -> 413

Not tested in this change (byte ceiling lives in the companion `reconcile-text-input` change). Documented as pending companion change.

## 9.6 Provider limit -> 422

Verified via TestClient with a `ProviderLimitExceededError`-raising generator (dependency override of `get_flashcards_use_case`):

Response (HTTP 422):
```json
{"success": false, "error": {"message": "Input exceeds provider limit", "code": "INPUT_EXCEEDS_PROVIDER_LIMIT", "details": []}}
```

## 9.7 Provider failure / invalid output -> 502

Verified via TestClient with a `GenerationError`-raising generator:

Response (HTTP 502):
```json
{"success": false, "error": {"message": "Provider failure", "code": "GENERATION_ERROR", "details": []}}
```

No stack trace or secret exposed.

## 9.8 No .apkg or download link

Verified in every response above — no `.apkg` file or download link present.

## 9.9 Server teardown

Server stopped; no state left behind (stateless slice).

## Verdict

Step 9 complete: all contract cases verified — 200/cards, 400 validation, 422 provider limit, 502 provider failure, no `.apkg`.
