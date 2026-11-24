"""Centralized exception handlers for the presentation layer.

Maps domain exceptions to standardized HTTP error responses so internal
stack traces are never leaked to clients (per API design standards).
"""

from typing import Awaitable, Callable, cast

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError as FastAPIRequestValidationError
from fastapi.responses import JSONResponse
from starlette.responses import Response

from src.domain.exceptions import (
    GenerationError,
    InputTooLargeError,
    ProviderLimitExceededError,
    ValidationError,
)


def _error_envelope(
    message: str,
    code: str,
    status_code: int,
    details: list[dict[str, int]] | None = None,
) -> dict[str, object]:
    return {
        "success": False,
        "error": {
            "message": message,
            "code": code,
            "details": details or [],
        },
    }


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Map ``ValidationError`` to HTTP 400 with a standard error envelope."""
    return JSONResponse(
        status_code=400,
        content=_error_envelope(
            message=exc.message,
            code="VALIDATION_ERROR",
            status_code=400,
        ),
    )


async def provider_limit_exceeded_handler(
    request: Request, exc: ProviderLimitExceededError
) -> JSONResponse:
    """Map ``ProviderLimitExceededError`` to HTTP 422."""
    return JSONResponse(
        status_code=422,
        content=_error_envelope(
            message=exc.message,
            code="INPUT_EXCEEDS_PROVIDER_LIMIT",
            status_code=422,
        ),
    )


async def generation_error_handler(request: Request, exc: GenerationError) -> JSONResponse:
    """Map ``GenerationError`` (incl. invalid output) to HTTP 502.

    No internal stack trace or secret is exposed to the client.
    """
    return JSONResponse(
        status_code=502,
        content=_error_envelope(
            message=exc.message,
            code="GENERATION_ERROR",
            status_code=502,
        ),
    )


async def input_too_large_handler(request: Request, exc: InputTooLargeError) -> JSONResponse:
    """Map ``InputTooLargeError`` to HTTP 413 with limit/received bytes in details."""
    return JSONResponse(
        status_code=413,
        content=_error_envelope(
            message=exc.message,
            code="INPUT_TOO_LARGE",
            status_code=413,
            details=[{"limit_bytes": exc.limit_bytes, "received_bytes": exc.received_bytes}],
        ),
    )


async def request_validation_error_handler(
    request: Request, exc: FastAPIRequestValidationError
) -> JSONResponse:
    """Map FastAPI's ``RequestValidationError`` to HTTP 422 with standard envelope.

    Strips submitted input from the response for security.
    """
    return JSONResponse(
        status_code=422,
        content=_error_envelope(
            message="Request validation failed",
            code="INVALID_REQUEST",
            status_code=422,
            details=[],
        ),
    )


# ``InvalidGeneratorOutputError`` is a subclass of ``GenerationError`` and is
# handled by ``generation_error_handler``.
HandlerType = Callable[[Request, Exception], Awaitable[Response]]


def register_exception_handlers(app: FastAPI) -> None:
    """Register centralized exception handlers on the FastAPI app."""
    app.add_exception_handler(
        ValidationError,
        cast(HandlerType, validation_error_handler),
    )
    app.add_exception_handler(
        InputTooLargeError,
        cast(HandlerType, input_too_large_handler),
    )
    app.add_exception_handler(
        ProviderLimitExceededError,
        cast(HandlerType, provider_limit_exceeded_handler),
    )
    app.add_exception_handler(
        GenerationError,
        cast(HandlerType, generation_error_handler),
    )
    app.add_exception_handler(
        FastAPIRequestValidationError,
        cast(HandlerType, request_validation_error_handler),
    )
