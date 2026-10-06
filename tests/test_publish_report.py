"""Report lifecycle checks use real files, hashes, processes and memory corrections."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime.project_memory import MemoryLedger
from scripts.publish_report import ReportError, publish, read_report


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'publish_report.py'


class PublishReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'data').mkdir()
        (self.root / 'data' / 'measurements.csv').write_text('case,value\na,10\n')
        self.manifest = {
            'task_id': 'T1', 'run_id': 'run-1', 'purpose': 'Verify report handoff',
            'summary': 'Fixture data only',
            'data': [{'kind': 'synthetic', 'description': 'One value: 10',
                      'meaning': 'No scientific result', 'useful': False}],
            'artifacts': [{'path': 'data/measurements.csv', 'role': 'raw fixture data',
                           'sha256': hashlib.sha256((self.root / 'data/measurements.csv').read_bytes()).hexdigest()}],
            'limitations': ['Synthetic'], 'memory_refs': []}

    @property
    def latest(self):
        return self.root / 'reports/T1/latest.json'

    def test_versions_keep_old_snapshot_and_update_one_stable_pointer(self):
        first = publish(self.root, self.manifest)
        old = self.root / first['reports']['report.json']['path']
        original = old.read_bytes()
        second = copy.deepcopy(self.manifest)
        second.update(run_id='run-2', summary='Follow-up result')
        publish(self.root, second)
        self.assertEqual(read_report(self.root, 'T1'), second)
        self.assertEqual(old.read_bytes(), original)
        self.assertEqual(json.loads(self.latest.read_text())['run_id'], 'run-2')
        self.assertFalse(any((self.root / 'reports/T1/runs/run-1').glob('*.csv')))

    def test_duplicate_run_never_overwrites_snapshot_or_latest(self):
        publish(self.root, self.manifest)
        original = self.latest.read_bytes()
        altered = dict(self.manifest, summary='Changed')
        with self.assertRaisesRegex(ReportError, 'already exists'):
            publish(self.root, altered)
        self.assertEqual(self.latest.read_bytes(), original)
        self.assertEqual(read_report(self.root, 'T1'), self.manifest)

    def test_artifact_mutation_blocks_publish_and_read(self):
        publish(self.root, self.manifest)
        original = self.latest.read_bytes()
        (self.root / 'data/measurements.csv').write_text('altered data')
        with self.assertRaisesRegex(ReportError, 'artifact hash changed'):
            read_report(self.root, 'T1')
        with self.assertRaisesRegex(ReportError, 'artifact hash changed'):
            publish(self.root, dict(self.manifest, run_id='run-2'))
        self.assertEqual(self.latest.read_bytes(), original)
        self.assertFalse((self.root / 'reports/T1/runs/run-2').exists())

    def test_json_and_readable_snapshot_tampering_are_rejected(self):
        publish(self.root, self.manifest)
        for name in ('report.json', 'report.md'):
            path = self.root / f'reports/T1/runs/run-1/{name}'
            original = path.read_bytes()
            path.write_bytes(original + b'changed')
            with self.assertRaisesRegex(ReportError, 'snapshot hash changed'):
                read_report(self.root, 'T1')
            path.write_bytes(original)

    def test_invalid_latest_cannot_redirect_to_another_run(self):
        pointer = publish(self.root, self.manifest)
        pointer['reports']['report.json']['path'] = 'data/measurements.csv'
        self.latest.write_text(json.dumps(pointer))
        with self.assertRaisesRegex(ReportError, 'path mismatch'):
            read_report(self.root, 'T1')

    def test_pointer_replace_failure_preserves_previous_latest(self):
        publish(self.root, self.manifest)
        original = self.latest.read_bytes()
        with patch('scripts.publish_report.os.replace', side_effect=OSError('disk error')):
            with self.assertRaisesRegex(OSError, 'disk error'):
                publish(self.root, dict(self.manifest, run_id='run-2'))
        self.assertEqual(self.latest.read_bytes(), original)
        self.assertEqual(read_report(self.root, 'T1')['run_id'], 'run-1')
        # Installed snapshot survives; retry must use a fresh run ID, never overwrite it.
        self.assertTrue((self.root / 'reports/T1/runs/run-2/report.json').is_file())
        self.assertEqual(list((self.root / 'reports/T1').glob('.latest-*')), [])

    def test_invalid_schema_and_nonfinite_metadata_create_no_output(self):
        invalid = [dict(self.manifest, task_id='../escape'), dict(self.manifest, run_id='/tmp/out'),
                   dict(self.manifest, purpose=''), dict(self.manifest, limitations='unknown'),
                   dict(self.manifest, extra=float('nan')), dict(self.manifest, extra=float('inf')),
                   dict(self.manifest, data=[]), dict(self.manifest, memory_refs='intent')]
        for useful in (None, 1, 'yes', [], {}):
            value = copy.deepcopy(self.manifest)
            value['data'][0]['useful'] = useful
            invalid.append(value)
        for value in invalid:
            with self.subTest(value=value), self.assertRaises((ValueError, TypeError)):
                publish(self.root, value)
        self.assertFalse((self.root / 'reports').exists())

    def test_traversal_and_symlink_artifacts_and_output_directories_rejected(self):
        link = self.root / 'linked'
        link.symlink_to(self.root / 'data', target_is_directory=True)
        for path in ('../data', '/etc/passwd', 'data/../data/measurements.csv',
                     'data//measurements.csv', 'linked/measurements.csv', 'data'):
            value = copy.deepcopy(self.manifest)
            value['artifacts'][0]['path'] = path
            with self.subTest(path=path), self.assertRaises((ReportError, OSError)):
                publish(self.root, value)
        (self.root / 'reports').symlink_to(self.root / 'data', target_is_directory=True)
        with self.assertRaisesRegex(ReportError, 'symlink'):
            publish(self.root, self.manifest)
        self.assertEqual(sorted(p.name for p in (self.root / 'data').iterdir()), ['measurements.csv'])

    def test_correction_invalidates_current_report_without_deleting_raw_data(self):
        ledger = MemoryLedger(self.root, create=True)
        ledger.add('intent-v1', 'intention', 'Optimize the wrong target', 'user-turn-1',
                   evidence='user_confirmed')
        ledger.add('claim-v1', 'claim', 'Target result', 'run-1', deps=['intent-v1'], evidence='verified')
        manifest = dict(self.manifest, memory_refs=['claim-v1'])
        publish(self.root, manifest)
        self.assertEqual(read_report(self.root, 'T1'), manifest)
        original = self.latest.read_bytes()
        ledger.correct('intent-v1', 'intent-v2', 'Actual target', 'user-turn-2', 'User corrected interpretation')
        with self.assertRaisesRegex(ValueError, 'stale'):
            read_report(self.root, 'T1')
        with self.assertRaisesRegex(ValueError, 'stale'):
            publish(self.root, dict(manifest, run_id='run-2'))
        self.assertEqual(self.latest.read_bytes(), original)
        self.assertEqual((self.root / 'data/measurements.csv').read_text(), 'case,value\na,10\n')

    def test_missing_memory_ledger_fails_closed_without_creating_one(self):
        with self.assertRaisesRegex(ValueError, 'missing'):
            publish(self.root, dict(self.manifest, memory_refs=['intent-v1']))
        self.assertFalse((self.root / '.agent-memory').exists())
        self.assertFalse((self.root / 'reports').exists())

    def test_competing_processes_publish_same_run_once(self):
        source = self.root / 'input.json'
        source.write_text(json.dumps(self.manifest))
        command = [sys.executable, str(SCRIPT), 'publish', '--root', str(self.root), '--manifest', 'input.json']
        processes = [subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(2)]
        outputs = [process.communicate(timeout=20) for process in processes]
        self.assertEqual(sorted(process.returncode for process in processes), [0, 1], outputs)
        self.assertEqual(read_report(self.root, 'T1'), self.manifest)
        self.assertEqual([p.name for p in (self.root / 'reports/T1/runs').iterdir()], ['run-1'])
        read = subprocess.run([sys.executable, str(SCRIPT), 'read', '--root', str(self.root), '--task', 'T1'],
                              capture_output=True, text=True, timeout=20)
        self.assertEqual(read.returncode, 0, read.stderr)
        self.assertEqual(json.loads(read.stdout), self.manifest)

    def test_cli_rejects_duplicate_json_keys(self):
        (self.root / 'bad.json').write_text('{"task_id":"T1","task_id":"T2"}')
        result = subprocess.run([sys.executable, str(SCRIPT), 'publish', '--root', str(self.root),
                                 '--manifest', 'bad.json'], capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 1)
        self.assertIn('duplicate JSON key', result.stderr)
        self.assertFalse((self.root / 'reports').exists())

    def test_competing_distinct_runs_preserve_both_and_coherent_latest(self):
        commands = []
        for run in ('run-1', 'run-2'):
            source = self.root / f'{run}.json'
            source.write_text(json.dumps(dict(self.manifest, run_id=run)))
            commands.append([sys.executable, str(SCRIPT), 'publish', '--root', str(self.root),
                             '--manifest', source.name])
        processes = [subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                     for command in commands]
        outputs = [process.communicate(timeout=20) for process in processes]
        self.assertEqual([process.returncode for process in processes], [0, 0], outputs)
        self.assertIn(read_report(self.root, 'T1')['run_id'], ('run-1', 'run-2'))
        self.assertEqual(sorted(p.name for p in (self.root / 'reports/T1/runs').iterdir()),
                         ['run-1', 'run-2'])


if __name__ == '__main__':
    unittest.main()
