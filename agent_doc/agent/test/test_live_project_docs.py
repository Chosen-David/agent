from tests.document_fixture import DocumentFixtureCase
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(os.environ["AGENT_TEST_PROJECT_ROOT"])
ENTRY = ROOT / "scripts/project_docs.py"


class LiveProjectDocsTests(DocumentFixtureCase):
    def test_real_cli_initialization_repeat_and_missing_target(self):
        evidence = []
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "actual-project"
            project.mkdir()
            def invoke(target, command):
                argv = [sys.executable, "-B", str(ENTRY), "--root", str(target), command]
                result = subprocess.run(argv, cwd=base, capture_output=True, text=True, timeout=15)
                evidence.append({"argv": argv, "exit": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
                return result
            health = subprocess.run([sys.executable, "-B", str(ENTRY), "--help"], capture_output=True, text=True, timeout=15)
            self.assertEqual(health.returncode, 0, health.stderr)
            self.assertFalse((project / "agent_doc").exists())
            first = invoke(project, "init")
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            task = project / "agent_doc/task/TASK.md"
            self.assertTrue(task.is_file())
            self.assertEqual(list((project / "agent_doc/guide").iterdir()), [])
            before = {str(p.relative_to(project)): p.read_bytes() for p in project.rglob("*") if p.is_file()}
            again = invoke(project, "init")
            self.assertEqual(again.returncode, 0, again.stdout + again.stderr)
            self.assertEqual(before, {str(p.relative_to(project)): p.read_bytes() for p in project.rglob("*") if p.is_file()})
            missing = base / "missing"
            rejected = invoke(missing, "init")
            self.assertEqual(rejected.returncode, 2)
            self.assertIn("existing directory", rejected.stdout)
            self.assertFalse(missing.exists())
            self.assertFalse((base / "agent_doc").exists())
        self.assertFalse(base.exists())
        print(json.dumps({"live_project_docs": evidence, "scratch_removed": True}))
