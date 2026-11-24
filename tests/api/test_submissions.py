"""Integration tests for POST /api/v1/submissions (FR-1 / AUTK-6)."""
import pytest
from fastapi.testclient import TestClient

from autokards.api.app import create_app
from autokards.input.policy import ProviderLimitExceededError


class RejectingGenerationPort:
    """Provider double that always rejects, simulating its own limit."""

    def __init__(self, provider_limit: int = 50):
        self.provider_limit = provider_limit

    def submit(self, text: str) -> str:
        raise ProviderLimitExceededError(provider_limit=self.provider_limit)


class AcceptingGenerationPort:
    def submit(self, text: str) -> str:
        return text


@pytest.fixture
def client():
    app = create_app(max_input_bytes=1024, generation_port=AcceptingGenerationPort())
    return TestClient(app)


@pytest.fixture
def rejecting_client():
    app = create_app(
        max_input_bytes=1024 * 1024,
        generation_port=RejectingGenerationPort(provider_limit=50),
    )
    return TestClient(app)


class TestSubmissionAcceptance:
    def test_valid_text_returns_202_with_submission_id(self, client):
        response = client.post("/api/v1/submissions", json={"text": "study notes"})
        assert response.status_code == 202
        body = response.json()
        assert "submission_id" in body
        assert body["bytes"] == len("study notes".encode("utf-8"))

    def test_unicode_text_is_preserved(self, client):
        text = "héllo wörld 日本語"
        response = client.post("/api/v1/submissions", json={"text": text})
        assert response.status_code == 202


class TestSubmissionRejectsEmptyInput:
    def test_empty_text_is_rejected(self, client):
        response = client.post("/api/v1/submissions", json={"text": ""})
        assert response.status_code != 202
        assert response.status_code == 400
        assert response.json()["code"] == "EMPTY_INPUT"


class TestSubmissionOversizedInput:
    def test_oversized_body_returns_413_with_explicit_sizes(self, client):
        oversized_text = "a" * 2000  # exceeds client's max_input_bytes=1024
        response = client.post("/api/v1/submissions", json={"text": oversized_text})
        assert response.status_code == 413
        body = response.json()
        assert body["code"] == "INPUT_TOO_LARGE"
        assert body["limit_bytes"] == 1024
        # received_bytes reflects the raw streamed request body (including
        # JSON framing overhead), not just the decoded text field, since
        # rejection happens before the body is parsed (AC-2: no buffering
        # of oversized input).
        assert body["received_bytes"] > 1024
        assert body["received_bytes"] >= len(oversized_text)


class TestSubmissionProviderRejection:
    def test_provider_rejection_returns_422(self, rejecting_client):
        response = rejecting_client.post(
            "/api/v1/submissions", json={"text": "a" * 100}
        )
        assert response.status_code == 422
        body = response.json()
        assert body["code"] == "INPUT_EXCEEDS_PROVIDER_LIMIT"
        assert body["provider_limit"] == 50


class TestStoreIsolation:
    def test_each_app_instance_has_its_own_empty_store(self, client):
        # The fixture's store starts empty; submitting in one app instance
        # must never be visible from a different instance's store.
        assert len(client.app.state.store) == 0
        client.post("/api/v1/submissions", json={"text": "notes"})
        assert len(client.app.state.store) == 1

        other_app = create_app(
            max_input_bytes=1024, generation_port=AcceptingGenerationPort()
        )
        assert len(other_app.state.store) == 0


class TestNoUnlimitedCapacityClaimsInResponses:
    def test_success_response_has_no_unlimited_claim(self, client):
        response = client.post("/api/v1/submissions", json={"text": "notes"})
        body_text = str(response.json()).lower()
        for forbidden in ("unlimited", "infinite", "no limit"):
            assert forbidden not in body_text
