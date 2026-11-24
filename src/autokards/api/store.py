"""In-memory submission store.

No persistence requirement exists for this capability (see design.md).
A restart loses all submissions; this is an accepted limitation for the
AC-1..AC-3 scope of FR-1.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field


@dataclass
class StoredSubmission:
    submission_id: str
    text: str
    byte_count: int


class SubmissionStore:
    """Simple dict-backed store, isolated per instance (per test/process)."""

    def __init__(self) -> None:
        self._submissions: dict[str, StoredSubmission] = {}

    def add(self, text: str, byte_count: int) -> StoredSubmission:
        submission_id = str(uuid.uuid4())
        record = StoredSubmission(
            submission_id=submission_id, text=text, byte_count=byte_count
        )
        self._submissions[submission_id] = record
        return record

    def get(self, submission_id: str) -> StoredSubmission | None:
        return self._submissions.get(submission_id)

    def __len__(self) -> int:
        return len(self._submissions)
