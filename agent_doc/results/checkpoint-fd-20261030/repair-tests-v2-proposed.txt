from pathlib import Path
import errno
import json
import os
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime import task_manifest as target

REAL_MKSTEMP = tempfile.mkstemp
VALUE = {'checkpoint': '恢复', 'status': 'pending'}
EXPECTED = (json.dumps(VALUE, ensure_ascii=False, indent=2) + '\n').replace('\n', os.linesep).encode('utf-8')


def closed(fd):
    try:
        os.fstat(fd)
    except OSError as exc:
        if exc.errno == errno.EBADF:
            return True
        raise
    return False


class CheckpointDescriptorDiagnosis(unittest.TestCase):
    def invoke(self, path, value, fault=None):
        acquired = []

        def tracked(*args, **kwargs):
            pair = REAL_MKSTEMP(*args, **kwargs)
            acquired.append(pair)
            return pair

        try:
            with patch.object(target.tempfile, 'mkstemp', side_effect=tracked):
                if fault is None:
                    target.atomic_json(path, value)
                else:
                    with patch.object(target.os, 'fdopen', side_effect=fault):
                        with self.assertRaises(OSError) as caught:
                            target.atomic_json(path, value)
                    self.assertIs(caught.exception, fault)
            self.assertEqual(len(acquired), 1)
            fd, temporary = acquired[0]
            is_closed = closed(fd)
            return acquired, is_closed, not Path(temporary).exists()
        except BaseException:
            for fd, _ in acquired:
                if not closed(fd):
                    os.close(fd)
            raise

    def test_normal_unicode_checkpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'checkpoint.json'
            owned, is_closed, removed = self.invoke(path, VALUE)
            try:
                self.assertEqual(path.read_bytes(), EXPECTED)
                self.assertEqual(json.loads(path.read_text(encoding='utf-8')), VALUE)
                self.assertTrue(is_closed)
                self.assertTrue(removed)
            finally:
                for fd, _ in owned:
                    if not closed(fd):
                        os.close(fd)

    def test_stream_construction_failure_preserves_state_and_releases_fd(self):
        for existing in (False, True):
            with self.subTest(existing=existing), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'checkpoint.json'
                old = b'old checkpoint bytes\n'
                if existing:
                    path.write_bytes(old)
                fault = OSError(errno.EIO, 'injected stream construction failure')
                owned, is_closed, removed = self.invoke(path, VALUE, fault)
                try:
                    self.assertEqual(path.exists(), existing)
                    if existing:
                        self.assertEqual(path.read_bytes(), old)
                    self.assertTrue(removed)
                    with self.subTest(check='raw descriptor closed'):
                        self.assertTrue(is_closed, 'raw fd remains open after fdopen construction failure')
                    target.atomic_json(path, VALUE)
                    self.assertEqual(path.read_bytes(), EXPECTED)
                    self.assertEqual(sorted(p.name for p in path.parent.iterdir()), [path.name])
                    print(json.dumps({'case': 'construct', 'existing': existing,
                                      'fd_closed_before_retry': is_closed,
                                      'temporary_removed': removed, 'retry_complete': True}), flush=True)
                finally:
                    for fd, _ in owned:
                        if not closed(fd):
                            os.close(fd)

    def test_serialization_failure_preserves_existing_and_closes_fd(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'checkpoint.json'
            old = b'old checkpoint bytes\n'
            path.write_bytes(old)
            acquired = []

            def tracked(*args, **kwargs):
                pair = REAL_MKSTEMP(*args, **kwargs)
                acquired.append(pair)
                return pair

            try:
                with patch.object(target.tempfile, 'mkstemp', side_effect=tracked):
                    with self.assertRaises(ValueError):
                        target.atomic_json(path, {'value': float('nan')})
                self.assertEqual(len(acquired), 1)
                fd, temporary = acquired[0]
                self.assertTrue(closed(fd))
                self.assertFalse(Path(temporary).exists())
                self.assertEqual(path.read_bytes(), old)
                self.assertEqual(sorted(p.name for p in path.parent.iterdir()), [path.name])
            finally:
                for fd, _ in acquired:
                    if not closed(fd):
                        os.close(fd)

