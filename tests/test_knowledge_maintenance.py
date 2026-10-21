"""Ownership and terminal failure checks for recurring model maintenance."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from scripts import knowledge_maintenance as maintenance


class MaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        base=Path(self.tmp.name); self.repo=base/'repo'; self.state=base/'state'
        (self.repo/'prompts').mkdir(parents=True); self.state.mkdir()
        (self.repo/'prompts/engineering_knowledge_continuous_learning.md').write_text('fixture',encoding='utf-8')
        self.config={'repo':str(self.repo),'state_dir':str(self.state),'runner':[],
                     'windows_repo':'','timeout_seconds':30,'session':'fixture'}

    def clean(self):
        return patch.object(maintenance.subprocess,'run',return_value=subprocess.CompletedProcess([],0,''))

    def run_status(self, config):
        script = Path(__file__).resolve().parents[1] / 'scripts/knowledge_maintenance.py'
        return subprocess.run([sys.executable, str(script), 'status', '--config', str(config)],
                              capture_output=True, text=True, timeout=5)

    def test_config_cli_rejects_strict_json_and_special_files_before_state_write(self):
        config = self.repo / 'maintenance.json'
        valid = json.dumps(self.config)
        regular = {
            'utf16': valid.encode('utf-16'),
            'duplicate': (valid[:-1] + ',"session":"fixture"}').encode(),
            'overflow': (valid[:-1] + ',"extra":1e400}').encode(),
            'deep': (valid[:-1] + ',"extra":' + '[' * 300 + '0' + ']' * 300 + '}').encode(),
            'oversized': b' ' * (maintenance.JSON_LIMIT + 1),
            'top-list': b'[]',
        }
        for name, raw in regular.items():
            with self.subTest(name=name):
                config.write_bytes(raw)
                before = config.read_bytes()
                result = self.run_status(config)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertEqual(result.stdout, '')
                self.assertEqual(json.loads(result.stderr)['status'], 'error')
                self.assertEqual(config.read_bytes(), before)
                self.assertEqual(list(self.state.iterdir()), [])
        config.unlink()
        target = self.repo / 'valid-target.json'
        target.write_text(valid)
        cases = ['directory', 'symlink'] + (['fifo'] if hasattr(os, 'mkfifo') else [])
        for kind in cases:
            with self.subTest(kind=kind):
                if config.exists() or config.is_symlink():
                    if config.is_dir() and not config.is_symlink():
                        config.rmdir()
                    else:
                        config.unlink()
                if kind == 'directory':
                    config.mkdir()
                elif kind == 'symlink':
                    config.symlink_to(target)
                else:
                    os.mkfifo(config)
                result = self.run_status(config)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertEqual(result.stdout, '')
                self.assertEqual(json.loads(result.stderr)['status'], 'error')
                self.assertEqual(list(self.state.iterdir()), [])
                if config.is_dir() and not config.is_symlink():
                    config.rmdir()
                else:
                    config.unlink()

    def test_legacy_calendar_migrates_once_without_losing_history(self):
        old={'next_due':90000,'rounds':[{'status':'runner_failed','exit_code':7}]}
        maintenance.atomic(self.state/'state.json',old)
        saved=maintenance.load_state(self.config,100)
        self.assertEqual(saved['next_due'],3700)
        self.assertEqual(saved['rounds'],old['rounds'])
        self.assertEqual(saved['schedule_migrations'][0]['previous_due'],90000)
        self.assertEqual(maintenance.load_state(self.config,200),saved)

    def test_new_state_is_hourly_and_restart_preserves_overdue_slot(self):
        first=maintenance.load_state(self.config,100)
        self.assertEqual((first['interval_seconds'],first['next_due']),(3600,3700))
        self.assertEqual(maintenance.load_state(self.config,8000),first)

    def test_interval_change_reanchors_once(self):
        maintenance.load_state(self.config,100)
        self.config['interval_seconds']=7200
        changed=maintenance.load_state(self.config,200)
        self.assertEqual(changed['next_due'],7400)
        self.assertEqual(changed['schedule_migrations'][0]['previous_interval_seconds'],3600)

    def test_cadence_does_not_drift_with_runner_duration(self):
        self.assertEqual(maintenance.advance_due(100,2800,3600),3700)

    def test_long_round_skips_missed_slots_including_exact_boundary(self):
        self.assertEqual(maintenance.advance_due(100,7500,3600),10900)
        self.assertEqual(maintenance.advance_due(100,7300,3600),10900)

    def test_invalid_intervals_rejected_before_state_write(self):
        for value in (0,-1,True,3600.5,'3600',float('nan')):
            with self.subTest(value=value), self.assertRaises(ValueError):
                maintenance.load_state(dict(self.config,interval_seconds=value),100)
        self.assertFalse((self.state/'state.json').exists())

    def test_malformed_state_fails_before_migration_write(self):
        path = self.state / 'state.json'
        for payload in ('[]', '{}', '{"rounds":"wrong"}',
                        '{"rounds":[],"interval_seconds":3600}',
                        '{"rounds":[],"interval_seconds":3600,"next_due":-1}'):
            with self.subTest(payload=payload):
                path.write_text(payload)
                before = path.read_bytes()
                with self.assertRaisesRegex(ValueError, 'invalid structure'):
                    maintenance.load_state(self.config, 100)
                self.assertEqual(path.read_bytes(), before)

    def test_status_treats_malformed_live_snapshot_as_not_live(self):
        live = self.state / 'live.json'
        for payload in ('[]', '{"pid":"wrong","heartbeat_at":0}',
                        '{"pid":1,"heartbeat_at":"wrong"}',
                        '{"pid":1,"heartbeat_at":0}',
                        '{"pid":1,"heartbeat_at":0,"session":""}',
                        '{"pid":1,"heartbeat_at":-1,"session":"fixture"}'):
            with self.subTest(payload=payload):
                live.write_text(payload)
                with patch.object(maintenance, 'tmux') as mocked_tmux:
                    mocked_tmux.return_value = subprocess.CompletedProcess([], 0, '0\n', '')
                    report = maintenance.status(self.config)
                self.assertFalse(report['live'])
                self.assertEqual(report['worker'], {})

    def test_status_rejects_mismatched_or_future_live_owner(self):
        with patch.object(maintenance.os, 'kill'), patch.object(maintenance, 'tmux') as mocked_tmux:
            mocked_tmux.return_value = subprocess.CompletedProcess([], 0, '0\n', '')
            for session, heartbeat in (('other', 100), ('fixture', 101)):
                with self.subTest(session=session, heartbeat=heartbeat), \
                     patch.object(maintenance.time, 'time', return_value=100):
                    maintenance.atomic(self.state / 'live.json', {
                        'pid': 1, 'heartbeat_at': heartbeat, 'session': session})
                    self.assertFalse(maintenance.status(self.config)['live'])

    def test_dirty_repository_never_launches_model(self):
        with patch.object(maintenance.subprocess,'run',return_value=subprocess.CompletedProcess([],0,' M x')), \
             patch.object(maintenance.subprocess,'Popen') as launch:
            self.assertEqual(maintenance.run_round(self.config)['status'],'blocked')
            launch.assert_not_called()

    def test_stale_lock_is_not_replayed_or_deleted(self):
        (self.state/'round.lock').mkdir(); self.config['runner']=['not-executed']
        with self.clean(), patch.object(maintenance.subprocess,'Popen') as launch:
            self.assertEqual(maintenance.run_round(self.config)['status'],'blocked')
            launch.assert_not_called()
        self.assertTrue((self.state/'round.lock').exists())

    def test_real_failed_runner_is_not_accepted(self):
        stub=self.repo/'stub.py'; stub.write_text('raise SystemExit(7)',encoding='utf-8')
        self.config['runner']=[sys.executable,str(stub)]
        with self.clean():
            result=maintenance.run_round(self.config)
        self.assertEqual((result['status'],result['exit_code']),('runner_failed',7))
        self.assertFalse((self.state/'round.lock').exists())
        self.assertEqual(json.loads((Path(result['run_dir'])/'receipt.json').read_text())['exit_code'],7)

    def test_supervisor_io_failure_preserves_live_runner_ownership(self):
        self.config['runner']=['fixture']
        with self.clean(), patch.object(maintenance.subprocess,'Popen') as launch, \
             patch.object(maintenance,'atomic',side_effect=OSError('disk unavailable')):
            launch.return_value.poll.return_value=None
            with self.assertRaises(OSError): maintenance.run_round(self.config)
        self.assertTrue((self.state/'round.lock').exists())


if __name__=='__main__': unittest.main()
