# Legacy fixture: exercises pre-dual-main invariants; independent review is tested separately.
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
        self.plan = prepare(self.task_file, 'test', 'auto', 'test user instruction', review_required=False)
        for task in self.plan['tasks']:
            task['action'] = 'verify_artifacts'
            task['done_when'] = {'artifacts': [{'path': task['task_id'] + '.txt',
                                    'sha256': hashlib.sha256(b'proof').hexdigest()}]}
            self.write_result(task)
        self.plan['tasks'][1]['depends_on'] = ['T1']
        self.store = Store(self.root / 'state.sqlite')
        self.store.create(self.plan)
        self.handler = ReportingHandler(ArtifactHandler(self.root), self.root)
        self.engine = Engine(self.store, {'verify_artifacts': self.handler}, authorize=lambda *_: True, allow_legacy=True)

    def write_result(self, task):
        atomic_json(self.root / task['report_path'], {'task_id': task['task_id'], 'summary': 'fixture output',
                    'data': [{'kind': 'synthetic', 'description': 'deterministic test bytes'}]})

    def proof(self, task_id):
        (self.root / (task_id + '.txt')).write_bytes(b'proof')

    def test_auto_and_manual_preserve_ids_and_never_trust_checkmarks(self):
        self.assertEqual(prepare(self.task_file, 'manual', 'manual', 'user', review_required=False)['task_source']['mode'], 'manual')
        self.assertEqual(validate_contract(self.plan, self.root)[1]['id'], 'T2')
        self.assertEqual(review(self.store.snapshot('test'), self.root, allow_legacy=True)['remaining'], ['T1', 'T2'])

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
        plan = prepare(nested, 'nested', 'auto', 'user', review_required=False)
        with self.assertRaisesRegex(ValueError, 'project-root TASK.md'):
            validate_contract(plan, self.root)

    def test_source_changes_prevent_dispatch_and_completion(self):
        self.task_file.write_text(self.task_file.read_text() + '- [ ] [T3] Newly requested work\n')
        config = {'run_id': 'test', 'project_root': str(self.root), 'state_dir': str(self.root)}
        engine = ManagedEngine(config, self.store, {'verify_artifacts': self.handler}, authorize=lambda *_: True, allow_legacy=True)
        with self.assertRaisesRegex(ValueError, 'changed'): engine.tick('test', 'event')
        self.assertEqual(self.store.snapshot('test')['state']['tasks']['T1']['attempts'], 0)
        report = review(self.store.snapshot('test'), self.root, allow_legacy=True)
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
        report = review(self.store.snapshot('test'), self.root, allow_legacy=True)
        self.assertEqual(report['remaining'], ['T2'])
        self.assertEqual(report['requirements'][0]['nodes'][0]['result']['data'][0]['kind'], 'synthetic')
        self.proof('T2')
        self.engine.tick('test', 'second')
        self.assertTrue(review(self.store.snapshot('test'), self.root, allow_legacy=True)['all_reportable'])
        # Reopening the real DB retains verified work and report provenance.
        self.assertTrue(review(Store(self.root / 'state.sqlite').snapshot('test'), self.root, allow_legacy=True)['all_reportable'])

    def test_missing_result_is_blocked_not_done(self):
        self.proof('T1')
        (self.root / self.plan['tasks'][0]['report_path']).unlink()
        state = self.engine.tick('test', 'first')
        self.assertEqual(state['tasks']['T1']['status'], 'blocked')
        self.assertFalse(review(self.store.snapshot('test'), self.root, allow_legacy=True)['all_reportable'])

    def test_progress_exposes_bounded_wait_and_task_identity(self):
        # No artifact yet: this is a real missing-file observation, not completion.
        self.engine.tick('test', 'pending')
        entry = review(self.store.snapshot('test'), self.root, allow_legacy=True)['requirements'][0]['nodes'][0]
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
                        authorize=lambda *_: True, clock=lambda: clock[0], allow_legacy=True)
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
        entry = review(self.store.snapshot('test'), self.root, allow_legacy=True)['requirements'][0]['nodes'][0]
        self.assertEqual(entry['status'], 'cancelled')
        self.assertEqual(entry['next_step'], 'respect cancellation')
        self.assertFalse(entry['execution']['diagnosis_required'])

    def test_reconciled_diagnosis_preserves_verified_completion(self):
        engine = self.diagnosed_wait()
        self.proof('T1')
        evidence = self.handler.run(self.plan['tasks'][0], None).evidence
        engine.reconcile('test', 'T1', evidence, 'host checked completed artifact')
        entry = review(self.store.snapshot('test'), self.root, allow_legacy=True)['requirements'][0]['nodes'][0]
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
        self.assertFalse(review(self.store.snapshot('test'), self.root, allow_legacy=True)['requirements'][0]['done'])

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
                start('unused', self.root, self.root / 'run', allow_legacy=True)

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
            result = start(path, self.root, self.root / 'managed-run', allow_legacy=True)
        self.assertEqual(result['status'], 'started')
        launch = next(args for args in calls if args[0] == 'new-session')
        self.assertIn('-d', launch)
        snapshot = json.loads((self.root / 'managed-run/source-snapshot.json').read_text())
        self.assertEqual(snapshot['content'], self.task_file.read_text())
        self.assertEqual(snapshot['sha256'], self.plan['task_source']['sha256'])

    def test_unconfigured_auto_draft_cannot_execute(self):
        path = self.root / 'draft.json'
        atomic_json(path, prepare(self.task_file, 'draft', 'auto', 'user', review_required=False))
        with patch('agent_runtime.task_supervisor.shutil.which', return_value='/tmux'):
            with self.assertRaisesRegex(ValueError, 'configure'):
                start(path, self.root, self.root / 'run', allow_legacy=True)


