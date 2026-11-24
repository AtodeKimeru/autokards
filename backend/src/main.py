"""FastAPI application entry point.

Wires together the presentation routers, dependency injection, and
centralized exception handlers. Resolves the flashcard generator based on
``LLM_PROVIDER`` (``stub`` for offline/tests, otherwise OpenAI-compatible).
"""

from fastapi import FastAPI

from src.application.services.generate_flashcards_use_case import (
    GenerateFlashcardsUseCase,
    get_flashcards_use_case,
)
from src.config import settings
from src.domain.ports.flashcard_generator import FlashcardGenerator
from src.infrastructure.llm.openai_compatible_generator import (
    OpenAICompatibleGenerator,
)
from src.infrastructure.llm.stub_generator import StubGenerator
from src.presentation.api.exceptions import register_exception_handlers
from src.presentation.api.flashcards_router import router as flashcards_router


def _wired_get_flashcards_use_case() -> GenerateFlashcardsUseCase:
    """Resolve the generator from ``LLM_PROVIDER`` and build the use case.

    Composition root: only ``main.py`` imports infrastructure adapters,
    keeping the application layer free of provider coupling.
    """
    generator: FlashcardGenerator = (
        StubGenerator() if settings.llm_provider == "stub" else OpenAICompatibleGenerator()
    )
    return GenerateFlashcardsUseCase(generator=generator)


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, debug=settings.debug)

    register_exception_handlers(app)

    # Wire the provider-resolved generator into the router's dependency.
    app.dependency_overrides[get_flashcards_use_case] = _wired_get_flashcards_use_case

    app.include_router(flashcards_router)

    return app


app = create_app()
