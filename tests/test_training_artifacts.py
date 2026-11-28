from pathlib import Path
import tempfile
import unittest

from agent_runtime.training_artifacts import plan


class TrainingArtifactsTest(unittest.TestCase):
    def test_alias_and_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            alias = root / "alias"
            alias.symlink_to(root, target_is_directory=True)
            p = plan(alias / "next", "run", "convergence", 1000, 100, 10, 0)
            self.assertEqual(p["physical_output"], str(root / "next"))
            self.assertEqual((p["interval"], p["estimated_bytes"]), (500, 210))
            self.assertFalse((root / "next").exists())
            self.assertFalse(plan(root, "run", "recovery", 100, 10**25, 0, 0)["fits"])

    def test_default_lightweight(self):
        for policy in ("profile", "spectral", "correctness"):
            p = plan(".", "run", policy, 100, 0, 512, 0)
            self.assertEqual(p["checkpoint_count"], 0)
            self.assertFalse(p["save_final"])

    def test_incomplete_budget(self):
        with self.assertRaises(ValueError):
            plan(".", "run", "final", 1000, 0, 0, 0)
