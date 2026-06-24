import unittest
import json
from decimal import Decimal

from agentcred import (
    InsufficientFundsError,
    InvalidTransferAmountError,
    Wallet,
)


class WalletTests(unittest.TestCase):
    def test_transfer_succeeds_and_records_history(self):
        sender = Wallet(100, address="sender")
        recipient = Wallet(25, address="recipient")

        transaction = sender.send(recipient, 30, memo="test")

        self.assertEqual(sender.balance, Decimal("70"))
        self.assertEqual(recipient.balance, Decimal("55"))
        self.assertEqual(transaction.amount, Decimal("30"))
        self.assertEqual(sender.history, (transaction,))
        self.assertEqual(recipient.history, (transaction,))

    def test_overdraft_fails_without_mutating_wallets(self):
        sender = Wallet(10)
        recipient = Wallet(5)

        with self.assertRaises(InsufficientFundsError):
            sender.send(recipient, 11)

        self.assertEqual(sender.balance, Decimal("10"))
        self.assertEqual(recipient.balance, Decimal("5"))
        self.assertEqual(sender.history, ())

    def test_invalid_transfer_amounts_fail(self):
        invalid_amounts = (-1, 0, float("nan"), float("inf"), float("-inf"))
        for amount in invalid_amounts:
            with self.subTest(amount=amount):
                with self.assertRaises(InvalidTransferAmountError):
                    Wallet().send(Wallet(), amount)

    def test_transaction_ids_exist_and_are_unique(self):
        sender = Wallet(100)
        recipient = Wallet(10)

        first = sender.send(recipient, 10)
        second = sender.send(recipient, 10)

        self.assertTrue(first.transaction_id)
        self.assertTrue(second.transaction_id)
        self.assertNotEqual(first.transaction_id, second.transaction_id)

    def test_wallet_serialization(self):
        sender = Wallet(100, address="sender")
        recipient = Wallet(10, address="recipient")
        transaction = sender.send(recipient, "12.50", memo="paid task")

        exported = sender.to_dict()

        self.assertEqual(exported["address"], "sender")
        self.assertEqual(exported["balance"], "87.50")
        self.assertEqual(exported["history"][0]["amount"], "12.50")
        self.assertEqual(
            exported["history"][0]["transaction_id"],
            transaction.transaction_id,
        )
        self.assertEqual(json.loads(sender.to_json()), exported)

    def test_wallet_json_round_trip_with_transaction_history(self):
        sender = Wallet(100, address="sender")
        recipient = Wallet(10, address="recipient")
        transaction = sender.send(recipient, "12.50", memo="paid task")

        restored = Wallet.from_json(sender.to_json())

        self.assertEqual(restored.to_dict(), sender.to_dict())
        self.assertEqual(restored.balance, Decimal("87.50"))
        self.assertEqual(restored.history[0].amount, Decimal("12.50"))
        self.assertEqual(
            restored.history[0].transaction_id, transaction.transaction_id
        )
        self.assertEqual(restored.history[0].created_at, transaction.created_at)

    def test_restored_wallet_can_transfer_credits(self):
        restored = Wallet.from_json(Wallet(40, address="restored").to_json())
        recipient = Wallet(0, address="recipient")

        transaction = restored.send(recipient, 15, memo="new transfer")

        self.assertEqual(restored.balance, Decimal("25"))
        self.assertEqual(recipient.balance, Decimal("15"))
        self.assertEqual(restored.history, (transaction,))


if __name__ == "__main__":
    unittest.main()
