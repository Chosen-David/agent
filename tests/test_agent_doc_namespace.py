"""Functional namespace isolation and immutable historical read boundaries."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from agent_runtime import plan_review, project_docs, result_store, result_validation
from agent_runtime.legacy_result_paths import legacy_read_binding
from agent_runtime.task_manifest import prepare, validate_contract
from test_result_validation import make_fixture, independent_verify, dag


class AgentDocumentNamespaceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def marker(self, files):
        target = self.root / 'agent_doc/legacy-result-paths.json'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps({'schema_version': 'agent-doc-relocation/v1', 'files': files}), encoding='utf-8')

    def moved_file(self, name='artifact.txt', data=b'original bytes\r\n'):
        old = 'doc/results/legacy/' + name
        new = self.root / ('agent_doc/' + old[4:])
        new.parent.mkdir(parents=True, exist_ok=True)
        new.write_bytes(data)
        self.marker({old: hashlib.sha256(data).hexdigest()})
        return old, new, data

    def canonical_task(self):
        project_docs.initialize_project_docs(self.root)
        task = self.root / project_docs.CANONICAL_TASK
        task.write_text('# Tasks\n\n## 2026-10-08\n\n- [ ] [REQ] Work ([detail](task_details/REQ.md))\n')
        (task.parent / 'task_details/REQ.md').write_text('# Work\n\nTask-ID: REQ\nDate: 2026-10-08\n\n## Plan\n\nUser task.\n\n## Progress\n\nPending.\n')
        return task

    def test_existing_project_doc_and_other_project_stay_untouched(self):
        ordinary = self.root / 'doc/architecture.md'
        ordinary.parent.mkdir()
        ordinary.write_bytes(b'Project documentation\r\n')
        other = self.root / 'OtherProject'
        other.mkdir()
        before = ordinary.read_bytes(), ordinary.stat().st_mtime_ns
        for target in (self.root, other):
            project_docs.initialize_project_docs(target)
            self.assertTrue((target / 'agent_doc/task/TASK.md').is_file())
            self.assertFalse(list((target / 'agent_doc/guide').iterdir()))
        self.assertEqual(before, (ordinary.read_bytes(), ordinary.stat().st_mtime_ns))
        self.assertFalse((other / 'doc').exists())
        self.assertFalse((self.root / 'doc/task').exists())

    def test_explicit_canonical_task_infers_real_project_and_validates_details(self):
        task = self.canonical_task()
        plan = prepare(task, 'namespace-test', 'manual', 'explicit user task')
        self.assertEqual(project_docs.project_root_for_task(task), self.root)
        self.assertEqual(Path(plan['task_source']['path']), task)
        validate_contract(plan, self.root)
        stale = copy.deepcopy(plan)
        stale['project_documents']['task_index']['path'] = 'doc/task/TASK.md'
        with self.assertRaises(ValueError):
            validate_contract(stale, self.root)

    def test_three_readers_resolve_only_registered_unchanged_bytes(self):
        old, new, data = self.moved_file()
        ref = {'path': old, 'sha256': hashlib.sha256(data).hexdigest()}
        self.assertEqual(result_store._read(self.root, old), data)
        self.assertEqual(result_validation._bytes(self.root, old), data)
        plan_review._bound(self.root, ref)
        result_store._check_ref(self.root, ref)
        # Generic paths remain unmapped; registration/new writes are canonical.
        self.assertEqual(result_store._path(self.root, old), self.root / old)
        self.assertEqual(result_store.ResultStore(self.root)._record_path('new'), 'agent_doc/results/new/record.json')
        new.write_bytes(b'tampered')
        for call in (lambda: result_store._read(self.root, old), lambda: result_validation._bytes(self.root, old),
                     lambda: plan_review._bound(self.root, ref), lambda: result_store._check_ref(self.root, ref)):
            with self.assertRaises(ValueError):
                call()

    def test_unregistered_paths_and_collisions_do_not_silently_choose(self):
        old, new, data = self.moved_file()
        self.assertEqual(legacy_read_binding(self.root, 'doc/results/unknown/a'), ('doc/results/unknown/a', None))
        previous = self.root / old
        previous.parent.mkdir(parents=True)
        previous.write_bytes(data)
        with self.assertRaisesRegex(ValueError, 'collision'):
            result_validation._bytes(self.root, old)
        self.assertEqual(previous.read_bytes(), data)
        self.assertEqual(new.read_bytes(), data)

    def test_frozen_checkout_representations_do_not_waive_original_ref_hash(self):
        old, new, data = self.moved_file(data=b'original\n')
        alternate = b'original\r\n'
        digests = [hashlib.sha256(x).hexdigest() for x in (data, alternate)]
        self.marker({old: digests})
        for raw in (data, alternate):
            new.write_bytes(raw)
            self.assertEqual(result_validation._bytes(self.root, old), raw)
            result_store._check_ref(self.root, {'path': old, 'sha256': hashlib.sha256(raw).hexdigest()})
        with self.assertRaises(ValueError):
            result_store._check_ref(self.root, {'path': old, 'sha256': digests[0]})
        new.write_bytes(b'unregistered third representation')
        with self.assertRaises(ValueError):
            result_validation._bytes(self.root, old)

    def test_invalid_marker_schema_duplicate_keys_and_case_collisions_refused(self):
        old, _, _ = self.moved_file()
        marker = self.root / 'agent_doc/legacy-result-paths.json'
        digest = '0' * 64
        cases = [b'[]', b'{"schema_version":"bad","files":{}}',
                 ('{"schema_version":"agent-doc-relocation/v1","files":{"' + old + '":"' + digest + '","' + old + '":"' + digest + '"}}').encode(),
                 json.dumps({'schema_version':'agent-doc-relocation/v1', 'files':{old:digest,old.upper():digest}}).encode(),
                 json.dumps({'schema_version':'agent-doc-relocation/v1', 'files':{'doc/results/../outside':digest}}).encode(),
                 b'x' * (1024 * 1024 + 1)]
        for raw in cases:
            marker.write_bytes(raw)
            with self.subTest(raw=raw[:70]), self.assertRaises(ValueError):
                legacy_read_binding(self.root, old)

    def test_malformed_legacy_path_cannot_escape_or_redirect(self):
        self.moved_file()
        for value in ('doc/results/../secret', 'doc/results/C:secret', 'doc/results//file', 'doc/results/./file', 'doc/results/a\\b'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                legacy_read_binding(self.root, value)

    def test_symlinked_relocated_artifact_and_marker_refused(self):
        old, new, _ = self.moved_file()
        outside = self.root / 'outside'
        outside.write_bytes(b'outside')
        new.unlink()
        try:
            new.symlink_to(outside)
        except OSError:
            self.skipTest('symlink creation unavailable')
        with self.assertRaises(ValueError):
            legacy_read_binding(self.root, old)
        new.unlink()
        marker = self.root / 'agent_doc/legacy-result-paths.json'
        marker.unlink()
        marker.symlink_to(outside)
        with self.assertRaises(ValueError):
            legacy_read_binding(self.root, old)

    def test_both_guide_namespaces_reject_rebased_case_and_controlled_writes(self):
        from setup import installation_root
        from scripts.setup_codex import writable_installation_root
        for directory in ('agent_doc/guide', 'doc/guide', 'AGENT_DOC/GuIdE', 'DoC/GuIdE'):
            target = self.root / directory
            target.mkdir(parents=True, exist_ok=True)
            for call in (lambda: project_docs.initialize_project_docs(target),
                         lambda: project_docs.assert_ai_writable(self.root, target / 'new.md'),
                         lambda: project_docs.guard_write_path(target / 'new.md'),
                         lambda: installation_root(target), lambda: writable_installation_root(target)):
                with self.assertRaises(ValueError):
                    call()
            self.assertFalse(list(target.iterdir()))

    def test_preserved_legacy_contract_consumption_and_managed_input_binding(self):
        contract = make_fixture(self.root)
        manifest = json.loads((self.root / 'manifest.json').read_text())
        files = {}
        def relocate(name):
            old = 'doc/results/legacy/' + name
            moved = self.root / ('agent_doc/' + old[4:])
            moved.parent.mkdir(parents=True, exist_ok=True)
            moved.write_bytes((self.root / name).read_bytes())
            files[old] = hashlib.sha256(moved.read_bytes()).hexdigest()
            return old
        contract['manifest_path'] = 'doc/results/legacy/manifest.json'
        contract['validation_plan']['path'] = relocate('validation-plan.json')
        manifest['validation_plan'] = contract['validation_plan']
        for group in manifest['artifacts'].values():
            for item in group:
                item['path'] = relocate(item['path'])
        raw = (json.dumps(manifest, indent=2) + '\n').encode()
        (self.root / 'agent_doc/results/legacy/manifest.json').write_bytes(raw)
        files[contract['manifest_path']] = hashlib.sha256(raw).hexdigest()
        self.marker(files)
        def verifier(root, value, protocol):
            record = independent_verify(root, value, protocol)
            record['manifest_sha256'] = hashlib.sha256(raw).hexdigest()
            return record
        self.assertNotEqual(result_validation.inspect_result(self.root, contract)['status'], 'usable-with-scope')
        accepted = result_validation.inspect_result(self.root, contract, verifier)
        self.assertEqual(accepted['status'], 'usable-with-scope', accepted)
        self.assertTrue(result_validation.check_task_results(self.root, dag(contract)['tasks'][2], verifier))
        task = self.canonical_task()
        plan = prepare(task, 'managed-relocation', 'manual', 'synthetic host task')
        # A new canonical consumer binds historical review evidence while new
        # producers must still use canonical storage. Mapping grants no writes.
        plan['tasks'][0]['action'] = 'reuse_validated_result'
        plan['plan_review']['evidence_refs'] = [contract['validation_plan']]
        plan_review.current_inputs(self.root, plan)
        base = plan['tasks'][0]
        plan['tasks'] = [{**base, **node, 'report_path': f'.agent-runs/managed-relocation/{node["task_id"]}.json'}
                         for node in dag(contract)['tasks']]
        with self.assertRaisesRegex(ValueError, 'central'):
            plan_review.current_inputs(self.root, plan)
        # Existing compatibility plans bind the preserved contract directly;
        # test the validation_plan reader as well as policy evidence above.
        task.unlink()
        (self.root / 'TASK.md').write_text('- [ ] [REQ] Work\n')
        plan = prepare(self.root, 'managed-legacy-relocation', 'manual', 'synthetic compatibility plan')
        base = plan['tasks'][0]
        plan['tasks'] = [{**base, **node, 'report_path': f'.agent-runs/managed-relocation/{node["task_id"]}.json'}
                         for node in dag(contract)['tasks']]
        plan_review.current_inputs(self.root, plan)


if __name__ == '__main__':
    unittest.main()
