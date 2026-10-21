"""Reject nonregular and redirected inputs before databases or documents are read."""
import os
from pathlib import Path
import stat
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from agent_runtime.knowledge import KnowledgeError
from agent_runtime.knowledge_index import _connect


class LocalPathGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='local-path-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_directory_refused_before_sqlite(self):
        with patch('agent_runtime.knowledge_index.sqlite3.connect') as connect:
            for readonly in (False, True):
                with self.assertRaisesRegex(KnowledgeError, 'regular'):
                    _connect(self.root, readonly=readonly)
            connect.assert_not_called()

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'FIFO requires POSIX')
    def test_fifo_refused_before_sqlite_without_opening_it(self):
        pipe = self.root / 'cache.sqlite'
        os.mkfifo(pipe)
        with patch('agent_runtime.knowledge_index.sqlite3.connect') as connect:
            with self.assertRaisesRegex(KnowledgeError, 'regular'):
                _connect(pipe)
            connect.assert_not_called()

    def test_parent_reparse_attribute_refused_before_sqlite(self):
        path = self.root / 'cache.sqlite'
        path.write_bytes(b'unchanged external cache')
        original = Path.lstat
        def info(candidate, *args, **kwargs):
            value = original(candidate, *args, **kwargs)
            if candidate == self.root:
                return SimpleNamespace(st_mode=value.st_mode,
                                       st_file_attributes=getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 1024))
            return value
        with patch.object(Path, 'lstat', info), patch('agent_runtime.knowledge_index.sqlite3.connect') as connect:
            for readonly in (False, True):
                with self.assertRaisesRegex(KnowledgeError, 'reparse'):
                    _connect(path, readonly=readonly)
            connect.assert_not_called()
        self.assertEqual(path.read_bytes(), b'unchanged external cache')

    def junction(self):
        if os.name != 'nt':
            self.skipTest('native Windows junction case')
        external = self.root / 'external'
        external.mkdir()
        alias = self.root / 'alias'
        result = subprocess.run(['cmd', '/c', 'mklink', '/J', str(alias), str(external)],
                                capture_output=True, timeout=10)
        if result.returncode:
            self.skipTest('host cannot create a fixture junction')
        return alias, external

    def test_native_junction_cache_is_not_opened(self):
        alias, external = self.junction()
        path = external / 'cache.sqlite'
        path.write_bytes(b'original cache bytes')
        with patch('agent_runtime.knowledge_index.sqlite3.connect') as connect:
            for readonly in (False, True):
                with self.assertRaisesRegex(KnowledgeError, 'reparse'):
                    _connect(alias / 'cache.sqlite', readonly=readonly)
            connect.assert_not_called()
        self.assertEqual(path.read_bytes(), b'original cache bytes')


if __name__ == '__main__':
    unittest.main()
