"""Unit tests for the StudyText domain value object."""

from dataclasses import FrozenInstanceError

import pytest

from src.domain.exceptions import ValidationError
from src.domain.models.study_text import StudyText


class TestStudyText:
    def test_rejects_empty_text_when_no_characters_provided(self) -> None:
        # Arrange
        raw_text = ""

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            StudyText(value=raw_text)

        assert exc_info.value.message == "Readable study text is required"

    def test_rejects_whitespace_only_text_when_only_spaces_provided(self) -> None:
        # Arrange
        raw_text = "   "

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            StudyText(value=raw_text)

        assert exc_info.value.message == "Readable study text is required"

    def test_rejects_whitespace_only_text_when_tabs_and_newlines_provided(self) -> None:
        # Arrange
        raw_text = " \t\n "

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            StudyText(value=raw_text)

        assert exc_info.value.message == "Readable study text is required"

    def test_accepts_valid_text_when_non_whitespace_character_present(self) -> None:
        # Arrange
        raw_text = "Review chapter 3"

        # Act
        study_text = StudyText(value=raw_text)

        # Assert
        assert study_text.value == "Review chapter 3"

    def test_accepts_text_with_leading_and_trailing_whitespace_when_content_present(
        self,
    ) -> None:
        # Arrange
        raw_text = "  Review chapter 3  "

        # Act
        study_text = StudyText(value=raw_text)

        # Assert
        assert study_text.value == "  Review chapter 3  "

    def test_is_immutable_when_attempting_to_reassign_value(self) -> None:
        # Arrange
        study_text = StudyText(value="Review chapter 3")

        # Act & Assert
        with pytest.raises(FrozenInstanceError):
            study_text.value = "changed"
