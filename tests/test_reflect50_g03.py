import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from agent_runtime import project_docs as d

class Navigation(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup); self.root=Path(temp.name)
        directory=self.root/'agent_doc/task/task_details'; directory.mkdir(parents=True)
        (directory.parent/'TASK.md').write_text('## 2026-10-21\n'+''.join('- [ ] ['+i+'] Title ([detail](task_details/'+i+'.md))\n' for i in ('A','B','C')),encoding='utf-8')
        for i in ('A','B','C'):
            (directory/(i+'.md')).write_text('Task-ID: '+i+'\nDate: 2026-10-21\n## Plan\n### 摘要\n'+i*100+'\n## Progress\nlive',encoding='utf-8')

    def test_R11_explicit_selection(self):
        self.assertEqual([t['id'] for t in d.task_navigation(self.root,task_ids=['C','A'])['tasks']],['A','C'])
        self.assertEqual(d.task_navigation(self.root,task_ids=['A'])['omitted_checked_tasks'],0)
        with self.assertRaises(d.DocumentError): d.task_navigation(self.root,task_ids=['missing'])

    def test_R12_summary_projection(self):
        task=d.task_navigation(self.root,summary_chars=4)['tasks'][0]
        self.assertEqual(task['summary'],'AAAA')
        self.assertEqual(task['summary_source'],{'chars':100,'sha256':hashlib.sha256(b'A'*100).hexdigest(),'truncated':True})
        self.assertEqual(len(d.task_navigation(self.root)['tasks'][0]['summary']),100)

    def test_R13_pages_bound_to_source(self):
        first=d.task_navigation(self.root,limit=1)
        second=d.task_navigation(self.root,limit=1,after_id=first['next_after_id'],expected_snapshot=first['snapshot'])
        self.assertEqual(second['tasks'][0]['id'],'B')
        path=self.root/'agent_doc/task/task_details/C.md'; path.write_bytes(path.read_bytes()+b'changed')
        with self.assertRaises(d.DocumentError): d.task_navigation(self.root,limit=1,after_id='A',expected_snapshot=first['snapshot'])

    def test_R13_index_is_read_once(self):
        original=d.regular_bytes; reads=[]
        def changed(root,path,**kw):
            data=original(root,path,**kw)
            if str(path).endswith('TASK.md'):
                reads.append(path)
                target=self.root/'agent_doc/task/TASK.md'
                target.write_bytes(data.replace(b'Title',b'changed'))
            return data
        with patch.object(d,'regular_bytes',side_effect=changed): first=d.task_navigation(self.root,limit=1)
        second=d.task_navigation(self.root,limit=1)
        self.assertEqual(len(reads),1)
        self.assertNotEqual(first['snapshot'],second['snapshot'])

    def test_R14_complete_wire_bound(self):
        data=d.task_navigation(self.root)
        size=len(json.dumps(data,ensure_ascii=False,separators=(',',':')))+len(os.linesep)
        self.assertEqual(d.task_navigation(self.root,max_chars=size),data)
        with self.assertRaises(d.DocumentError): d.task_navigation(self.root,max_chars=size-1)

    def test_R15_read_details_once(self):
        reads=[]; original=d.regular_bytes
        def tracked(root,path,**kw): reads.append(str(path)); return original(root,path,**kw)
        with patch.object(d,'regular_bytes',side_effect=tracked): snapshot=d.snapshot_project_docs(self.root)
        self.assertEqual(len(snapshot['task_details']),3)
        for i in ('A','B','C'): self.assertEqual(sum(p.endswith('/'+i+'.md') for p in reads),1)

if __name__=='__main__': unittest.main()
