import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'plugins/research-assistant/skills/research-implement-optimize/scripts/experiment.py'
spec = importlib.util.spec_from_file_location('experiment_fixture', SCRIPT)
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)


class ExperimentTests(unittest.TestCase):
    def cli(self, *args, ok=True):
        p = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True, timeout=30)
        self.assertEqual(p.returncode == 0, ok, p.stderr)
        return json.loads(p.stdout) if ok else p.stderr

    def test_default_probe_has_no_gpu_side_effect(self):
        with patch.object(e.subprocess, 'run', side_effect=AssertionError('no process')):
            self.assertEqual(e.probe()['gpu'], 'not_queried')

    def test_gpu_failure_is_unknown(self):
        with patch.object(e.subprocess, 'run', side_effect=FileNotFoundError):
            self.assertEqual(e.probe(True)['gpu']['devices']['status'], 'unknown')

    def test_gpu_never_runs(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                e.run({'device': 'gpu'}, d, 'no-gpu')
            self.assertEqual(list(Path(d).iterdir()), [])

    def test_plan_caps_and_does_not_reserve(self):
        p = e.plan({'workers': 8}, {'affinity_count': 2})
        self.assertEqual(p['workers'], 2)
        self.assertEqual(p['reservation'], 'none')

    def test_schema_budget(self):
        for c in [{'workers': True}, {'seed': -1}, {'samples': 0}, {'oops': 1},
                  {'mode': 'performance', 'workers': 2}, {'size': 100000, 'samples': 1000}]:
            with self.subTest(c=c), self.assertRaises(ValueError):
                e.config(c)
        for text in ['{"seed":1,"seed":2}', '{"seed":NaN}']:
            with self.assertRaises(ValueError):
                e.parse(text)

    def test_backoff_retries_only_pending(self):
        calls = []
        def invoke(xs):
            calls.append(xs)
            if len(xs) > 2:
                raise MemoryError()
            return xs
        chunks = list(e.batches(list(range(7)), 4, invoke))
        self.assertEqual([v for rows, _ in chunks for v in rows], list(range(7)))
        self.assertEqual(chunks[0][1], [{'event': 'oom_backoff', 'from_batch_size': 4}])
        self.assertEqual(calls[:2], [[0, 1, 2, 3], [0, 1]])

    def test_failure_not_swallowed(self):
        for error in [MemoryError, RuntimeError]:
            with self.assertRaises(error):
                list(e.batches([1], 1, lambda xs: (_ for _ in ()).throw(error())))
        with self.assertRaises(ValueError):
            list(e.batches([1], 1, lambda xs: []))

    def test_rows_identity_and_completeness(self):
        c = e.config({'samples': 2})
        row = e.sample((0, c['size'], c['seed']))
        for rows in [{}, [row, row], [row | {'value': -1}], [row | {'id': True}]]:
            with self.assertRaises(ValueError):
                e.validate_rows(rows, c)
        with self.assertRaises(ValueError):
            e.validate_rows([row], c, complete=True)
        # Resume/checkpoint validation uses O(samples) closed form, no workload loops.
        with patch.object(e, 'sample', side_effect=AssertionError('replayed workload')):
            e.validate_rows([row], c)

    def test_real_cpu_parallel_resume_and_immutable_outputs(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cfg = root / 'config.json'
            cfg.write_text(json.dumps({'workers': 2, 'samples': 7, 'size': 20, 'batch_size': 3}))
            a = self.cli('run', '--config', cfg, '--output', root, '--run-id', 'first')
            checkpoint = root / 'first/checkpoint-0003.json'
            old = checkpoint.read_bytes()
            b = self.cli('run', '--config', cfg, '--output', root, '--run-id', 'resumed', '--resume-from', checkpoint)
            self.assertEqual(a['rows'], b['rows'])
            self.assertEqual(b['metric']['correct'], 7)
            self.assertEqual(checkpoint.read_bytes(), old)
            self.cli('run', '--config', cfg, '--output', root, '--run-id', 'first', ok=False)
            self.cli('run', '--config', cfg, '--output', root, '--run-id', '../escape', ok=False)
            for key, value in [('schema', 99), ('runner_sha256', 'wrong'), ('config_sha256', 'wrong'), ('rows_sha256', 'wrong')]:
                broken = json.loads(old)
                broken[key] = value
                bad = root / 'bad.json'
                bad.write_text(json.dumps(broken))
                self.cli('run', '--config', cfg, '--output', root, '--run-id', 'bad-'+key, '--resume-from', bad, ok=False)
                self.assertFalse((root / ('bad-'+key)).exists())

    def test_performance_serial_raw_statistics(self):
        r = e.performance(e.config({'mode': 'performance', 'size': 20, 'repeats': 5}))
        self.assertEqual(len(r['steady_pairs_ns']), 5)
        self.assertIn('not process cold-start', r['first_call_note'])
        self.assertIn('uncontrolled', r['claim'])
        self.assertGreaterEqual(r['summary']['candidate']['stdev_ns'], 0)


if __name__ == '__main__':
    unittest.main()
