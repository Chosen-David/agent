import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from agent_runtime import artifact_index as a
from agent_runtime.project_docs import DocumentError

class Inventory(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.root=Path(temp.name)
        (self.root/'a.md').write_bytes(b'abc')

    def test_lexical_symlink_refusal(self):
        alias = self.root / 'alias'
        try:
            alias.symlink_to(self.root / 'missing-target', target_is_directory=True)
        except OSError as exc:
            if os.name == 'nt' and getattr(exc, 'winerror', None) == 1314:
                self.skipTest('host does not permit creating fixture symlinks')
            raise
        with self.assertRaisesRegex(DocumentError, 'symlink'):
            a.build_artifact_index(self.root, directory='alias')

    def test_required_path_identity(self):
        with self.assertRaises(DocumentError):a.build_artifact_index(self.root,required=['bad\x00name'])
        for key in ('/a.md','../a.md','a//b','a/./b','C:/a','a\\b',3):
            with self.assertRaises(DocumentError):a.build_artifact_index(self.root,required=[key])
        self.assertTrue(a.build_artifact_index(self.root,required=['a.md'])['required']['a.md']['present'])

    def test_digest_refusal(self):
        self.assertTrue(a.build_artifact_index(self.root,required={'a.md':None})['required']['a.md']['present'])
        for value in (3,'X'*64,'abc'):
            with self.assertRaises(DocumentError):a.build_artifact_index(self.root,required={'a.md':value})
        result=a.build_artifact_index(self.root,required={'a.md':hashlib.sha256(b'abc').hexdigest()})
        self.assertTrue(result['required']['a.md']['match'])

    def test_diff_scope(self):
        current=a.build_artifact_index(self.root)
        for key in ('root','directory'):
            changed=dict(current);changed[key]='other'
            with self.assertRaises(DocumentError):a.diff_artifact_index(current,changed)
        self.assertFalse(a.diff_artifact_index(current,current)['any_changed'])

    def test_total_bytes(self):
        self.assertEqual(a.build_artifact_index(self.root,max_total_bytes=3)['count'],1)
        with self.assertRaises(DocumentError):a.build_artifact_index(self.root,max_total_bytes=2)
        (self.root/'b').write_bytes(b'd')
        with self.assertRaises(DocumentError):a.build_artifact_index(self.root,max_total_bytes=3)
        self.assertEqual(a.build_artifact_index(self.root,max_total_bytes=4)['count'],2)

if __name__=='__main__':unittest.main()
