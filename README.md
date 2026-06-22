# AgentCred

AgentCred is a small Python SDK that gives AI agents a wallet interface, a
deterministic local identity, and a reputation score. This MVP is entirely
local: it makes no network calls, uses no API keys, and has no Coinbase or Base
dependency.

## Quick start

AgentCred requires Python 3.10 or newer and has no third-party dependencies.

```python
from agentcred import AgentCredAgent

buyer = AgentCredAgent("buyer", initial_balance=100)
seller = AgentCredAgent("seller", initial_balance=25)

buyer.wallet.send(seller.wallet, 10, memo="sample trade")
buyer.reputation.record_completed("trade")

print(buyer.wallet.balance)       # Decimal('90')
print(seller.wallet.balance)      # Decimal('35')
print(buyer.identity.agent_id)    # deterministic local identifier
print(buyer.reputation.score)     # 55.0
```

## Components

- `AgentCredAgent` wires the SDK components together.
- `Wallet` maintains a local credit balance and transaction history.
- `Identity` derives an agent ID and address from the name and metadata.
- `Reputation` records completed and failed work and computes a score from 0
  to 100, starting at a neutral 50.

The component boundaries are intentionally small so local implementations can
later be replaced by Coinbase AgentKit and Base-backed adapters.

## Tests

```bash
python3 -m unittest discover -s tests -v
```
