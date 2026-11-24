"""Framework-free text-input policy (FR-1 / AUTK-6).

This module owns the AC-1/AC-2/AC-3 behavior with no dependency on any web
framework, so it can be ported to a different stack without rewriting the
business rule. The only enforced limit is a byte ceiling that represents a
real infrastructure constraint, not a product-defined character/word rule.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


class SubmissionError(Exception):
    """Base class for explicit, user-facing submission failures."""

    code: str = "SUBMISSION_ERROR"


class EmptyInputError(SubmissionError):
    """Raised when the submitted text is empty.

    This is only a minimal non-empty guard. Full empty/whitespace-only
    validation and its user-facing UX are owned by a separate capability
    (AUTK-7 / FR-3).
    """

    code = "EMPTY_INPUT"

    def __init__(self) -> None:
        super().__init__("Submitted text must not be empty.")


class InputTooLargeError(SubmissionError):
    """Raised when the input exceeds the infrastructure byte ceiling.

    This is an infrastructure limit, not a product-defined rule (AC-3).
    """

    code = "INPUT_TOO_LARGE"

    def __init__(self, limit_bytes: int, received_bytes: int) -> None:
        self.limit_bytes = limit_bytes
        self.received_bytes = received_bytes
        super().__init__(
            f"Submitted text exceeds the current infrastructure limit of "
            f"{limit_bytes} bytes (received {received_bytes} bytes). "
            "Reduce the input size and resubmit."
        )


class GenerationPort(ABC):
    """Boundary to the flashcard generation provider.

    A real implementation will wrap the actual model/provider integration
    (FR-4/FR-7+). For this slice, only the error contract matters: a
    provider that cannot process the complete input must raise
    ProviderLimitExceededError rather than truncate or return a partial
    result.
    """

    @abstractmethod
    def submit(self, text: str) -> str:
        """Submit text to the provider and return its accepted text.

        Raises ProviderLimitExceededError if the provider cannot process
        the complete input.
        """
        raise NotImplementedError


class ProviderLimitExceededError(SubmissionError):
    """Raised when the generation provider rejects input as too large.

    This is distinct from InputTooLargeError: it is the provider's own
    constraint, not ours, and must be reported explicitly rather than
    triggering a silent truncation or partial result (AC-2).
    """

    code = "INPUT_EXCEEDS_PROVIDER_LIMIT"

    def __init__(self, provider_limit: int | None = None) -> None:
        self.provider_limit = provider_limit
        detail = (
            f" The provider's stated limit is {provider_limit}."
            if provider_limit is not None
            else ""
        )
        super().__init__(
            "The generation provider could not process the complete "
            f"input and reported it as exceeding its own limit.{detail}"
        )


@dataclass(frozen=True)
class SubmissionResult:
    """The outcome of accepting a text submission."""

    text: str
    byte_count: int


class SubmissionPolicy:
    """Enforces FR-1 acceptance rules on raw text submissions."""

    def __init__(self, max_input_bytes: int) -> None:
        self._max_input_bytes = max_input_bytes

    def accept(self, text: str) -> SubmissionResult:
        """Validate and accept a text submission.

        Raises EmptyInputError or InputTooLargeError on rejection. Never
        returns a truncated or partial version of the input.
        """
        if text == "":
            raise EmptyInputError()

        byte_count = len(text.encode("utf-8"))
        if byte_count > self._max_input_bytes:
            raise InputTooLargeError(
                limit_bytes=self._max_input_bytes, received_bytes=byte_count
            )

        return SubmissionResult(text=text, byte_count=byte_count)
