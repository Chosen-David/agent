"""Import validation copies the corpus, not unrelated root-local artifacts."""
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime.knowledge import KnowledgeError, KnowledgeStore
from agent_runtime.knowledge_ingest import ingest

ROOT = Path(__file__).resolve().parents[1]


class IngestScopeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.root = self.base / 'knowledge'
        shutil.copytree(ROOT / 'knowledge', self.root)
        self.meta, self.body = self.base / 'draft.json', self.base / 'draft.md'
        data = json.loads((self.root / 'entries/math.cauchy-schwarz.json').read_text(encoding='utf-8'))
        data.update(id='math.scope-import', status='candidate', requires=[], relations=[])
        self.meta.write_text(json.dumps(data), encoding='utf-8')
        self.body.write_text('# Draft\nUnverified.\n', encoding='utf-8')

    def test_root_artifacts_are_not_copied_and_entries_attachments_remain(self):
        extra = self.root / 'unused.cache'
        extra.write_bytes(b'cache' * 1000)
        attachment = self.root / 'entries' / 'attachment.bin'
        attachment.write_bytes(b'keep entries subtree complete')
        copied = []
        attachments = []
        original = shutil.copytree
        def trace(src, dst, *args, **kwargs):
            copied.append(Path(src))
            result = original(src, dst, *args, **kwargs)
            candidate = Path(dst) / 'attachment.bin'
            if candidate.is_file():
                attachments.append(candidate.read_bytes())
            return result
        with patch.object(shutil, 'copytree', trace):
            receipt = ingest(self.root, self.meta, self.body)
        self.assertNotIn(self.root, copied)
        self.assertIn(self.root / 'entries', copied)
        self.assertIn(attachment.read_bytes(), attachments)
        self.assertEqual(extra.read_bytes(), b'cache' * 1000)
        self.assertEqual(receipt['status'], 'candidate')
        self.assertEqual(KnowledgeStore(self.root).ref('math.scope-import'), receipt['knowledge_ref'])

    def test_unrelated_dangling_link_does_not_break_import(self):
        link = self.root / 'unused.link'
        link.symlink_to(self.base / 'absent')
        receipt = ingest(self.root, self.meta, self.body)
        self.assertEqual(receipt['status'], 'candidate')
        self.assertTrue(link.is_symlink())

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'POSIX FIFO required')
    def test_unrelated_fifo_does_not_break_import(self):
        fifo = self.root / 'unused.pipe'
        os.mkfifo(fifo)
        self.assertEqual(ingest(self.root, self.meta, self.body)['status'], 'candidate')
        self.assertTrue(fifo.exists())

    def test_invalid_entry_subtree_is_still_rejected(self):
        original = KnowledgeStore(self.root).snapshot
        link = self.root / 'entries' / 'bad.link'
        link.symlink_to(self.base / 'absent')
        with self.assertRaisesRegex(KnowledgeError, 'symlink'):
            ingest(self.root, self.meta, self.body)
        link.unlink()
        orphan = self.root / 'entries' / 'orphan.md'
        orphan.write_text('no metadata', encoding='utf-8')
        with self.assertRaisesRegex(KnowledgeError, 'orphan'):
            ingest(self.root, self.meta, self.body)
        orphan.unlink()
        self.assertEqual(KnowledgeStore(self.root).snapshot, original)
        self.assertFalse((self.root / 'entries/math.scope-import').exists())

    def test_invalid_dependency_and_duplicate_leave_corpus_unchanged(self):
        original = KnowledgeStore(self.root).snapshot
        data = json.loads(self.meta.read_text(encoding='utf-8'))
        data['requires'] = [{'id': 'math.missing', 'version': 1}]
        self.meta.write_text(json.dumps(data), encoding='utf-8')
        with self.assertRaisesRegex(KnowledgeError, 'missing'):
            ingest(self.root, self.meta, self.body)
        self.assertEqual(KnowledgeStore(self.root).snapshot, original)
        data['requires'] = []
        self.meta.write_text(json.dumps(data), encoding='utf-8')
        ingest(self.root, self.meta, self.body)
        imported = KnowledgeStore(self.root).snapshot
        with self.assertRaisesRegex(KnowledgeError, 'already exists'):
            ingest(self.root, self.meta, self.body)
        self.assertEqual(KnowledgeStore(self.root).snapshot, imported)

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'POSIX FIFO required')
    def test_entry_fifo_is_not_silently_filtered(self):
        os.mkfifo(self.root / 'entries' / 'invalid.pipe')
        with self.assertRaises(shutil.Error):
            ingest(self.root, self.meta, self.body)
        self.assertFalse((self.root / 'entries/math.scope-import').exists())

    def test_corpus_change_during_staging_still_prevents_commit(self):
        original = shutil.copytree
        mutated = False
        def changing(src, dst, *args, **kwargs):
            nonlocal mutated
            result = original(src, dst, *args, **kwargs)
            if Path(src) in (self.root, self.root / 'entries') and not mutated:
                mutated = True
                with (self.root / 'entries/math.cauchy-schwarz.md').open('a', encoding='utf-8') as stream:
                    stream.write('\nConcurrent edit.\n')
            return result
        with patch.object(shutil, 'copytree', changing):
            with self.assertRaisesRegex(KnowledgeError, 'corpus changed'):
                ingest(self.root, self.meta, self.body)
        self.assertTrue(mutated)
        self.assertFalse((self.root / 'entries/math.scope-import').exists())


if __name__ == '__main__':
    unittest.main()
