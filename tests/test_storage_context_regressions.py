import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

class Storage(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.root=Path(temp.name)

    def test_whole_output_real_tokenizer(self):
        from agent_runtime.markdown_context import read_sections
        from agent_runtime.handoff_basis import make_token_counter
        try:
            import tiktoken
        except ImportError:
            self.skipTest('optional tiktoken unavailable; install in an isolated test environment')
        cache = patch.dict(os.environ, {'TIKTOKEN_CACHE_DIR': str(self.root / 'token-cache')})
        cache.start()
        self.addCleanup(cache.stop)
        raw=b'# A\n' + b'word '*100 + b'\n# B\n' + b'other '*1000
        (self.root/'file.md').write_bytes(raw)
        ref={'path':'file.md','sha256':hashlib.sha256(raw).hexdigest()}
        counter=make_token_counter('o200k_base')
        view=read_sections(self.root,ref,['s1'])
        size=counter(json.dumps(view,ensure_ascii=False,separators=(',',':'))+os.linesep)
        self.assertEqual(read_sections(self.root,ref,['s1'],max_tokens=size,token_counter=counter),view)
        with self.assertRaisesRegex(ValueError,'token budget'):read_sections(self.root,ref,['s1'],max_tokens=size-1,token_counter=counter)
        with self.assertRaises(ValueError):read_sections(self.root,ref,['s1'],max_tokens=1000,token_counter=lambda text:True)

    def test_compact_receipt_complete_restore(self):
        from agent_runtime.validation_context import write_validation_context,restore_validation_context
        result={'status':'pending','scope':'test','errors':['preserved'],'next_action':'verify','proof':{'artifact_hashes':{'a':'1'*64,'b':'2'*64},'review_evidence':{},'other':[1,2,'中文']}}
        pretty=write_validation_context(self.root,result,'agent_doc/results/pretty')
        compact=write_validation_context(self.root,result,'agent_doc/results/compact',compact_storage=True)
        self.assertEqual(restore_validation_context(self.root,pretty['record_ref']),result)
        self.assertEqual(restore_validation_context(self.root,compact['record_ref']),result)
        a=(self.root/pretty['record_ref']['path']).read_bytes();b=(self.root/compact['record_ref']['path']).read_bytes()
        self.assertEqual(json.loads(a),json.loads(b));self.assertLess(len(b),len(a))
        self.assertEqual(hashlib.sha256(b).hexdigest(),compact['record_ref']['sha256'])

    def test_compact_registry_same_values(self):
        from agent_runtime.result_store import ResultStore,ResultStoreError
        raw=b'data';(self.root/'input').write_bytes(raw)
        ref={'path':'input','sha256':hashlib.sha256(raw).hexdigest()}
        store=ResultStore(self.root)
        pretty=store.register_history('pretty','historical',[ref])
        record=pretty['record']
        record=dict(record,run_id='compact')
        compact=ResultStore(self.root,compact_storage=True)._save(record)
        a=(self.root/pretty['record_ref']['path']).read_bytes();b=(self.root/compact['record_ref']['path']).read_bytes()
        self.assertEqual(json.loads(b),record);self.assertLess(len(b),len(a))
        self.assertEqual(ResultStore(self.root).show('compact')['record'],record)
        with self.assertRaises(ResultStoreError):ResultStore(self.root,compact_storage=1)

    def test_metadata_only_bounded(self):
        from agent_runtime.storage_inventory import inventory
        (self.root/'.agent-memory').mkdir();(self.root/'.agent-memory/memory.sqlite3-wal').write_bytes(b'x'*100)
        (self.root/'a.md').write_bytes(b'abc')
        with patch('builtins.open',side_effect=AssertionError('file body read')):
            result=inventory(self.root,top=1)
        self.assertEqual(result['logical_bytes'],103);self.assertEqual(result['files'],2)
        self.assertEqual(result['groups']['private-memory']['logical_bytes'],100)
        self.assertEqual(result['largest'][0]['path'],'.agent-memory/memory.sqlite3-wal')
        with self.assertRaises(ValueError):inventory(self.root,max_entries=1)

    def test_generated_workflow_references(self):
        root=Path(__file__).resolve().parents[1]
        run=subprocess.run([sys.executable,'-X','utf8','-B',str(root/'scripts/sync_plugin_references.py'),'--check'],cwd=root,capture_output=True)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)

if __name__=='__main__':unittest.main()
