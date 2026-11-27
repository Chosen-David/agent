import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/result_store.py'


class RegistrationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.adapter = self.root / 'adapter.py'
        self.adapter.write_text("""import json
def save_completed(root, manifest):
    return (root / "save.committed").is_file()
def restore(root, manifest):
    state = json.loads((root / manifest['files'][0]['path']).read_bytes())
    return state['step'] == 5 and len(state['optimizer']) == 2
""")
        (self.root / "save.committed").touch()
        self.refs = []
        for kind, name, payload in [('rank', 'rank0.json', b'{"step":5,"optimizer":[1,2]}'),
                                    ('metadata', 'meta', b'complete')]:
            (self.root / name).write_bytes(payload)
            self.refs.append(dict(type=kind, rank=0, path=name, expected_size_bytes=len(payload),
                                  sha256=hashlib.sha256(payload).hexdigest()))
        self.manifest = dict(schema_version='recovery-manifest/v1', run_id='point1', source_run='train',
                             producer='saver', code_revision='rev1', input_revision='data1',
                             consumers=['evaluation'], dependencies=[], retention_reason='restart',
                             save_state='complete', world_size=1, files=self.refs)

    def register(self, budget=1000):
        source = self.root / (self.manifest['run_id'] + '.json')
        source.write_text(json.dumps(self.manifest))
        result = subprocess.run([sys.executable, SCRIPT, '--root', self.root, 'register-recovery',
                                 '--manifest', source.name, '--restore-adapter', self.adapter,
                                 '--max-hash-bytes', str(budget)], capture_output=True, text=True)
        return result.returncode, json.loads(result.stdout) if result.stdout else {}

    def test_failed_replacement_preserves_complete_record_and_payload(self):
        code, record = self.register()
        self.assertEqual(code, 0, record)
        original = (self.root / 'agent_doc/results/point1/record.json').read_bytes()
        self.manifest['run_id'] = 'point2'
        self.manifest['save_state'] = 'writing'
        self.assertIn('protocol incomplete', self.register()[1]['error'])
        self.manifest['save_state'] = 'complete'
        self.manifest['world_size'] = 2
        self.assertIn('missing ranks', self.register()[1]['error'])
        self.manifest['world_size'] = 1
        self.assertIn('budget insufficient', self.register(1)[1]['error'])
        self.adapter.write_text('def save_completed(*args): return True\ndef restore(root, manifest): return False')
        self.assertIn('trial restore failed', self.register()[1]['error'])
        self.assertFalse((self.root / 'agent_doc/results/point2/record.json').exists())
        self.assertEqual((self.root / 'agent_doc/results/point1/record.json').read_bytes(), original)
        self.assertEqual(json.loads((self.root / 'rank0.json').read_bytes())['optimizer'], [1, 2])

    def test_stale_content_or_in_restore_change_refused(self):
        self.refs[0]['sha256'] = '0'*64
        code, result = self.register()
        self.assertEqual(code, 2)
        self.assertIn('stale artifact', result['error'])
        self.refs[0]['sha256'] = hashlib.sha256((self.root / 'rank0.json').read_bytes()).hexdigest()
        self.adapter.write_text("def save_completed(*args): return True\ndef restore(root, manifest):\n (root/'meta').write_bytes(b'changed!')\n return True")
        self.assertIn('changed during trial', self.register()[1]['error'])

    def test_adapter_exit_preserves_prior_recovery_record(self):
        code, _ = self.register()
        self.assertEqual(code, 0)
        prior = self.root / 'agent_doc/results/point1/record.json'
        original = prior.read_bytes()
        self.manifest['run_id'] = 'interrupted'
        self.adapter.write_text('import os\ndef save_completed(*args): return True\ndef restore(root, manifest): os._exit(77)')
        self.assertEqual(self.register()[0], 77)
        self.assertEqual(prior.read_bytes(), original)
        self.assertFalse((self.root / 'agent_doc/results/interrupted/record.json').exists())

    def test_reclaim_preserves_shared_payload_and_active_consumers(self):
        self.assertEqual(self.register()[0], 0)
        self.manifest['run_id'] = 'point2'
        self.assertEqual(self.register()[0], 0)
        with self.adapter.open('a') as stream:
            stream.write("def release_facts(root, old, new):\n return dict(owner_verified=True,save_complete=True,replacement_compatible=True,retention_satisfied=True,active_writes=[],consumers=['eval'],recovery_dependencies=[],retention_holds=[],locks=[])")
        response = subprocess.check_output([sys.executable, SCRIPT, '--root', self.root, 'review-recovery',
                                            'point1', '--replacement', 'point2', '--restore-adapter', self.adapter,
                                            '--max-hash-bytes', '1000'])
        report = json.loads(response)
        self.assertEqual(report['action'], 'retain')
        self.assertIn('active or unknown consumers', report['reasons'])
        self.assertIn('replacement references original payload', report['reasons'])
        self.assertTrue((self.root / 'rank0.json').exists())

    def test_declared_complete_without_protocol_commit_is_rejected(self):
        (self.root / 'save.committed').unlink()
        code, result = self.register()
        self.assertEqual(code, 2)
        self.assertIn('protocol completion unverified', result['error'])
        self.assertFalse((self.root / 'agent_doc/results/point1/record.json').exists())
