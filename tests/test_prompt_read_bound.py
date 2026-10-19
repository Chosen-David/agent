"""Reject oversized prompts without allocating their complete contents."""
import hashlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime.prompt_context import _read


class PromptReadBoundTests(unittest.TestCase):
    def test_reader_never_requests_unbounded_input(self):
        class Guarded(io.BytesIO):
            def read(self, size=-1):
                if not 0 <= size <= 1000001:
                    raise AssertionError('unbounded prompt read')
                return super().read(size)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'prompt.md').touch()
            with patch.object(Path, 'open', return_value=Guarded(b'x' * 1000002)):
                with self.assertRaisesRegex(ValueError, 'exceeds byte limit'):
                    _read(root, 'prompt.md')

    def test_exact_byte_boundary_and_raw_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / 'prompt.md'
            for raw in (b'', b'a\r\nb\rc\n', '中文'.encode(), b'x' * 1000000):
                with self.subTest(size=len(raw)):
                    path.write_bytes(raw)
                    self.assertEqual(_read(root, 'prompt.md'),
                                     (raw.decode(), hashlib.sha256(raw).hexdigest()))
            path.write_bytes(b'x' * 1000001)
            with self.assertRaisesRegex(ValueError, 'exceeds byte limit'):
                _read(root, 'prompt.md')

    def test_invalid_utf8_under_limit_still_raises(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'prompt.md').write_bytes(b'\xff')
            with self.assertRaises(UnicodeDecodeError):
                _read(root, 'prompt.md')
