import unittest

from agentcred import Identity


class IdentityTests(unittest.TestCase):
    def test_identity_is_created_and_deterministic(self):
        first = Identity("researcher", {"model": "local"})
        second = Identity("researcher", {"model": "local"})

        self.assertEqual(first.agent_id, second.agent_id)
        self.assertEqual(first.address, second.address)
        self.assertEqual(first.name, "researcher")
        self.assertEqual(first.metadata, {"model": "local"})
        self.assertTrue(first.address.startswith("0x"))


if __name__ == "__main__":
    unittest.main()
