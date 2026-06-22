"""Deterministic local identities for agents."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Mapping


class Identity:
    """An agent identity derived locally from its name and metadata."""

    def __init__(self, name: str, metadata: Mapping[str, Any] | None = None) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("identity name must be a non-empty string")

        self.name = name.strip()
        self.metadata = deepcopy(dict(metadata or {}))
        try:
            payload = json.dumps(
                {"name": self.name, "metadata": self.metadata},
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            )
        except (TypeError, ValueError) as error:
            raise ValueError("identity metadata must be JSON serializable") from error

        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        self.agent_id = f"agent_{digest}"
        self.address = f"0x{digest[:40]}"

    def __repr__(self) -> str:
        return f"Identity(name={self.name!r}, agent_id={self.agent_id!r})"
