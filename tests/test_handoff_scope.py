"""Consumer-owned scope tests; requests are independent of mutated producer records."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.validate_handoff import validate

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/validate_handoff.py'


class ConsumerScopeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'result.txt').write_bytes(b'synthetic evidence')
        self.request = {'schema_version': 1, 'input_version': 'scope-v2', 'tasks': [
            {'task_id': 'MEASURE'}, {'task_id': 'REVIEW', 'allow_skip': False}]}
        self.record = {
            'schema_version': 1, 'run_id': 'r', 'role': 'worker',
            'input_version': 'scope-v2', 'status': 'completed', 'limitations': [],
            'artifacts': [{'id': 'a', 'path': 'result.txt',
                           'sha256': hashlib.sha256(b'synthetic evidence').hexdigest()}],
            'checks': [{'criterion': 'fixture', 'status': 'pass', 'artifact_ids': ['a']}],
            'tasks': [{'task_id': 'MEASURE', 'status': 'done', 'evidence': ['a']},
                      {'task_id': 'REVIEW', 'status': 'done', 'depends_on': ['MEASURE'], 'evidence': ['a']}]}

    def check(self, record=None, request=None, complete=True):
        return validate(self.record if record is None else record, self.root, complete,
                        consumer_request=self.request if request is None else request)

    def test_complete_scope_preserves_valid_control_and_inputs(self):
        before = copy.deepcopy((self.record, self.request))
        self.assertEqual(self.check(), [])
        self.assertEqual((self.record, self.request), before)

    def test_omitted_required_task_or_entire_list_rejected(self):
        self.record['tasks'].pop()
        self.assertIn('consumer task missing: REVIEW', self.check())
        self.record.pop('tasks')
        self.assertIn('consumer task missing: MEASURE', self.check())

    def test_extra_task_is_not_implicitly_authorized(self):
        self.record['tasks'].append({'task_id': 'EXTRA', 'status': 'done', 'evidence': ['a']})
        self.assertIn('task outside consumer scope: EXTRA', self.check())

    def test_skip_needs_consumer_permission_not_producer_claim(self):
        self.record['tasks'][1].update(status='skipped', reason='producer prefers to skip', allow_skip=True)
        self.assertIn('REVIEW: skip not authorized by consumer', self.check())
        self.request['tasks'][1]['allow_skip'] = True
        self.assertEqual(self.check(), [])
        self.record['tasks'][1]['reason'] = ' '
        self.assertIn('REVIEW: reason/recovery required', self.check())

    def test_authorized_skip_does_not_satisfy_dependency(self):
        self.request['tasks'][0]['allow_skip'] = True
        self.record['tasks'][0].update(status='skipped', reason='optional measurement')
        self.assertIn('REVIEW: done before dependency MEASURE', self.check())

    def test_forged_inline_request_does_not_supply_consumer(self):
        self.record['consumer_request'] = self.request
        self.assertIn('unverified: consumer request required for completion',
                      validate(self.record, self.root, True, expected_input_version='scope-v2'))
        self.assertEqual(validate(self.record, self.root), [])

    def test_explicit_empty_scope_for_single_answer(self):
        self.record.pop('tasks')
        self.request['tasks'] = []
        self.assertEqual(self.check(), [])
        self.request.pop('tasks')
        self.assertIn('consumer request tasks must be an explicit list', self.check())

    def test_malformed_consumer_contracts_fail_without_exceptions(self):
        bad = [[], False, 'scope', {}, dict(self.request, schema_version=True),
               dict(self.request, input_version=' '), dict(self.request, tasks=None),
               dict(self.request, tasks=[False]), dict(self.request, tasks=[{'task_id': []}]),
               dict(self.request, tasks=[{'task_id': 'MEASURE'}, {'task_id': 'MEASURE'}])]
        for flag in (1, 'true', [], None):
            bad.append(dict(self.request, tasks=[{'task_id': 'MEASURE', 'allow_skip': flag}]))
        for request in bad:
            with self.subTest(request=request):
                self.assertTrue(self.check(request=request))

    def test_exact_ids_and_request_revision(self):
        self.request['tasks'][1]['task_id'] = 'REVIEW '
        self.assertIn('consumer task missing: REVIEW ', self.check())
        self.assertIn('task outside consumer scope: REVIEW', self.check())
        self.request['input_version'] = 'scope-v3'
        self.assertIn('consumer input version mismatch', self.check())
        self.assertIn('consumer request conflicts with expected input version',
                      validate(self.record, self.root, True, expected_input_version='scope-v2',
                               consumer_request=self.request))

    def test_partial_is_valid_but_not_complete_and_cannot_hide_scope(self):
        self.record.update(status='partial', limitations=['Review needs input'])
        self.record['tasks'][1].update(status='blocked', reason='need independent review', evidence=[])
        self.assertEqual(self.check(complete=False), [])
        self.assertIn('completion gate: run is not completed', self.check())
        self.record['tasks'].pop()
        self.assertIn('consumer task missing: REVIEW', self.check(complete=False))

    def cli(self, request_text):
        record = self.root / 'handoff.json'
        request = self.root / 'request.json'
        record.write_text(json.dumps(self.record))
        request.write_text(request_text)
        result = subprocess.run([sys.executable, str(SCRIPT), str(record), '--root', str(self.root),
                                 '--require-complete', '--request', str(request)],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.stderr, '')
        return result.returncode, json.loads(result.stdout)

    def test_cli_actual_bytes_scope_and_status_flags(self):
        code, result = self.cli(json.dumps(self.request))
        self.assertEqual(code, 0)
        self.assertTrue(result['completion_verified'])
        self.assertTrue(result['consumer_scope_verified'])
        (self.root / 'result.txt').write_bytes(b'changed')
        code, result = self.cli(json.dumps(self.request))
        self.assertEqual(code, 1)
        self.assertFalse(result['completion_verified'])
        self.assertFalse(result['consumer_scope_verified'])

    def test_cli_null_duplicate_keys_and_invalid_json_are_not_verified(self):
        for payload in ('null', '[1]', '{', '{"tasks":[],"tasks":[{}]}',
                        '{"schema_version":NaN}', '{"tasks":[{"allow_skip":false,"allow_skip":true}]}'):
            with self.subTest(payload=payload):
                code, result = self.cli(payload)
                self.assertEqual(code, 1)
                self.assertFalse(result['completion_verified'])
                self.assertFalse(result['consumer_scope_verified'])


if __name__ == '__main__':
    unittest.main()
