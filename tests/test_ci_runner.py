"""The diagnostic runner must preserve unittest selection and failure semantics."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/run_ci_tests.py"
FIXTURE = '''import unittest
class Cases(unittest.TestCase):
    def setUp(self): print("SETUP")
    def tearDown(self): print("TEARDOWN")
    def test_a_pass(self): print("BODY")
    def test_b_fail(self): self.fail("intentional failure")
    @unittest.skip("fixture skip")
    def test_c_skip(self): pass
    def test_d_error(self): raise RuntimeError("intentional error")
    @unittest.expectedFailure
    def test_e_expected_fail(self): self.fail("fixture expected failure")
class Interrupted(unittest.TestCase):
    def test_interrupt(self): raise KeyboardInterrupt
'''


class CIRunnerTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / "fixture_ci.py").write_text(FIXTURE, encoding="utf-8")

    def invoke(self, *args, diagnostic=True):
        command = [sys.executable, "-B"] + (
            [str(RUNNER)] if diagnostic else ["-m", "unittest"])
        return subprocess.run(command + list(args), cwd=self.root,
                              capture_output=True, text=True, encoding="utf-8",
                              env=dict(os.environ, PYTHONIOENCODING="utf-8"), timeout=15)

    @staticmethod
    def events(run):
        return [json.loads(line[len("CI_TEST "):]) for line in run.stderr.splitlines()
                if line.startswith("CI_TEST ")]

    def test_pass_skip_failure_error_and_failfast_match_standard_cli(self):
        for args in [("fixture_ci.Cases.test_a_pass",),
                     ("fixture_ci.Cases.test_c_skip",),
                     ("fixture_ci.Cases.test_b_fail",),
                     ("fixture_ci.Cases.test_d_error",),
                     ("fixture_ci.Cases.test_e_expected_fail",),
                     ("fixture_ci.Cases", "-f"), ("fixture_ci.Cases", "-b")]:
            with self.subTest(args=args):
                original, observed = self.invoke(*args, diagnostic=False), self.invoke(*args)
                self.assertEqual(observed.returncode, original.returncode)
                self.assertEqual(observed.stdout, original.stdout)
                for label in ("Ran 1 test", "Ran 2 tests", "Ran 5 tests", "FAILED", "OK",
                              "skipped=1", "expected failures=1", "intentional failure", "intentional error"):
                    self.assertEqual(label in observed.stderr, label in original.stderr, label)
                events = self.events(observed)
                starts = [e["test"] for e in events if e["event"] == "start"]
                ends = [e for e in events if e["event"] == "finish"]
                self.assertEqual(starts, [e["test"] for e in ends])
                self.assertTrue(starts)
                for e in ends:
                    self.assertGreaterEqual(e["wall_seconds"], 0)
                    self.assertGreaterEqual(e["process_cpu_seconds"], 0)

    def test_discovery_and_load_errors_keep_standard_exit_codes(self):
        for args in [("discover", "-s", ".", "-p", "fixture_ci.py", "-v"),
                     ("missing_ci_module",), ("--invalid-ci-option",)]:
            with self.subTest(args=args):
                original, observed = self.invoke(*args, diagnostic=False), self.invoke(*args)
                self.assertEqual(observed.returncode, original.returncode)
                self.assertEqual("FAILED" in observed.stderr, "FAILED" in original.stderr)

    def test_interruption_is_not_reported_as_success(self):
        args = ("fixture_ci.Interrupted.test_interrupt",)
        original, observed = self.invoke(*args, diagnostic=False), self.invoke(*args)
        self.assertEqual(observed.returncode, original.returncode)
        self.assertNotEqual(observed.returncode, 0)
        self.assertIn("KeyboardInterrupt", observed.stderr)
        self.assertNotIn("\nOK", observed.stderr)
        self.assertEqual([e["event"] for e in self.events(observed)], ["run", "start", "finish"])
