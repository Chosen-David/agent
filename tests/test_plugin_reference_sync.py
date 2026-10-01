import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PluginReferenceSyncTests(unittest.TestCase):
    def test_generated_plugin_references_are_current(self):
        run = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "sync_plugin_references.py"), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
