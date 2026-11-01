"""Regression modules must load without another test changing sys.path first."""
import os
from pathlib import Path
import subprocess
import sys
import unittest


class FixtureImportTests(unittest.TestCase):
    def test_fixture_consumers_import_in_fresh_processes(self):
        root = Path(__file__).resolve().parents[1]
        modules = (
            'agent_doc_namespace', 'communication_output', 'communication_snapshot',
            'contamination', 'handoff_knowledge_snapshot', 'memory_tables',
            'result_dispatch_freshness', 'result_reuse_acceptance', 'result_store',
            'selective_context', 'semantic_acceptance', 'serial_recovery',
        )
        env = dict(os.environ)
        env.pop('PYTHONPATH', None)
        for name in modules:
            with self.subTest(module=name):
                # The paper-delivery CLI fixture retains its explicit script bootstrap.
                prefix = [str(root / 'scripts'), str(root)] if name == 'semantic_acceptance' else []
                code = ('import importlib, sys; before = list(sys.path); '
                        f'importlib.import_module("tests.test_{name}"); '
                        f'assert sys.path == {prefix!r} + before, "unexpected import path mutation"')
                result = subprocess.run([sys.executable, '-B', '-c', code], cwd=root,
                                        env=env, capture_output=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr.decode('utf-8', 'replace'))
