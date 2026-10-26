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

class TaskPhysicalLineTests(unittest.TestCase):
    setUp = TaskViewTests.setUp
    separators = ('\v', '\f', '\x1c', '\x1d', '\x1e', '\x85', '\u2028', '\u2029')

    def view_chunks(self, chunks, selected, omitted):
        text = ''.join(chunks)
        raw = text.encode('utf-8')
        self.path.write_bytes(raw)
        view = task_view(self.root, selected, hashlib.sha256(raw).hexdigest())
        kept = [i for i in range(len(chunks)) if i not in omitted]
        self.assertEqual(view['text'], ''.join(chunks[i] for i in kept))
        self.assertEqual(view['source_lines'], [i + 1 for i in kept])
        self.assertEqual(view['omitted_task_rows'], len(omitted))
        self.assertEqual(self.path.read_bytes(), raw)
        return view

    def test_nonphysical_separators_preserve_instruction_suffixes(self):
        for sep in self.separators:
            with self.subTest(separator=repr(sep)):
                chunks = ['# Global\n', '## 2026-10-26\n',
                          'Correction stays' + sep + '- [ ] [OLD] this is literal constraint text\n',
                          '- [ ] [OLD] old task ([detail](task_details/OLD.md))\n',
                          '- [ ] [NOW] current task ([detail](task_details/NOW.md))\n']
                self.view_chunks(chunks, ['NOW'], {3})

    def test_nonphysical_fence_prefix_does_not_hide_real_tasks(self):
        for sep in self.separators:
            with self.subTest(separator=repr(sep)):
                chunks = ['## 2026-10-26\n', 'Literal prefix' + sep + '```md\n',
                          '- [ ] [OLD] old task ([detail](task_details/OLD.md))\n',
                          '- [ ] [NOW] current task ([detail](task_details/NOW.md))\n']
                self.view_chunks(chunks, ['NOW'], {2})

    def test_titles_and_source_positions_follow_physical_lines(self):
        for sep in self.separators:
            for ending in ('\n', '\r\n', '\r'):
                with self.subTest(separator=repr(sep), ending=repr(ending)):
                    chunks = ['## 2026-10-26' + ending,
                              '- [ ] [OLD] omit' + sep + 'entire title ([detail](task_details/OLD.md))' + ending,
                              'Constraint' + sep + 'literal' + ending,
                              '- [ ] [NOW] keep' + sep + 'entire title ([detail](task_details/NOW.md))']
                    self.view_chunks(chunks, ['NOW'], {1})

    def test_actual_cli_retains_literal_constraints_and_positions(self):
        import json, os, subprocess, sys
        for sep in self.separators:
            with self.subTest(separator=repr(sep)):
                chunks = ['## 2026-10-26\r\n',
                          'Cancellation' + sep + '- [ ] [OLD] retained literal condition\r\n',
                          '- [ ] [OLD] old task ([detail](task_details/OLD.md))\r\n',
                          '- [ ] [NOW] current task ([detail](task_details/NOW.md))']
                raw = ''.join(chunks).encode('utf-8')
                self.path.write_bytes(raw)
                command = [sys.executable, '-B', str(Path(__file__).resolve().parents[1] / 'scripts/task_context.py'),
                           '--root', str(self.root), '--task-id', 'NOW', '--sha256', hashlib.sha256(raw).hexdigest(),
                           '--compact']
                completed = subprocess.run(command, capture_output=True, timeout=15,
                                           env=dict(os.environ, PYTHONUTF8='0', PYTHONIOENCODING='cp936'))
                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertEqual(completed.stderr, b'')
                view = json.loads(completed.stdout.decode('utf-8'))
                self.assertEqual(view['text'], chunks[0] + chunks[1] + chunks[3])
                self.assertEqual(view['source_lines'], [1, 2, 4])
                self.assertEqual(view['omitted_task_rows'], 1)
                self.assertEqual(self.path.read_bytes(), raw)
