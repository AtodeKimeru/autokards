"""Composition root wiring for FastAPI dependency injection.

Resolves the configured ``FlashcardGenerator`` adapter and builds the
``GenerateFlashcardsUseCase`` through ``Depends``-based provider functions.
Only this module and ``main.py`` import infrastructure adapters, keeping the
application layer free of provider coupling. Tests override
``get_flashcards_use_case`` directly via ``app.dependency_overrides`` and
remove only that entry, so production wiring is never test-order dependent.
"""

from typing import Annotated

from fastapi import Depends

from src.application.services.generate_flashcards_use_case import (
    GenerateFlashcardsUseCase,
)
from src.config import settings
from src.domain.ports.flashcard_generator import FlashcardGenerator
from src.infrastructure.llm.openai_compatible_generator import (
    OpenAICompatibleGenerator,
)
from src.infrastructure.llm.stub_generator import StubGenerator


def get_flashcard_generator() -> FlashcardGenerator:
    """Resolve the ``FlashcardGenerator`` adapter configured via ``LLM_PROVIDER``.

    ``LLM_PROVIDER`` is validated at startup (see ``Settings``); this only
    maps an already-valid value to a concrete adapter.
    """
    if settings.llm_provider == "stub":
        return StubGenerator()
    return OpenAICompatibleGenerator()


def get_flashcards_use_case(
    generator: Annotated[FlashcardGenerator, Depends(get_flashcard_generator)],
) -> GenerateFlashcardsUseCase:
    """Dependency factory providing a use case wired to the configured generator."""
    return GenerateFlashcardsUseCase(generator=generator)
