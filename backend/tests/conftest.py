"""Global pytest fixtures and configuration."""

import os
import pytest

@pytest.fixture(autouse=True, scope="session")
def test_env() -> None:
    """Set up a consistent test environment for all tests.

    Ensures we use the stub provider and development settings by default
    to avoid accidental external API calls during local test runs.
    """
    os.environ["APP_ENV"] = "development"
    os.environ["LLM_PROVIDER"] = "stub"
    os.environ["MAX_INPUT_BYTES"] = str(10 * 1024 * 1024)  # 10 MiB
    os.environ["LLM_MODEL"] = "test-model"
    os.environ["LLM_API_KEY"] = "test-api-key"