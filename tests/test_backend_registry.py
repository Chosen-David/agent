import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config" / "backend_registry.json"


class BackendRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.backends = cls.data["backends"]
        cls.by_id = {item["id"]: item for item in cls.backends}

    def test_registry_has_unique_ids_and_required_fields(self):
        self.assertEqual(len(self.by_id), len(self.backends))
        required = {"id", "name", "repo", "category", "adoption", "use_when", "avoid_when", "strengths", "handoff_to", "detect"}
        for item in self.backends:
            self.assertTrue(required <= item.keys(), item["id"])
            self.assertTrue(item["repo"].startswith("https://github.com/"), item["id"])

    def test_core_specialists_are_registered(self):
        expected = {"gpt-researcher", "paperqa2", "storm", "openhands", "ai-scientist", "journeypilot"}
        self.assertTrue(expected <= set(self.by_id))

    def test_high_autonomy_backend_is_not_automatic(self):
        ai_scientist = self.by_id["ai-scientist"]
        self.assertEqual(ai_scientist["adoption"], "manual_only")
        requirements = set(ai_scientist.get("requirements", []))
        self.assertIn("explicit_user_authorization", requirements)
        self.assertIn("sandbox_or_container", requirements)
        self.assertIn("resource_budget", requirements)

    def test_travel_runtime_does_not_replace_acceptance_layer(self):
        journey = self.by_id["journeypilot"]
        self.assertEqual(journey["adoption"], "optional_runtime")
        self.assertIn("travel-planner", journey["handoff_to"])

    def test_runtime_is_optional(self):
        for backend_id in ("openai-agents-sdk", "langgraph"):
            self.assertEqual(self.by_id[backend_id]["adoption"], "optional_runtime")


if __name__ == "__main__":
    unittest.main()
