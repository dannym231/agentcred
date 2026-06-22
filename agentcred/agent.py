"""Top-level AgentCred agent."""

from __future__ import annotations

from typing import Any, Mapping

from .identity import Identity
from .reputation import Reputation
from .wallet import Wallet


class AgentCredAgent:
    """Bundle an agent's wallet, identity, and reputation."""

    def __init__(
        self,
        name: str,
        metadata: Mapping[str, Any] | None = None,
        initial_balance: Any = 100,
    ) -> None:
        self.identity = Identity(name=name, metadata=metadata)
        self.name = self.identity.name
        self.wallet = Wallet(balance=initial_balance, address=self.identity.address)
        self.reputation = Reputation()

    def __repr__(self) -> str:
        return f"AgentCredAgent(name={self.name!r})"
