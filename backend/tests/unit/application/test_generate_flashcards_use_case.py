"""Unit tests for the GenerateFlashcardsUseCase application service."""

import pytest

from src.application.schemas.generate_flashcards import GenerateFlashcardsRequest
from src.application.services.generate_flashcards_use_case import (
    GenerateFlashcardsUseCase,
)
from src.domain.exceptions import ValidationError


class TestGenerateFlashcardsUseCase:
    def test_stops_flow_without_generating_when_text_is_empty(self) -> None:
        # Arrange
        use_case = GenerateFlashcardsUseCase()
        request = GenerateFlashcardsRequest(text="")

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            use_case.execute(request)

        assert exc_info.value.message == "Readable study text is required"

    def test_stops_flow_without_generating_when_text_is_whitespace_only(
        self,
    ) -> None:
        # Arrange
        use_case = GenerateFlashcardsUseCase()
        request = GenerateFlashcardsRequest(text="   \t\n  ")

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            use_case.execute(request)

        assert exc_info.value.message == "Readable study text is required"

    def test_proceeds_to_generation_when_text_contains_non_whitespace_character(
        self,
    ) -> None:
        # Arrange
        use_case = GenerateFlashcardsUseCase()
        request = GenerateFlashcardsRequest(text="Review chapter 3")

        # Act
        study_text = use_case.execute(request)

        # Assert
        assert study_text.value == "Review chapter 3"
