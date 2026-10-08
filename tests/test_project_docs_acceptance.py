# Legacy fixture: exercises pre-dual-main invariants; independent review is tested separately.
"""Independent adversarial checks frozen before reading candidate implementation.

Synthetic human-guide fixture bytes are only created inside temporary projects.
These tests establish controlled application-API behavior, never OS enforcement.
Acceptance specification and original source snapshot are retained externally.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from agent_runtime import project_docs as docs
from agent_runtime.core import Outcome, Store
from agent_runtime.task_manifest import ReportingHandler, atomic_json, prepare, validate_contract
from agent_runtime.task_supervisor import ManagedEngine


LEGACY = '''# Synthetic legacy project\n\n## 2026-10-06 Baseline\n\n- [ ] [A-1] Build a baseline\n  - Evidence: [original measurement](evidence/measurement.txt)\n\nKeep this historical failure, not just the checkbox.\n\n## 2026-10-07 Review\n\n- [x] [A-2] Review the baseline\n  - Evidence SHA256: SYNTHETIC-OLD-EVIDENCE\n'''


class ProjectDocumentAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='project-doc-acceptance-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'TASK.md').write_text(LEGACY, encoding='utf-8')
        (self.root / 'evidence').mkdir()
        (self.root / 'evidence/measurement.txt').write_bytes(b'synthetic historical measurement\n')

    def migrated(self):
        docs.migrate(self.root, '2026-10-07')
        return self.root / 'agent_doc/task/TASK.md'

    def human_guide(self, name='policy.md', text='Synthetic human guide: preserve all raw measurements.\n'):
        path = self.root / 'agent_doc/guide' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
        return path

    def all_bytes(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes()
                for p in self.root.rglob('*') if p.is_file() and not p.is_symlink()}

    def plan(self):
        plan = prepare(self.root / 'agent_doc/task/TASK.md', 'acceptance', 'auto', 'synthetic fixture authorization', review_required=False)
        snapshot = docs.snapshot_project_docs(self.root)
        plan['guide_reviews'] = [{'path':path, 'sha256':sha, 'origin':'owner_authored',
            'authorization_reference':'synthetic fixture human rule', 'task_refs':[x['task_id'] for x in plan['tasks']],
            'disposition':'applied', 'reason':'Preserve synthetic raw measurements in this fixture.'}
            for path, sha in snapshot['guides'].items()]
        docs.bind_guide_reviews(plan, plan['guide_reviews'])
        docs.bind_advice(plan, [])
        return plan

    def assert_rejected_without_writes(self, call):
        before = self.all_bytes()
        with self.assertRaises((ValueError, OSError)):
            call()
        self.assertEqual(before, self.all_bytes())

    def test_migration_preserves_source_ids_dates_and_is_idempotent(self):
        task = self.migrated()
        self.assertEqual(list((self.root / 'agent_doc/guide').rglob('*')), [])
        self.assertEqual(docs.resolve_task_file(self.root), task)
        items = docs.parse_requirements(task.read_text(), canonical=True)
        self.assertEqual({x['id']:(x['checked'], x['date']) for x in items},
                         {'A-2':(True, '2026-10-07'), 'A-1':(False, '2026-10-06')})
        archives = list((self.root / 'agent_doc/task/legacy').glob('TASK.*.md'))
        self.assertEqual(len(archives), 1)
        self.assertEqual(archives[0].read_bytes(), LEGACY.encode())
        self.assertEqual((self.root / 'evidence/measurement.txt').read_bytes(), b'synthetic historical measurement\n')
        before = self.all_bytes()
        docs.migrate(self.root, '2026-10-08')
        self.assertEqual(before, self.all_bytes())

    def test_legacy_progress_heading_is_preserved_without_breaking_new_boundary(self):
        text=LEGACY+'\n## Progress\nHistorical per-project status must remain available.\n'
        (self.root/'TASK.md').write_text(text)
        self.migrated();snapshot=docs.snapshot_project_docs(self.root)
        self.assertEqual(set(snapshot['task_details']),{'A-1','A-2'})
        self.assertTrue(any(p.read_bytes()==text.encode() for p in (self.root/'agent_doc/task/legacy').glob('TASK.*.md')))
        self.assertIn('Historical per-project status must remain available.',
                      (self.root/'agent_doc/task/task_details/A-2.md').read_text())
        before=self.all_bytes();self.migrated();self.assertEqual(self.all_bytes(),before)

    def test_relocated_evidence_link_resolves_to_original_measurement(self):
        self.migrated()
        detail = self.root / 'agent_doc/task/task_details/A-1.md'
        import re
        match = re.search(r'\[original measurement\]\(([^)]+)\)', detail.read_text())
        self.assertIsNotNone(match)
        self.assertEqual((detail.parent / match[1]).resolve(), self.root / 'evidence/measurement.txt')

    def test_two_active_task_roots_are_rejected_before_migration_or_ingestion(self):
        self.migrated()
        (self.root / 'TASK.md').write_text('- [ ] [OTHER] Competing requirements\n')
        self.assert_rejected_without_writes(lambda: docs.resolve_task_file(self.root))
        self.assert_rejected_without_writes(lambda: self.plan())
        self.assert_rejected_without_writes(lambda: docs.migrate(self.root, '2026-10-07'))

    def test_canonical_detail_identity_date_missing_or_orphan_are_rejected(self):
        self.migrated()
        detail = self.root / 'agent_doc/task/task_details/A-1.md'
        raw = detail.read_text()
        for replacement in (raw.replace('Task-ID: A-1', 'Task-ID: wrong'),
                            raw.replace('Date: 2026-10-06', 'Date: 2026-10-05')):
            with self.subTest(replacement=replacement[:90]):
                detail.write_text(replacement)
                with self.assertRaises(ValueError): docs.snapshot_project_docs(self.root)
        detail.write_text(raw)
        extra = detail.with_name('ORPHAN.md'); extra.write_text(raw)
        with self.assertRaises(ValueError): docs.snapshot_project_docs(self.root)
        extra.unlink(); detail.unlink()
        with self.assertRaises((ValueError, OSError)): docs.snapshot_project_docs(self.root)

    def test_canonical_date_link_and_duplicate_identity_validation(self):
        self.migrated()
        task = self.root / 'agent_doc/task/TASK.md'; raw = task.read_text()
        cases = [raw.replace('2026-10-07', '2026-13-07'),
                 raw.replace('task_details/A-1.md', 'task_details/A-2.md'),
                 raw + '\n- [ ] [A-1] Duplicate ([detail](task_details/A-1.md))\n']
        for text in cases:
            with self.subTest(text=text[:50]):
                task.write_text(text)
                with self.assertRaises((ValueError, OSError)): docs.snapshot_project_docs(self.root)
        task.write_text(raw)

    def test_guide_creation_write_and_path_aliases_are_denied(self):
        self.migrated(); guide = self.human_guide(); before = guide.read_bytes()
        targets = ['agent_doc/guide/new.md', 'agent_doc/guide/policy.md', './agent_doc/guide/policy.md',
                   'agent_doc//guide/policy.md', 'agent_doc/advice/../guide/policy.md', guide,
                   self.root / 'agent_doc/guide/../guide/policy.md', '../outside.md']
        for target in targets:
            with self.subTest(target=str(target)):
                self.assert_rejected_without_writes(lambda: docs.atomic_write(self.root, target, b'forbidden AI edit'))
        self.assertEqual(guide.read_bytes(), before)
        self.assertFalse((guide.parent / 'new.md').exists())

    def test_changing_project_root_to_guide_cannot_bypass_writes(self):
        self.migrated(); guide=self.human_guide().parent
        alias=self.root / 'guide-root-alias';alias.symlink_to(guide,target_is_directory=True)
        for supplied_root in (guide,alias):
            with self.subTest(root=str(supplied_root)):
                self.assert_rejected_without_writes(lambda: docs.atomic_write(supplied_root,'injected.md',b'forbidden'))
        self.assertFalse((guide/'injected.md').exists())

    def test_symlink_parent_leaf_and_lexical_guide_aliases_are_denied(self):
        self.migrated(); guide = self.human_guide()
        (self.root / 'shortcut.md').symlink_to(guide)
        (self.root / 'shortcut-dir').symlink_to(guide.parent, target_is_directory=True)
        ordinary = self.root / 'ordinary.md'; ordinary.write_bytes(b'ordinary')
        (guide.parent / 'outgoing.md').symlink_to(ordinary)
        for target in ('shortcut.md', 'shortcut-dir/policy.md', 'shortcut-dir/new.md', 'agent_doc/guide/outgoing.md'):
            with self.subTest(target=target):
                self.assert_rejected_without_writes(lambda: docs.atomic_write(self.root, target, b'forbidden'))
        self.assertEqual(ordinary.read_bytes(), b'ordinary')

    def test_hardlink_alias_is_denied_but_advice_write_is_allowed(self):
        self.migrated(); guide = self.human_guide()
        alias = self.root / 'hardlink.md'; os.link(guide, alias)
        self.assert_rejected_without_writes(lambda: docs.atomic_write(self.root, alias, b'forbidden'))
        docs.atomic_write(self.root, 'agent_doc/advice/idea.md', b'# Synthetic suggestion\n')
        self.assertEqual((self.root / 'agent_doc/advice/idea.md').read_bytes(), b'# Synthetic suggestion\n')

    def test_generic_json_writer_cannot_overwrite_guide_or_alias(self):
        self.migrated(); guide = self.human_guide('policy.json', '{"synthetic_human":true}\n')
        for target in (guide, self.root / 'agent_doc/guide/new.json'):
            with self.subTest(target=str(target)):
                self.assert_rejected_without_writes(lambda: atomic_json(target, {'forbidden': True}))

    def test_sqlite_runtime_store_cannot_create_inside_human_guide(self):
        self.migrated(); self.human_guide()
        self.assert_rejected_without_writes(lambda: Store(self.root / 'agent_doc/guide/runtime.sqlite'))
        self.assertFalse((self.root / 'agent_doc/guide/runtime.sqlite').exists())

    def test_additional_runtime_writers_preflight_human_guide_destinations(self):
        from agent_runtime.communication import Mailbox
        from agent_runtime.project_memory import MemoryLedger
        from agent_runtime.knowledge_index import build_index
        from agent_runtime.knowledge_ingest import ingest
        from agent_runtime.knowledge import KnowledgeStore
        self.migrated(); guide=self.human_guide().parent
        communication={'schema_version':1,'run_id':'synthetic','input_version':'synthetic-v1',
                       'routes':[{'sender':'producer','recipient':'consumer','task_id':'A-1','kind':'artifact'}]}
        corpus=KnowledgeStore(Path(docs.__file__).resolve().parents[1] / 'knowledge')
        actions=[lambda:Mailbox(guide/'mail.sqlite',communication,self.root),
                 lambda:MemoryLedger(guide,create=True),
                 lambda:build_index(corpus,guide/'knowledge.sqlite'),
                 lambda:ingest(guide,self.root/'missing-meta.json',self.root/'missing-body.md')]
        before=self.all_bytes()
        for action in actions:
            with self.subTest(action=action):
                with self.assertRaisesRegex(ValueError,'guide'):action()
                self.assertEqual(self.all_bytes(),before)
        self.assertEqual([p.name for p in guide.iterdir()],['policy.md'])

    def test_human_guide_edit_add_delete_and_rename_stale_plans(self):
        self.migrated(); guide = self.human_guide()
        for change in ('edit', 'add', 'delete', 'rename'):
            with self.subTest(change=change):
                original = self.all_bytes(); plan = self.plan()
                if change == 'edit': guide.write_text('Synthetic new human rule\n')
                elif change == 'add': self.human_guide('added.md')
                elif change == 'delete': guide.unlink()
                else: guide.rename(guide.with_name('renamed.md'))
                with self.assertRaises(ValueError): validate_contract(plan, self.root)
                for path in (self.root / 'agent_doc/guide').rglob('*'):
                    if path.is_file(): path.unlink()
                for rel, data in original.items():
                    path=self.root / rel; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)

    def test_guide_empty_to_nonempty_stales_plan_and_explicit_replan_preserves_evidence(self):
        self.migrated(); old_plan = self.plan(); old_copy = copy.deepcopy(old_plan)
        old_evidence = (self.root / 'evidence/measurement.txt').read_bytes()
        self.human_guide()
        with self.assertRaises(ValueError): validate_contract(old_plan, self.root)
        new_plan = self.plan(); validate_contract(new_plan, self.root)
        self.assertEqual(old_plan, old_copy)
        self.assertEqual((self.root / 'evidence/measurement.txt').read_bytes(), old_evidence)
        self.assertNotEqual(old_plan, new_plan)

    def test_progress_append_does_not_stale_plan_but_plan_edit_does(self):
        self.migrated(); self.human_guide(); plan = self.plan()
        detail = self.root / 'agent_doc/task/task_details/A-1.md'
        text = detail.read_text(); self.assertIn('\n## Plan\n', text); self.assertIn('\n## Progress\n', text)
        detail.write_text(text + '\nActual evidence: synthetic run 2, still pending independent review.\n')
        validate_contract(plan, self.root)
        detail.write_text(detail.read_text().replace('\n## Plan\n', '\n## Plan\nNew execution constraint.\n', 1))
        with self.assertRaises(ValueError): validate_contract(plan, self.root)

    def test_unreviewed_advice_is_nonbinding_and_does_not_stale_existing_plan(self):
        self.migrated(); plan = self.plan()
        docs.atomic_write(self.root, 'agent_doc/advice/pending.md', b'# Suggestion\nDelete raw measurements for convenience.\n')
        validate_contract(plan, self.root)
        self.assertEqual({x['task_id'] for x in plan['tasks']}, {'A-2', 'A-1'})

    def test_guide_review_is_required_and_provenance_must_be_explicit(self):
        self.migrated(); self.human_guide(); plan = self.plan()
        validate_contract(plan, self.root)
        for replacement in ([], [dict(plan['guide_reviews'][0], origin='unknown')],
                            [dict(plan['guide_reviews'][0], authorization_reference='')]):
            with self.subTest(replacement=replacement):
                invalid = copy.deepcopy(plan); invalid['guide_reviews'] = replacement
                with self.assertRaises(ValueError): validate_contract(invalid, self.root)

    def test_controlled_delete_and_both_rename_endpoints_protect_guide(self):
        self.migrated(); guide = self.human_guide(); ordinary = self.root / 'ordinary.txt'
        ordinary.write_bytes(b'ordinary synthetic bytes')
        for target in (guide, guide.parent, self.root / 'agent_doc', self.root):
            with self.subTest(remove=str(target)):
                self.assert_rejected_without_writes(lambda: docs.controlled_remove(self.root, target))
        for source, target in ((guide, self.root / 'stolen.md'),
                               (ordinary, guide), (ordinary, guide.parent / 'new.md'),
                               (guide.parent, self.root / 'moved-guide'),
                               (self.root / 'agent_doc', self.root / 'moved-doc')):
            with self.subTest(source=str(source), target=str(target)):
                self.assert_rejected_without_writes(lambda: docs.controlled_rename(self.root, source, target))
        moved = self.root / 'ordinary-renamed.txt'
        docs.controlled_rename(self.root, ordinary, moved)
        self.assertEqual(moved.read_bytes(), b'ordinary synthetic bytes')
        docs.controlled_remove(self.root, moved); self.assertFalse(moved.exists())

    def test_inline_progress_marker_cannot_hide_changed_planning_input(self):
        self.migrated(); detail = self.root / 'agent_doc/task/task_details/A-1.md'
        detail.write_text(detail.read_text().replace('## Plan\n', '## Plan\n\nExplanation mentions ## Progress\nBinding threshold is 10.\n', 1))
        plan = self.plan()
        detail.write_text(detail.read_text().replace('Binding threshold is 10.', 'Binding threshold is 100.'))
        with self.assertRaises(ValueError): validate_contract(plan, self.root)

    def test_canonical_handler_cannot_drop_document_refs_to_bypass_human_guide(self):
        self.migrated(); self.human_guide(); plan = self.plan(); task = copy.deepcopy(plan['tasks'][0])
        del task['document_refs']
        atomic_json(self.root / task['report_path'], {'task_id':task['task_id'], 'summary':'Synthetic result',
                        'data':[{'kind':'synthetic', 'description':'Fixture bytes'}]})
        calls=[]
        class Handler:
            idempotent=True
            required_capabilities=()
            def run(self, task, context):
                calls.append(task['task_id'])
                return Outcome('complete', 'Synthetic handler', [])
            def verify(self, task, evidence): return True
        outcome = ReportingHandler(Handler(), self.root).run(task, SimpleNamespace())
        self.assertEqual(outcome.status, 'blocked')
        self.assertEqual(calls, [])

    def test_advice_disposition_alignment_binding_and_source_change(self):
        self.migrated(); self.human_guide()
        advice='agent_doc/advice/idea.md'
        docs.atomic_write(self.root, advice, b'# Synthetic suggestion\nUse an explicit measured threshold.\n')
        plan=prepare(self.root / 'agent_doc/task/TASK.md', 'advice', 'auto', 'synthetic fixture approval', review_required=False)
        snapshot=docs.snapshot_project_docs(self.root)
        review=[{'path':path, 'sha256':sha, 'origin':'owner_authored',
                 'authorization_reference':'synthetic fixture', 'task_refs':['A-1','A-2'],
                 'disposition':'applied', 'reason':'Preserve raw evidence.'}
                for path,sha in snapshot['guides'].items()]
        docs.bind_guide_reviews(plan,review)
        base={'path':advice,'sha256':snapshot['advice'][advice], 'task_refs':['A-1'],
              'disposition':'adopt','reason':'Measured-threshold proposal fits the synthetic task.',
              'guide_alignment':'compatible'}
        invalid=[dict(base,guide_alignment='unresolved'), dict(base,reason=''),
                 dict(base,task_refs=['UNKNOWN']), dict(base,task_refs=[]),
                 dict(base,disposition='auto_accept')]
        for item in invalid:
            with self.subTest(item=item):
                with self.assertRaises(ValueError): docs.bind_advice(copy.deepcopy(plan),[item])
        docs.bind_advice(plan,[base]); validate_contract(plan,self.root)
        for task in plan['tasks']:
            self.assertEqual(advice in task['document_refs']['adopted_advice'], task['task_id']=='A-1')
        docs.atomic_write(self.root,advice,b'# Synthetic edited suggestion\nDifferent threshold.\n')
        with self.assertRaises(ValueError): validate_contract(plan,self.root)

    def test_rejected_or_deferred_advice_change_is_nonbinding(self):
        self.migrated(); advice='agent_doc/advice/idea.md'
        for disposition in ('reject','defer'):
            with self.subTest(disposition=disposition):
                docs.atomic_write(self.root,advice,b'# Synthetic proposal\n')
                plan=prepare(self.root / 'agent_doc/task/TASK.md','advice','auto','synthetic approval', review_required=False)
                source=docs.snapshot_project_docs(self.root)
                docs.bind_advice(plan,[{'path':advice,'sha256':source['advice'][advice],
                    'task_refs':['A-1'],'disposition':disposition,'reason':'Not required by current tasks.'}])
                validate_contract(plan,self.root)
                docs.atomic_write(self.root,advice,b'# Synthetic proposal update\n')
                validate_contract(plan,self.root)
                self.assertEqual(plan['project_documents']['adopted_advice'],{})

    def test_progress_helper_rejects_stale_planning_hash(self):
        self.migrated(); snapshot=docs.snapshot_project_docs(self.root)
        old_hash=snapshot['task_details']['A-1']['sha256']
        docs.write_task_progress(self.root,'A-1','Synthetic progress 1.\n',expected_plan_sha256=old_hash)
        self.assertEqual(docs.snapshot_project_docs(self.root)['task_details']['A-1']['sha256'],old_hash)
        detail=self.root / 'agent_doc/task/task_details/A-1.md'
        detail.write_text(detail.read_text().replace('## Plan\n','## Plan\nNew requirement.\n',1))
        self.assert_rejected_without_writes(lambda: docs.write_task_progress(
            self.root,'A-1','Stale progress overwrite.',expected_plan_sha256=old_hash))

    def test_stale_guide_blocks_actual_managed_dispatch(self):
        self.migrated(); guide = self.human_guide(); plan = self.plan()
        store = Store(self.root / 'state.sqlite'); store.create(plan)
        guide.write_text('Synthetic changed guide, must replan.\n')
        engine = ManagedEngine({'run_id':'acceptance', 'project_root':str(self.root), 'state_dir':str(self.root)},
                               store, {}, authorize=lambda *_: True, allow_legacy=True)
        with self.assertRaises(ValueError): engine.tick('acceptance', 'synthetic-event')
        self.assertTrue(all(x['attempts'] == 0 for x in store.snapshot('acceptance')['state']['tasks'].values()))

    def test_guide_changed_during_handler_blocks_completion(self):
        self.migrated(); guide = self.human_guide(); plan = self.plan(); task = plan['tasks'][0]
        atomic_json(self.root / task['report_path'], {'task_id':task['task_id'], 'summary':'Synthetic result',
                        'data':[{'kind':'synthetic', 'description':'Fixture bytes'}]})
        class Handler:
            idempotent = True
            required_capabilities = ()
            def run(self, task, context):
                guide.write_text('Synthetic human update while the operation ran.\n')
                return Outcome('complete', 'Fixture handler completed', [])
            def verify(self, task, evidence): return True
        outcome = ReportingHandler(Handler(), self.root).run(task, SimpleNamespace())
        self.assertEqual(outcome.status, 'blocked')

    def test_atomic_write_failure_preserves_previous_bytes(self):
        self.migrated(); target = self.root / 'agent_doc/advice/suggestion.md'
        docs.atomic_write(self.root, target, b'old suggestion')
        with patch.object(docs.os, 'replace', side_effect=OSError('synthetic interrupted commit')):
            with self.assertRaises(OSError): docs.atomic_write(self.root, target, b'new suggestion')
        self.assertEqual(target.read_bytes(), b'old suggestion')
        docs.atomic_write(self.root, target, b'new suggestion')
        self.assertEqual(target.read_bytes(), b'new suggestion')

    def test_migration_interruption_after_index_before_pointer_fails_closed_then_recovers(self):
        original=docs.atomic_write
        def interrupted(root,path,data):
            if Path(path)==Path('TASK.md') or Path(path)==self.root / 'TASK.md':
                raise OSError('synthetic interruption before final source pointer')
            return original(root,path,data)
        with patch.object(docs,'atomic_write',side_effect=interrupted):
            with self.assertRaises(OSError): docs.migrate(self.root,'2026-10-07')
        self.assertEqual((self.root / 'TASK.md').read_text(),LEGACY)
        self.assertTrue((self.root / 'agent_doc/task/TASK.md').exists())
        with self.assertRaises(ValueError): docs.resolve_task_file(self.root)
        self.migrated(); self.assertEqual(docs.resolve_task_file(self.root),self.root / 'agent_doc/task/TASK.md')

    def test_migration_refuses_to_overwrite_concurrent_legacy_source_change(self):
        original=docs.atomic_write; changed=[False]
        def concurrent_edit(root,path,data):
            result=original(root,path,data)
            if not changed[0]:
                changed[0]=True
                (self.root / 'TASK.md').write_text(LEGACY+'\n- [ ] [A-3] Concurrent human task\n')
            return result
        with patch.object(docs,'atomic_write',side_effect=concurrent_edit):
            with self.assertRaises(ValueError): docs.migrate(self.root,'2026-10-07')
        self.assertIn('[A-3] Concurrent human task',(self.root / 'TASK.md').read_text())
        self.assertTrue(any(p.read_bytes()==LEGACY.encode() for p in (self.root / 'agent_doc/task/legacy').glob('TASK.*.md')))
        self.assert_rejected_without_writes(lambda: docs.migrate(self.root,'2026-10-07'))

    def test_partial_migration_preserves_legacy_and_retries_idempotently(self):
        original = docs.atomic_write; count = [0]
        def interrupted(root, path, data):
            count[0] += 1
            if count[0] == 3: raise OSError('synthetic interruption between document writes')
            return original(root, path, data)
        with patch.object(docs, 'atomic_write', side_effect=interrupted):
            with self.assertRaises(OSError): docs.migrate(self.root, '2026-10-07')
        self.assertEqual((self.root / 'TASK.md').read_text(), LEGACY)
        self.migrated(); snapshot = docs.snapshot_project_docs(self.root)
        self.assertEqual(set(snapshot['task_details']), {'A-1','A-2'})
        before = self.all_bytes(); self.migrated(); self.assertEqual(before, self.all_bytes())


class ProjectDocumentInstallerAcceptanceTests(unittest.TestCase):
    setUp=ProjectDocumentAcceptanceTests.setUp
    migrated=ProjectDocumentAcceptanceTests.migrated
    human_guide=ProjectDocumentAcceptanceTests.human_guide

    def installer(self):
        import importlib.util
        source=Path(docs.__file__).resolve().parents[1] / 'setup.py'
        spec=importlib.util.spec_from_file_location('independent_document_installer',source)
        module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        return module

    def test_installer_skill_parent_alias_cannot_create_guide_files(self):
        self.migrated(); guide=self.human_guide().parent
        (self.root / '.claude').mkdir()
        (self.root / '.claude/skills').symlink_to(guide,target_is_directory=True)
        module=self.installer(); before={x.name:x.read_bytes() for x in guide.iterdir()}
        with patch.object(module.subprocess,'run',return_value=SimpleNamespace(stdout='synthetic-no-git\n')):
            with self.assertRaises(ValueError): module.install(self.root)
        self.assertEqual({x.name:x.read_bytes() for x in guide.iterdir()},before)
        self.assertFalse((self.root / '.claude/agent-workflows').exists())

    def test_uninstaller_skill_parent_alias_cannot_delete_human_guide_contents(self):
        import shutil
        self.migrated(); guide=self.human_guide().parent; module=self.installer()
        with patch.object(module.subprocess,'run',return_value=SimpleNamespace(stdout='synthetic-no-git\n')):
            module.install(self.root)
        skills=self.root / '.claude/skills'
        moved=guide / 'synthetic-human-links'; shutil.move(str(skills),str(moved))
        skills.symlink_to(moved,target_is_directory=True)
        before={x.name:os.readlink(x) for x in moved.iterdir()}
        with self.assertRaises(ValueError): module.uninstall(self.root)
        self.assertEqual({x.name:os.readlink(x) for x in moved.iterdir()},before)


class ProjectDocumentPublicationAcceptanceTests(unittest.TestCase):
    setUp = ProjectDocumentAcceptanceTests.setUp
    migrated = ProjectDocumentAcceptanceTests.migrated
    human_guide = ProjectDocumentAcceptanceTests.human_guide
    def local_git(self, *args):
        result = subprocess.run(['git', '-C', str(self.root), *args], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def test_ignored_human_guide_change_blocks_publication_gate(self):
        from agent_runtime.publication import PublicationLedger
        self.migrated(); guide = self.human_guide()
        (self.root / '.gitignore').write_text('.agent-runs/\nagent_doc/guide/\n')
        (self.root / 'app.py').write_text("print('synthetic baseline')\n")
        self.local_git('init', '-b', 'main')
        self.local_git('config', 'user.email', 'acceptance@example.invalid')
        self.local_git('config', 'user.name', 'Synthetic acceptance fixture')
        self.local_git('add', '.'); self.local_git('commit', '-m', 'synthetic baseline')
        remote = self.root.parent / (self.root.name + '-remote.git')
        self.addCleanup(lambda: __import__('shutil').rmtree(remote, ignore_errors=True))
        result = subprocess.run(['git', 'init', '--bare', str(remote)], capture_output=True)
        self.assertEqual(result.returncode, 0)
        self.local_git('remote', 'add', 'origin', str(remote))
        (self.root / 'app.py').write_text("print('synthetic candidate')\n")
        self.local_git('add', 'app.py')
        ledger = PublicationLedger(self.root, self.root / '.agent-runs/publication.json',
                                   authorize=lambda *_: True, accept=lambda *_: True, allow_legacy=True)
        frozen = ledger.freeze({'app.py':['A-1']}, remote='origin', branch='main',
                               authorization_reference='synthetic local fixture approval')
        self.assertNotIn('agent_doc/guide/policy.md', frozen['candidate']['files'])
        evidence = self.root / '.agent-runs/acceptance.json'; evidence.write_text('{"synthetic":true}\n')
        proof = [{'path':str(evidence), 'sha256':hashlib.sha256(evidence.read_bytes()).hexdigest(),
                  'task_refs':['A-1'], 'candidate_sha256':frozen['candidate']['sha256']}]
        guide.write_text('Synthetic human guide changed after candidate freeze.\n')
        with self.assertRaises(ValueError): ledger.mark_tested(proof)
        self.assertFalse(ledger.status()['tested'])


if __name__ == '__main__':
    unittest.main()
