"""Exercise the public CLI with a real sibling Git repository and external tests."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

RUNNER = Path(os.environ["AGENT_TEST_PROJECT_ROOT"]) / "scripts/project_test.py"


class ExternalTestEntryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.target = self.base / "actual-code"
        self.target.mkdir()
        self.workflow = self.base / "agent"
        self.suite = self.workflow / "agent_doc/example/test"
        self.suite.mkdir(parents=True)
        self.git("init", "-q")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "Fixture")
        self.git("remote", "add", "origin", "https://example.invalid/example.git")
        (self.target / "product.py").write_text("VALUE = 42\n")
        self.git("add", "product.py")
        self.git("commit", "-qm", "fixture")
        (self.suite / "suite.json").write_text(json.dumps({"version": 1, "origin": "https://example.invalid/example.git", "checks": [{"id": "unit", "kind": "unittest", "path": ".", "timeout_seconds": 20, "requirement": "prompt: external tests"}]}))

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.target), *args], stderr=subprocess.PIPE)

    def check(self, body, expected, *, target=None):
        (self.suite / "test_product.py").write_text("import unittest\nimport product\nclass Checks(unittest.TestCase):\n" + body)
        output = self.base / "evidence"
        result = subprocess.run([sys.executable, "-B", str(RUNNER), "--workflow-root", str(self.workflow),
            "--project", "example", "--target", str(target or self.target), "--output", str(output)],
            capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        self.receipt = json.loads(result.stdout) if result.stdout else None
        return json.loads((output / "report.json").read_text()) if (output / "report.json").exists() else None

    def test_sibling_target_import_and_no_target_artifacts(self):
        report = self.check(" def test_value(self): self.assertEqual(product.VALUE, 42)\n", 0)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(set(self.receipt), {"status", "report"})
        self.assertEqual(report["before"], report["after"])
        self.assertEqual(self.git("status", "--porcelain"), b"")
        self.assertFalse((self.target / "agent_doc").exists())

    def test_real_assertion_failure_is_not_pass(self):
        report = self.check(" def test_value(self): self.assertEqual(product.VALUE, 99)\n", 1)
        self.assertEqual(report["checks"][0]["result"]["failures"], 1)
        self.assertEqual(self.receipt["checks"][0]["result"]["failures"], 1)
        self.assertEqual(self.receipt["checks"][0]["status"], "fail")
        self.assertTrue(Path(self.receipt["checks"][0]["log"]).is_file())

    def test_empty_suite_is_not_pass(self):
        report = self.check(" pass\n", 1)
        self.assertEqual(report["checks"][0]["result"]["tests"], 0)

    def test_skipped_required_check_is_not_pass(self):
        report = self.check(" @unittest.skip('missing backend')\n def test_value(self): pass\n", 1)
        self.assertEqual(report["checks"][0]["result"]["skipped"], 1)

    def test_wrong_repository_is_blocked_before_test(self):
        self.git("remote", "set-url", "origin", "https://example.invalid/other.git")
        self.assertIsNone(self.check(" def test_value(self): self.fail()\n", 2))

    def test_subdirectory_is_not_repository_root(self):
        nested = self.target / "nested"
        nested.mkdir()
        self.assertIsNone(self.check(" def test_value(self): pass\n", 2, target=nested))

    def test_code_change_during_test_invalidates_pass(self):
        report = self.check(" def test_value(self):\n  from pathlib import Path\n  Path('product.py').write_text('VALUE = 43\\n')\n", 1)
        self.assertFalse(report["stable_inputs"])
        self.assertFalse(self.receipt["stable_inputs"])
        self.assertEqual(self.receipt["status"], "fail")

    def test_expected_failure_is_not_completed_check(self):
        report = self.check(" @unittest.expectedFailure\n def test_value(self): self.fail()\n", 1)
        self.assertEqual(report["checks"][0]["result"]["expected_failures"], 1)

    def configure(self, checks):
        (self.suite / "suite.json").write_text(json.dumps({"version": 1,
            "origin": "https://example.invalid/example.git", "checks": checks}))

    def script(self, identity, kind, content, timeout=10):
        path = identity + (".sh" if kind == "shell" else ".py")
        (self.suite / path).write_text(content)
        return {"id": identity, "kind": kind, "path": path,
                "timeout_seconds": timeout, "requirement": "prompt: serial lightweight checks"}

    def test_shell_failure_prevents_later_check(self):
        self.configure([self.script("lint", "shell", "exit 7\n"),
                        self.script("later", "python", "raise RuntimeError('must not run')\n")])
        report = self.check(" pass\n", 1)
        self.assertEqual([item["status"] for item in report["checks"]], ["fail", "not-run"])
        self.assertEqual(report["checks"][0]["returncode"], 7)
        self.assertFalse((self.base / "evidence/later.log").exists())
        self.assertEqual(self.receipt["checks"][1], {"id": "later", "status": "not-run"})

    def test_python_and_shell_checks_execute_in_order(self):
        self.configure([self.script("lint", "shell", 'test -f "$AGENT_TEST_PROJECT_ROOT/product.py"\n'),
                        self.script("compile", "python", "import product; assert product.VALUE == 42\n")])
        report = self.check(" pass\n", 0)
        self.assertEqual([item["status"] for item in report["checks"]], ["pass", "pass"])

    def test_timeout_is_blocked_and_does_not_advance(self):
        self.configure([self.script("slow", "python", "import time; time.sleep(5)\n", 1),
                        self.script("later", "python", "raise RuntimeError('must not run')\n")])
        report = self.check(" pass\n", 1)
        self.assertEqual(report["status"], "blocked")
        self.assertEqual([item["status"] for item in report["checks"]], ["blocked", "not-run"])

    def test_python_crash_is_failure(self):
        self.configure([self.script("crash", "python", "raise RuntimeError('checker crashed')\n")])
        report = self.check(" pass\n", 1)
        self.assertEqual(report["checks"][0]["status"], "fail")

    def test_explicit_external_document_root_supplies_tests(self):
        external = self.base / 'agent_doc/example'
        external.mkdir(parents=True)
        destination = external / 'test'
        self.suite.rename(destination)
        self.suite = destination
        with patch.dict(os.environ, {'AGENT_DOC_ROOT': str(external)}):
            report = self.check(" def test_value(self): self.assertEqual(product.VALUE, 42)\n", 0)
        self.assertEqual(report['status'], 'pass')
        self.assertFalse((self.target / 'agent_doc').exists())
        self.assertFalse((self.workflow / 'agent_doc/example/test').exists())

    def test_explicit_missing_external_suite_does_not_use_legacy(self):
        external = self.base / 'agent_doc/example'
        with patch.dict(os.environ, {'AGENT_DOC_ROOT': str(external)}):
            self.assertIsNone(self.check(" def test_value(self): self.assertEqual(product.VALUE, 42)\n", 2))

    def test_external_suite_rejects_wrong_product_value(self):
        external = self.base / 'agent_doc/example'
        external.mkdir(parents=True)
        self.suite.rename(external / 'test')
        self.suite = external / 'test'
        with patch.dict(os.environ, {'AGENT_DOC_ROOT': str(external)}):
            report = self.check(" def test_value(self): self.assertEqual(product.VALUE, 99)\n", 1)
        self.assertEqual(report['checks'][0]['result']['failures'], 1)
        self.assertEqual(report['checks'][0]['result']['errors'], 0)

    def test_external_evidence_cannot_write_into_document_tree(self):
        external = self.base / 'agent_doc/example'
        external.mkdir(parents=True)
        self.suite.rename(external / 'test')
        self.suite = external / 'test'
        output = external / 'results/new-evidence'
        environment = dict(os.environ, AGENT_DOC_ROOT=str(external))
        result = subprocess.run([sys.executable, '-B', str(RUNNER), '--workflow-root', str(self.workflow),
            '--project', 'example', '--target', str(self.target), '--output', str(output)],
            env=environment, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertFalse(output.exists())
