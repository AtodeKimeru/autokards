"""Domain exceptions raised by domain layer business rules."""


class ValidationError(Exception):
    """Raised when a domain value object or business rule rejects input.

    Carries a human-readable message intended for API responses.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
