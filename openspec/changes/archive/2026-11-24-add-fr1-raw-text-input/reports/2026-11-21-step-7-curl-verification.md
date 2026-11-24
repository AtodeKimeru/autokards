# Step 7 Report - Manual Endpoint Testing with curl

- Date: 2026-11-21
- Change: add-fr1-raw-text-input
- Agent: Kiro (opencode)

## Server Setup

Started a local instance with `uvicorn` via a throwaway `run_server.py` (not committed) wiring:
- `max_input_bytes=1024` (infra ceiling for this run)
- A `LimitedProviderPort(limit=200)` test double simulating the provider's own limit

```
nohup .venv/bin/uvicorn --app-dir /tmp/opencode run_server:app --port 8000 ...
```

No persistent datastore exists in this slice; the in-memory store starts empty per process and requires no cleanup/restoration between requests.

## Commands and Responses

### 7.2 — Valid text submission
```
curl -s -i -X POST http://localhost:8000/api/v1/submissions \
  -H "Content-Type: application/json" \
  -d '{"text":"The mitochondria is the powerhouse of the cell."}'
```
Response: `202 Accepted`
```json
{"submission_id":"6611fdf7-a7f2-47d2-8657-bb5873427b56","bytes":47}
```

### 7.3 — Oversized body (2000-byte text, limit 1024 bytes)
```
curl -s -i -X POST http://localhost:8000/api/v1/submissions \
  -H "Content-Type: application/json" -d "$PAYLOAD"   # {"text": "a"*2000}
```
Response: `413 Content Too Large`
```json
{"code":"INPUT_TOO_LARGE","message":"Submitted text exceeds the current infrastructure limit of 1024 bytes (received at least 2012 bytes). Reduce the input size and resubmit.","limit_bytes":1024,"received_bytes":2012}
```
`received_bytes` (2012) reflects the raw streamed JSON body including framing, confirming the streaming reject-before-buffering path is live.

### 7.4 — Empty text
```
curl -s -i -X POST http://localhost:8000/api/v1/submissions \
  -H "Content-Type: application/json" -d '{"text":""}'
```
Response: `400 Bad Request`
```json
{"code":"EMPTY_INPUT","message":"Submitted text must not be empty."}
```

### 7.5 — Provider limit exceeded (250-byte text, provider limit 200 bytes)
```
curl -s -i -X POST http://localhost:8000/api/v1/submissions \
  -H "Content-Type: application/json" -d "$PAYLOAD2"   # {"text": "b"*250}
```
Response: `422 Unprocessable Content`
```json
{"code":"INPUT_EXCEEDS_PROVIDER_LIMIT","message":"The generation provider could not process the complete input and reported it as exceeding its own limit. The provider's stated limit is 200.","provider_limit":200}
```

## Error Case Coverage

- Validation error (empty input): covered by 7.4.
- Infrastructure limit error: covered by 7.3.
- Provider limit error: covered by 7.5.
- No 404/auth cases apply — this endpoint has no path parameters or auth requirement in this slice.

## Cleanup

- Server process stopped with `pkill -f "run_server:app"`.
- Verified stopped: subsequent `curl` to `http://localhost:8000/api/v1/submissions` returned exit code 7 (connection refused).
- No persistent state existed to restore (in-memory store, process-scoped).

## Outcome

- Step 7 status: PASS
- Blocking issues: none
