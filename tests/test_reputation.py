import unittest
import json

from agentcred import Reputation


class ReputationTests(unittest.TestCase):
    def test_reputation_updates_after_success_and_failure(self):
        reputation = Reputation()
        self.assertEqual(reputation.score, 50.0)

        completed = reputation.record_completed("trade")
        self.assertEqual(reputation.score, 55.0)
        self.assertEqual(reputation.completed_count, 1)

        failed = reputation.record_failed("job")
        self.assertEqual(reputation.score, 45.0)
        self.assertEqual(reputation.failed_count, 1)
        self.assertEqual(reputation.history, (completed, failed))

    def test_event_ids_exist_and_are_unique(self):
        reputation = Reputation()

        first = reputation.record_completed()
        second = reputation.record_failed()

        self.assertTrue(first.event_id)
        self.assertTrue(second.event_id)
        self.assertNotEqual(first.event_id, second.event_id)

    def test_event_can_link_to_wallet_transaction(self):
        reputation = Reputation()

        event = reputation.record_completed(
            "task", transaction_id="transaction-123"
        )

        self.assertEqual(event.transaction_id, "transaction-123")

    def test_event_can_exist_without_wallet_transaction(self):
        event = Reputation().record_completed("task")

        self.assertIsNone(event.transaction_id)

    def test_record_void_appends_neutral_event(self):
        reputation = Reputation()
        score = reputation.score

        event = reputation.record_void("prediction", details="market refunded")

        self.assertEqual(event.outcome, "void")
        self.assertEqual(event.category, "prediction")
        self.assertEqual(event.details, "market refunded")
        self.assertEqual(reputation.history, (event,))
        self.assertEqual(reputation.score, score)
        self.assertEqual(reputation.completed_count, 0)
        self.assertEqual(reputation.failed_count, 0)

    def test_record_void_can_link_to_wallet_transaction(self):
        reputation = Reputation()

        event = reputation.record_void(
            "prediction", transaction_id="transaction-void"
        )

        self.assertEqual(event.transaction_id, "transaction-void")

    def test_void_event_json_round_trip(self):
        reputation = Reputation()
        event = reputation.record_void(
            "prediction",
            details="refunded market",
            transaction_id="transaction-void",
        )

        restored = Reputation.from_json(reputation.to_json())

        self.assertEqual(restored.to_dict(), reputation.to_dict())
        self.assertEqual(restored.score, 50.0)
        self.assertEqual(restored.completed_count, 0)
        self.assertEqual(restored.failed_count, 0)
        self.assertEqual(restored.history[0].event_id, event.event_id)
        self.assertEqual(restored.history[0].outcome, "void")
        self.assertEqual(restored.history[0].transaction_id, "transaction-void")
        self.assertEqual(restored.history[0].created_at, event.created_at)

    def test_reputation_serialization(self):
        reputation = Reputation()
        event = reputation.record_completed(
            "task", details="on time", transaction_id="transaction-123"
        )

        exported = reputation.to_dict()

        self.assertEqual(exported["score"], 55.0)
        self.assertEqual(exported["completed_count"], 1)
        self.assertEqual(exported["failed_count"], 0)
        self.assertEqual(exported["history"][0]["event_id"], event.event_id)
        self.assertEqual(
            exported["history"][0]["transaction_id"], "transaction-123"
        )
        self.assertEqual(json.loads(reputation.to_json()), exported)

    def test_reputation_json_round_trip_with_transaction_link(self):
        reputation = Reputation()
        event = reputation.record_completed(
            "task", details="on time", transaction_id="transaction-123"
        )
        reputation.record_failed("review", details="needs revision")

        restored = Reputation.from_json(reputation.to_json())

        self.assertEqual(restored.to_dict(), reputation.to_dict())
        self.assertEqual(restored.score, reputation.score)
        self.assertEqual(restored.completed_count, 1)
        self.assertEqual(restored.failed_count, 1)
        self.assertEqual(restored.history[0].event_id, event.event_id)
        self.assertEqual(restored.history[0].transaction_id, "transaction-123")
        self.assertEqual(restored.history[0].created_at, event.created_at)

    def test_restored_reputation_can_record_events(self):
        reputation = Reputation()
        reputation.record_completed("initial")
        restored = Reputation.from_json(reputation.to_json())

        event = restored.record_failed("follow-up", details="missed deadline")

        self.assertEqual(restored.completed_count, 1)
        self.assertEqual(restored.failed_count, 1)
        self.assertEqual(restored.history[-1], event)
        self.assertEqual(restored.score, 45.0)


if __name__ == "__main__":
    unittest.main()
