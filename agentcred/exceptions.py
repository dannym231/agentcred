"""Exceptions raised by AgentCred."""


class AgentCredError(Exception):
    """Base exception for AgentCred errors."""


class InvalidTransferAmountError(AgentCredError, ValueError):
    """Raised when a transfer amount is not a positive finite number."""


class InsufficientFundsError(AgentCredError):
    """Raised when a wallet cannot cover a transfer."""


class InvalidWalletError(AgentCredError, TypeError):
    """Raised when a transfer recipient is not a wallet."""
