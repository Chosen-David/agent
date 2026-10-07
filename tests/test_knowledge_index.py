import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from agent_runtime.knowledge import KnowledgeStore, KnowledgeError
from agent_runtime.knowledge_index import build_index, indexed_search, navigate, sections
from agent_runtime.knowledge_ingest import ingest

ROOT=Path(__file__).resolve().parents[1]

class IndexTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'knowledge'
        shutil.copytree(ROOT/'knowledge',self.root)
        self.store=KnowledgeStore(self.root)
        self.count=len(self.store.records)
        self.db=Path(self.tmp.name)/'cache/search.sqlite'

    def test_incremental_noop_update_remove_and_rebuild(self):
        self.assertEqual(build_index(self.store,self.db)['updated'],self.count)
        self.assertEqual(build_index(self.store,self.db)['unchanged'],self.count)
        p=self.root/'entries/math.low-rank-svd.md';p.write_text(p.read_text()+'\nAdditional boundary.\n')
        fresh=KnowledgeStore(self.root)
        with self.assertRaisesRegex(KnowledgeError,'stale'):
            indexed_search(fresh,self.db,'low rank')
        self.assertEqual(build_index(fresh,self.db)['updated'],1)
        p=self.root/'entries/physics.dimensionless.json';d=json.loads(p.read_text());d['status']='deprecated';p.write_text(json.dumps(d))
        fresh=KnowledgeStore(self.root)
        self.assertEqual(build_index(fresh,self.db)['removed'],1)
        results=indexed_search(fresh,self.db,'量纲',limit=min(len(fresh.records),20))['results']
        self.assertNotIn('physics.dimensionless', [r['id'] for r in results])
        self.assertEqual(build_index(fresh,self.db,rebuild=True)['updated'],self.count-1)

    def test_index_search_pins_sections_filter_and_query_syntax(self):
        build_index(self.store,self.db)
        result=indexed_search(self.store,self.db,'量纲 单位 周期',domain='physics')
        row=result['results'][0]
        self.assertEqual(row['id'],'physics.dimensionless')
        self.assertEqual(row['sha256'],self.store.ref(row['id'])['sha256'])
        self.assertTrue(row['sections'])
        self.assertTrue(all(s['start_line']<=s['end_line'] for s in row['sections']))
        self.assertEqual(indexed_search(self.store,self.db,'量纲',domain='group-theory')['results'],[])
        # TABLE is legitimate paper locator text in the expanded corpus.
        # SQL-looking input must remain search data and preserve the index.
        indexed_search(self.store,self.db,'" DROP TABLE docs; -- zzqxnonexistent')
        with sqlite3.connect(self.db) as con:
            self.assertEqual(con.execute('SELECT count(*) FROM docs').fetchone()[0],self.count)
        self.assertEqual(indexed_search(self.store,self.db,'zzqxnonexistent')['results'],[])
        self.assertEqual(indexed_search(self.store,self.db,'!!!')['results'],[])
        self.assertTrue(indexed_search(self.store,self.db,'量纲')['results'])

    def test_missing_unrelated_or_wrong_root_rejected(self):
        with self.assertRaisesRegex(KnowledgeError,'missing'):
            indexed_search(self.store,self.db,'q')
        self.db.parent.mkdir()
        with sqlite3.connect(self.db) as c: c.execute('CREATE TABLE valuable(data)')
        with self.assertRaisesRegex(KnowledgeError,'unrelated'):
            build_index(self.store,self.db)
        with sqlite3.connect(self.db) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM valuable').fetchone()[0],0)
        self.db.unlink();build_index(self.store,self.db)
        other=Path(self.tmp.name)/'other';shutil.copytree(self.root,other)
        with self.assertRaisesRegex(KnowledgeError,'different corpus'):
            build_index(KnowledgeStore(other),self.db)

    def test_failed_reindex_preserves_previous_index(self):
        build_index(self.store,self.db)
        p=self.root/'entries/math.low-rank-svd.md'
        p.write_text(p.read_text()+'\nChanged content.\n')
        fresh=KnowledgeStore(self.root)
        with patch('agent_runtime.knowledge_index.sections', side_effect=RuntimeError('interrupted writer')):
            with self.assertRaisesRegex(RuntimeError, 'interrupted'):
                build_index(fresh,self.db)
        self.assertTrue(indexed_search(self.store,self.db,'low rank')['results'])
        self.assertEqual(build_index(fresh,self.db)['updated'],1)

    def test_stemming_and_engine_refresh(self):
        build_index(self.store,self.db)
        plural = indexed_search(self.store,self.db,'residuals',limit=min(self.count,20))['results']
        singular = indexed_search(self.store,self.db,'residual',limit=min(self.count,20))['results']
        self.assertIn('math.linear-system-stability', [r['id'] for r in plural])
        self.assertEqual({r['id'] for r in plural}, {r['id'] for r in singular})
        with sqlite3.connect(self.db) as con:
            con.execute("UPDATE meta SET value='old-engine' WHERE key='engine_version'")
        with self.assertRaisesRegex(KnowledgeError, 'stale index engine'):
            indexed_search(self.store,self.db,'residuals')
        result=build_index(self.store,self.db)
        self.assertTrue(result['engine_changed'])
        self.assertEqual(result['updated'], self.count)
        self.assertFalse(build_index(self.store,self.db)['engine_changed'])

    def test_incoming_relations_discover_new_corollary(self):
        results=self.store.related('math.topk-margin')['results']
        self.assertTrue(any(x['id']=='math.score-difference-bound' and x['direction']=='incoming' for x in results))
        self.assertTrue(any(x['id']=='math.cauchy-schwarz' and x['direction']=='outgoing' for x in results))
        self.assertTrue(self.store.related('math.cauchy-schwarz',limit=1)['truncated'])

    def test_heading_tree_fences_and_section_read(self):
        record={'title':'Test','content':'Preamble\n# A\nbody\n## B\nchild\n```md\n# ignored\n```\n# C\nend'}
        nodes=sections(record)
        self.assertEqual([n['title'] for n in nodes],['Test','A','B','C'])
        self.assertEqual(nodes[2]['parent'],'s1')
        self.assertEqual(nodes[2]['start_line'],4)
        self.assertEqual(nodes[2]['end_line'],8)
        tree=navigate(self.store,'math.topk-margin')
        section=navigate(self.store,'math.topk-margin',tree['nodes'][1]['node'])
        self.assertIn('content', self.store.get('math.topk-margin'))
        self.assertIn('text',section['section'])
        self.assertEqual(len(section['knowledge_refs']),2)
        original = self.store.get('math.topk-margin')['content'].splitlines(keepends=True)
        for node in navigate(self.store, 'math.topk-margin')['nodes']:
            actual = navigate(self.store, 'math.topk-margin', node['node'])['section']['text']
            self.assertEqual(actual, ''.join(original[node['start_line']-1:node['end_line']]))
        with self.assertRaises(KnowledgeError): navigate(self.store,'math.topk-margin','bad')

    def draft(self):
        d=json.loads((self.root/'entries/math.cauchy-schwarz.json').read_text())
        d.update(id='math.import-example',status='candidate',requires=[],relations=[])
        metadata=Path(self.tmp.name)/'draft.json';body=Path(self.tmp.name)/'draft.md'
        metadata.write_text(json.dumps(d));body.write_text('# Draft\nUnverified educational example.\n')
        return metadata,body

    def test_ingest_records_provenance_and_stays_candidate(self):
        meta,body=self.draft()
        result=ingest(self.root,meta,body)
        self.assertTrue((self.root/result['path']/'provenance.txt').is_file())
        store=KnowledgeStore(self.root)
        self.assertEqual(len(store.records),self.count+1)
        with self.assertRaises(KnowledgeError): store.get('math.import-example')
        self.assertEqual(build_index(store,self.db)['indexed'],self.count)
        with self.assertRaisesRegex(KnowledgeError,'already exists'): ingest(self.root,meta,body)

    def test_bad_import_does_not_change_corpus(self):
        meta,body=self.draft();d=json.loads(meta.read_text());d['requires']=[{'id':'math.missing','version':1}];meta.write_text(json.dumps(d))
        with self.assertRaises(KnowledgeError): ingest(self.root,meta,body)
        self.assertEqual(KnowledgeStore(self.root).snapshot,self.store.snapshot)
        d['requires']=[];d['status']='published';meta.write_text(json.dumps(d))
        with self.assertRaisesRegex(KnowledgeError,'candidate'): ingest(self.root,meta,body)
        self.assertEqual(KnowledgeStore(self.root).snapshot,self.store.snapshot)

    def test_isolated_index_and_tree_cli(self):
        skill=Path(self.tmp.name)/'isolated'
        shutil.copytree(ROOT/'plugins/research-assistant/skills/model-with-knowledge',skill)
        cmd=[sys.executable,'-I',str(skill/'scripts/knowledge.py'),'--root',str(skill/'assets/knowledge')]
        for args in (['index','--db',str(self.db)],['search','量纲','--index',str(self.db)],['tree','math.symmetry-quotient']):
            result=subprocess.run(cmd+args,cwd=self.tmp.name,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIsInstance(json.loads(result.stdout),dict)

if __name__=='__main__': unittest.main()
