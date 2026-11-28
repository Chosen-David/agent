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

    def test_independent_resource_budgets(self):
        from agent_runtime.storage_budget import storage_budget
        common=dict(disk_bytes=1, inodes=1,cpu_bytes=1,pinned_bytes=1,gpu_bytes=20)
        p=dict(available=dict(cpu_bytes=50,pinned_bytes=50,gpu_bytes=10),
               phases=[['staging']],allocations={'staging':common})
        result=storage_budget('.',p)
        self.assertEqual(result['limiting_or_unknown'],['gpu_bytes'])

    def test_watermarks_and_external_quota(self):
        p=plan('.', 'q', 'profile', 10, 0, 200, 0, quota_free_bytes=150)
        self.assertFalse(p['fits'])
        p=plan('.', 'q', 'profile', 10, 0, 1, 0, watermarks=(.001,.002,.003,.004))
        self.assertEqual(p['pressure'],'emergency')
        self.assertFalse(p['fits'])
