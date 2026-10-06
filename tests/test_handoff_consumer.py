"""Consumer context comes from the trusted caller, not a producer assertion."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.validate_handoff import validate


class ConsumerBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root/'result').write_bytes(b'generic synthetic payload')
        self.request = dict(schema_version=1, input_version='batch32:v1', tasks=[])
        self.record = dict(schema_version=1, run_id='synthetic', role='writer',
            input_version='batch32:v1', status='completed', limitations=[],
            artifacts=[dict(id='r', path='result', sha256=hashlib.sha256((self.root/'result').read_bytes()).hexdigest())],
            checks=[dict(criterion='intact', status='pass', artifact_ids=['r'])])

    def test_matching_consumer_accepts_and_mismatch_rejects(self):
        self.assertEqual(validate(self.record, self.root, True, expected_input_version='batch32:v1', consumer_request=self.request), [])
        self.assertIn('consumer input version mismatch',
                      validate(self.record, self.root, True, expected_input_version='batch64:v2'))

    def test_no_consumer_is_unverified_even_with_inline_claim(self):
        self.record['expected_input_version'] = 'batch32:v1'
        self.assertIn('unverified: expected consumer input version required for completion',
                      validate(self.record, self.root, True))
        self.assertEqual(validate(self.record, self.root), [])

    def test_holdout_exact_identifiers_and_malformed_intent(self):
        self.record['input_version'] = '数据:revision-9'
        self.request['input_version'] = '数据:revision-9'
        self.assertEqual(validate(self.record, self.root, True, expected_input_version='数据:revision-9', consumer_request=self.request), [])
        for wrong in ('数据:revision-8', '数据:revision-9 ', '', ' ', False):
            with self.subTest(wrong=wrong):
                self.assertTrue(validate(self.record, self.root, True, expected_input_version=wrong))

    def test_cli_independent_version_and_unverified_default(self):
        path = self.root/'handoff.json'; path.write_text(json.dumps(self.record))
        request_path = self.root/'request.json'; request_path.write_text(json.dumps(self.request))
        script = Path(__file__).resolve().parents[1]/'scripts/validate_handoff.py'
        for extra, code, complete in [([], 0, False), (['--require-complete'], 1, False),
            (['--require-complete', '--expected-input-version', 'batch64:v2'], 1, False),
            (['--require-complete', '--expected-input-version', 'batch32:v1'], 1, False),
            (['--require-complete', '--request', str(request_path)], 0, True)]:
            result = subprocess.run([sys.executable, str(script), str(path), '--root', str(self.root), *extra],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, code, result.stderr)
            self.assertEqual(json.loads(result.stdout)['completion_verified'], complete)


if __name__ == '__main__':
    unittest.main()
