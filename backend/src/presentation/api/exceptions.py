"""Centralized exception handlers for the presentation layer.

Maps domain exceptions to standardized HTTP error responses so internal
stack traces are never leaked to clients (per API design standards).
"""

from typing import Awaitable, Callable, cast

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.responses import Response

from src.domain.exceptions import ValidationError


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


HandlerType = Callable[[Request, Exception], Awaitable[Response]]


def register_exception_handlers(app: FastAPI) -> None:
    """Register centralized exception handlers on the FastAPI app."""
    app.add_exception_handler(
        ValidationError,
        cast(HandlerType, validation_error_handler),
    )
