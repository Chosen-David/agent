"""TASK identity and requirements must come from one bounded raw snapshot."""
import copy
import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import agent_runtime.task_manifest as manifest
from agent_runtime.task_manifest import prepare, task_source_snapshot, validate_contract


class TaskSourceSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.task = self.root / 'TASK.md'
        self.old = '- [ ] [OLD] original requirement\n'
        self.task.write_text(self.old)

    def test_validation_never_parses_a_second_transient_path_version(self):
        plan = prepare(self.task, 'snapshot-repro', 'auto', 'test', review_required=False)
        runtime_task = plan['tasks'][0]
        runtime_task.update(task_id='NEW', task_refs=['NEW'],
                            report_path='.agent-runs/snapshot-repro/results/NEW.json')
        original_read_text = Path.read_text
        swapped = False

        def transient_read(path, *args, **kwargs):
            nonlocal swapped
            if path == self.task and not swapped:
                swapped = True
                self.task.write_text('- [ ] [NEW] transient requirement\n')
                try:
                    return original_read_text(path, *args, **kwargs)
                finally:
                    self.task.write_text(self.old)
            return original_read_text(path, *args, **kwargs)

        with patch.object(Path, 'read_text', transient_read):
            with self.assertRaisesRegex(ValueError, 'known'):
                validate_contract(plan, self.root)
        self.assertFalse(swapped, 'validation must not reopen TASK through Path.read_text')
        self.assertEqual(self.task.read_text(), self.old)

    def test_prepare_rejects_task_and_document_snapshots_from_different_versions(self):
        original_snapshot = manifest.snapshot_project_docs

        def changed_documents(root):
            self.task.write_text('- [ ] [NEW] replacement requirement\n')
            try:
                return original_snapshot(root)
            finally:
                self.task.write_text(self.old)

        with patch.object(manifest, 'snapshot_project_docs', changed_documents):
            with self.assertRaisesRegex(ValueError, 'changed while preparing'):
                prepare(self.task, 'mixed-draft', 'auto', 'test', review_required=False)
        self.assertEqual(self.task.read_text(), self.old)

    def test_task_source_and_project_document_identities_must_match(self):
        plan = prepare(self.task, 'identity-conflict', 'auto', 'test', review_required=False)
        inconsistent = copy.deepcopy(plan)
        inconsistent['project_documents']['task_index']['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'snapshots differ'):
            validate_contract(inconsistent, self.root)

    def test_post_read_replacement_is_rejected_by_project_document_recheck(self):
        plan = prepare(self.task, 'post-read-replacement', 'auto', 'test', review_required=False)
        original_read = manifest.regular_bytes
        replaced = False

        def replace_after_read(root, path, **kwargs):
            nonlocal replaced
            data = original_read(root, path, **kwargs)
            if Path(path) == self.task and not replaced:
                replaced = True
                self.task.write_text('- [ ] [NEW] replacement after snapshot\n')
            return data

        try:
            with patch.object(manifest, 'regular_bytes', replace_after_read):
                with self.assertRaisesRegex(ValueError, 'project documents changed'):
                    validate_contract(plan, self.root)
            self.assertTrue(replaced)
        finally:
            self.task.write_text(self.old)

    def test_post_read_aba_cannot_change_bound_requirements(self):
        plan = prepare(self.task, 'post-read-aba', 'auto', 'test', review_required=False)
        original_read = manifest.regular_bytes
        swapped = False

        def aba_after_read(root, path, **kwargs):
            nonlocal swapped
            data = original_read(root, path, **kwargs)
            if Path(path) == self.task and not swapped:
                swapped = True
                self.task.write_text('- [ ] [NEW] transient after snapshot\n')
                self.task.write_text(self.old)
            return data

        with patch.object(manifest, 'regular_bytes', aba_after_read):
            items = validate_contract(plan, self.root)
        self.assertTrue(swapped)
        self.assertEqual([item['id'] for item in items], ['OLD'])
        self.assertEqual(items[0]['title'], 'original requirement')

    def test_raw_utf8_crlf_identity_is_not_normalized(self):
        raw = '- [ ] [T] 中文任务\r\n'.encode('utf-8')
        self.task.write_bytes(raw)
        snapshot = task_source_snapshot(self.task, self.root)
        self.assertEqual(snapshot['sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual(snapshot['items'][0]['id'], 'T')
        self.assertEqual(snapshot['items'][0]['title'], '中文任务')

    def test_invalid_oversized_and_nonregular_sources_fail_closed(self):
        cases = []
        invalid = self.root / 'invalid.md'
        invalid.write_bytes(b'\xff')
        cases.append(invalid)
        oversized = self.root / 'oversized.md'
        oversized.write_bytes(b'x' * (manifest.TASK_SOURCE_LIMIT + 1))
        cases.append(oversized)
        directory = self.root / 'directory.md'
        directory.mkdir()
        cases.append(directory)
        fifo = self.root / 'fifo.md'
        os.mkfifo(fifo)
        cases.append(fifo)
        target = self.root / 'target.md'
        target.write_text('- [ ] [T] target\n')
        link = self.root / 'link.md'
        link.symlink_to(target)
        cases.append(link)
        parent = self.root / 'real-parent'
        parent.mkdir()
        (parent / 'TASK.md').write_text('- [ ] [T] target\n')
        parent_link = self.root / 'parent-link'
        parent_link.symlink_to(parent, target_is_directory=True)
        cases.append(parent_link / 'TASK.md')

        for path in cases:
            with self.subTest(path=path), self.assertRaises((OSError, ValueError)):
                task_source_snapshot(path, self.root)

    def test_exact_byte_limit_is_accepted_and_bound(self):
        prefix = b'- [ ] [BOUNDARY] exact limit\n'
        raw = prefix + b'#' * (manifest.TASK_SOURCE_LIMIT - len(prefix))
        self.task.write_bytes(raw)
        snapshot = task_source_snapshot(self.task, self.root)
        self.assertEqual(snapshot['sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual([item['id'] for item in snapshot['items']], ['BOUNDARY'])


if __name__ == '__main__':
    unittest.main()
