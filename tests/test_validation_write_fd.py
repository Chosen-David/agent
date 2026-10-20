"""Writer must release its own descriptor at every stream lifecycle boundary."""
import errno
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime.validation_context import write_validation_context, restore_validation_context


class ValidationWriteFDTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.result = dict(status='pending', scope='fd test', errors=[],
                           next_action='verify', proof=None)

    def exercise(self, phase=None, error=None):
        real_open, real_fdopen, real_close = os.open, os.fdopen, os.close
        opened = []

        def tracked_open(*args, **kwargs):
            fd = real_open(*args, **kwargs)
            opened.append(fd)
            return fd

        class Stream:
            def __init__(self, stream):
                self.stream = stream

            def __enter__(self):
                if phase == 'enter':
                    raise error
                return self

            def __exit__(self, *args):
                self.stream.close()

            def write(self, data):
                if phase == 'write':
                    raise error
                return self.stream.write(data)

            def flush(self):
                if phase == 'flush':
                    raise error
                return self.stream.flush()

            def fileno(self):
                return self.stream.fileno()

        streams = []

        def construct(*args, **kwargs):
            if phase == 'construct':
                raise error
            stream = real_fdopen(*args, **kwargs)
            streams.append(stream)
            return Stream(stream)

        try:
            with patch('os.open', side_effect=tracked_open), patch('os.fdopen', side_effect=construct):
                with patch('os.fsync', side_effect=error if phase == 'fsync' else None):
                    if phase:
                        with self.assertRaises(type(error)) as caught:
                            write_validation_context(self.root, self.result, 'agent_doc/results/fd')
                        self.assertIs(caught.exception, error)
                    else:
                        receipt = write_validation_context(self.root, self.result, 'agent_doc/results/fd')
            self.assertEqual(len(opened), 1)
            with self.assertRaises(OSError) as caught:
                os.fstat(opened[0])
            self.assertEqual(caught.exception.errno, errno.EBADF)
            if phase is None:
                self.assertEqual(restore_validation_context(self.root, receipt['record_ref']), self.result)
        finally:
            # Baseline failures must not leak into other tests; close owned fds only.
            for stream in streams:
                stream.close()
            for fd in opened:
                try:
                    os.fstat(fd)
                except OSError:
                    pass
                else:
                    real_close(fd)

    def test_constructor_failure_closes_fd(self):
        self.exercise('construct', OSError('constructor failure'))

    def test_interrupted_constructor_closes_fd(self):
        self.exercise('construct', KeyboardInterrupt('interrupted constructor'))

    def test_context_entry_failure_closes_fd(self):
        self.exercise('enter', RuntimeError('enter failure'))

    def test_write_failure_closes_fd(self):
        self.exercise('write', OSError('write failure'))

    def test_flush_failure_closes_fd(self):
        self.exercise('flush', OSError('flush failure'))

    def test_fsync_failure_closes_fd(self):
        self.exercise('fsync', OSError('fsync failure'))

    def test_success_closes_fd_and_roundtrips(self):
        self.exercise()

    def test_failed_open_does_not_close_unowned_fd(self):
        error = PermissionError('open denied')
        with patch('os.open', side_effect=error), patch('os.close') as close:
            with self.assertRaises(PermissionError) as caught:
                write_validation_context(self.root, self.result, 'agent_doc/results/fd')
        self.assertIs(caught.exception, error)
        close.assert_not_called()