class ProjectDocumentsTests(unittest.TestCase):
    """New document architecture, on temporary projects; no live guide writes."""
    def setUp(self):
        from agent_runtime import project_docs
        self.docs = project_docs
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.legacy = b'# Tasks\n\n## 2026-10-06\n\n- [x] [T1] Preserve evidence\n  See [log](docs/log.md).\n- [ ] [T2] Finish work\n'
        (self.root / 'TASK.md').write_bytes(self.legacy)

    def migrated(self):
        return self.docs.migrate(self.root, '2026-10-07')

    def plan(self):
        return prepare(self.root, 'docs', 'auto', 'fixture explicit user task', review_required=False)

    def guide(self, data='Owner-authored fixture scope'):
        path = self.root / 'doc/guide/guide.md'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data)
        return path

    def reviewed(self, plan):
        return self.docs.bind_guide_reviews(plan, [
            {'path': path, 'sha256': sha, 'origin': 'owner_authored',
             'authorization_reference': 'fixture verified owner message', 'task_refs': ['T1', 'T2'],
             'disposition': 'applied', 'reason': 'same user-authorized scope'}
            for path, sha in plan['project_documents']['guides'].items()])

    def advice(self):
        path = self.root / 'doc/advice/idea.md'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('Try the bounded implementation')
        return path

    def assessed(self, plan, disposition='adopt'):
        items = [{'path': path, 'sha256': sha, 'task_refs': ['T1'], 'disposition': disposition,
                  'guide_alignment': 'compatible', 'reason': 'evaluated within existing scope'}
                 for path, sha in plan['project_documents']['advice'].items()]
        return self.docs.bind_advice(plan, items)

    def test_migration_preserves_ids_checks_dates_archive_links_and_has_no_guide_files(self):
        result = self.migrated()
        self.assertEqual(set(result['task_details']), {'T1', 'T2'})
        self.assertEqual(next((self.root / 'doc/task/legacy').glob('TASK.*.md')).read_bytes(), self.legacy)
        self.assertEqual(list((self.root / 'doc/guide').iterdir()), [])
        self.assertNotIn('- [', (self.root / 'TASK.md').read_text())
        detail = (self.root / 'doc/task/task_details/T1.md').read_text()
        self.assertIn('Date: 2026-10-06', detail)
        self.assertIn('[log](../../../docs/log.md)', detail)
        self.assertEqual(self.migrated(), result)
        self.assertEqual(validate_contract(self.plan(), self.root)[0]['id'], 'T1')

    def test_crash_before_index_or_pointer_recovers_without_overwriting_other_bytes(self):
        original = self.docs.atomic_write
        count = [0]
        def interrupt(root, path, data):
            count[0] += 1
            if count[0] == 4:
                raise OSError('injected interrupted migration')
            return original(root, path, data)
        with patch.object(self.docs, 'atomic_write', side_effect=interrupt):
            with self.assertRaisesRegex(OSError, 'interrupted'):
                self.migrated()
        self.assertEqual((self.root / 'TASK.md').read_bytes(), self.legacy)
        self.assertEqual(len(self.migrated()['task_details']), 2)

    def test_migration_conflict_preflight_preserves_all_existing_files(self):
        detail = self.root / 'doc/task/task_details/T1.md'
        detail.parent.mkdir(parents=True)
        detail.write_text('Unrelated user edits')
        with self.assertRaisesRegex(ValueError, 'different bytes'):
            self.migrated()
        self.assertEqual(detail.read_text(), 'Unrelated user edits')
        self.assertEqual((self.root / 'TASK.md').read_bytes(), self.legacy)
        self.assertFalse((self.root / 'doc/task/legacy').exists())

    def test_dual_active_index_and_orphan_details_fail_closed(self):
        self.migrated()
        (self.root / 'TASK.md').write_bytes(self.legacy)
        with self.assertRaisesRegex(ValueError, 'dual active'):
            self.docs.resolve_task_file(self.root)
        (self.root / 'TASK.md').write_text('Pointer only')
        (self.root / 'doc/task/task_details/extra.md').write_text('orphan')
        with self.assertRaisesRegex(ValueError, 'orphan'):
            self.docs.snapshot_project_docs(self.root)

    def test_progress_is_mutable_but_plan_and_identity_are_pinned(self):
        self.migrated()
        plan = self.plan()
        old = plan['project_documents']['task_details']['T1']['sha256']
        self.docs.write_task_progress(self.root, 'T1', '\nNew evidence\nTask-ID: quoted-evidence\n',
                                      expected_plan_sha256=old)
        validate_contract(plan, self.root)
        detail = self.root / 'doc/task/task_details/T1.md'
        detail.write_text(detail.read_text().replace('## Plan\n', '## Plan\nChanged method\n'))
        with self.assertRaisesRegex(ValueError, 'changed'):
            validate_contract(plan, self.root)
        with self.assertRaisesRegex(ValueError, 'planning version'):
            self.docs.write_task_progress(self.root, 'T1', 'discarded', expected_plan_sha256=old)

    def test_guide_review_is_required_and_changes_in_inventory_force_replan(self):
        self.migrated()
        guide = self.guide()
        plan = self.plan()
        with self.assertRaisesRegex(ValueError, 'guide review'):
            validate_contract(plan, self.root)
        self.reviewed(plan)
        validate_contract(plan, self.root)
        guide.write_text('Owner changed goal')
        with self.assertRaisesRegex(ValueError, 'guides'):
            validate_contract(plan, self.root)
        new = self.reviewed(self.plan())
        validate_contract(new, self.root)
        guide.unlink()
        with self.assertRaisesRegex(ValueError, 'guides'):
            validate_contract(new, self.root)

    def test_guide_changes_during_action_block_outcome(self):
        self.migrated()
        guide = self.guide()
        plan = self.reviewed(self.plan())
        class Handler:
            idempotent = True
            required_capabilities = set()
            def run(self, *_):
                guide.write_text('Human changes scope during work')
                return Outcome('pending', 'waiting')
            def verify(self, *_): return True
        outcome = ReportingHandler(Handler(), self.root).run(plan['tasks'][0], None)
        self.assertEqual(outcome.status, 'blocked')
        self.assertIn('documents changed', outcome.reason)

    def test_adopted_advice_is_scoped_and_nonadopted_or_new_advice_is_not_binding(self):
        self.migrated()
        advice = self.advice()
        plan = self.assessed(self.plan())
        validate_contract(plan, self.root)
        advice.write_text('Changed suggestion')
        with self.assertRaisesRegex(ValueError, 'adopted_advice'):
            self.docs.check_task_documents(self.root, plan['tasks'][0])
        self.docs.check_task_documents(self.root, plan['tasks'][1])
        plan = self.assessed(self.plan(), 'reject')
        advice.write_text('Another rejected suggestion')
        (advice.parent / 'new.md').write_text('New, unassessed, nonbinding suggestion')
        validate_contract(plan, self.root)

    def test_advice_conflict_and_missing_reason_cannot_be_adopted(self):
        self.migrated(); self.advice()
        plan = self.assessed(self.plan())
        for key, value in (('guide_alignment', 'unresolved'), ('reason', ''), ('task_refs', ['unknown'])):
            items = copy.deepcopy(plan['advice_assessments']); items[0][key] = value
            with self.assertRaises(ValueError):
                self.docs.bind_advice(plan, items)

    def test_controlled_write_delete_rename_reject_guide_and_ancestor_paths(self):
        self.migrated(); guide = self.guide()
        before = guide.read_bytes()
        for path in ('doc/guide/new.md', 'doc/guide/guide.md', 'doc/guide', 'doc', '.'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.docs.assert_ai_writable(self.root, path)
        with self.assertRaises(ValueError): atomic_json(guide, {'overwrite': True})
        with self.assertRaises(ValueError): self.docs.controlled_remove(self.root, guide)
        with self.assertRaises(ValueError): self.docs.controlled_rename(self.root, 'doc', 'moved')
        with self.assertRaises(ValueError): self.docs.controlled_rename(self.root, 'TASK.md', guide)
        self.assertEqual(guide.read_bytes(), before)

    def test_symlink_and_hardlink_aliases_cannot_reach_guide(self):
        self.migrated(); guide = self.guide()
        alias = self.root / 'alias'; alias.symlink_to(guide.parent, target_is_directory=True)
        with self.assertRaises(ValueError): atomic_json(alias / 'guide.md', {})
        hard = self.root / 'hard.md'; os.link(guide, hard)
        with self.assertRaises(ValueError): atomic_json(hard, {})
        self.assertEqual(guide.read_text(), 'Owner-authored fixture scope')

    def test_runtime_store_and_state_directory_cannot_write_guide(self):
        self.migrated(); self.guide()
        with self.assertRaises(ValueError): Store(self.root / 'doc/guide/state.sqlite')
        plan = self.reviewed(self.plan())
        path = self.root / 'ready.json'; atomic_json(path, plan)
        with patch('agent_runtime.task_supervisor.shutil.which', return_value='/fixture/tmux'):
            with self.assertRaisesRegex(ValueError, 'human-only'):
                start(path, self.root, self.root / 'doc/guide', allow_legacy=True)


    def test_inline_boundary_text_does_not_hide_later_planning_changes(self):
        self.migrated()
        detail = self.root / 'doc/task/task_details/T1.md'
        detail.write_text(detail.read_text().replace('## Plan\n',
                          '## Plan\nExplanation mentions ## Progress\nThreshold is 10.\n'))
        plan = self.plan()
        detail.write_text(detail.read_text().replace('Threshold is 10.', 'Threshold is 99.'))
        with self.assertRaisesRegex(ValueError, 'changed'):
            validate_contract(plan, self.root)

    def test_missing_refs_cannot_bypass_canonical_handler_gate(self):
        self.migrated()
        task = self.plan()['tasks'][0]
        task.pop('document_refs')
        class Handler:
            idempotent = True
            required_capabilities = set()
            called = False
            def run(self, *_):
                self.called = True
                return Outcome('complete', 'not valid')
        handler = Handler()
        result = ReportingHandler(handler, self.root).run(task, None)
        self.assertEqual(result.status, 'blocked')
        self.assertFalse(handler.called)

    def test_stale_adopted_advice_blocks_only_linked_live_branch(self):
        self.migrated(); advice = self.advice()
        plan = self.assessed(self.plan())
        class Handler:
            idempotent = True
            required_capabilities = set()
            def run(self, *_): return Outcome('pending', 'independent work dispatched')
        for task in plan['tasks']:
            task['action'] = 'fixture'
            task['done_when'] = {'fixture': True}
        store = Store(self.root / 'state.sqlite'); store.create(plan)
        config = {'run_id': 'docs', 'project_root': str(self.root), 'state_dir': str(self.root / 'run')}
        engine = ManagedEngine(config, store, {'fixture': ReportingHandler(Handler(), self.root)},
                               authorize=lambda *_: True, allow_legacy=True)
        advice.write_text('changed adopted suggestion')
        engine.tick('docs', 'changed-advice')
        state = engine.tick('docs', 'next-independent-branch')
        self.assertEqual(state['tasks']['T1']['status'], 'blocked')
        self.assertEqual(state['tasks']['T2']['dispatches'], 1)
        self.assertIsNone(review(store.snapshot('docs'), self.root, allow_legacy=True)['source_error'])


    def test_rebasing_project_root_does_not_bypass_guide_guard(self):
        self.migrated(); guide = self.guide()
        alias = self.root / 'guide-alias'; alias.symlink_to(guide.parent, target_is_directory=True)
        for root in (guide.parent, alias):
            with self.subTest(root=root), self.assertRaisesRegex(ValueError, 'human-only'):
                self.docs.atomic_write(root, 'injected.md', b'forbidden')
        self.assertEqual(sorted(path.name for path in guide.parent.iterdir()), ['guide.md'])

    def test_other_runtime_writer_entrypoints_reject_guide_destination(self):
        from agent_runtime.communication import Mailbox
        from agent_runtime.knowledge_index import _connect
        from agent_runtime.knowledge_ingest import ingest
        from agent_runtime.project_memory import MemoryLedger
        self.migrated(); guide = self.guide()
        communication = {'schema_version': 1, 'run_id': 'fixture', 'input_version': 'v1',
                         'routes': [{'sender': 'code', 'recipient': 'review', 'task_id': 'T1', 'kind': 'artifact'}]}
        for action in (lambda: Mailbox(guide.parent / 'mail.sqlite', communication, self.root),
                       lambda: _connect(guide.parent / 'index.sqlite'),
                       lambda: ingest(guide.parent, 'unread', 'unread'),
                       lambda: MemoryLedger(guide.parent, create=True)):
            with self.assertRaisesRegex(ValueError, 'human-only'):
                action()
        self.assertEqual(sorted(path.name for path in guide.parent.iterdir()), ['guide.md'])


    def test_supervisor_lock_alias_cannot_modify_human_guide(self):
        self.migrated(); guide = self.guide()
        plan = self.reviewed(self.plan())
        for task in plan['tasks']:
            task['action'] = 'verify_artifacts'; task['done_when'] = {'fixture': True}
        plan_path = self.root / 'ready.json'; atomic_json(plan_path, plan)
        state_dir = self.root / 'run'; state_dir.mkdir()
        (state_dir / 'launch.lock').symlink_to(guide)
        with patch('agent_runtime.task_supervisor.shutil.which', return_value='/fixture/tmux'):
            with self.assertRaises(ValueError):
                start(plan_path, self.root, state_dir, allow_legacy=True)
        self.assertEqual(guide.read_text(), 'Owner-authored fixture scope')


    def test_legacy_progress_heading_is_excerpt_not_second_live_boundary(self):
        raw = self.legacy + b'\n## Progress\nHistorical status data.\n'
        (self.root / 'TASK.md').write_bytes(raw)
        snapshot = self.migrated()
        self.assertEqual(len(snapshot['task_details']), 2)
        self.assertEqual(next((self.root / 'doc/task/legacy').glob('TASK.*.md')).read_bytes(), raw)
        self.assertIn('### Legacy Progress', (self.root / 'doc/task/task_details/T2.md').read_text())
        self.assertEqual(self.migrated(), snapshot)


    def test_omitted_detail_dependencies_and_report_input_overlap_are_rejected(self):
        self.migrated()
        plan = self.plan()
        task = copy.deepcopy(plan['tasks'][0]); task['document_refs']['task_details'] = {}
        with self.assertRaisesRegex(ValueError, 'omitted'):
            self.docs.check_task_documents(self.root, task)
        plan['tasks'][0]['report_path'] = 'doc/task/task_details/T1.md'
        with self.assertRaisesRegex(ValueError, 'report paths'):
            validate_contract(plan, self.root)


    def test_prepare_and_live_dispatch_perform_prior_result_lookup_before_data_work(self):
        from agent_runtime.result_store import ResultStore
        self.migrated()
        evidence = self.root / 'prior.txt'; evidence.write_text('preserved previous result')
        registered = ResultStore(self.root).register_history('earlier', 'Preserve evidence', [
            {'path': 'prior.txt', 'sha256': hashlib.sha256(evidence.read_bytes()).hexdigest()}])
        plan = self.plan(); task = plan['tasks'][0]
        self.assertEqual(task['prior_result_search']['results'][0]['run_id'], 'earlier')
        # A forged plan-side no-hit does not substitute for a fresh live lookup.
        task['prior_result_search'] = {'status': 'no_hits', 'results': []}
        task['produces_data'] = True
        class Handler:
            idempotent = True
            required_capabilities = set()
            called = False
            def run(self, received, _):
                self.called = True
                self.received = received
                return Outcome('pending', 'data work started after rationale')
        handler = Handler(); wrapper = ReportingHandler(handler, self.root)
        self.assertEqual(wrapper.run(task, None).status, 'blocked')
        self.assertFalse(handler.called)
        task['prior_result_review'] = {'decision': 'rerun', 'reason': 'prior record lacks verified conditions',
                                       'record_refs': [{'run_id': 'earlier',
                                                        'record_sha256': registered['record_ref']['sha256']}]}
        self.assertEqual(wrapper.run(task, None).status, 'pending')
        self.assertTrue(handler.called)
        self.assertEqual(handler.received['prior_result_search']['results'][0]['run_id'], 'earlier')

    def test_live_lookup_is_journaled_and_no_hit_does_not_create_registry(self):
        self.migrated()
        plan = self.plan()
        self.assertFalse((self.root / 'doc/results').exists())
        for task in plan['tasks']:
            task['action'] = 'fixture'; task['done_when'] = {'fixture': True}
        class Handler:
            idempotent = True
            required_capabilities = set()
            def run(self, *_): return Outcome('pending', 'bounded task')
        store = Store(self.root / 'state.sqlite'); store.create(plan)
        engine = Engine(store, {'fixture': ReportingHandler(Handler(), self.root)}, authorize=lambda *_: True, allow_legacy=True)
        engine.tick('docs', 'first-lookup')
        with store.transaction() as db:
            rows = db.execute("SELECT detail FROM journal WHERE kind='prior_result_search'").fetchall()
        self.assertEqual(len(rows), 1)
        logged = json.loads(rows[0][0])
        self.assertEqual(logged['task_id'], 'T1')
        self.assertEqual(logged['search']['status'], 'no_hits')
        self.assertFalse((self.root / 'doc/results').exists())
