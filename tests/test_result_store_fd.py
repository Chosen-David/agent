"""Owned descriptors must not survive failed result-store I/O operations."""
from contextlib import ExitStack
import errno
import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime import result_store as rs


class ResultStoreFDTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.payload = b'payload\x00\xff'
        (self.root / 'input').write_bytes(self.payload)
        self.ref = {'path': 'input', 'sha256': hashlib.sha256(self.payload).hexdigest()}
        self.store = rs.ResultStore(self.root)

    def exercise(self, action, phase=None, error=None):
        opened, streams = [], []
        real_open, real_fdopen, real_close = os.open, os.fdopen, os.close

        def acquire(*args, **kwargs):
            fd = real_open(*args, **kwargs)
            opened.append(fd)
            return fd

        class Stream:
            def __init__(self, inner):
                self.inner = inner

            def __enter__(self):
                if phase == 'enter':
                    raise error
                return self

            def __exit__(self, *args):
                self.inner.close()

            def read(self, *args):
                if phase == 'read':
                    raise error
                return self.inner.read(*args)

            def write(self, *args):
                if phase == 'write':
                    raise error
                return self.inner.write(*args)

            def flush(self):
                if phase == 'flush':
                    raise error
                return self.inner.flush()

            def fileno(self):
                return self.inner.fileno()

        def construct(*args, **kwargs):
            if phase == 'construct':
                raise error
            inner = real_fdopen(*args, **kwargs)
            streams.append(inner)
            return Stream(inner)

        try:
            with ExitStack() as stack:
                stack.enter_context(patch.object(rs.os, 'open', side_effect=acquire))
                stack.enter_context(patch.object(rs.os, 'fdopen', side_effect=construct))
                if phase in ('fstat', 'fsync', 'link'):
                    stack.enter_context(patch.object(rs.os, phase, side_effect=error))
                if error is not None:
                    with self.assertRaises(type(error)) as caught:
                        action()
                    if phase:
                        self.assertIs(caught.exception, error)
                else:
                    action()
            self.assertTrue(opened, 'fault must follow an actual fd acquisition')
            for fd in opened:
                with self.assertRaises(OSError) as caught:
                    os.fstat(fd)
                self.assertEqual(caught.exception.errno, errno.EBADF)
        finally:
            # Only reclaim this test's descriptors; observe leaks BEFORE cleanup.
            for stream in streams:
                stream.close()
            for fd in opened:
                try:
                    os.fstat(fd)
                except OSError as exc:
                    if exc.errno != errno.EBADF:
                        raise
                else:
                    real_close(fd)

    def readers(self, path='input'):
        return (lambda: rs._read(self.root, path),
                lambda: rs._check_ref(self.root, dict(self.ref, path=path)))

    @unittest.skipUnless(os.name == 'posix', 'directory descriptor behavior')
    def test_real_directory_rejection_closes_each_read_fd(self):
        (self.root / 'directory').mkdir()
        for action in self.readers('directory'):
            with self.subTest(action=action):
                self.exercise(action, error=IsADirectoryError())

    def test_read_construction_and_entry_failures_close_fd(self):
        for phase in ('construct', 'enter'):
            for action in self.readers():
                with self.subTest(phase=phase, action=action):
                    self.exercise(action, phase, RuntimeError(phase))

    def test_read_stat_and_read_failures_close_fd(self):
        for phase in ('fstat', 'read'):
            for action in self.readers():
                with self.subTest(phase=phase, action=action):
                    self.exercise(action, phase, OSError(phase))

    def test_read_success_and_stale_hash_preserve_contract(self):
        self.exercise(lambda: self.assertEqual(rs._read(self.root, 'input'), self.payload))
        self.exercise(lambda: self.assertIsNone(rs._check_ref(self.root, self.ref)))
        self.exercise(lambda: rs._check_ref(self.root, dict(self.ref, sha256='0' * 64)),
                      error=rs.ResultStoreError())

    def test_read_open_failure_does_not_close_unowned_fd(self):
        for action in self.readers():
            with self.subTest(action=action):
                with patch.object(rs.os, 'open', side_effect=PermissionError('denied')):
                    with patch.object(rs.os, 'close') as close:
                        with self.assertRaises(PermissionError):
                            action()
                        close.assert_not_called()

    def test_save_failures_close_fd_without_publishing(self):
        for phase in ('construct', 'enter', 'write', 'flush', 'fsync', 'link'):
            with self.subTest(phase=phase):
                # _save is exercised alone so faults cannot be consumed by _check_ref.
                run_id = 'failed-' + phase
                self.exercise(lambda: self.store._save({'run_id': run_id}),
                              phase, OSError(phase))
                self.assertEqual(list((self.root / rs.HOME / run_id).iterdir()), [])

    def test_interrupted_constructor_closes_fd(self):
        for action in (*self.readers(), lambda: self.store._save({'run_id': 'interrupted'})):
            with self.subTest(action=action):
                self.exercise(action, 'construct', KeyboardInterrupt('interrupted'))

    def test_registration_roundtrip_and_immutable_record(self):
        self.exercise(lambda: self.store.register_history('saved', 'needle', [self.ref]))
        record = self.root / rs.HOME / 'saved/record.json'
        original = record.read_bytes()
        with self.assertRaisesRegex(rs.ResultStoreError, 'immutable'):
            self.store.register_history('saved', 'different', [self.ref])
        self.assertEqual(record.read_bytes(), original)
        self.assertEqual(self.store.search('needle')['results'][0]['run_id'], 'saved')

    @unittest.skipUnless(os.name == 'posix', 'directory descriptor behavior')
    def test_search_repeated_bad_directory_does_not_leak(self):
        path = self.root / rs.HOME / 'bad/record.json'
        path.mkdir(parents=True)
        def search():
            result = self.store.search('needle')
            self.assertEqual(result['status'], 'incomplete')
            self.assertEqual(result['errors'][0]['run_id'], 'bad')
        for _ in range(4):
            self.exercise(search)


if __name__ == '__main__':
    unittest.main()
