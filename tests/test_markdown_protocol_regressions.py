import unittest
from contextlib import closing
from agent_runtime import project_docs as d, knowledge_index as k

class Markdown(unittest.TestCase):
    def test_literal_boundary(self):
        text='Task-ID: A\n## Plan\n```md\n## Plan\n## Progress\n```\nbody\n## Progress\nlive\n'
        plan,progress=d.split_detail(text)
        self.assertTrue(plan.endswith('body\n'))
        self.assertEqual(progress,'live\n')
        with self.assertRaises(d.DocumentError): d.split_detail(text+'## Progress\nx')

    def test_identity_fields(self):
        text='Task-ID: A\nStatus: ready\n~~~\nTask-ID: example\nStatus: old\n~~~\n'
        self.assertEqual(d._field_values(text,'Task-ID'),['A'])
        self.assertEqual(d._field_once(text,'Status'),'ready')
        with self.assertRaises(d.DocumentError): d._field_once(text+'Status: duplicate\n','Status')

    def test_sections_keep_fenced_body(self):
        text='## Plan\n### 摘要\ntext\n```\n### example\n```\ntail\n### Other\nstop'
        self.assertEqual(d._plan_section(text,'摘要'),'text\n```\n### example\n```\ntail')
        self.assertIsNone(d._plan_section('```\n### 摘要\n```\n','摘要'))

    def test_writer_allows_examples(self):
        from pathlib import Path
        from contextlib import closing
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); task=root/'agent_doc/task/task_details/A.md'; task.parent.mkdir(parents=True)
            task.write_text('Task-ID: A\nDate: 2026-10-21\n## Plan\nx\n## Progress\nold',encoding='utf-8')
            (root/'agent_doc/task/TASK.md').write_text('## 2026-10-21\n- [ ] [A] Test ([detail](task_details/A.md))\n',encoding='utf-8')
            import hashlib
            sha=hashlib.sha256(d.split_detail(task.read_text())[0].encode()).hexdigest()
            d.write_task_progress(root,'A','```\n## Progress\n```\nnew',expected_plan_sha256=sha)
            self.assertIn('new',task.read_text())
            with self.assertRaises(d.DocumentError): d.write_task_progress(root,'A','## Progress\nbad',expected_plan_sha256=sha)

    def test_only_physical_lines(self):
        self.assertEqual(d.physical_lines('a\u2028b\r\nc\rd\n'),['a\u2028b','c','d'])
        record={'title':'T','content':'# Real\nvalue\u2028# fake\n## Next\nx'}
        sections=k.sections(record)
        self.assertEqual([s['title'] for s in sections],['Real','Next'])
        self.assertIn('\u2028# fake',sections[0]['text'])

    def test_old_engine_requires_rebuild(self):
        import sqlite3
        import tempfile
        from pathlib import Path
        from agent_runtime.knowledge import KnowledgeStore, KnowledgeError
        store=KnowledgeStore(Path(__file__).resolve().parents[1]/'knowledge')
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'index.sqlite'
            k.build_index(store,path)
            with closing(sqlite3.connect(path)) as con:
                with con:
                    con.execute("UPDATE meta SET value='fts5-porter-alias-first-section-v6' WHERE key='engine_version'")
            with self.assertRaisesRegex(KnowledgeError,'stale index engine'):
                k.indexed_search(store,path,'memory')
            rebuilt=k.build_index(store,path)
            self.assertTrue(rebuilt['engine_changed'])
            self.assertGreater(rebuilt['updated'],0)
            self.assertIsInstance(k.indexed_search(store,path,'memory')['results'],list)

if __name__=='__main__': unittest.main()
