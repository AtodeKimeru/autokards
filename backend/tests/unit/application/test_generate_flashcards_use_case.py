"""Unit tests for the GenerateFlashcardsUseCase application service."""

import pytest

from src.application.schemas.generate_flashcards import GenerateFlashcardsRequest
from src.application.services.generate_flashcards_use_case import (
    GenerateFlashcardsUseCase,
)
from src.domain.exceptions import (
    GenerationError,
    InvalidGeneratorOutputError,
    ProviderLimitExceededError,
    ValidationError,
)
from src.domain.models.flashcard import Flashcard
from src.domain.models.study_text import StudyText


class FakeGenerator:
    """Test double implementing the FlashcardGenerator port."""

    def __init__(
        self,
        cards: list[Flashcard] | None = None,
        exc: Exception | None = None,
    ) -> None:
        self._cards = cards or []
        self.exc = exc
        self.called_with: StudyText | None = None

    async def generate(self, study_text: StudyText) -> tuple[Flashcard, ...]:
        self.called_with = study_text
        if self.exc is not None:
            raise self.exc
        return tuple(self._cards)


class TestGenerateFlashcardsUseCase:
    async def test_stops_flow_without_generating_when_text_is_empty(self) -> None:
        # Arrange
        use_case = GenerateFlashcardsUseCase(generator=FakeGenerator())
        request = GenerateFlashcardsRequest(text="")

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await use_case.execute(request)

        assert exc_info.value.message == "Readable study text is required"

    async def test_stops_flow_without_generating_when_text_is_whitespace_only(
        self,
    ) -> None:
        # Arrange
        use_case = GenerateFlashcardsUseCase(generator=FakeGenerator())
        request = GenerateFlashcardsRequest(text="   \t\n  ")

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await use_case.execute(request)

        assert exc_info.value.message == "Readable study text is required"

    async def test_returns_generated_cards_when_generation_succeeds(self) -> None:
        # Arrange
        generator = FakeGenerator(
            cards=[
                Flashcard(front="Q1", back="A1"),
                Flashcard(front="Q2", back="A2"),
            ]
        )
        use_case = GenerateFlashcardsUseCase(generator=generator)
        request = GenerateFlashcardsRequest(text="Review chapter 3")

        # Act
        cards = await use_case.execute(request)

        # Assert
        assert cards == (
            Flashcard(front="Q1", back="A1"),
            Flashcard(front="Q2", back="A2"),
        )
        assert generator.called_with is not None
        assert generator.called_with.value == "Review chapter 3"

    async def test_returns_single_card_when_generator_produces_one_card(self) -> None:
        # Arrange
        generator = FakeGenerator(cards=[Flashcard(front="Q", back="A")])
        use_case = GenerateFlashcardsUseCase(generator=generator)
        request = GenerateFlashcardsRequest(text="Study text")

        # Act
        cards = await use_case.execute(request)

        # Assert
        assert cards == (Flashcard(front="Q", back="A"),)

    async def test_raises_generation_error_when_generator_returns_zero_cards(self) -> None:
        # Arrange
        generator = FakeGenerator(cards=[])
        use_case = GenerateFlashcardsUseCase(generator=generator)
        request = GenerateFlashcardsRequest(text="Review chapter 3")

        # Act & Assert
        with pytest.raises(GenerationError):
            await use_case.execute(request)

    async def test_propagates_invalid_generator_output_error(self) -> None:
        # Arrange
        generator = FakeGenerator(
            cards=[],
            exc=InvalidGeneratorOutputError("Malformed generator output"),
        )
        use_case = GenerateFlashcardsUseCase(generator=generator)
        request = GenerateFlashcardsRequest(text="Review chapter 3")

        # Act & Assert
        with pytest.raises(InvalidGeneratorOutputError):
            await use_case.execute(request)

    async def test_propagates_provider_limit_exceeded_error(self) -> None:
        # Arrange
        generator = FakeGenerator(
            cards=[],
            exc=ProviderLimitExceededError("Input exceeds provider limit"),
        )
        use_case = GenerateFlashcardsUseCase(generator=generator)
        request = GenerateFlashcardsRequest(text="Review chapter 3")

        # Act & Assert
        with pytest.raises(ProviderLimitExceededError):
            await use_case.execute(request)

    async def test_wraps_unexpected_generator_exception_as_generation_error(self) -> None:
        # Arrange
        generator = FakeGenerator(cards=[], exc=RuntimeError("boom"))
        use_case = GenerateFlashcardsUseCase(generator=generator)
        request = GenerateFlashcardsRequest(text="Review chapter 3")

        # Act & Assert
        with pytest.raises(GenerationError) as exc_info:
            await use_case.execute(request)

        assert exc_info.value.message == "Generation failed unexpectedly"

    def test_requires_a_generator_at_construction(self) -> None:
        # Arrange & Act & Assert
        with pytest.raises(TypeError):
            GenerateFlashcardsUseCase()  # type: ignore[call-arg]
