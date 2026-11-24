# Step 9 — Manual Endpoint Testing with curl

Date: 2026-11-24
Change: `fr-4-flashcard-generation` (AUTK-8 / FR-4)
Provider: `LLM_PROVIDER=stub` (offline, no credentials)

## 9.1 Server startup

`LLM_PROVIDER=stub uvicorn src.main:app --port 8001` from `backend/`

## 9.2 Valid text -> 200 + data.cards

Request:
```
curl -X POST http://localhost:8001/api/v1/flashcards/generate \
  -H "Content-Type: application/json" \
  -d '{"text":"The capital of France is Paris."}'
```

Response (HTTP 200):
```json
{
    "success": true,
    "data": {
        "cards": [
            {
                "front": "What is the main topic of the text?",
                "back": "The text covers the submitted study content."
            },
            {
                "front": "Name one key detail from the text.",
                "back": "A key detail is present in the submitted study content."
            }
        ]
    },
    "message": "Flashcards generated"
}
```

## 9.3 Empty text -> 400

Request:
```
curl -X POST http://localhost:8001/api/v1/flashcards/generate \
  -H "Content-Type: application/json" \
  -d '{"text":""}'
```

Response (HTTP 400):
```json
{
    "success": false,
    "error": {
        "message": "Readable study text is required",
        "code": "VALIDATION_ERROR",
        "details": []
    }
}
```

## 9.4 Whitespace-only text -> 400

Request:
```
curl -X POST http://localhost:8001/api/v1/flashcards/generate \
  -H "Content-Type: application/json" \
  -d '{"text":"   \t\n  "}'
```

Response (HTTP 400):
```json
{
    "success": false,
    "error": {
        "message": "Readable study text is required",
        "code": "VALIDATION_ERROR",
        "details": []
    }
}
```

## 9.5 Oversized input -> 413

Tested with 11 MiB of text (exceeding the 10 MiB limit). Request:
```
curl -X POST http://localhost:8001/api/v1/flashcards/generate \
  -H "Content-Type: application/json" \
  --data-binary @<(python3 -c "import json; print(json.dumps({'text': 'x' * (11 * 1024 * 1024)}))")
```

Response (HTTP 413):
```json
{
    "success": false,
    "error": {
        "message": "Input exceeds byte limit",
        "code": "INPUT_TOO_LARGE",
        "details": [
            {
                "limit_bytes": 10485760,
                "received_bytes": 11534336
            }
        ]
    }
}
```

## 9.6 Text at byte ceiling -> 200

Tested with text exactly at 10 MiB limit:
```
curl -X POST http://localhost:8001/api/v1/flashcards/generate \
  -H "Content-Type: application/json" \
  --data-binary @<(python3 -c "import json; print(json.dumps({'text': 'x' * 10485760}))")
```

Response (HTTP 200) with generated flashcards.

## 9.7 Missing field -> 422 INVALID_REQUEST

Request:
```
curl -X POST http://localhost:8001/api/v1/flashcards/generate \
  -H "Content-Type: application/json" \
  -d '{}'
```

Response (HTTP 422):
```json
{
    "success": false,
    "error": {
        "message": "Request validation failed",
        "code": "INVALID_REQUEST",
        "details": []
    }
}
```

## 9.8 Provider limit -> 422 INPUT_EXCEEDS_PROVIDER_LIMIT

Verified via integration test with a generator that raises `ProviderLimitExceededError`:

Response (HTTP 422):
```json
{
    "success": false,
    "error": {
        "message": "Input exceeds provider limit",
        "code": "INPUT_EXCEEDS_PROVIDER_LIMIT",
        "details": []
    }
}
```

## 9.9 Provider failure -> 502 GENERATION_ERROR

Verified via integration test with a generator that raises `GenerationError`:

Response (HTTP 502):
```json
{
    "success": false,
    "error": {
        "message": "Provider failure",
        "code": "GENERATION_ERROR",
        "details": []
    }
}
```

No stack trace or secret exposed.

## 9.10 No .apkg or download link

Verified in every response - no `.apkg` file or download link present in any response.

## 9.11 Server teardown

Server stopped via `pkill -f "uvicorn src.main:app"`; no state left behind (stateless slice).

## Verdict

Step 9 complete: all contract cases verified — 200/cards, 400 validation, 413 input too large, 422 invalid request/provider limit, 502 generation error, no `.apkg`.