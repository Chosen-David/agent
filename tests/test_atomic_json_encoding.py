"""Runtime state JSON must stay UTF-8 even under a non-UTF-8 locale."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AtomicJSONEncodingTests(unittest.TestCase):
    def run_writer(self, path, invalid=False):
        # ASCII-only argv also works when the child cannot decode non-ASCII argv.
        code = (
            "from pathlib import Path; import sys; "
            "from agent_runtime.task_manifest import atomic_json; "
            "atomic_json(Path(sys.argv[1]), "
            "{'reason':'\\u4efb\\u52a1\\u6062\\u590d','symbol':'\\U0001f680'"
            + (",'invalid':float('nan')" if invalid else "") + "})"
        )
        return subprocess.run(
            [sys.executable, '-X', 'utf8=0', '-c', code, str(path)], cwd=ROOT,
            env={**os.environ, 'PYTHONUTF8': '0', 'PYTHONCOERCECLOCALE': '0', 'LC_ALL': 'C'},
            capture_output=True, timeout=20,
        )

    def test_create_and_replace_are_utf8(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'state.json'
            for initial in (None, b'{"old":true}\n'):
                with self.subTest(replacing=initial is not None):
                    if initial is not None:
                        path.write_bytes(initial)
                    result = self.run_writer(path)
                    self.assertEqual(result.returncode, 0, result.stderr.decode('ascii', 'backslashreplace'))
                    self.assertEqual(json.loads(path.read_bytes().decode('utf-8')),
                                     {'reason': '\u4efb\u52a1\u6062\u590d', 'symbol': '\U0001f680'})
                    self.assertEqual(list(path.parent.glob('state.json.*')), [])

    def test_serialization_failure_preserves_previous_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'state.json'
            original = b'{"previous":"accepted"}\n'
            path.write_bytes(original)
            result = self.run_writer(path, invalid=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b'ValueError', result.stderr)
            self.assertNotIn(b'UnicodeEncodeError', result.stderr)
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(list(path.parent.glob('state.json.*')), [])
