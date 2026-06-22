"""Local reputation tracking."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class ReputationEvent:
    """A completed or failed unit of work."""

    outcome: str
    category: str
    details: str | None
    created_at: datetime


class Reputation:
    """A bounded score computed from local outcome history."""

    NEUTRAL_SCORE = 50.0
    SUCCESS_WEIGHT = 5.0
    FAILURE_WEIGHT = 10.0

    def __init__(self) -> None:
        self._history: list[ReputationEvent] = []

    @property
    def history(self) -> tuple[ReputationEvent, ...]:
        return tuple(self._history)

    @property
    def completed_count(self) -> int:
        return sum(event.outcome == "completed" for event in self._history)

    @property
    def failed_count(self) -> int:
        return sum(event.outcome == "failed" for event in self._history)

    @property
    def score(self) -> float:
        raw_score = (
            self.NEUTRAL_SCORE
            + self.completed_count * self.SUCCESS_WEIGHT
            - self.failed_count * self.FAILURE_WEIGHT
        )
        return max(0.0, min(100.0, raw_score))

    def record_completed(
        self, category: str = "job", details: str | None = None
    ) -> ReputationEvent:
        return self._record("completed", category, details)

    def record_failed(
        self, category: str = "job", details: str | None = None
    ) -> ReputationEvent:
        return self._record("failed", category, details)

    def record_success(
        self, category: str = "job", details: str | None = None
    ) -> ReputationEvent:
        """Alias for recording a completed outcome."""
        return self.record_completed(category, details)

    def record_failure(
        self, category: str = "job", details: str | None = None
    ) -> ReputationEvent:
        """Alias for recording a failed outcome."""
        return self.record_failed(category, details)

    def _record(
        self, outcome: str, category: str, details: str | None
    ) -> ReputationEvent:
        if not isinstance(category, str) or not category.strip():
            raise ValueError("reputation category must be a non-empty string")
        event = ReputationEvent(
            outcome=outcome,
            category=category.strip(),
            details=details,
            created_at=datetime.now(timezone.utc),
        )
        self._history.append(event)
        return event
