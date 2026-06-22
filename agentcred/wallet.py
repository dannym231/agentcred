"""Local credit wallet implementation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import uuid4

from .exceptions import (
    InsufficientFundsError,
    InvalidTransferAmountError,
    InvalidWalletError,
)


def _positive_decimal(value: Any, *, label: str) -> Decimal:
    if isinstance(value, bool):
        raise InvalidTransferAmountError(f"{label} must be a positive finite number")
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise InvalidTransferAmountError(
            f"{label} must be a positive finite number"
        ) from error
    if not amount.is_finite() or amount <= 0:
        raise InvalidTransferAmountError(f"{label} must be a positive finite number")
    return amount


@dataclass(frozen=True)
class Transaction:
    """An immutable local record of a credit transfer."""

    transaction_id: str
    sender: str
    recipient: str
    amount: Decimal
    memo: str | None
    created_at: datetime


class Wallet:
    """An in-memory wallet with a mock credit balance."""

    def __init__(self, balance: Any = 100, address: str | None = None) -> None:
        self._balance = _positive_decimal(balance, label="starting balance")
        self.address = address or f"mock_{uuid4().hex}"
        self._history: list[Transaction] = []

    @property
    def balance(self) -> Decimal:
        return self._balance

    @property
    def transaction_history(self) -> tuple[Transaction, ...]:
        return tuple(self._history)

    @property
    def history(self) -> tuple[Transaction, ...]:
        """Short alias for transaction history."""
        return self.transaction_history

    def send(
        self, recipient: Wallet, amount: Any, memo: str | None = None
    ) -> Transaction:
        """Transfer credits atomically to another local wallet."""
        if not isinstance(recipient, Wallet):
            raise InvalidWalletError("recipient must be a Wallet")
        transfer_amount = _positive_decimal(amount, label="transfer amount")
        if transfer_amount > self._balance:
            raise InsufficientFundsError(
                f"balance {self._balance} cannot cover transfer {transfer_amount}"
            )

        transaction = Transaction(
            transaction_id=uuid4().hex,
            sender=self.address,
            recipient=recipient.address,
            amount=transfer_amount,
            memo=memo,
            created_at=datetime.now(timezone.utc),
        )
        self._balance -= transfer_amount
        recipient._balance += transfer_amount
        self._history.append(transaction)
        if recipient is not self:
            recipient._history.append(transaction)
        return transaction
