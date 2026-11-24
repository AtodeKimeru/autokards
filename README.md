# autokards
Create custom flashcards for Anki from any text or PDF — skip the setup and start studying now.

## Backend

The backend is a FastAPI service under `backend/` implementing:

- **FR-3**: empty/whitespace-only input validation (HTTP 400).
- **FR-4**: front/back flashcard generation from validated study text (HTTP 200 with `data.cards`).

### Startup

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

### Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | Provider selector: `stub` or any OpenAI-compatible provider | `stub` |
| `LLM_BASE_URL` | Base URL of the OpenAI-compatible chat-completions endpoint | `http://localhost:11434/v1` |
| `LLM_API_KEY` | API key for the provider | `""` |
| `LLM_MODEL` | Model name used for generation | `gpt-4o-mini` |
| `LLM_TIMEOUT_SECONDS` | Request timeout in seconds | `30` |
| `MAX_INPUT_BYTES` | Infrastructure byte ceiling for submitted text | `2000` |

### API contract

`POST /api/v1/flashcards/generate`

- `200` with `{ success, data: { cards: [{ front, back }] }, message }`
- `400` for empty/whitespace-only input
- `422` when the provider cannot process the input (provider limit)
- `502` on provider failure or invalid output

No `.apkg` file or download link is included in this slice (packaging is FR-8, a separate change).

### Testing

```bash
cd backend
uv run pytest --cov=src
uv run ruff check .
uv run mypy src
```
