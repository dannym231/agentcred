"""Top-level AgentCred agent."""

from __future__ import annotations

import json
from typing import Any, Mapping

from .identity import Identity
from .reputation import Reputation
from .wallet import BaseWallet, Wallet


class AgentCredAgent:
    """Bundle an agent's wallet, identity, and reputation."""

    def __init__(
        self,
        name: str,
        metadata: Mapping[str, Any] | None = None,
        initial_balance: Any = 100,
        wallet: BaseWallet | None = None,
    ) -> None:
        self.identity = Identity(name=name, metadata=metadata)
        self.name = self.identity.name
        if wallet is not None and not isinstance(wallet, BaseWallet):
            raise TypeError("wallet must implement BaseWallet")
        self.wallet = (
            wallet
            if wallet is not None
            else Wallet(balance=initial_balance, address=self.identity.address)
        )
        self.reputation = Reputation()

    def __repr__(self) -> str:
        return f"AgentCredAgent(name={self.name!r})"

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable snapshot of the full agent."""
        return {
            "name": self.name,
            "identity": self.identity.to_dict(),
            "wallet": self.wallet.to_dict(),
            "reputation": self.reputation.to_dict(),
        }

    def to_json(self) -> str:
        """Return the full agent snapshot as JSON."""
        return json.dumps(self.to_dict(), sort_keys=True)
