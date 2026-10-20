"""Resource ownership at the production artifact-read boundary."""
import errno
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime import result_validation as rv


class ResultReadFdTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / 'file').write_bytes(b'payload')

    def check_closed(self, action):
        opened = []
        real_open = os.open
        def record(*args, **kwargs):
            fd = real_open(*args, **kwargs)
            opened.append(fd)
            return fd
        try:
            with patch.object(rv.os, 'open', record):
                action()
            self.assertEqual(len(opened), 1)
            with self.assertRaises(OSError) as caught:
                os.fstat(opened[0])
            self.assertEqual(caught.exception.errno, errno.EBADF)
        finally:
            # Reclaim only our descriptors when running against the old bug.
            for fd in opened:
                try:
                    os.close(fd)
                except OSError as exc:
                    if exc.errno != errno.EBADF:
                        raise

    @unittest.skipUnless(os.name == 'posix', 'directory descriptor regression')
    def test_directory_rejection_releases_fd(self):
        (self.root / 'directory').mkdir()
        def reject():
            with self.assertRaises(IsADirectoryError):
                rv._bytes(self.root, 'directory')
        for _ in range(8):
            self.check_closed(reject)

    def test_factory_failure_releases_fd(self):
        failure = RuntimeError('factory failed')
        def reject():
            with patch.object(rv.os, 'fdopen', side_effect=failure):
                with self.assertRaises(RuntimeError) as caught:
                    rv._bytes(self.root, 'file')
            self.assertIs(caught.exception, failure)
        self.check_closed(reject)

    def test_stat_failure_releases_fd(self):
        def reject():
            with patch.object(rv.os, 'fstat', side_effect=OSError('stat failed')):
                with self.assertRaisesRegex(OSError, 'stat failed'):
                    rv._bytes(self.root, 'file')
        self.check_closed(reject)

    def test_success_releases_fd(self):
        self.check_closed(lambda: self.assertEqual(rv._bytes(self.root, 'file'), b'payload'))


if __name__ == '__main__':
    unittest.main()
