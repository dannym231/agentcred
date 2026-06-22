import unittest
import json
from decimal import Decimal

from agentcred import AgentCredAgent, BaseWallet, Identity, Reputation, Wallet


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

    def test_documented_minimal_usage(self):
        agent = AgentCredAgent("momentum-01")

        self.assertEqual(agent.wallet.balance, Decimal("100"))
        self.assertTrue(agent.identity.agent_id)
        self.assertEqual(agent.reputation.score, 50.0)

    def test_agent_serialization(self):
        agent = AgentCredAgent("worker", metadata={"model": "local"})
        recipient = Wallet(10)
        transaction = agent.wallet.send(recipient, 20, memo="task payment")
        agent.reputation.record_completed(
            "task", transaction_id=transaction.transaction_id
        )

        exported = agent.to_dict()

        self.assertEqual(exported["identity"]["agent_id"], agent.identity.agent_id)
        self.assertEqual(exported["wallet"]["balance"], "80")
        self.assertEqual(
            exported["wallet"]["history"][0]["transaction_id"],
            transaction.transaction_id,
        )
        self.assertEqual(exported["reputation"]["score"], 55.0)
        self.assertEqual(
            exported["reputation"]["history"][0]["transaction_id"],
            transaction.transaction_id,
        )
        self.assertEqual(json.loads(agent.to_json()), exported)

    def test_agent_accepts_wallet_interface_implementation(self):
        wallet = Wallet(25, address="adapter-address")

        agent = AgentCredAgent("adapter-user", wallet=wallet)

        self.assertIsInstance(agent.wallet, BaseWallet)
        self.assertIs(agent.wallet, wallet)


if __name__ == "__main__":
    unittest.main()
