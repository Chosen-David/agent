"""Task-local observation keeps all kinds, pending state and recipient/run boundaries."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import unittest

from tests import test_communication as fixtures
from agent_runtime.communication import Mailbox, KINDS


class TaskScopeTests(unittest.TestCase):
    save = fixtures.CommunicationTests.save

    def setUp(self):
        fixtures.CommunicationTests.setUp(self)
        plan = deepcopy(self.plan)
        plan['run_id'] = 'scoped'
        plan['max_events'] = 100
        plan['routes'] = [dict(sender='code', recipient=recipient, task_id=task, kind=kind)
                          for recipient in ('writer', 'reviewer')
                          for task in ('FIG-1', 'FIG-2', "FIG-'3") for kind in sorted(KINDS)]
        self.box = Mailbox(self.db, plan, self.root)
        self.plan = plan
        self.event.update(run_id='scoped', task_id='FIG-1')

    def test_filter_before_limit_and_all_kinds(self):
        for i in range(22):
            self.box.publish(dict(self.event, event_id=f'other-{i}', task_id='FIG-2'))
        scoped = []
        for kind in sorted(KINDS):
            scoped.append(self.box.publish(dict(self.event, event_id=kind, kind=kind))['seq'])
        self.assertEqual([r['seq'] for r in self.box.inbox('writer', limit=2, task_id='FIG-1')], scoped[:2])
        self.assertEqual({r['event']['kind'] for r in self.box.inbox('writer', task_id='FIG-1')}, KINDS)
        self.assertEqual(len(self.box.inbox('writer')), 20)
        self.assertTrue(all(r['event']['task_id'] == 'FIG-2' for r in self.box.inbox('writer')))
        self.assertTrue(all(r['receipt'] is None for r in self.box.status()))

    def test_small_branch_exact_values_reopen_ack_and_isolation(self):
        other = self.box.publish(dict(self.event, event_id='other', task_id='FIG-2'))['seq']
        chosen = self.box.publish(self.event)['seq']
        full = self.box.inbox('writer')
        self.assertEqual(self.box.inbox('writer', task_id='FIG-1'), [r for r in full if r['seq'] == chosen])
        self.box.acknowledge('writer', chosen, {'status': 'consumed', 'reason': 'handled only one delivery'})
        reopened = Mailbox(self.db, self.plan, self.root)
        self.assertEqual(reopened.inbox('writer', task_id='FIG-1'), [])
        self.assertEqual(reopened.inbox('writer')[0]['seq'], other)
        self.assertEqual(len(reopened.inbox('reviewer', task_id='FIG-1')), 1)
        plan = dict(self.plan, run_id='different')
        self.assertEqual(Mailbox(self.db, plan, self.root).inbox('writer', task_id='FIG-1'), [])

    def test_explicit_exact_scope_and_sql_parameter(self):
        before = self.box.status()
        for task in ('', ' ', [], {}, True, 'absent', 'FIG-1 '):
            with self.subTest(task=task), self.assertRaises(ValueError):
                self.box.inbox('writer', task_id=task)
        with self.assertRaises(ValueError):
            self.box.inbox('absent', task_id='FIG-1')
        self.box.publish(dict(self.event, task_id="FIG-'3"))
        self.assertEqual(len(self.box.inbox('writer', task_id="FIG-'3")), 1)
        self.assertEqual(self.box.inbox('writer', task_id='FIG-1'), [])
        self.assertEqual(before, [])

    def test_cli_opt_in_and_default(self):
        self.box.publish(self.event)
        self.box.publish(dict(self.event, event_id='other', task_id='FIG-2', kind='blocker'))
        plan = self.root/'plan.json'
        plan.write_text(json.dumps(self.plan), encoding='utf-8')
        command = [sys.executable, '-m', 'agent_runtime.communication', '--root', str(self.root),
                   '--db', str(self.db), '--plan', str(plan), 'inbox', 'writer']
        for extra, expected in (([], 2), (['--task-id', 'FIG-1'], 1)):
            observed = subprocess.run(command+extra, capture_output=True, text=True, timeout=10)
            self.assertEqual(observed.returncode, 0, observed.stderr)
            self.assertEqual(len(json.loads(observed.stdout)), expected)
        bad = subprocess.run(command+['--task-id', 'absent'], capture_output=True, text=True, timeout=10)
        self.assertEqual(bad.returncode, 1)
        self.assertIn('error', json.loads(bad.stdout))

