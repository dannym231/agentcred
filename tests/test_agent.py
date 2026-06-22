import unittest
from decimal import Decimal

from agentcred import AgentCredAgent, Identity, Reputation, Wallet


class AgentCredAgentTests(unittest.TestCase):
    def test_agent_wires_components_together(self):
        agent = AgentCredAgent(
            "trader", metadata={"strategy": "mock"}, initial_balance=75
        )

        self.assertEqual(agent.name, "trader")
        self.assertIsInstance(agent.wallet, Wallet)
        self.assertIsInstance(agent.identity, Identity)
        self.assertIsInstance(agent.reputation, Reputation)
        self.assertEqual(agent.wallet.address, agent.identity.address)
        self.assertEqual(agent.wallet.balance, Decimal("75"))
        self.assertEqual(agent.reputation.score, 50.0)


if __name__ == "__main__":
    unittest.main()
