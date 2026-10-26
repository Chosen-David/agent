"""Recoverable display must preserve all decision gates and never confer trust."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from agent_runtime.validation_context import write_validation_context, restore_validation_context
from agent_runtime.result_validation import inspect_result
from tests.test_result_validation import make_fixture

ROOT = Path(__file__).resolve().parents[1]


class ValidationContextTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.contract = make_fixture(self.root)
        self.result = inspect_result(self.root, self.contract)

    def test_pending_full_roundtrip_and_idempotency(self):
        original = deepcopy(self.result)
        receipt = write_validation_context(self.root, self.result, 'agent_doc/results/context-fixture')
        self.assertEqual(receipt['status'], 'pending')
        for key in ('scope', 'errors', 'next_action'):
            self.assertEqual(receipt[key], self.result[key])
        self.assertEqual(restore_validation_context(self.root, receipt['record_ref']), self.result)
        self.assertEqual(write_validation_context(self.root, self.result, 'agent_doc/results/context-fixture'), receipt)
        self.assertEqual(self.result, original)
        self.assertEqual(receipt['proof']['status'], 'pending')
        self.assertIn('Display only', receipt['trust'])

    def test_failures_limits_and_verifier_are_preserved(self):
        result = deepcopy(self.result)
        result['status'] = 'invalid'; result['errors'] = ['scope mismatch', 'freshness changed']
        result['proof'].update(limitations=['CPU only', 'no speed evidence'], verifier={'actor': 'host'},
                               review_evidence={'evidence.txt': '1' * 64})
        receipt = write_validation_context(self.root, result, 'agent_doc/results/failure-context')
        self.assertEqual(receipt['proof']['limitations'], result['proof']['limitations'])
        self.assertEqual(receipt['proof']['verifier'], result['proof']['verifier'])
        self.assertEqual(receipt['errors'], result['errors'])
        self.assertEqual(restore_validation_context(self.root, receipt['record_ref']), result)

    def test_path_unknown_fields_and_modified_record_refuse(self):
        for bad in ('../escape', 'agent_doc/guide/unsafe', 'doc/context', 'agent_doc/results/../escape'):
            with self.assertRaises(ValueError):
                write_validation_context(self.root, self.result, bad)
        with self.assertRaises(ValueError):
            write_validation_context(self.root, {**self.result, 'new_gate': 'must preserve'}, 'agent_doc/results/x')
        receipt = write_validation_context(self.root, self.result, 'agent_doc/results/x')
        path = self.root / receipt['record_ref']['path']; path.write_text('changed')
        with self.assertRaises(ValueError): restore_validation_context(self.root, receipt['record_ref'])
        with self.assertRaises(ValueError): write_validation_context(self.root, self.result, 'agent_doc/results/x')

    def test_real_cli_default_pending_exit_and_restore(self):
        command = [sys.executable, '-X', 'utf8', str(ROOT/'scripts/validate_experiment_result.py'),
                   '--root', str(self.root), '--contract', str(self.root/'contract.json')]
        baseline = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', timeout=20)
        candidate = subprocess.run(command+['--context-dir', 'agent_doc/results/cli-context'],
                                   capture_output=True, text=True, encoding='utf-8', timeout=20)
        self.assertEqual((baseline.returncode, candidate.returncode), (2, 2))
        self.assertEqual(json.loads(baseline.stdout), self.result)
        receipt = json.loads(candidate.stdout)
        self.assertEqual(restore_validation_context(self.root, receipt['record_ref']), self.result)
        restored = subprocess.run([sys.executable, '-X', 'utf8', str(ROOT/'scripts/validation_context.py'),
            '--root', str(self.root), '--path', receipt['record_ref']['path'], '--sha256', receipt['record_ref']['sha256']],
            capture_output=True, text=True, encoding='utf-8', timeout=20)
        self.assertEqual(restored.returncode, 0)
        self.assertEqual(json.loads(restored.stdout), self.result)

    def test_rebased_guide_root_cannot_write(self):
        guide = self.root / 'agent_doc/guide'; guide.mkdir(parents=True)
        with self.assertRaises(ValueError):
            write_validation_context(guide, self.result, 'agent_doc/results/unsafe')
        self.assertFalse((guide / 'agent_doc').exists())

    def test_identical_record_copied_to_other_project_cannot_restore(self):
        receipt = write_validation_context(self.root, self.result, 'agent_doc/results/cross-project')
        with tempfile.TemporaryDirectory() as other:
            target = Path(other) / receipt['record_ref']['path']; target.parent.mkdir(parents=True)
            target.write_bytes((self.root / receipt['record_ref']['path']).read_bytes())
            with self.assertRaisesRegex(ValueError, 'another project'):
                restore_validation_context(Path(other), receipt['record_ref'])

    def native_cli(self, script, *args):
        return subprocess.run([sys.executable, str(ROOT / 'scripts' / script),
                               '--root', str(self.root), *args], capture_output=True,
                              env=dict(os.environ, PYTHONUTF8='0', PYTHONIOENCODING='cp936'),
                              timeout=20)

    def file_hashes(self):
        return {p.relative_to(self.root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.root.rglob('*') if p.is_file()}

    def test_native_restore_preserves_full_unicode_observations(self):
        for status in ('pending', 'invalid', 'usable-with-scope'):
            result = deepcopy(self.result)
            result.update(status=status, scope='范围 \U00010000\r\n原文',
                          errors=['异议 \U00010000', '取消：不消费'], next_action='重新核验 \U00010000')
            result['proof'].update(status=status, limitations=['仅显示 \U00010000'],
                                   artifact_hashes={'产物\U00010000.txt': '1' * 64},
                                   review_evidence={'异议\U00010000.txt': '2' * 64})
            # Arbitrary saved observations are display-only, never live acceptance.
            receipt = write_validation_context(self.root, result,
                                              'agent_doc/results/native-' + status)
            before = self.file_hashes()
            for formatting in ((), ('--compact',)):
                with self.subTest(status=status, formatting=formatting):
                    out = self.native_cli('validation_context.py', '--path',
                        receipt['record_ref']['path'], '--sha256', receipt['record_ref']['sha256'],
                        *formatting)
                    self.assertEqual(out.returncode, 0, out.stderr)
                    self.assertEqual(out.stderr, b'')
                    self.assertEqual(json.loads(out.stdout.decode('utf-8')), result)
            self.assertEqual(self.file_hashes(), before)

    def test_native_inspection_pending_and_display_roundtrip(self):
        scope = '当前范围 \U00010000\r\n保留更正、依赖与异议'
        plan = json.loads((self.root / 'validation-plan.json').read_bytes())
        manifest = json.loads((self.root / 'manifest.json').read_bytes())
        plan['scope'] = manifest['scope'] = self.contract['scope'] = scope
        raw = json.dumps(plan, ensure_ascii=False).encode('utf-8')
        (self.root / 'validation-plan.json').write_bytes(raw)
        self.contract['validation_plan']['sha256'] = hashlib.sha256(raw).hexdigest()
        manifest['validation_plan'] = dict(self.contract['validation_plan'])
        (self.root / 'manifest.json').write_bytes(json.dumps(manifest, ensure_ascii=False).encode('utf-8'))
        (self.root / 'contract.json').write_bytes(json.dumps(self.contract, ensure_ascii=False).encode('utf-8'))
        expected = inspect_result(self.root, self.contract)
        self.assertEqual(expected['status'], 'pending')
        self.assertIsNotNone(expected['proof'])
        before = self.file_hashes()
        for formatting in ((), ('--compact',)):
            with self.subTest(formatting=formatting):
                out = self.native_cli('validate_experiment_result.py', '--contract',
                                     str(self.root / 'contract.json'), *formatting)
                self.assertEqual(out.returncode, 2, out.stderr)
                self.assertEqual(out.stderr, b'')
                self.assertEqual(json.loads(out.stdout.decode('utf-8')), expected)
        self.assertEqual(self.file_hashes(), before)
        out = self.native_cli('validate_experiment_result.py', '--contract',
            str(self.root / 'contract.json'), '--context-dir', 'agent_doc/results/native-inspect')
        self.assertEqual(out.returncode, 2, out.stderr)
        self.assertEqual(out.stderr, b'')
        receipt = json.loads(out.stdout.decode('utf-8'))
        self.assertEqual(receipt['status'], 'pending')
        self.assertEqual(receipt['scope'], scope)
        self.assertEqual(receipt['errors'], expected['errors'])
        self.assertEqual(restore_validation_context(self.root, receipt['record_ref']), expected)

    def test_native_input_failure_retains_utf8_error_protocol(self):
        broken = self.root / 'duplicate.json'
        broken.write_bytes('{"异议\U00010000":1,"异议\U00010000":2}'.encode('utf-8'))
        before = self.file_hashes()
        out = self.native_cli('validate_experiment_result.py', '--contract', str(broken))
        self.assertEqual(out.returncode, 2)
        self.assertEqual(out.stdout, b'')
        self.assertEqual(json.loads(out.stderr.decode('utf-8')),
                         {'status': 'error', 'error': 'duplicate JSON key: 异议\U00010000'})
        self.assertEqual(self.file_hashes(), before)
