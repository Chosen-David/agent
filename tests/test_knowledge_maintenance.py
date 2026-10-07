"""Ownership and terminal failure checks for recurring model maintenance."""
import json
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
