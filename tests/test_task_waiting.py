"""Real SQLite with controlled clocks/handlers; not model execution evidence."""
import copy
from pathlib import Path
import tempfile
import unittest

from agent_runtime.core import Engine, Outcome, Store, validate


def task(name='slow', attempts=2, waiting=True):
    value = {'task_id': name, 'action': 'local-test', 'owner': 'main-ai',
             'depends_on': [], 'done_when': {'test': True}, 'max_attempts': attempts,
             'estimated_seconds': 20, 'risk': 'low'}
    if waiting:
        value['wait_policy'] = {'max_polls': 10, 'max_seconds': 100, 'diagnose_after_seconds': 20}
    return value


def plan(*tasks):
    return {'schema_version': 'task-dag/v1', 'run_id': 'waiting', 'user_goal': 'bounded observation',
            'authorization_reference': 'synthetic local test',
            'supervision': {'min_seconds': 1, 'max_seconds': 1, 'rationale': 'controlled clock'},
            'tasks': list(tasks)}


class Observer:
    idempotent = True
    required_capabilities = frozenset()

    def __init__(self):
        self.calls = []
        self.outcome = Outcome('pending', 'owned job still running')

    def run(self, task, context):
        self.calls.append((task['task_id'], context.idempotency_key))
        if task['task_id'] == 'quick':
            return Outcome('complete', evidence=['checked'])
        return copy.deepcopy(self.outcome)

    def verify(self, task, evidence):
        return evidence == ['checked']


class WaitingContracts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'state.sqlite'
        self.store = Store(self.path)
        self.now, self.event = 1000., 0
        self.handler = Observer()

    def tick(self, step=1):
        self.now += step
        self.event += 1
        return Engine(self.store, {'local-test': self.handler}, authorize=lambda *_: True,
                      clock=lambda: self.now, allow_legacy=True).tick('waiting', f'event-{self.event}')

    def test_pending_does_not_exhaust_failed_attempt_budget(self):
        self.store.create(plan(task(attempts=1)))
        for _ in range(4):
            state = self.tick()
            self.assertEqual(state['tasks']['slow']['status'], 'todo')
        self.handler.outcome = Outcome('complete', evidence=['checked'])
        self.assertEqual(self.tick()['status'], 'done')

    def test_ready_independent_task_gets_second_turn(self):
        self.store.create(plan(task(attempts=20), task('quick')))
        self.tick()
        self.assertEqual(self.tick()['tasks']['quick']['status'], 'done')
        self.assertEqual([t for t, _ in self.handler.calls], ['slow', 'quick'])

    def test_poll_budget_blocks_without_failing_or_marking_done(self):
        t = task(); t['wait_policy']['max_polls'] = 2
        self.store.create(plan(t))
        self.tick()
        state = self.tick()
        node = state['tasks']['slow']
        self.assertEqual((node['status'], node['attempts'], node['pending_polls']), ('blocked', 0, 2))
        self.assertEqual(node['reason_kind'], 'wait_budget')
        self.tick(step=60)
        self.assertEqual(len(self.handler.calls), 2)

    def test_wait_time_budget_blocks_before_another_poll(self):
        self.store.create(plan(task()))
        self.tick()
        node = self.tick(step=100)['tasks']['slow']
        self.assertEqual(node['status'], 'blocked')
        self.assertEqual(node['reason_kind'], 'wait_budget')
        self.assertEqual(len(self.handler.calls), 1)

    def test_early_wake_and_duplicate_cannot_poll(self):
        self.store.create(plan(task()))
        self.tick()
        self.tick(step=0)
        engine = Engine(self.store, {'local-test': self.handler}, authorize=lambda *_: True, clock=lambda: self.now, allow_legacy=True)
        engine.tick('waiting', 'event-1')
        self.assertEqual(len(self.handler.calls), 1)
        self.assertEqual(self.store.snapshot('waiting')['state']['tasks']['slow']['pending_polls'], 1)

    def test_restart_preserves_cursor_counters_and_key(self):
        self.store.create(plan(task(), task('quick')))
        self.tick()
        self.store = Store(self.path)
        self.tick()
        self.tick()
        self.assertEqual([t for t, _ in self.handler.calls], ['slow', 'quick', 'slow'])
        self.assertEqual(self.handler.calls[0][1], self.handler.calls[2][1])
        node = self.store.snapshot('waiting')['state']['tasks']['slow']
        self.assertEqual((node['attempts'], node['pending_polls']), (0, 2))

    def test_retries_after_pending_still_exhaust_attempts(self):
        self.store.create(plan(task()))
        self.tick()
        self.handler.outcome = Outcome('retry', 'observed failure')
        self.assertEqual(self.tick()['tasks']['slow']['attempts'], 1)
        node = self.tick()['tasks']['slow']
        self.assertEqual((node['status'], node['attempts']), ('failed', 2))

    def test_elapsed_time_requests_diagnosis_not_automatic_replacement(self):
        self.store.create(plan(task()))
        node = self.tick()['tasks']['slow']
        self.assertFalse(node['diagnosis_required'])
        node = self.tick(step=20)['tasks']['slow']
        self.assertTrue(node['diagnosis_required'])
        self.assertEqual(node['status'], 'todo')
        self.assertEqual(node['pending_polls'], 2)
        self.assertNotIn('optimization_success', node)

    def test_legacy_plan_keeps_old_budget(self):
        self.store.create(plan(task(attempts=1, waiting=False)))
        node = self.tick()['tasks']['slow']
        self.assertEqual((node['status'], node['attempts']), ('failed', 1))

    def test_diagnosis_updates_on_tick_before_next_poll_is_due(self):
        t = task(); t['wait_policy']['diagnose_after_seconds'] = 5
        p = plan(t); p['supervision'].update(min_seconds=30, max_seconds=60)
        self.store.create(p)
        self.tick()
        node = self.tick(step=5)['tasks']['slow']
        self.assertGreater(node['next_at'], self.now)
        self.assertTrue(node['diagnosis_required'])
        self.assertEqual(len(self.handler.calls), 1)

    def test_cancel_during_wait_never_redispatches(self):
        self.store.create(plan(task()))
        self.tick()
        self.store.cancel('waiting', 'explicit-stop', now=self.now)
        self.assertEqual(self.tick()['status'], 'cancelled')
        self.assertEqual(len(self.handler.calls), 1)

    def test_wait_policy_requires_explicit_finite_bounds(self):
        for key, value in [('max_polls', 0), ('max_polls', True), ('max_polls', 100001),
                           ('max_seconds', float('nan')), ('max_seconds', 0),
                           ('diagnose_after_seconds', 101), ('diagnose_after_seconds', False)]:
            p = plan(task()); p['tasks'][0]['wait_policy'][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                validate(p)
        for value in [None, {}, {'max_polls': 10}, {'max_polls': 10, 'max_seconds': 100,
                                                 'diagnose_after_seconds': 20, 'typo': 1}]:
            p = plan(task()); p['tasks'][0]['wait_policy'] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate(p)


if __name__ == '__main__':
    unittest.main()
