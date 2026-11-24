"""Domain exceptions raised by domain layer business rules."""


class ValidationError(Exception):
    """Raised when a domain value object or business rule rejects input.

    Carries a human-readable message intended for API responses.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class GenerationError(Exception):
    """Raised when flashcard generation fails for any reason.

    Carries a human-readable message intended for API responses.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ProviderLimitExceededError(GenerationError):
    """Raised when the generation provider rejects input as exceeding its own limit."""

    def __init__(self, message: str = "Input exceeds provider limit") -> None:
        super().__init__(message)
        self.message = message


class InvalidGeneratorOutputError(GenerationError):
    """Raised when the generator returns malformed, empty, or partial output."""

    def __init__(self, message: str = "Invalid generator output") -> None:
        super().__init__(message)
        self.message = message
