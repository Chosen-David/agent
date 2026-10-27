"""Import must recheck after private copying and never replace a claimed target."""
import ctypes
import errno
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from agent_runtime import knowledge_ingest as module
from agent_runtime.knowledge import KnowledgeError, KnowledgeStore

ROOT = Path(__file__).resolve().parents[1]


class ImportPublicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / 'knowledge'
        entries = self.root / 'entries'
        entries.mkdir(parents=True)
        for suffix in ('json', 'md'):
            shutil.copyfile(ROOT / 'knowledge/entries' / ('math.cauchy-schwarz.' + suffix),
                            entries / ('math.cauchy-schwarz.' + suffix))
        data = json.loads((entries / 'math.cauchy-schwarz.json').read_text(encoding='utf-8'))
        data.update(id='math.publication-import', status='candidate',
                    requires=[{'id': 'math.cauchy-schwarz', 'version': 1}], relations=[])
        self.meta, self.body = self.base / 'draft.json', self.base / 'draft.md'
        self.meta.write_text(json.dumps(data), encoding='utf-8')
        self.body.write_text('# Draft\nUnverified.\n', encoding='utf-8')
        self.destination = entries / data['id']

    def _late_edit(self, *, remove):
        original = shutil.copytree
        fired = False
        def interleave(src, dst, *args, **kwargs):
            nonlocal fired
            result = original(src, dst, *args, **kwargs)
            if Path(src).name == 'math.publication-import' and Path(dst).name == 'entry':
                fired = True
                if remove:
                    for suffix in ('json', 'md'):
                        (self.root / 'entries' / ('math.cauchy-schwarz.' + suffix)).unlink()
                else:
                    with (self.root / 'entries/math.cauchy-schwarz.md').open('ab') as stream:
                        stream.write(b'\nExternal edit.\n')
            return result
        with patch.object(shutil, 'copytree', interleave):
            with self.assertRaises(KnowledgeError):
                module.ingest(self.root, self.meta, self.body)
        self.assertTrue(fired)
        self.assertFalse(self.destination.exists())
        self.assertFalse(list(self.base.glob('.knowledge-import-*')))
        if not remove:
            self.assertTrue((self.root / 'entries/math.cauchy-schwarz.md').read_bytes().endswith(b'External edit.\n'))

    def test_dependency_removal_during_last_copy_is_refused(self):
        self._late_edit(remove=True)

    def test_body_edit_during_last_copy_is_refused(self):
        self._late_edit(remove=False)

    def test_success_keeps_complete_pair_provenance_and_reference(self):
        receipt = module.ingest(self.root, self.meta, self.body)
        self.assertEqual(set(p.name for p in self.destination.iterdir()),
                         {'entry.json', 'entry.md', 'provenance.txt'})
        self.assertEqual(KnowledgeStore(self.root).ref('math.publication-import'), receipt['knowledge_ref'])
        self.assertEqual(receipt['status'], 'candidate')
        self.assertFalse(list(self.base.glob('.knowledge-import-*')))

    def test_native_publisher_preserves_all_existing_targets(self):
        # The baseline's sole publication operation is os.rename. This fallback
        # is a test reference, never an alternative production implementation.
        publish = getattr(module, '_publish_entry', os.rename)
        for kind in ('empty', 'nonempty', 'file'):
            with self.subTest(kind=kind):
                parent = self.base / kind
                parent.mkdir()
                ready, target = parent / 'ready', parent / 'target'
                ready.mkdir()
                (ready / 'payload').write_bytes(b'ready')
                if kind == 'file':
                    target.write_bytes(b'owner')
                else:
                    target.mkdir()
                    if kind == 'nonempty':
                        (target / 'owner').write_bytes(b'owner')
                identity = (target.stat().st_dev, target.stat().st_ino)
                with self.assertRaises((OSError, KnowledgeError)):
                    publish(ready, target)
                self.assertEqual((target.stat().st_dev, target.stat().st_ino), identity)
                self.assertEqual((ready / 'payload').read_bytes(), b'ready')
                if kind == 'file':
                    self.assertEqual(target.read_bytes(), b'owner')
                elif kind == 'nonempty':
                    self.assertEqual((target / 'owner').read_bytes(), b'owner')

    def test_native_publisher_preserves_dangling_target(self):
        ready, target = self.base / 'ready', self.base / 'target'
        ready.mkdir()
        try:
            target.symlink_to(self.base / 'absent', target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest('symlink creation unavailable: ' + str(exc))
        publish = getattr(module, '_publish_entry', os.rename)
        with self.assertRaises((OSError, KnowledgeError)):
            publish(ready, target)
        self.assertTrue(target.is_symlink())
        self.assertTrue(ready.is_dir())

    def _publisher(self):
        publish = getattr(module, '_publish_entry', None)
        if publish is None:
            self.skipTest('baseline lacks explicit no-replace publisher; ABI tests apply to repair')
        return publish

    def test_posix_abi_and_error_propagation_without_unsafe_fallback(self):
        publish = self._publisher()
        for platform, name, args in (
                ('linux', 'renameat2', (-100, b'source', -100, b'target', 1)),
                ('darwin', 'renamex_np', (b'source', b'target', 4))):
            for code in (0, errno.EEXIST, errno.ENOSYS, errno.EPERM):
                with self.subTest(platform=platform, code=code):
                    native = Mock(return_value=0 if code == 0 else -1)
                    libc = SimpleNamespace(**{name: native})
                    with patch.object(module.sys, 'platform', platform), \
                         patch.object(module.ctypes, 'CDLL', return_value=libc) as load, \
                         patch.object(module.ctypes, 'get_errno', return_value=code), \
                         patch.object(module.os, 'rename') as unsafe:
                        if code:
                            with self.assertRaises(OSError) as raised:
                                publish(Path('source'), Path('target'))
                            self.assertEqual(raised.exception.errno, code)
                        else:
                            publish(Path('source'), Path('target'))
                        native.assert_called_once_with(*args)
                        load.assert_called_once_with(None, use_errno=True)
                        self.assertEqual(native.restype, ctypes.c_int)
                        self.assertEqual(native.argtypes[-1], ctypes.c_uint)
                        unsafe.assert_not_called()

    def test_missing_symbol_and_unsupported_platform_fail_closed(self):
        publish = self._publisher()
        for platform in ('linux', 'darwin', 'freebsd14'):
            with self.subTest(platform=platform), \
                 patch.object(module.sys, 'platform', platform), \
                 patch.object(module.ctypes, 'CDLL', return_value=SimpleNamespace()), \
                 patch.object(module.os, 'rename') as unsafe:
                with self.assertRaisesRegex(KnowledgeError, 'unavailable'):
                    publish('source', 'target')
                unsafe.assert_not_called()

    def test_windows_uses_native_rename_and_propagates_collision(self):
        publish = self._publisher()
        with patch.object(module.sys, 'platform', 'win32'), \
             patch.object(module.os, 'rename', side_effect=FileExistsError('owner')) as rename, \
             patch.object(module.ctypes, 'CDLL') as load:
            with self.assertRaises(FileExistsError):
                publish('source', 'target')
            rename.assert_called_once_with('source', 'target')
            load.assert_not_called()

    def test_target_claimed_after_final_guard_is_preserved(self):
        original = module.guard_write_path
        calls = 0
        def interleave(path):
            nonlocal calls
            result = original(path)
            if Path(path) == self.destination:
                calls += 1
                if calls == 2:
                    self.destination.mkdir()
            return result
        with patch.object(module, 'guard_write_path', interleave):
            with self.assertRaises((OSError, KnowledgeError)):
                module.ingest(self.root, self.meta, self.body)
        self.assertEqual(calls, 2)
        self.assertEqual(list(self.destination.iterdir()), [])
        self.assertFalse(list(self.base.glob('.knowledge-import-*')))


if __name__ == '__main__':
    unittest.main()
