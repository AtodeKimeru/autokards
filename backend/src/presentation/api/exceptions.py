"""Centralized exception handlers for the presentation layer.

Maps domain exceptions to standardized HTTP error responses so internal
stack traces are never leaked to clients (per API design standards).
"""

from typing import Awaitable, Callable, cast

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.responses import Response

from src.domain.exceptions import (
    GenerationError,
    ProviderLimitExceededError,
    ValidationError,
)


def _error_envelope(message: str, code: str, status_code: int) -> dict[str, object]:
    return {
        "success": False,
        "error": {
            "message": message,
            "code": code,
            "details": [],
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
        ProviderLimitExceededError,
        cast(HandlerType, provider_limit_exceeded_handler),
    )
    app.add_exception_handler(
        GenerationError,
        cast(HandlerType, generation_error_handler),
    )
