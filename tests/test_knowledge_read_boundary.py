"""Actual input-byte limits, deterministic post-stat growth and text compatibility."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime.knowledge import KnowledgeError, KnowledgeStore, MAX_BYTES
from agent_runtime.knowledge_ingest import ingest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'plugins/research-assistant/skills/model-with-knowledge'


def files(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}


class ReadBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / 'knowledge'
        shutil.copytree(ROOT / 'knowledge', self.root)
        self.store = KnowledgeStore(self.root)

    def draft(self):
        data = json.loads((self.root / 'entries/math.cauchy-schwarz.json').read_text())
        data.update(id='math.read-boundary', status='candidate', requires=[], relations=[])
        meta, body = self.base / 'draft.json', self.base / 'draft.md'
        meta.write_text(json.dumps(data))
        body.write_text('# Draft\nUnverified.\n')
        return meta, body

    def growth_hook(self, target, extra, calls):
        original = Path.open
        fired = False

        class Reader:
            def __init__(self, stream):
                self.stream = stream
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return self.stream.__exit__(*args)
            def read(self, size=-1):
                result = self.stream.read(size)
                calls.append((size, len(result)))
                return result

        def opening(path, *args, **kwargs):
            nonlocal fired
            if path == target and not fired:
                fired = True
                with original(path, 'ab') as stream:
                    stream.write(extra)
                return Reader(original(path, *args, **kwargs))
            return original(path, *args, **kwargs)
        return patch.object(Path, 'open', opening)

    def test_post_stat_growth_all_four_entrypoints(self):
        # CRLF padding deliberately shrinks under universal newline conversion:
        # downstream staging must not accidentally conceal the input-byte breach.
        for entry in ('store_metadata', 'store_body', 'ingest_metadata', 'ingest_body'):
            for growth in (1, 4096):
                with self.subTest(entry=entry, growth=growth):
                    with tempfile.TemporaryDirectory(dir=self.base) as case:
                        corpus = Path(case) / 'knowledge'
                        shutil.copytree(ROOT / 'knowledge', corpus)
                        if entry.startswith('store'):
                            target = corpus / ('entries/math.cauchy-schwarz.' +
                                               ('json' if entry.endswith('metadata') else 'md'))
                            run = lambda: KnowledgeStore(corpus)
                            error = 'entry exceeds byte budget'
                        else:
                            meta, body = self.draft()
                            target = meta if entry.endswith('metadata') else body
                            run = lambda: ingest(corpus, meta, body)
                            error = 'import exceeds byte budget'
                        raw = target.read_bytes()
                        remaining = MAX_BYTES - len(raw)
                        target.write_bytes(raw + b'\r\n' * (remaining // 2) + b' ' * (remaining % 2))
                        before = files(corpus)
                        before_dirs = sorted(str(p.relative_to(Path(case))) for p in Path(case).rglob('*'))
                        calls = []
                        with self.growth_hook(target, b' ' * growth, calls):
                            with self.assertRaisesRegex(KnowledgeError, error):
                                run()
                        self.assertEqual(calls, [(MAX_BYTES + 1, MAX_BYTES + 1)])
                        if entry.startswith('ingest'):
                            self.assertEqual(files(corpus), before)
                            self.assertEqual(sorted(str(p.relative_to(Path(case))) for p in Path(case).rglob('*')), before_dirs)

    def test_text_and_exact_byte_limit_compatibility(self):
        target = self.root / 'probe.txt'
        for raw in (b'', b'a', b'a' * MAX_BYTES, 'é'.encode() * (MAX_BYTES // 2),
                    'BOM:\ufeff\r\nCR\rLF\nLS:\u2028PS:\u2029'.encode()):
            with self.subTest(length=len(raw)):
                target.write_bytes(raw)
                expected = target.read_text(encoding='utf-8')
                self.assertEqual(self.store._read(target), expected)
        for raw in (b'\xff', b'\xc3'):
            target.write_bytes(raw)
            with self.assertRaises(UnicodeDecodeError):
                self.store._read(target)
        target.write_bytes(b'a' * (MAX_BYTES + 1))
        with self.assertRaisesRegex(KnowledgeError, 'entry exceeds byte budget'):
            self.store._read(target)

    def test_growing_invalid_utf8_is_budget_error_before_decode(self):
        target = self.root / 'probe.txt'
        for extra in (b'\xff', b'\xc3\xa9'):
            target.write_bytes(b'a' * MAX_BYTES)
            calls = []
            with self.growth_hook(target, extra, calls):
                with self.assertRaisesRegex(KnowledgeError, 'entry exceeds byte budget'):
                    self.store._read(target)
            self.assertEqual(calls, [(MAX_BYTES + 1, MAX_BYTES + 1)])

    def test_normal_ingest_newlines_provenance_and_snapshot(self):
        meta, body = self.draft()
        meta.write_bytes(meta.read_bytes().replace(b',', b',\r\n'))
        body.write_bytes('Draft\r\nCR\rLF\nLS:\u2028'.encode())
        expected_meta = meta.read_text(encoding='utf-8')
        expected_body = body.read_text(encoding='utf-8')
        receipt = ingest(self.root, meta, body)
        self.assertEqual(receipt['metadata_sha256'], hashlib.sha256(expected_meta.encode()).hexdigest())
        self.assertEqual(receipt['body_sha256'], hashlib.sha256(expected_body.encode()).hexdigest())
        self.assertEqual((self.root / receipt['path'] / 'entry.md').read_text(), expected_body)
        loaded = KnowledgeStore(self.root)
        for kid, record in self.store.records.items():
            self.assertEqual(loaded.records[kid], record)
        # Existing corpus semantics are identical to the old read_text path.
        with patch.object(KnowledgeStore, '_read', lambda _, p: p.read_text(encoding='utf-8')):
            legacy = KnowledgeStore(self.root)
        self.assertEqual(loaded.snapshot, legacy.snapshot)
        self.assertEqual(loaded.records, legacy.records)

    def test_isolated_plugin_ingest_and_byte_identity(self):
        isolated = self.base / 'skill'
        shutil.copytree(SKILL, isolated)
        for name in ('knowledge.py', 'knowledge_ingest.py'):
            self.assertEqual((isolated / 'scripts' / name).read_bytes(),
                             (ROOT / 'agent_runtime' / name).read_bytes())
        meta, body = self.draft()
        result = subprocess.run([sys.executable, '-I', str(isolated / 'scripts/knowledge.py'),
                                 '--root', str(self.root), 'ingest', str(meta), str(body)],
                                cwd=self.base, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'candidate')
        self.assertIn('math.read-boundary', KnowledgeStore(self.root).records)


if __name__ == '__main__':
    unittest.main()
