import hashlib,tempfile,unittest
from pathlib import Path
from agent_runtime.task_context import task_view

TEXT='# Global\nNever infer global completion.\n## 2026-10-11\n- [x] [OLD] done ([detail](task_details/OLD.md))\n- [ ] [NOW] pending verification ([detail](task_details/NOW.md))\n  shared condition retained\n```md\n- [ ] [EXAMPLE] non-task example\n```\n'
class TaskViewTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve();self.path=self.root/'agent_doc/task/TASK.md'
        self.path.parent.mkdir(parents=True);self.path.write_bytes(TEXT.encode())
        self.sha=hashlib.sha256(self.path.read_bytes()).hexdigest()
    def test_exact_row_selection_preserves_global_and_fence(self):
        v=task_view(self.root,['NOW'],self.sha)
        self.assertNotIn('[OLD]',v['text']);self.assertIn('Never infer',v['text'])
        self.assertIn('[EXAMPLE]',v['text']);self.assertIn('shared condition',v['text'])
        self.assertEqual(v['omitted_task_rows'],1)
        expected=''.join(line for i,line in enumerate(TEXT.splitlines(keepends=True),1) if i!=4)
        self.assertEqual(v['text'],expected)
        self.assertEqual(v['source_lines'],[1,2,3,5,6,7,8,9])
    def test_unknown_duplicate_empty_ids(self):
        for ids in ([],['NOW','NOW'],['MISSING'],[False]):
            with self.assertRaises(ValueError):task_view(self.root,ids,self.sha)
    def test_version_and_budget_fail_closed(self):
        with self.assertRaises(ValueError):task_view(self.root,['NOW'],self.sha,max_chars=1)
        self.path.write_bytes((TEXT+'changed\n').encode())
        with self.assertRaises(ValueError):task_view(self.root,['NOW'],self.sha)
    def test_duplicate_task_source_rejected(self):
        self.path.write_bytes((TEXT+'- [ ] [NOW] again ([detail](task_details/NOW.md))\n').encode())
        with self.assertRaises(ValueError):task_view(self.root,['NOW'],hashlib.sha256(self.path.read_bytes()).hexdigest())
    def test_crlf_and_multi_selection(self):
        self.path.write_bytes(TEXT.replace('\n','\r\n').encode())
        v=task_view(self.root,['OLD','NOW'],hashlib.sha256(self.path.read_bytes()).hexdigest())
        self.assertEqual(v['text'],TEXT.replace('\n','\r\n'));self.assertEqual(v['omitted_task_rows'],0)
    def test_fence_closer_with_suffix_is_not_a_closer(self):
        text=TEXT.replace('- [ ] [EXAMPLE] non-task example','```suffix\n- [ ] [OLD] example row, not a canonical task')
        self.path.write_bytes(text.encode())
        v=task_view(self.root,['NOW'],hashlib.sha256(self.path.read_bytes()).hexdigest())
        self.assertIn('example row, not a canonical task',v['text'])
        self.assertEqual(v['omitted_task_rows'],1)
