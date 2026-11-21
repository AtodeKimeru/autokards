"""Thin FastAPI shell for FR-1 (AUTK-6).

All AC-1/AC-2/AC-3 behavior lives in autokards.input.policy. This module
only adapts HTTP in/out: parsing the request, calling the policy, and
mapping its errors to HTTP responses.
"""
from __future__ import annotations

import json

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from autokards.api.store import SubmissionStore
from autokards.input.policy import (
    EmptyInputError,
    GenerationPort,
    InputTooLargeError,
    ProviderLimitExceededError,
    SubmissionPolicy,
)

DEFAULT_MAX_INPUT_BYTES = 10 * 1024 * 1024  # infra ceiling, not a product rule


def create_app(
    max_input_bytes: int = DEFAULT_MAX_INPUT_BYTES,
    generation_port: GenerationPort | None = None,
) -> FastAPI:
    app = FastAPI()
    policy = SubmissionPolicy(max_input_bytes=max_input_bytes)
    store = SubmissionStore()
    app.state.store = store

    if generation_port is None:
        raise ValueError(
            "generation_port is required: no default provider integration "
            "exists yet (FR-4/FR-7+ will wire the real one)."
        )

    @app.post("/api/v1/submissions", status_code=202)
    async def submit(request: Request):
        # Stream the body and abort as soon as the infra byte ceiling is
        # crossed, so an oversized submission is never fully buffered or
        # stored (AC-2). JSON framing overhead means the raw body can
        # exceed max_input_bytes slightly even for an accepted text field;
        # the policy re-checks the decoded text's own byte length below.
        received_bytes = 0
        chunks: list[bytes] = []
        async for chunk in request.stream():
            received_bytes += len(chunk)
            if received_bytes > max_input_bytes:
                return JSONResponse(
                    status_code=413,
                    content={
                        "code": "INPUT_TOO_LARGE",
                        "message": (
                            "Submitted text exceeds the current infrastructure "
                            f"limit of {max_input_bytes} bytes (received at "
                            f"least {received_bytes} bytes). Reduce the input "
                            "size and resubmit."
                        ),
                        "limit_bytes": max_input_bytes,
                        "received_bytes": received_bytes,
                    },
                )
            chunks.append(chunk)

        try:
            payload = json.loads(b"".join(chunks).decode("utf-8"))
            text = payload["text"]
        except (json.JSONDecodeError, KeyError, UnicodeDecodeError, TypeError):
            return JSONResponse(
                status_code=400,
                content={
                    "code": "INVALID_REQUEST_BODY",
                    "message": "Request body must be JSON with a 'text' field.",
                },
            )

        try:
            accepted = policy.accept(text)
        except EmptyInputError as exc:
            return JSONResponse(
                status_code=400,
                content={"code": exc.code, "message": str(exc)},
            )
        except InputTooLargeError as exc:
            return JSONResponse(
                status_code=413,
                content={
                    "code": exc.code,
                    "message": str(exc),
                    "limit_bytes": exc.limit_bytes,
                    "received_bytes": exc.received_bytes,
                },
            )

        try:
            generation_port.submit(accepted.text)
        except ProviderLimitExceededError as exc:
            return JSONResponse(
                status_code=422,
                content={
                    "code": exc.code,
                    "message": str(exc),
                    "provider_limit": exc.provider_limit,
                },
            )

        record = store.add(text=accepted.text, byte_count=accepted.byte_count)
        return {"submission_id": record.submission_id, "bytes": record.byte_count}

    return app
