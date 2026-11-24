"""FastAPI application entry point.

Wires together the presentation routers, dependency injection, and
centralized exception handlers.
"""

from fastapi import FastAPI

from src.application.services.generate_flashcards_use_case import (
    GenerateFlashcardsUseCase,
)
from src.config import settings
from src.presentation.api.exceptions import register_exception_handlers
from src.presentation.api.flashcards_router import router as flashcards_router


def get_flashcards_use_case() -> GenerateFlashcardsUseCase:
    """Dependency that provides a ``GenerateFlashcardsUseCase`` instance."""
    return GenerateFlashcardsUseCase()


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, debug=settings.debug)

    register_exception_handlers(app)

    app.include_router(flashcards_router)

    return app


app = create_app()
