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
