"""Real temporary SQLite/files; no live model calls."""
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from agent_runtime.core import ArtifactHandler, Engine, Outcome, Store
from agent_runtime.scheduler import LocalScheduler, arm
from agent_runtime.task_manifest import (ReportingHandler, atomic_json, prepare,
                                          requirements, review, validate_contract)
from agent_runtime.task_supervisor import ManagedEngine, start


class TaskManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.task_file = self.root / 'TASK.md'
        self.task_file.write_text('- [ ] [T1] Produce output\n- [x] [T2] Review output\n')
        self.plan = prepare(self.task_file, 'test', 'auto', 'test user instruction')
        for task in self.plan['tasks']:
            task['action'] = 'verify_artifacts'
            task['done_when'] = {'artifacts': [{'path': task['task_id'] + '.txt',
                                    'sha256': hashlib.sha256(b'proof').hexdigest()}]}
            self.write_result(task)
        self.plan['tasks'][1]['depends_on'] = ['T1']
        self.store = Store(self.root / 'state.sqlite')
        self.store.create(self.plan)
        self.handler = ReportingHandler(ArtifactHandler(self.root), self.root)
        self.engine = Engine(self.store, {'verify_artifacts': self.handler}, authorize=lambda *_: True)

    def write_result(self, task):
        atomic_json(self.root / task['report_path'], {'task_id': task['task_id'], 'summary': 'fixture output',
                    'data': [{'kind': 'synthetic', 'description': 'deterministic test bytes'}]})

    def proof(self, task_id):
        (self.root / (task_id + '.txt')).write_bytes(b'proof')

    def test_auto_and_manual_preserve_ids_and_never_trust_checkmarks(self):
        self.assertEqual(prepare(self.task_file, 'manual', 'manual', 'user')['task_source']['mode'], 'manual')
        self.assertEqual(validate_contract(self.plan, self.root)[1]['id'], 'T2')
        self.assertEqual(review(self.store.snapshot('test'), self.root)['remaining'], ['T1', 'T2'])

    def test_fenced_examples_ignored_but_duplicate_or_unidentified_tasks_rejected(self):
        self.task_file.write_text('```md\n- [ ] example\n```\n- [ ] [T] real\n')
        self.assertEqual([t['id'] for t in requirements(self.task_file)], ['T'])
        for text in ('- [ ] missing ID\n', '- [ ] [T] a\n- [x] [T] b\n', '# No tasks'):
            self.task_file.write_text(text)
            with self.assertRaises(ValueError): requirements(self.task_file)

    def test_omitted_and_unknown_requirements_rejected(self):
        plan = copy.deepcopy(self.plan)
        plan['tasks'].pop()
        with self.assertRaisesRegex(ValueError, 'omits'): validate_contract(plan, self.root)
        plan['tasks'][0]['task_refs'] = ['UNKNOWN']
        with self.assertRaisesRegex(ValueError, 'known'): validate_contract(plan, self.root)

    def test_nested_task_file_is_not_a_second_project_source(self):
        nested = self.root / 'agent-output' / 'TASK.md'
        nested.parent.mkdir()
        nested.write_text(self.task_file.read_text())
        plan = prepare(nested, 'nested', 'auto', 'user')
        with self.assertRaisesRegex(ValueError, 'project-root TASK.md'):
            validate_contract(plan, self.root)

    def test_source_changes_prevent_dispatch_and_completion(self):
        self.task_file.write_text(self.task_file.read_text() + '- [ ] [T3] Newly requested work\n')
        config = {'run_id': 'test', 'project_root': str(self.root), 'state_dir': str(self.root)}
        engine = ManagedEngine(config, self.store, {'verify_artifacts': self.handler}, authorize=lambda *_: True)
        with self.assertRaisesRegex(ValueError, 'changed'): engine.tick('test', 'event')
        self.assertEqual(self.store.snapshot('test')['state']['tasks']['T1']['attempts'], 0)
        report = review(self.store.snapshot('test'), self.root)
        self.assertIn('T3', report['remaining'])
        self.assertFalse(report['all_reportable'])

    def test_report_paths_must_be_unique_and_within_project(self):
        for path in ('../outside.json', self.plan['tasks'][0]['report_path'], 'TASK.md'):
            plan = copy.deepcopy(self.plan)
            plan['tasks'][1]['report_path'] = path
            with self.assertRaises(ValueError): validate_contract(plan, self.root)

    def test_real_evidence_and_report_required_and_remaining_updates(self):
        self.proof('T1')
        state = self.engine.tick('test', 'first')
        self.assertEqual(state['tasks']['T1']['status'], 'done')
        report = review(self.store.snapshot('test'), self.root)
        self.assertEqual(report['remaining'], ['T2'])
        self.assertEqual(report['requirements'][0]['nodes'][0]['result']['data'][0]['kind'], 'synthetic')
        self.proof('T2')
        self.engine.tick('test', 'second')
        self.assertTrue(review(self.store.snapshot('test'), self.root)['all_reportable'])
        # Reopening the real DB retains verified work and report provenance.
        self.assertTrue(review(Store(self.root / 'state.sqlite').snapshot('test'), self.root)['all_reportable'])

    def test_missing_result_is_blocked_not_done(self):
        self.proof('T1')
        (self.root / self.plan['tasks'][0]['report_path']).unlink()
        state = self.engine.tick('test', 'first')
        self.assertEqual(state['tasks']['T1']['status'], 'blocked')
        self.assertFalse(review(self.store.snapshot('test'), self.root)['all_reportable'])

    def test_progress_exposes_bounded_wait_and_task_identity(self):
        # No artifact yet: this is a real missing-file observation, not completion.
        self.engine.tick('test', 'pending')
        entry = review(self.store.snapshot('test'), self.root)['requirements'][0]['nodes'][0]
        self.assertEqual(entry['task_refs'], ['T1'])
        self.assertEqual(entry['execution']['attempts'], 0)
        self.assertEqual(entry['execution']['pending_polls'], 1)
        self.assertEqual(entry['execution']['dispatches'], 1)
        self.assertEqual(entry['execution']['wait_policy']['max_seconds'], 3600)
        self.assertFalse(entry['execution']['diagnosis_required'])
        self.assertIsNone(entry['result'])

    def diagnosed_wait(self):
        clock = [1000.]
        engine = Engine(self.store, {'verify_artifacts': self.handler},
                        authorize=lambda *_: True, clock=lambda: clock[0])
        engine.tick('test', 'wait-start')
        clock[0] += 3600
        engine.tick('test', 'wait-limit')
        node = self.store.snapshot('test')['state']['tasks']['T1']
        self.assertEqual(node['status'], 'blocked')
        self.assertTrue(node['diagnosis_required'])
        return engine

    def test_cancelled_diagnosis_preserves_stop_instruction(self):
        self.diagnosed_wait()
        self.store.cancel('test', 'explicit-stop')
        entry = review(self.store.snapshot('test'), self.root)['requirements'][0]['nodes'][0]
        self.assertEqual(entry['status'], 'cancelled')
        self.assertEqual(entry['next_step'], 'respect cancellation')
        self.assertFalse(entry['execution']['diagnosis_required'])

    def test_reconciled_diagnosis_preserves_verified_completion(self):
        engine = self.diagnosed_wait()
        self.proof('T1')
        evidence = self.handler.run(self.plan['tasks'][0], None).evidence
        engine.reconcile('test', 'T1', evidence, 'host checked completed artifact')
        entry = review(self.store.snapshot('test'), self.root)['requirements'][0]['nodes'][0]
        self.assertEqual(entry['status'], 'done')
        self.assertEqual(entry['next_step'], 'verified result available')
        self.assertFalse(entry['execution']['diagnosis_required'])

    def test_mutated_report_invalidates_done_and_dependencies(self):
        self.proof('T1')
        self.engine.tick('test', 'first')
        path = self.root / self.plan['tasks'][0]['report_path']
        value = json.loads(path.read_text()); value['summary'] = 'changed'
        atomic_json(path, value)
        state = self.engine.tick('test', 'second')
        self.assertEqual(state['tasks']['T1']['status'], 'failed')
        self.assertEqual(state['tasks']['T2']['status'], 'blocked')

    def test_structural_report_does_not_replace_artifact_verification(self):
        (self.root / 'T1.txt').write_bytes(b'wrong bytes')
        self.engine.tick('test', 'first')
        self.assertFalse(review(self.store.snapshot('test'), self.root)['requirements'][0]['done'])

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'POSIX')
    def test_nonregular_report_rejected_without_reading_fifo(self):
        path = self.root / self.plan['tasks'][0]['report_path']
        path.unlink(); os.mkfifo(path)
        self.proof('T1')
        self.assertEqual(self.engine.tick('test', 'first')['tasks']['T1']['status'], 'blocked')

    def test_scoped_scheduler_cannot_execute_another_chain(self):
        other = copy.deepcopy(self.plan); other['run_id'] = 'other'
        self.store.create(other)
        scheduler = LocalScheduler(self.store)
        scheduler.heartbeat('fixture')
        arm(scheduler, 'other'); arm(scheduler, 'test')
        self.proof('T1')
        scheduler.drain_once(self.engine, 'test')
        self.assertEqual(self.store.snapshot('other')['state']['tasks']['T1']['attempts'], 0)
        self.assertEqual(self.store.snapshot('test')['state']['tasks']['T1']['status'], 'done')

    def test_no_tmux_never_falls_back_to_foreground(self):
        with patch('agent_runtime.task_supervisor.shutil.which', return_value=None):
            with self.assertRaisesRegex(RuntimeError, 'NOT started'):
                start('unused', self.root, self.root / 'run')

    def test_start_snapshots_root_source_and_requests_detached_session(self):
        path = self.root / 'ready.json'; atomic_json(path, self.plan)
        calls = []
        def fake_tmux(*args, **kwargs):
            calls.append(args)
            return SimpleNamespace(returncode=1 if args[0] == 'has-session' else 0)
        receipt = {'live': True, 'final_report': None, 'runtime_status': 'active',
                   'monitor': {'live': True, 'status': 'active'}}
        with patch('agent_runtime.task_supervisor.shutil.which', return_value='/fixture/tmux'), \
             patch('agent_runtime.task_supervisor.tmux', side_effect=fake_tmux), \
             patch('agent_runtime.task_supervisor.status', return_value=receipt):
            result = start(path, self.root, self.root / 'managed-run')
        self.assertEqual(result['status'], 'started')
        launch = next(args for args in calls if args[0] == 'new-session')
        self.assertIn('-d', launch)
        snapshot = json.loads((self.root / 'managed-run/source-snapshot.json').read_text())
        self.assertEqual(snapshot['content'], self.task_file.read_text())
        self.assertEqual(snapshot['sha256'], self.plan['task_source']['sha256'])

    def test_unconfigured_auto_draft_cannot_execute(self):
        path = self.root / 'draft.json'
        atomic_json(path, prepare(self.task_file, 'draft', 'auto', 'user'))
        with patch('agent_runtime.task_supervisor.shutil.which', return_value='/tmux'):
            with self.assertRaisesRegex(ValueError, 'configure'):
                start(path, self.root, self.root / 'run')
