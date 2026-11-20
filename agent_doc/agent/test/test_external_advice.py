import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]


class ExternalAdviceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.project = self.base / 'code'
        self.project.mkdir()
        self.docs = self.base / 'agent_doc/example'
        (self.docs / 'advice').mkdir(parents=True)
        self.source = self.docs / 'advice/review.md'
        self.source.write_bytes(b'Unresolved objection\n')
        self.environment = dict(os.environ)
        self.environment.pop('AGENT_DOC_ROOT', None)

    def run_cli(self, *arguments):
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/advice_poll.py'),
            '--root', str(self.project), *arguments], env=self.environment,
            capture_output=True, text=True, encoding='utf-8', timeout=10)
        self.assertNotIn('Traceback', result.stderr)
        return result, json.loads(result.stdout)

    def test_external_cli_inventory_and_modified_event(self):
        self.environment['AGENT_DOC_ROOT'] = str(self.docs)
        result, view = self.run_cli('--snapshot-out', '.agent-runs/advice/first.json')
        self.assertEqual(result.returncode, 0, view)
        self.assertEqual(view['file_count'], 1)
        self.assertEqual(view['events'][0]['after'], {'path': 'agent_doc/advice/review.md',
            'sha256': hashlib.sha256(self.source.read_bytes()).hexdigest()})
        snapshot = self.project / '.agent-runs/advice/first.json'
        digest = hashlib.sha256(snapshot.read_bytes()).hexdigest()
        self.source.write_bytes(b'Correction still unverified\n')
        result, view = self.run_cli('--baseline', '.agent-runs/advice/first.json',
                                    '--baseline-sha256', digest)
        self.assertEqual(result.returncode, 0, view)
        self.assertEqual([event['kind'] for event in view['events']], ['modified'])
        self.assertFalse((self.project / 'agent_doc').exists())

    def test_existing_anchor_without_environment(self):
        try:
            (self.project / 'agent_doc').symlink_to(self.docs, target_is_directory=True)
        except OSError:
            self.skipTest('symbolic links unavailable')
        result, view = self.run_cli()
        self.assertEqual(result.returncode, 0, view)
        self.assertEqual(view['file_count'], 1)
        self.assertTrue((self.project / 'agent_doc').is_symlink())

    def test_redirected_advice_refused_before_snapshot_write(self):
        self.environment['AGENT_DOC_ROOT'] = str(self.docs)
        try:
            (self.docs / 'advice/link.md').symlink_to(self.source)
        except OSError:
            self.skipTest('symbolic links unavailable')
        result, view = self.run_cli('--snapshot-out', '.agent-runs/refused.json')
        self.assertNotEqual(result.returncode, 0, view)
        self.assertIn('error', view)
        self.assertFalse((self.project / '.agent-runs/refused.json').exists())
        self.assertEqual(self.source.read_bytes(), b'Unresolved objection\n')

    def test_missing_external_advice_does_not_scan_local_decoy(self):
        self.environment['AGENT_DOC_ROOT'] = str(self.base / 'missing')
        local = self.project / 'agent_doc/advice'
        local.mkdir(parents=True)
        (local / 'decoy.md').write_text('Wrong document tree')
        result, view = self.run_cli()
        self.assertEqual(result.returncode, 0, view)
        self.assertEqual(view['file_count'], 0)


if __name__ == '__main__':
    unittest.main()
