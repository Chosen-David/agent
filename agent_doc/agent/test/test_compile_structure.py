from tests.document_fixture import DocumentFixtureCase
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


CHECKER = Path(__file__).with_name('compile_structure.py')


class CompileStructureScopeTests(DocumentFixtureCase):
    def invoke(self, core, nested):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runtime = root / 'agent_runtime'
            (runtime / 'nested').mkdir(parents=True)
            (runtime / 'core.py').write_text(core)
            (runtime / 'nested/core.py').write_text(nested)
            return subprocess.run([sys.executable, '-B', str(CHECKER)],
                env={**os.environ, 'AGENT_TEST_PROJECT_ROOT': str(root)},
                capture_output=True, text=True, timeout=10)

    def test_nested_namesake_is_not_the_root_core_boundary(self):
        result = self.invoke('VALUE = 1\n', 'import scripts.project_test\n')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('compiled 2 Python files', result.stdout)

    def test_root_core_still_rejects_cli_imports(self):
        result = self.invoke('import scripts.project_test\n', 'VALUE = 1\n')
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('core must not import CLI scripts', result.stdout)
        self.assertEqual(result.stderr, '')

    def test_nested_python_still_must_compile(self):
        result = self.invoke('VALUE = 1\n', 'def broken(:\n')
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('compile failure:', result.stdout)
        self.assertEqual(result.stderr, '')
