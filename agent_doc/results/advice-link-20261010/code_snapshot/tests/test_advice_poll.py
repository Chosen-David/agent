"""Meaningful advice change/relocation/isolation/CLI boundaries, no model claims."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime.advice_poll import encode, observe_advice, validate_snapshot


class AdvicePollTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.advice = self.root / 'agent_doc/advice'; self.advice.mkdir(parents=True)
        self.source = self.advice / 'review.md'; self.source.write_bytes(b'Unresolved objection\r\n')

    def test_first_unchanged_and_append(self):
        first, baseline = observe_advice(self.root)
        self.assertTrue(first['changed']); self.assertTrue(first['initial_observation'])
        same, again = observe_advice(self.root, baseline)
        self.assertEqual(baseline, again); self.assertFalse(same['changed']); self.assertEqual(same['events'], [])
        self.assertNotIn('files', same); self.assertNotIn('Unresolved objection', json.dumps(same))
        self.source.write_bytes(self.source.read_bytes() + b'Fix dispatched, not verified\n')
        changed, _ = observe_advice(self.root, baseline)
        self.assertEqual([e['kind'] for e in changed['events']], ['modified'])
        self.assertNotEqual(changed['events'][0]['before']['sha256'], changed['events'][0]['after']['sha256'])

    def test_archive_move_never_means_closed_and_edit_seen(self):
        _, baseline = observe_advice(self.root)
        archive = self.advice / 'archive'; archive.mkdir()
        moved = archive / self.source.name; self.source.rename(moved)
        view, current = observe_advice(self.root, baseline)
        event = view['events'][0]
        self.assertEqual(event['kind'], 'content_relocated')
        self.assertEqual(event['after']['path'], 'agent_doc/advice/archive/review.md')
        self.assertNotIn('closed', event)
        moved.write_bytes(b'New counterexample in archived advice\n')
        view, _ = observe_advice(self.root, current)
        self.assertEqual(view['events'][0]['kind'], 'modified')

    def test_duplicate_content_not_arbitrary_relocation(self):
        (self.advice / 'second.md').write_bytes(self.source.read_bytes())
        _, baseline = observe_advice(self.root)
        raw = self.source.read_bytes(); self.source.unlink(); (self.advice / 'second.md').unlink()
        (self.advice / 'third.md').write_bytes(raw)
        view, _ = observe_advice(self.root, baseline)
        self.assertEqual(sorted(e['kind'] for e in view['events']), ['added', 'removed', 'removed'])

    def test_bad_foreign_and_colliding_baselines_rejected(self):
        _, baseline = observe_advice(self.root)
        for mutate in (lambda b: b.update(project_root='other-project'),
                       lambda b: b['files'].update({'agent_doc/advice/../guide/GUIDE.md':'0'*64}),
                       lambda b: b['files'].update({'agent_doc/advice/REVIEW.md':'0'*64}),
                       lambda b: b['files'].update({'agent_doc/advice/new.md':'not-a-sha'}),
                       lambda b: b.update(assessed=True)):
            bad = copy.deepcopy(baseline); mutate(bad)
            with self.assertRaises(ValueError): validate_snapshot(self.root, bad)
        with self.assertRaises(ValueError): observe_advice('relative')

    def test_bounds_and_observed_churn_fail_without_partial(self):
        with self.assertRaises(ValueError): observe_advice(self.root, max_bytes=1)
        (self.advice / 'new.md').write_bytes(b'New')
        with self.assertRaises(ValueError): observe_advice(self.root, max_files=1)
        with self.assertRaises(ValueError): observe_advice(self.root, max_files=True)
        (self.advice / 'empty').mkdir()
        with self.assertRaises(ValueError): observe_advice(self.root, max_dirs=1)
        _, baseline = observe_advice(self.root)
        other = copy.deepcopy(baseline); other['files'] = {}
        with patch('agent_runtime.advice_poll._scan', side_effect=[baseline, other]):
            with self.assertRaisesRegex(ValueError, 'changed during'): observe_advice(self.root)

    def test_link_outside_source_rejected(self):
        linked = self.advice / 'link.md'
        try: linked.symlink_to(self.source)
        except OSError: self.skipTest('host cannot create symbolic links')
        with self.assertRaises(ValueError): observe_advice(self.root)

    def test_directory_read_error_never_becomes_complete_empty_inventory(self):
        with patch('agent_runtime.advice_poll.os.scandir', side_effect=PermissionError('unreadable advice subtree')):
            with self.assertRaises(PermissionError): observe_advice(self.root)

    def test_cli_explicit_new_snapshot_hash_and_no_overwrite(self):
        script = Path(__file__).resolve().parents[1] / 'scripts/advice_poll.py'
        def run(*args):
            return subprocess.run([sys.executable, '-X', 'utf8', str(script), '--root', str(self.root), *args],
                                  capture_output=True, text=True, encoding='utf-8')
        original = self.source.read_bytes()
        path = '.agent-runs/advice-poll/first.json'
        result = run('--snapshot-out', path); self.assertEqual(result.returncode, 0, result.stdout)
        view = json.loads(result.stdout); raw = (self.root / path).read_bytes()
        self.assertEqual(view['snapshot_ref']['sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual(raw, encode(json.loads(raw)))
        same = run('--baseline', path, '--baseline-sha256', hashlib.sha256(raw).hexdigest())
        self.assertEqual(same.returncode, 0, same.stdout); self.assertFalse(json.loads(same.stdout)['changed'])
        for args in (('--snapshot-out', path), ('--baseline', path),
                     ('--baseline', path, '--baseline-sha256', '0'*64),
                     ('--snapshot-out', 'agent_doc/guide/new.md'), ('--snapshot-out', '.agent-runs/../escape.json'),
                     ('--snapshot-out', '.agent-runs/sub\\..\\..\\escape.json')):
            self.assertNotEqual(run(*args).returncode, 0)
        bad_path = self.root / '.agent-runs/bad.json'
        for bad in (None, [], True):
            bad_raw = json.dumps(bad).encode(); bad_path.write_bytes(bad_raw)
            self.assertNotEqual(run('--baseline', '.agent-runs/bad.json', '--baseline-sha256',
                                    hashlib.sha256(bad_raw).hexdigest()).returncode, 0)
        self.assertEqual((self.root / path).read_bytes(), raw); self.assertEqual(self.source.read_bytes(), original)


if __name__ == '__main__': unittest.main()
