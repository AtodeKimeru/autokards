"""Tests for the framework-free text-input policy (AC-1, AC-2, AC-3).

AC-3 boundary-sweep test (test_no_character_or_word_cap_exists) is written
alongside the AC-1 acceptance tests: since the policy enforces a byte
ceiling only, it already satisfies "no product-defined length limit"
without any extra code. That is confirmed, not assumed, by running the
sweep below.
"""
import pytest

from autokards.input.policy import (
    EmptyInputError,
    GenerationPort,
    InputTooLargeError,
    ProviderLimitExceededError,
    SubmissionPolicy,
)


BIG_TEXT_BYTES = 5 * 1024 * 1024  # 5 MiB, well within a generous infra ceiling


def make_policy(max_input_bytes: int = 10 * 1024 * 1024) -> SubmissionPolicy:
    return SubmissionPolicy(max_input_bytes=max_input_bytes)


class TestAC1CompleteTextReachesGeneration:
    def test_large_payload_is_stored_byte_for_byte_identical(self):
        policy = make_policy()
        text = "x" * BIG_TEXT_BYTES
        result = policy.accept(text)
        assert result.text == text
        assert len(result.text.encode("utf-8")) == len(text.encode("utf-8"))

    def test_unicode_and_mixed_line_endings_are_preserved(self):
        policy = make_policy()
        text = "héllo wörld\r\nsecond line\nthird line\r\n日本語のテキスト"
        result = policy.accept(text)
        assert result.text == text

    def test_submission_result_carries_byte_count(self):
        policy = make_policy()
        text = "abc"
        result = policy.accept(text)
        assert result.byte_count == 3


class TestAC2InputIntegrityPreservation:
    def test_over_limit_raises_explicit_error_with_sizes(self):
        limit = 100
        policy = make_policy(max_input_bytes=limit)
        oversized_text = "a" * (limit + 1)

        with pytest.raises(InputTooLargeError) as exc_info:
            policy.accept(oversized_text)

        error = exc_info.value
        assert error.limit_bytes == limit
        assert error.received_bytes == limit + 1
        assert error.code == "INPUT_TOO_LARGE"

    def test_over_limit_does_not_return_a_partial_result(self):
        policy = make_policy(max_input_bytes=10)
        with pytest.raises(InputTooLargeError):
            result = policy.accept("a" * 11)
            # If execution ever reached this line, no truncated result
            # object should exist to be mistaken for valid output.
            assert result is None  # pragma: no cover - unreachable by design

    def test_empty_input_is_rejected(self):
        policy = make_policy()
        with pytest.raises(EmptyInputError) as exc_info:
            policy.accept("")
        assert exc_info.value.code == "EMPTY_INPUT"


class TestAC3NoArbitraryLengthLimit:
    @pytest.mark.parametrize(
        "size_bytes",
        [1024, 64 * 1024, 1024 * 1024, 5 * 1024 * 1024, 9 * 1024 * 1024 + 900 * 1024],
    )
    def test_no_character_or_word_cap_exists(self, size_bytes):
        policy = make_policy(max_input_bytes=10 * 1024 * 1024)
        text = "a" * size_bytes
        # No character/word threshold rejects this; only the byte ceiling
        # (checked separately in AC-2 tests) would ever reject input.
        result = policy.accept(text)
        assert result.byte_count == size_bytes

    def test_boundary_just_under_limit_is_accepted(self):
        limit = 1024
        policy = make_policy(max_input_bytes=limit)
        text = "a" * (limit - 1)
        result = policy.accept(text)
        assert result.byte_count == limit - 1


class FakeGenerationPort(GenerationPort):
    """Test double simulating a generation provider's own limit."""

    def __init__(self, provider_limit_bytes: int | None = None) -> None:
        self._provider_limit_bytes = provider_limit_bytes

    def submit(self, text: str):
        if self._provider_limit_bytes is not None:
            byte_count = len(text.encode("utf-8"))
            if byte_count > self._provider_limit_bytes:
                raise ProviderLimitExceededError(
                    provider_limit=self._provider_limit_bytes
                )
        return text


class TestAC2ProviderFailurePath:
    def test_provider_rejection_surfaces_as_explicit_error_not_truncation(self):
        policy = make_policy(max_input_bytes=10 * 1024 * 1024)
        port = FakeGenerationPort(provider_limit_bytes=100)
        text = "a" * 200

        accepted = policy.accept(text)
        with pytest.raises(ProviderLimitExceededError) as exc_info:
            port.submit(accepted.text)

        error = exc_info.value
        assert error.code == "INPUT_EXCEEDS_PROVIDER_LIMIT"
        assert error.provider_limit == 100
        assert "truncat" not in str(error).lower()

    def test_provider_accepts_within_its_limit(self):
        policy = make_policy(max_input_bytes=10 * 1024 * 1024)
        port = FakeGenerationPort(provider_limit_bytes=100)
        text = "a" * 50

        accepted = policy.accept(text)
        result = port.submit(accepted.text)
        assert result == text


class TestNoUnlimitedCapacityClaims:
    def test_error_messages_contain_no_unlimited_claim(self):
        policy = make_policy(max_input_bytes=10)
        with pytest.raises(InputTooLargeError) as exc_info:
            policy.accept("a" * 11)
        message = str(exc_info.value).lower()
        for forbidden in ("unlimited", "infinite", "no limit", "any size"):
            assert forbidden not in message
