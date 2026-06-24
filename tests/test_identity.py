import unittest
import json

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

    def test_identity_serialization(self):
        identity = Identity("researcher", {"model": "local"})

        exported = identity.to_dict()

        self.assertEqual(exported["name"], "researcher")
        self.assertEqual(exported["agent_id"], identity.agent_id)
        self.assertEqual(exported["address"], identity.address)
        self.assertEqual(exported["metadata"], {"model": "local"})
        self.assertEqual(json.loads(identity.to_json()), exported)

    def test_identity_json_round_trip(self):
        identity = Identity("researcher", {"model": "local", "level": 2})

        restored = Identity.from_json(identity.to_json())

        self.assertEqual(restored.to_dict(), identity.to_dict())
        self.assertEqual(restored.name, identity.name)
        self.assertEqual(restored.agent_id, identity.agent_id)
        self.assertEqual(restored.address, identity.address)
        self.assertEqual(restored.metadata, identity.metadata)


if __name__ == "__main__":
    unittest.main()
