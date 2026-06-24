"""Top-level AgentCred agent."""

from __future__ import annotations

import json
from typing import Any, Mapping

from .identity import Identity
from .reputation import Reputation, ReputationEvent
from .wallet import BaseWallet, Transaction, Wallet


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

    def pay_for_completed_task(
        self,
        recipient: AgentCredAgent,
        amount: Any,
        category: str,
        details: str | None = None,
    ) -> tuple[Transaction, ReputationEvent]:
        """Pay another agent and credit its reputation for completed work."""
        if not isinstance(recipient, AgentCredAgent):
            raise TypeError("recipient must be an AgentCredAgent")

        transaction = self.wallet.send(recipient.wallet, amount, memo=details)
        event = recipient.reputation.record_completed(
            category=category,
            details=details,
            transaction_id=transaction.transaction_id,
        )
        return transaction, event

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

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> AgentCredAgent:
        """Restore an agent and all of its local components."""
        identity = Identity.from_dict(data["identity"])
        wallet = Wallet.from_dict(data["wallet"])
        agent = cls(name=identity.name, metadata=identity.metadata, wallet=wallet)
        agent.identity = identity
        agent.name = data.get("name", identity.name)
        agent.reputation = Reputation.from_dict(data["reputation"])
        return agent

    @classmethod
    def from_json(cls, data: str) -> AgentCredAgent:
        """Restore an agent from a JSON snapshot."""
        return cls.from_dict(json.loads(data))
