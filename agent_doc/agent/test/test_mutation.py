import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


DIRECTORY = Path(__file__).resolve().parent


class MutationEvidenceTests(unittest.TestCase):
    def run_probe(self, syntax_body):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'agent_runtime').mkdir()
            (root / 'agent_runtime/core.py').write_text('VALUE = 1\n')
            shutil.copyfile(DIRECTORY / 'mutation.py', root / 'mutation.py')
            checker = "import os\nfrom pathlib import Path\ns = (Path(os.environ['AGENT_TEST_PROJECT_ROOT']) / 'agent_runtime/core.py').read_text()\n"
            checker += "if 'broken' in s:\n" + syntax_body
            checker += "elif '\\nimport scripts.project_test\\n' in s:\n print('core must not import CLI scripts')\n raise SystemExit(1)\n"
            (root / 'compile_structure.py').write_text(checker)
            return subprocess.run([sys.executable, '-B', str(root / 'mutation.py')],
                env={**os.environ, 'AGENT_TEST_PROJECT_ROOT': str(root)},
                capture_output=True, text=True, timeout=20)

    def test_checker_crash_is_not_mutation_detection(self):
        result = self.run_probe(" raise RuntimeError('checker crashed')\n")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_unrelated_rejection_is_not_mutation_detection(self):
        result = self.run_probe(" print('unrelated rejection')\n raise SystemExit(1)\n")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_diagnostic_followed_by_crash_is_not_detection(self):
        result = self.run_probe(" print('compile failure: invalid syntax')\n raise RuntimeError('checker crashed')\n")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_target_diagnostics_are_accepted(self):
        result = self.run_probe(" print('compile failure: invalid syntax')\n raise SystemExit(1)\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
