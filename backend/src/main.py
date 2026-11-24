"""FastAPI application entry point.

Wires together the presentation routers, dependency injection, and
centralized exception handlers. The flashcard generator is resolved by
``src.infrastructure.composition`` based on ``LLM_PROVIDER`` (``stub`` for
offline/tests, otherwise OpenAI-compatible) through a ``Depends``-based
provider function, not through ``app.dependency_overrides``.
"""

from fastapi import FastAPI

from src.config import settings
from src.presentation.api.exceptions import register_exception_handlers
from src.presentation.api.flashcards_router import router as flashcards_router


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, debug=settings.debug)

    register_exception_handlers(app)
    app.include_router(flashcards_router)

    return app


app = create_app()
