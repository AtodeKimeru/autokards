"""Application configuration loaded from environment variables."""

import os


def _get_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}


class Settings:
    """Runtime configuration.

    Values are loaded from environment variables with sensible defaults
    for local development. Secrets should never be hardcoded.
    """

    def __init__(self) -> None:
        self.app_name = os.getenv("APP_NAME", "autokards-backend")
        self.debug = _get_bool("DEBUG", False)


settings = Settings()
