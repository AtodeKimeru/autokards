# Flashcards API

Implements FR-4 (AUTK-8): generating one or more front/back flashcards from
validated study text.

## `POST /api/v1/flashcards/generate`

Accepts validated study text and returns generated flashcards.

### Request

```json
{ "text": "<raw study text>" }
```

- `text` (string, required): study text containing at least one non-whitespace
  character. Empty or whitespace-only input returns HTTP 400.

### Responses

#### `200 OK` — generation succeeded

```json
{
  "success": true,
  "data": {
    "cards": [
      { "front": "What is the capital of France?", "back": "Paris" }
    ]
  },
  "message": "Flashcards generated"
}
```

- `data.cards` (array): one or more flashcards, each with `front` and `back`
  as separate non-empty string fields. No `.apkg` file or download link is
  included (persistence and packaging are separate capabilities, FR-7/FR-8).

#### `400 Bad Request` — empty or whitespace-only input

```json
{ "success": false, "error": { "message": "Readable study text is required", "code": "VALIDATION_ERROR", "details": [] } }
```

#### `422 Unprocessable Content` — provider cannot process the input

```json
{ "success": false, "error": { "message": "Input exceeds provider limit", "code": "INPUT_EXCEEDS_PROVIDER_LIMIT", "details": [] } }
```

Originates from the generation provider's own limit (not an editorial rule).
No cards are returned; input is never silently truncated.

#### `502 Bad Gateway` — provider failure or invalid output

```json
{ "success": false, "error": { "message": "Provider failure", "code": "GENERATION_ERROR", "details": [] } }
```

Returned when the provider times out, fails, or returns malformed output
(including zero cards or empty Front/Back fields). No internal stack trace or
secret is exposed.

### Errors

All errors use the standard envelope:

```json
{ "success": false, "error": { "message": "<string>", "code": "<string>", "details": [] } }
```

Error codes: `VALIDATION_ERROR` (400), `INPUT_EXCEEDS_PROVIDER_LIMIT` (422),
`GENERATION_ERROR` (502).

## Configuration (environment variables)

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | Provider selector: `stub` for offline/tests, otherwise OpenAI-compatible | `stub` |
| `LLM_BASE_URL` | Base URL of the OpenAI-compatible chat-completions endpoint | `http://localhost:11434/v1` |
| `LLM_API_KEY` | API key for the provider (empty when not required) | `""` |
| `LLM_MODEL` | Model name used for generation | `gpt-4o-mini` |
| `LLM_TIMEOUT_SECONDS` | Request timeout in seconds | `30` |
| `MAX_INPUT_BYTES` | Infrastructure byte ceiling for submitted text | `2000` |

### Backend startup

From `backend/`:

```bash
# Offline / deterministic (no credentials required)
LLM_PROVIDER=stub uvicorn src.main:app

# Real provider (credentials required)
LLM_PROVIDER=openai \
  LLM_BASE_URL=https://api.openai.com/v1 \
  LLM_API_KEY=<key> \
  LLM_MODEL=gpt-4o-mini \
  uvicorn src.main:app
```

## Non-goals (this slice)

- Persistence, `.apkg` generation, deck targeting (FR-7/FR-8).
- Pre-export preview, in-app editing (FR-5/FR-6).
- Frontend.
