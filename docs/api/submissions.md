# Submissions API

Implements FR-1 (AUTK-6): accepting raw study text for flashcard generation with no product-defined length limit, and explicit failure reporting instead of silent truncation.

## `POST /api/v1/submissions`

Accepts raw text and forwards the complete, unmodified text toward flashcard generation.

### Request

```json
{ "text": "<raw study text>" }
```

### Responses

#### `202 Accepted` — text accepted

```json
{ "submission_id": "<uuid>", "bytes": 47 }
```

The generation flow receives the complete text, byte-for-byte identical to what was submitted (AC-1).

#### `400 Bad Request` — empty input

```json
{ "code": "EMPTY_INPUT", "message": "Submitted text must not be empty." }
```

This is a minimal non-empty guard only. Full empty/whitespace-only validation and its user-facing UX are owned by a separate capability (AUTK-7 / FR-3).

#### `413 Content Too Large` — infrastructure byte limit exceeded

```json
{
  "code": "INPUT_TOO_LARGE",
  "message": "Submitted text exceeds the current infrastructure limit of 1024 bytes (received at least 2012 bytes). Reduce the input size and resubmit.",
  "limit_bytes": 1024,
  "received_bytes": 2012
}
```

**The limit is measured in bytes of the raw HTTP request body, not characters.** This is deliberate: AC-3 (FR-1) forbids any product-defined character/word limit. The byte ceiling represents a real infrastructure constraint (`max_input_bytes`, configurable via the `create_app(max_input_bytes=...)` parameter), not an editorial rule. Because the check runs on the streamed request body before JSON parsing, `received_bytes` reflects raw wire bytes including JSON framing overhead — it can be slightly larger than the decoded `text` field's own byte length. Rejection happens while streaming, before the body is ever fully buffered, so an oversized submission is never partially stored (AC-2).

#### `422 Unprocessable Content` — provider cannot process the input

```json
{
  "code": "INPUT_EXCEEDS_PROVIDER_LIMIT",
  "message": "The generation provider could not process the complete input and reported it as exceeding its own limit. The provider's stated limit is 200.",
  "provider_limit": 200
}
```

This is a distinct failure from `413`: it originates from the generation provider's own constraint (via the `GenerationPort` interface), not from our infrastructure. The system never truncates input or returns a partial generation result in this case (AC-2). In this slice, no real provider is wired; a test double is used until FR-4/FR-7+ integrate the actual model/provider.

### No unlimited-capacity claims

No response or user-facing message states or implies that input size is unlimited or infinite, consistent with FR-1's requirement notes.

### Known limitations of this slice

- Submissions are held in an in-memory store; a process restart loses all data. No durability requirement exists yet for this capability.
- No real generation provider is integrated; `GenerationPort` is satisfied by a fake implementation.
- This endpoint is implemented in Python/FastAPI as a reversible choice for this slice only. It does not supersede `docs/backend-standards.md`'s Node/TS prescription; the durable stack decision is tracked as a separate follow-up.
