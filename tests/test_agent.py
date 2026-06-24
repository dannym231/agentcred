import unittest
import json
from decimal import Decimal

from agentcred import (
    AgentCredAgent,
    BaseWallet,
    Identity,
    InsufficientFundsError,
    InvalidTransferAmountError,
    Reputation,
    Wallet,
)


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

    def test_agent_json_round_trip(self):
        buyer = AgentCredAgent(
            "buyer", metadata={"model": "local"}, initial_balance=100
        )
        seller = AgentCredAgent("seller", initial_balance=0)
        transaction, event = buyer.pay_for_completed_task(
            recipient=seller,
            amount="25.50",
            category="labeling-task",
            details="Seller completed labeling task",
        )

        restored = AgentCredAgent.from_json(seller.to_json())

        self.assertEqual(restored.to_dict(), seller.to_dict())
        self.assertEqual(restored.identity.agent_id, seller.identity.agent_id)
        self.assertEqual(restored.wallet.balance, seller.wallet.balance)
        self.assertEqual(restored.reputation.score, seller.reputation.score)
        self.assertEqual(
            restored.wallet.history[0].transaction_id, transaction.transaction_id
        )
        self.assertEqual(restored.reputation.history[0].event_id, event.event_id)
        self.assertEqual(
            restored.reputation.history[0].transaction_id,
            restored.wallet.history[0].transaction_id,
        )

    def test_restored_agent_remains_operational(self):
        original = AgentCredAgent("buyer", initial_balance=100)
        restored = AgentCredAgent.from_json(original.to_json())
        seller = AgentCredAgent("seller", initial_balance=0)

        transaction, event = restored.pay_for_completed_task(
            recipient=seller,
            amount=20,
            category="restored-task",
            details="Task completed after restore",
        )
        recorded = restored.reputation.record_completed("self-check")

        self.assertEqual(restored.wallet.balance, Decimal("80"))
        self.assertEqual(seller.wallet.balance, Decimal("20"))
        self.assertEqual(event.transaction_id, transaction.transaction_id)
        self.assertEqual(seller.reputation.history, (event,))
        self.assertEqual(restored.reputation.history, (recorded,))

    def test_agent_accepts_wallet_interface_implementation(self):
        wallet = Wallet(25, address="adapter-address")

        agent = AgentCredAgent("adapter-user", wallet=wallet)

        self.assertIsInstance(agent.wallet, BaseWallet)
        self.assertIs(agent.wallet, wallet)

    def test_pay_for_completed_task_links_payment_to_recipient_reputation(self):
        buyer = AgentCredAgent("buyer", initial_balance=100)
        seller = AgentCredAgent("seller", initial_balance=0)

        transaction, event = buyer.pay_for_completed_task(
            recipient=seller,
            amount=25,
            category="labeling-task",
            details="Seller completed labeling task",
        )

        self.assertEqual(buyer.wallet.balance, Decimal("75"))
        self.assertEqual(seller.wallet.balance, Decimal("25"))
        self.assertEqual(transaction.memo, "Seller completed labeling task")
        self.assertEqual(event.outcome, "completed")
        self.assertEqual(event.category, "labeling-task")
        self.assertEqual(event.details, "Seller completed labeling task")
        self.assertEqual(event.transaction_id, transaction.transaction_id)
        self.assertEqual(seller.reputation.history, (event,))
        self.assertEqual(buyer.reputation.history, ())

    def test_pay_for_completed_task_overdraft_does_not_record_reputation(self):
        buyer = AgentCredAgent("buyer", initial_balance=10)
        seller = AgentCredAgent("seller", initial_balance=0)

        with self.assertRaises(InsufficientFundsError):
            buyer.pay_for_completed_task(
                recipient=seller,
                amount=25,
                category="labeling-task",
                details="Seller completed labeling task",
            )

        self.assertEqual(buyer.wallet.balance, Decimal("10"))
        self.assertEqual(seller.wallet.balance, Decimal("0"))
        self.assertEqual(buyer.wallet.history, ())
        self.assertEqual(seller.wallet.history, ())
        self.assertEqual(seller.reputation.history, ())

    def test_pay_for_completed_task_invalid_amount_does_not_record_reputation(self):
        invalid_amounts = (-1, 0, float("nan"), float("inf"), float("-inf"))

        for amount in invalid_amounts:
            with self.subTest(amount=amount):
                buyer = AgentCredAgent("buyer", initial_balance=100)
                seller = AgentCredAgent("seller", initial_balance=0)

                with self.assertRaises(InvalidTransferAmountError):
                    buyer.pay_for_completed_task(
                        recipient=seller,
                        amount=amount,
                        category="labeling-task",
                        details="Seller completed labeling task",
                    )

                self.assertEqual(buyer.wallet.balance, Decimal("100"))
                self.assertEqual(seller.wallet.balance, Decimal("0"))
                self.assertEqual(buyer.wallet.history, ())
                self.assertEqual(seller.wallet.history, ())
                self.assertEqual(seller.reputation.history, ())


if __name__ == "__main__":
    unittest.main()
