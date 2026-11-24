"""Unit tests for the Flashcard domain value object and FlashcardSet aggregate."""

from dataclasses import FrozenInstanceError

import pytest

from src.domain.exceptions import ValidationError
from src.domain.models.flashcard import Flashcard
from src.domain.models.flashcard_set import FlashcardSet


class TestFlashcard:
    def test_rejects_empty_front(self) -> None:
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            Flashcard(front="", back="Answer")

        assert exc_info.value.message == "Front must be non-empty"

    def test_rejects_whitespace_only_front(self) -> None:
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            Flashcard(front="   \t\n  ", back="Answer")

        assert exc_info.value.message == "Front must be non-empty"

    def test_rejects_empty_back(self) -> None:
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            Flashcard(front="Question", back="")

        assert exc_info.value.message == "Back must be non-empty"

    def test_rejects_whitespace_only_back(self) -> None:
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            Flashcard(front="Question", back="   \t\n  ")

        assert exc_info.value.message == "Back must be non-empty"

    def test_accepts_valid_front_and_back(self) -> None:
        # Arrange & Act
        card = Flashcard(front="What is Paris?", back="The capital of France")

        # Assert
        assert card.front == "What is Paris?"
        assert card.back == "The capital of France"

    def test_front_and_back_are_independent_fields(self) -> None:
        # Arrange & Act
        card = Flashcard(front="Front only", back="Back only")

        # Assert - neither field is derived from or embedded in the other
        assert card.front == "Front only"
        assert card.back == "Back only"
        assert card.front != card.back

    def test_is_immutable_when_attempting_to_reassign_front(self) -> None:
        # Arrange
        card = Flashcard(front="Question", back="Answer")

        # Act & Assert
        with pytest.raises(FrozenInstanceError):
            card.front = "changed"

    def test_is_immutable_when_attempting_to_reassign_back(self) -> None:
        # Arrange
        card = Flashcard(front="Question", back="Answer")

        # Act & Assert
        with pytest.raises(FrozenInstanceError):
            card.back = "changed"


class TestFlashcardSet:
    def test_requires_at_least_one_card(self) -> None:
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            FlashcardSet(cards=[])

        assert exc_info.value.message == "A flashcard set must contain at least one card"

    def test_accepts_single_card(self) -> None:
        # Arrange & Act
        card = Flashcard(front="Question", back="Answer")
        flashcard_set = FlashcardSet(cards=[card])

        # Assert
        assert flashcard_set.cards == [card]

    def test_accepts_multiple_cards(self) -> None:
        # Arrange & Act
        cards = [
            Flashcard(front="Q1", back="A1"),
            Flashcard(front="Q2", back="A2"),
        ]
        flashcard_set = FlashcardSet(cards=cards)

        # Assert
        assert len(flashcard_set.cards) == 2
