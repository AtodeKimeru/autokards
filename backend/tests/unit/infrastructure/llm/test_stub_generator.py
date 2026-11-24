"""Unit tests for the deterministic StubGenerator infrastructure adapter."""

import pytest

from src.domain.exceptions import ValidationError
from src.domain.models.study_text import StudyText
from src.infrastructure.llm.stub_generator import StubGenerator


class TestStubGenerator:
    async def test_returns_known_cards_without_network(self) -> None:
        # Arrange
        generator = StubGenerator()
        study_text = StudyText(value="The capital of France is Paris.")

        # Act
        cards = await generator.generate(study_text)

        # Assert
        assert len(cards) >= 1
        for card in cards:
            assert card.front.strip()
            assert card.back.strip()

    async def test_is_deterministic_for_same_input(self) -> None:
        # Arrange
        generator = StubGenerator()
        study_text = StudyText(value="The capital of France is Paris.")

        # Act
        first = await generator.generate(study_text)
        second = await generator.generate(study_text)

        # Assert
        assert first == second

    async def test_rejects_empty_study_text(self) -> None:
        # Arrange
        generator = StubGenerator()

        # Act & Assert
        with pytest.raises(ValidationError):
            await generator.generate(StudyText(value=""))

    async def test_returns_two_deterministic_cards(self) -> None:
        # Arrange
        generator = StubGenerator()
        study_text = StudyText(value="The capital of France is Paris.")

        # Act
        cards = await generator.generate(study_text)

        # Assert
        assert len(cards) == 2
        # Stub returns fixed card content for verification
        assert cards[0].front == "What is the main topic of the text?"
        assert cards[0].back == "The text covers the submitted study content."
        assert cards[1].front == "Name one key detail from the text."
        assert cards[1].back == "A key detail is present in the submitted study content."
