"""Bounded artifact reads preserve bytes without max-size small-file allocation."""
import os
from pathlib import Path
import tempfile
import tracemalloc
import unittest
from unittest.mock import patch

from agent_runtime import result_validation as rv


class ResultReadAllocationTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.path = self.root / 'artifact'

    def test_small_artifact_peak(self):
        self.path.write_bytes(b'hello')
        tracemalloc.start()
        try:
            self.assertEqual(rv._bytes(self.root, 'artifact'), b'hello')
            self.assertLess(tracemalloc.get_traced_memory()[1], 1024 * 1024)
        finally:
            tracemalloc.stop()

    def test_stat_growth_and_shrink_exact_bytes(self):
        real_stat = os.fstat
        for old, new in ((0, 3), (1, 64), (3, 65), (64, 0), (64, 1)):
            with self.subTest(old=old, new=new):
                self.path.write_bytes(b'a' * old)
                payload = b'z' * new
                def mutate(fd):
                    info = real_stat(fd)
                    self.path.write_bytes(payload)
                    return info
                with patch.object(rv, 'LIMIT', 64), patch.object(rv.os, 'fstat', mutate):
                    if new > 64:
                        with self.assertRaisesRegex(rv.ResultValidationError, 'grew beyond'):
                            rv._bytes(self.root, 'artifact')
                    else:
                        self.assertEqual(rv._bytes(self.root, 'artifact'), payload)

    def test_empty_threshold_limit_and_oversized(self):
        for size in (0, 1, 65535, 65536, rv.LIMIT, rv.LIMIT + 1):
            with self.subTest(size=size):
                payload = b'\xff' * size
                self.path.write_bytes(payload)
                if size > rv.LIMIT:
                    with self.assertRaisesRegex(rv.ResultValidationError, 'exceeds 16 MiB'):
                        rv._bytes(self.root, 'artifact')
                else:
                    self.assertEqual(rv._bytes(self.root, 'artifact'), payload)

    def test_nonseekable_retains_original_read(self):
        self.path.write_bytes(b'hello')
        real_fdopen = os.fdopen
        calls = []
        class Stream:
            def __init__(self, fd, mode, **kwargs):
                self.raw = real_fdopen(fd, mode, **kwargs)
            def __enter__(self):
                return self
            def __exit__(self, *args):
                self.raw.close()
            def fileno(self):
                return self.raw.fileno()
            def seekable(self):
                return False
            def seek(self, *args):
                raise AssertionError('must not seek')
            def read(self, size):
                calls.append(size)
                return self.raw.read(size)
        with patch.object(rv.os, 'fdopen', Stream):
            self.assertEqual(rv._bytes(self.root, 'artifact'), b'hello')
        self.assertEqual(calls, [rv.LIMIT + 1])


if __name__ == '__main__':
    unittest.main()
