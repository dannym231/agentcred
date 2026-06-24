"""Local reputation tracking."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4


@dataclass(frozen=True)
class ReputationEvent:
    """A completed, failed, or voided unit of work."""

    event_id: str
    outcome: str
    category: str
    details: str | None
    transaction_id: str | None
    created_at: datetime

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable reputation event snapshot."""
        return {
            "event_id": self.event_id,
            "outcome": self.outcome,
            "category": self.category,
            "details": self.details,
            "transaction_id": self.transaction_id,
            "created_at": self.created_at.isoformat(),
        }


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
        self,
        category: str = "job",
        details: str | None = None,
        transaction_id: str | None = None,
    ) -> ReputationEvent:
        return self._record("completed", category, details, transaction_id)

    def record_failed(
        self,
        category: str = "job",
        details: str | None = None,
        transaction_id: str | None = None,
    ) -> ReputationEvent:
        return self._record("failed", category, details, transaction_id)

    def record_void(
        self,
        category: str = "job",
        details: str | None = None,
        transaction_id: str | None = None,
    ) -> ReputationEvent:
        return self._record("void", category, details, transaction_id)

    def record_success(
        self,
        category: str = "job",
        details: str | None = None,
        transaction_id: str | None = None,
    ) -> ReputationEvent:
        """Alias for recording a completed outcome."""
        return self.record_completed(category, details, transaction_id)

    def record_failure(
        self,
        category: str = "job",
        details: str | None = None,
        transaction_id: str | None = None,
    ) -> ReputationEvent:
        """Alias for recording a failed outcome."""
        return self.record_failed(category, details, transaction_id)

    def _record(
        self,
        outcome: str,
        category: str,
        details: str | None,
        transaction_id: str | None,
    ) -> ReputationEvent:
        if not isinstance(category, str) or not category.strip():
            raise ValueError("reputation category must be a non-empty string")
        event = ReputationEvent(
            event_id=uuid4().hex,
            outcome=outcome,
            category=category.strip(),
            details=details,
            transaction_id=transaction_id,
            created_at=datetime.now(timezone.utc),
        )
        self._history.append(event)
        return event

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable reputation snapshot."""
        return {
            "score": self.score,
            "completed_count": self.completed_count,
            "failed_count": self.failed_count,
            "history": [event.to_dict() for event in self.history],
        }

    def to_json(self) -> str:
        """Return the reputation snapshot as JSON."""
        return json.dumps(self.to_dict(), sort_keys=True)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Reputation:
        """Restore reputation state and its event history."""
        reputation = cls()
        reputation._history = [
            ReputationEvent(
                event_id=event["event_id"],
                outcome=event["outcome"],
                category=event["category"],
                details=event.get("details"),
                transaction_id=event.get("transaction_id"),
                created_at=datetime.fromisoformat(event["created_at"]),
            )
            for event in data.get("history", [])
        ]
        return reputation

    @classmethod
    def from_json(cls, data: str) -> Reputation:
        """Restore reputation state from a JSON snapshot."""
        return cls.from_dict(json.loads(data))
