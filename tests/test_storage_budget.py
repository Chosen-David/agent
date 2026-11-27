import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class StorageBudgetTests(unittest.TestCase):
    def run_budget(self, allocations, phases, available=None):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'plan.json'
            path.write_text(json.dumps(dict(allocations=allocations, phases=phases,
                                            available=available or {})))
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/result_store.py'),
                                     '--root', tmp, 'budget', '--plan', str(path)],
                                    capture_output=True, text=True, check=False)
            return result.returncode, json.loads(result.stdout)

    def test_concurrent_rank_and_staging_overlap(self):
        shard = dict(disk_bytes=12, inodes=1, cpu_bytes=4, pinned_bytes=2)
        code, result = self.run_budget(dict(a=shard, b=shard), [['a'], ['a', 'b']],
                                       dict(cpu_bytes=8, pinned_bytes=3))
        self.assertEqual(code, 2)
        self.assertIn('pinned_bytes', result['limiting_or_unknown'])
        self.assertEqual(result['estimated_peak_increment'],
                         dict(disk_bytes=24, inodes=2, cpu_bytes=8, pinned_bytes=4))

    def test_shortfall_and_missing_phase(self):
        shard = dict(disk_bytes=2**80, inodes=0, cpu_bytes=0, pinned_bytes=0)
        code, result = self.run_budget(dict(a=shard), [['a']])
        self.assertEqual(code, 2)
        self.assertEqual(result['limiting_or_unknown'], ['disk_bytes'])
        code, result = self.run_budget(dict(a=shard), [[]])
        self.assertEqual(code, 2)
        self.assertIn('unaccounted allocation', result['error'])
