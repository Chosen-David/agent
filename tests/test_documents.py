"""Documents host boundaries; real capability checks opt in to an installed root."""
import json
import contextlib
import io
import os
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
from unittest.mock import patch

from agent_runtime import documents as tools
from agent_runtime.documents_adapter import latex_escape


def pinned_document_platform():
    try:
        tools.platform_identity()
        return True
    except tools.DocumentsUnavailable:
        return False


class DocumentsBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'managed'

    def test_arbitrary_existing_directory_is_not_adopted(self):
        self.root.mkdir()
        sentinel = self.root / 'user.txt'
        sentinel.write_text('keep')
        with self.assertRaises((OSError, ValueError)):
            with tools.managed_root(self.root, create=True):
                pass
        self.assertEqual(sentinel.read_text(), 'keep')

    def test_symlink_root_and_ancestor_rejected(self):
        target = Path(self.temp.name) / 'target'
        target.mkdir()
        self.root.symlink_to(target, target_is_directory=True)
        for path in (self.root, self.root / 'child'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                with tools.managed_root(path, create=True):
                    pass

    def test_lock_fifo_rejected_without_blocking(self):
        with tools.managed_root(self.root, create=True):
            pass
        lock = self.root / 'install.lock'
        lock.unlink()
        os.mkfifo(lock)
        with self.assertRaises(ValueError):
            with tools.managed_root(self.root):
                pass

    def test_lock_symlink_rejected(self):
        with tools.managed_root(self.root, create=True):
            pass
        lock = self.root / 'install.lock'
        lock.unlink()
        lock.symlink_to(self.root / 'owner.json')
        with self.assertRaises(OSError):
            with tools.managed_root(self.root):
                pass

    def test_concurrent_lock_rejected_and_released(self):
        with tools.managed_root(self.root, create=True):
            with self.assertRaises(BlockingIOError):
                with tools.managed_root(self.root):
                    pass
        with tools.managed_root(self.root):
            pass

    def test_explicit_license_required_before_side_effects(self):
        with self.assertRaisesRegex(ValueError, 'license'):
            tools.install(self.root, None)
        self.assertFalse(self.root.exists())

    def test_unsupported_platform_is_explicit(self):
        with patch.object(tools.platform, 'system', return_value='Windows'):
            with self.assertRaisesRegex(tools.DocumentsUnavailable, 'unsupported'):
                tools.platform_identity()

    @unittest.skipUnless(pinned_document_platform(), 'optional wheel profile requires CPython3.12 Linux x86_64 glibc')
    def test_dependency_closure_and_wheel_tags(self):
        profile, sha = tools.load_profile()
        self.assertEqual(len(profile['packages']), 10)
        self.assertEqual(len(sha), 64)

    def test_invalid_current_version_cannot_traverse(self):
        with tools.managed_root(self.root, create=True):
            tools.atomic_json(self.root / 'current.json', dict(schema_version='documents-current/v1',
                              version='../escape', receipt_sha256='a' * 64))
            with self.assertRaisesRegex(ValueError, 'version'):
                tools.current(self.root)

    def test_incomplete_environment_never_reused(self):
        with tools.managed_root(self.root, create=True):
            version = 'a' * 64
            directory = self.root / version
            directory.mkdir()
            (directory / '.incomplete').write_text('{}')
            with self.assertRaisesRegex(ValueError, 'incomplete'):
                tools.verify(self.root, version, {})

    def test_latex_all_special_characters_are_literal(self):
        self.assertEqual(latex_escape('\\{}$&#%_~^'),
                         r'\textbackslash{}\{\}\$\&\#\%\_\textasciitilde{}\textasciicircum{}')

    @unittest.skipUnless(pinned_document_platform(), 'optional wheel profile requires CPython3.12 Linux x86_64 glibc')
    def test_offline_failure_preserves_current_bytes(self):
        with tools.managed_root(self.root, create=True):
            tools.atomic_json(self.root / 'current.json', {'old': True})
        before = (self.root / 'current.json').read_bytes()
        with self.assertRaisesRegex(ValueError, 'wheelhouse'):
            tools.install(self.root, 'agpl-3.0', offline=True)
        self.assertEqual((self.root / 'current.json').read_bytes(), before)

    def _adapter(self):
        path = Path(self.temp.name) / 'adapter.py'
        path.write_text("""import json, pathlib, sys, time
request = json.loads(pathlib.Path(sys.argv[2]).read_text())
out = pathlib.Path(sys.argv[3])
(out / 'artifact.txt').write_text('complete' if request['mode'] == 'ok' else 'partial')
if request['mode'] == 'race':
    target = pathlib.Path(request['target'])
    target.mkdir()
    if request.get('nonempty'):
        (target / 'sentinel').write_text('keep')
if request['mode'] == 'sleep':
    time.sleep(30)
if request['mode'] == 'invalid':
    print(json.dumps({'schema_version':'documents-result/v1','status':'invalid','error':'fixture invalid'}))
    raise SystemExit(3)
print(json.dumps({'schema_version':'documents-result/v1','status':'ok','result':{'file':'artifact.txt'}}))
""", encoding='utf-8')
        return path

    def test_atomic_output_failure_is_retryable_and_nested_parent_works(self):
        target = Path(self.temp.name) / 'nested' / 'result'
        with patch.object(tools, 'ADAPTER', self._adapter()):
            with self.assertRaisesRegex(ValueError, 'fixture invalid'):
                tools.run_adapter(sys.executable, 'fixture', {'mode': 'invalid'}, target,
                                  publish=True)
            self.assertFalse(target.exists())
            result = tools.run_adapter(sys.executable, 'fixture', {'mode': 'ok'}, target,
                                       publish=True)
        self.assertEqual(result['result']['file'], 'artifact.txt')
        self.assertEqual((target / 'artifact.txt').read_text(), 'complete')
        self.assertFalse(any(target.parent.glob('.result.staging-*')))

    def test_atomic_output_timeout_removes_partial_stage(self):
        target = Path(self.temp.name) / 'timeout'
        with (patch.object(tools, 'ADAPTER', self._adapter()),
              patch.object(tools.time, 'monotonic', side_effect=(0, 61))):
            with self.assertRaisesRegex(tools.DocumentsUnavailable, 'timeout'):
                tools.run_adapter(sys.executable, 'fixture', {'mode': 'sleep'}, target,
                                  publish=True)
        self.assertFalse(target.exists())
        self.assertFalse(any(target.parent.glob('.timeout.staging-*')))

    def test_atomic_output_never_replaces_concurrent_target(self):
        for nonempty in (False, True):
            with self.subTest(nonempty=nonempty):
                target = Path(self.temp.name) / f'race-{nonempty}'
                with patch.object(tools, 'ADAPTER', self._adapter()):
                    with self.assertRaisesRegex(ValueError, 'claimed concurrently'):
                        tools.run_adapter(sys.executable, 'fixture',
                                          {'mode': 'race', 'target': str(target),
                                           'nonempty': nonempty}, target, publish=True)
                self.assertTrue(target.is_dir())
                self.assertEqual((target / 'sentinel').read_text() if nonempty else None,
                                 'keep' if nonempty else None)
                self.assertFalse((target / 'artifact.txt').exists())
                self.assertFalse(any(target.parent.glob(f'.{target.name}.staging-*')))

    def test_atomic_publish_unavailable_does_not_fall_back_to_replace(self):
        target = Path(self.temp.name) / 'unsupported'
        fake = type('LibC', (), {})()
        with (patch.object(tools, 'ADAPTER', self._adapter()),
              patch.object(tools.ctypes, 'CDLL', return_value=fake)):
            with self.assertRaisesRegex(tools.DocumentsUnavailable, 'no-replace'):
                tools.run_adapter(sys.executable, 'fixture', {'mode': 'ok'}, target,
                                  publish=True)
        self.assertFalse(target.exists())
        self.assertFalse(any(target.parent.glob('.unsupported.staging-*')))

    def test_stage_cleanup_never_deletes_replaced_identity(self):
        parent = Path(self.temp.name) / 'parent'
        parent.mkdir()
        original = parent / 'stage'
        original.mkdir()
        observed = original.stat()
        identity = (observed.st_dev, observed.st_ino)
        original.rename(parent / 'moved')
        original.mkdir()
        (original / 'sentinel').write_text('keep')
        fd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            with self.assertRaisesRegex(tools.DocumentsUnavailable, 'manual recovery'):
                tools._remove_stage(fd, 'stage', identity)
        finally:
            os.close(fd)
        self.assertEqual((original / 'sentinel').read_text(), 'keep')


@unittest.skipUnless(os.environ.get('AGENT_DOCUMENTS_TEST_ROOT'), 'explicit installed documents root required')
class DocumentsCapabilityTests(unittest.TestCase):
    def test_real_probe_and_offline_reuse_never_invoke_pip(self):
        root = Path(os.environ['AGENT_DOCUMENTS_TEST_ROOT'])
        with tools.managed_root(root):
            _, receipt = tools.current(root)
        with (patch.object(tools.venv.EnvBuilder, 'create', side_effect=AssertionError('venv recreated')),
              patch.object(tools.subprocess, 'run', side_effect=AssertionError('pip called'))):
            result = tools.install(root, receipt['binding']['pymupdf_license'], offline=True)
        self.assertEqual(result['status'], 'reused')
        self.assertTrue(all(v == 'ready' for v in receipt['observation']['capabilities'].values()))

    def test_real_public_cli_artifacts_and_rejection(self):
        root = Path(os.environ['AGENT_DOCUMENTS_TEST_ROOT'])
        version = tools.read_json(root / 'current.json')['version']
        with tempfile.TemporaryDirectory() as temporary:
            temporary = Path(temporary)
            pdf = temporary / 'input.pdf'
            subprocess.run([str(root / version / 'bin/python'), '-I', '-c',
                            "import pymupdf,sys; d=pymupdf.open(); p=d.new_page(); "
                            "p.insert_text((72,72),'CLI fixture'); d.save(sys.argv[1])", str(pdf)],
                           check=True, timeout=30)
            text = temporary / 'text.txt'
            text.write_text('# Heading\n\n**bold** <script>alert(1)</script> a_b%{x}', encoding='utf-8')
            slides = temporary / 'slides.json'
            slides.write_text(json.dumps([dict(title='Title', body='Body')]))
            for command, source, filename in (
                    ('pdf-read', pdf, 'page-1.png'), ('markdown-render', text, 'document.html'),
                    ('pptx-create', slides, 'document.pptx'), ('latex-source', text, 'document.tex')):
                output = temporary / command
                result = subprocess.run([sys.executable, '-m', 'agent_runtime.documents',
                                         '--root', str(root), command, '--input', str(source),
                                         '--output-dir', str(output)], capture_output=True, text=True, timeout=90)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(json.loads(result.stdout)['status'], 'ok')
                self.assertGreater((output / filename).stat().st_size, 0)
            self.assertNotIn('<script>', (temporary / 'markdown-render/document.html').read_text())
            self.assertIn(r'a\_b\%\{x\}', (temporary / 'latex-source/document.tex').read_text())
            before = (temporary / 'markdown-render/document.html').read_bytes()
            with contextlib.redirect_stdout(io.StringIO()):
                code = tools.main(['--root', str(root), 'markdown-render', '--input', str(text),
                                   '--output-dir', str(temporary / 'markdown-render')])
            self.assertEqual(code, 3)
            self.assertEqual((temporary / 'markdown-render/document.html').read_bytes(), before)

    def test_invalid_multipage_pdf_leaves_no_partial_output_and_can_retry(self):
        root = Path(os.environ['AGENT_DOCUMENTS_TEST_ROOT'])
        version = tools.read_json(root / 'current.json')['version']
        with tempfile.TemporaryDirectory() as temporary:
            temporary = Path(temporary)
            pdf = temporary / 'two-pages.pdf'
            subprocess.run([str(root / version / 'bin/python'), '-I', '-c',
                            "import pymupdf,sys; d=pymupdf.open(); d.new_page(); d.new_page(); "
                            "d.save(sys.argv[1])", str(pdf)], check=True, timeout=30)
            output = temporary / 'rendered'
            invalid = subprocess.run([sys.executable, '-m', 'agent_runtime.documents',
                                      '--root', str(root), 'pdf-read', '--input', str(pdf),
                                      '--pages', '1', '3', '--output-dir', str(output)],
                                     capture_output=True, text=True, timeout=90)
            self.assertEqual(invalid.returncode, 3, invalid.stdout + invalid.stderr)
            self.assertEqual(json.loads(invalid.stdout)['status'], 'invalid')
            self.assertFalse(output.exists())
            valid = subprocess.run([sys.executable, '-m', 'agent_runtime.documents',
                                    '--root', str(root), 'pdf-read', '--input', str(pdf),
                                    '--pages', '1', '2', '--output-dir', str(output)],
                                   capture_output=True, text=True, timeout=90)
            self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)
            self.assertEqual(sorted(path.name for path in output.iterdir()),
                             ['page-1.png', 'page-2.png'])


if __name__ == '__main__':
    unittest.main()
