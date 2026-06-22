import unittest

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


if __name__ == "__main__":
    unittest.main()
