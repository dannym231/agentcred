# AgentCred

AgentCred is a small Python SDK that gives AI agents a wallet interface, a
deterministic local identity, and a reputation score. This MVP is entirely
local: it makes no network calls, uses no API keys, and has no Coinbase or Base
dependency.

## Installation

AgentCred requires Python 3.10 or newer and has no third-party dependencies.

Install it locally in editable mode:

```bash
pip install -e .
```

## Minimal usage

```python
from agentcred import AgentCredAgent

agent = AgentCredAgent("researcher")
print(agent.identity.agent_id)
print(agent.wallet.balance)
print(agent.reputation.score)
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
python -m unittest discover -s tests -v
```
