"""Knowledge identity, applicability boundaries, standalone packaging and task gates."""
import itertools
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime.knowledge import KnowledgeStore, KnowledgeError, check_task_knowledge
from agent_runtime.task_manifest import ReportingHandler
from agent_runtime.core import Outcome

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'plugins/research-assistant/skills/model-with-knowledge'


class KnowledgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)
        self.root = self.project / 'knowledge'
        shutil.copytree(ROOT / 'knowledge', self.root)
        self.store = KnowledgeStore(self.root)

    def edit(self, kid, **changes):
        p = self.root / 'entries' / (kid + '.json')
        d = json.loads(p.read_text())
        d.update(changes)
        p.write_text(json.dumps(d))

    def test_seed_and_chinese_task_structure_search(self):
        self.assertEqual(len(self.store.records), 5)
        rows = self.store.search('压缩 查询键误差 分数扰动 排名', limit=3)['results']
        self.assertIn('math.cauchy-schwarz', [r['id'] for r in rows])
        self.assertTrue(all(r['matches'] and r['assumptions'] for r in rows))
        self.assertEqual(self.store.search('zzqxnonexistent')['results'], [])
        self.assertEqual(self.store.search('量纲', domain='group-theory')['results'], [])
        self.assertEqual(self.store.search('量纲', domain='physics')['results'][0]['id'], 'physics.dimensionless')
        self.assertEqual(self.store.search('inner product', structure='inner-product')['results'][0]['id'], 'math.cauchy-schwarz')

    def test_snapshot_formatting_and_return_isolation(self):
        self.edit('math.low-rank-svd')
        self.assertEqual(KnowledgeStore(self.root).snapshot, self.store.snapshot)
        d = self.store.get('math.low-rank-svd')
        d['assumptions'].clear()
        self.assertTrue(self.store.get('math.low-rank-svd')['assumptions'])

    def test_search_result_isolation(self):
        row = self.store.search('量纲')['results'][0]
        row['assumptions'].clear()
        row['verification']['source'] = 'unverified'
        self.assertTrue(self.store.get(row['id'])['assumptions'])
        self.assertEqual(self.store.get(row['id'])['verification']['source'], 'checked')

    def test_deep_prerequisite_chain_is_iterative(self):
        template = json.loads((self.root/'entries/math.cauchy-schwarz.json').read_text())
        for i in range(1100):
            kid = f'test.chain-{i}'
            d = dict(template, id=kid, requires=[{'id':f'test.chain-{i-1}', 'version':1}] if i else [])
            (self.root/'entries'/f'{kid}.json').write_text(json.dumps(d))
            (self.root/'entries'/f'{kid}.md').write_text('Synthetic dependency chain.')
        store = KnowledgeStore(self.root)
        refs = store.get('test.chain-1099')['knowledge_refs']
        self.assertEqual(len(refs), 1100)
        self.assertTrue(store.check_refs(refs)['valid'])

    def test_omitted_prerequisite_rejected(self):
        refs = self.store.get('math.topk-margin')['knowledge_refs']
        self.assertEqual({r['id'] for r in refs}, {'math.topk-margin','math.cauchy-schwarz'})
        self.assertTrue(self.store.check_refs(refs)['valid'])
        with self.assertRaisesRegex(KnowledgeError, 'omit prerequisites'):
            self.store.check_refs([self.store.ref('math.topk-margin')])

    def test_same_version_content_change_invalidates_dependency_refs(self):
        refs = self.store.get('math.topk-margin')['knowledge_refs']
        p = self.root / 'entries/math.cauchy-schwarz.md'
        p.write_text(p.read_text() + '\nCorrection to prerequisite.\n')
        newer = KnowledgeStore(self.root)
        self.assertNotEqual(newer.snapshot, self.store.snapshot)
        with self.assertRaisesRegex(KnowledgeError, 'stale knowledge ref'):
            newer.check_refs(refs)

    def test_version_change_requires_dependent_revision(self):
        self.edit('math.cauchy-schwarz', version=2)
        with self.assertRaisesRegex(KnowledgeError, 'stale prerequisite'):
            KnowledgeStore(self.root)

    def test_candidate_and_deprecated_are_not_normal_results(self):
        for status in ('candidate', 'deprecated'):
            with self.subTest(status=status):
                self.edit('physics.dimensionless', status=status)
                store=KnowledgeStore(self.root)
                self.assertEqual(store.search('量纲')['results'], [])
                self.assertTrue(store.search('量纲', include_unpublished=True)['results'])
                with self.assertRaises(KnowledgeError):
                    store.get('physics.dimensionless')
                with self.assertRaises(KnowledgeError):
                    store.check_refs([store.ref('physics.dimensionless')])

    def test_cycles_missing_relations_and_unpublished_prerequisite(self):
        for change in ({'requires':[{'id':'math.topk-margin','version':1}]},
                       {'relations':[{'type':'related','id':'missing.entry'}]},
                       {'status':'candidate'}):
            original = (self.root/'entries/math.cauchy-schwarz.json').read_text()
            with self.subTest(change=change):
                self.edit('math.cauchy-schwarz', **change)
                with self.assertRaises(KnowledgeError):
                    KnowledgeStore(self.root)
            (self.root/'entries/math.cauchy-schwarz.json').write_text(original)

    def test_bad_metadata(self):
        path=self.root/'entries/math.low-rank-svd.json'
        original=path.read_text()
        for change in ({'id':'../escape'}, {'version':True}, {'status':[]}, {'extra':1},
                       {'assumptions':[]}, {'sources':[]}, {'schema_version':2},
                       {'verification':{'source':'unverified','proof':'not-checked','checks':[]}}):
            with self.subTest(change=change):
                self.edit('math.low-rank-svd', **change)
                with self.assertRaises(KnowledgeError):
                    KnowledgeStore(self.root)
            path.write_text(original)

    def test_duplicate_keys_and_ids(self):
        path=self.root/'entries/math.low-rank-svd.json'
        original=path.read_text()
        path.write_text(original.replace('"version": 1', '"version": 1, "version": 1'))
        with self.assertRaisesRegex(KnowledgeError, 'duplicate JSON'):
            KnowledgeStore(self.root)
        path.write_text(original)
        shutil.copy(path,path.with_name('duplicate.json'))
        shutil.copy(path.with_suffix('.md'),path.with_name('duplicate.md'))
        with self.assertRaisesRegex(KnowledgeError, 'duplicate knowledge ID'):
            KnowledgeStore(self.root)

    def test_missing_body_orphan_and_byte_budget(self):
        p=self.root/'entries/math.low-rank-svd.md';body=p.read_text();p.unlink()
        with self.assertRaisesRegex(KnowledgeError, 'missing entry'):
            KnowledgeStore(self.root)
        p.write_text('x'*1_048_577)
        with self.assertRaisesRegex(KnowledgeError, 'byte budget'):
            KnowledgeStore(self.root)
        p.write_text(body)
        (self.root/'entries/orphan.md').write_text('orphan')
        with self.assertRaisesRegex(KnowledgeError, 'orphan'):
            KnowledgeStore(self.root)

    def test_redirected_paths_rejected(self):
        (self.root/'entries/link.md').symlink_to(self.root/'entries/math.low-rank-svd.md')
        with self.assertRaisesRegex(KnowledgeError, 'symlink'):
            KnowledgeStore(self.root)
        with self.assertRaisesRegex(KnowledgeError, 'outside project'):
            check_task_knowledge(self.project, {'knowledge_root':'../external','knowledge_refs':[self.store.ref('math.low-rank-svd')]})
        with self.assertRaisesRegex(KnowledgeError, 'project-relative'):
            check_task_knowledge(self.project, {'knowledge_root':str(self.root),'knowledge_refs':[self.store.ref('math.low-rank-svd')]})

    def test_limits_and_refs_validation(self):
        for value in (0,21,True):
            with self.assertRaises(KnowledgeError): self.store.search('matrix',limit=value)
        for refs in ([], {}, [self.store.ref('math.topk-margin')]*2,
                     [{'id':'math.low-rank-svd','version':1,'sha256':'fake'}]):
            with self.assertRaises(KnowledgeError): self.store.check_refs(refs)
        self.assertEqual(check_task_knowledge(self.project, {}), [])

    def fixture_handler(self):
        class Handler:
            idempotent=True
            required_capabilities=()
            calls=0
            def run(self,task,context):
                self.calls+=1
                return Outcome('complete','derived',[{'fixture':True}])
            def verify(self,task,evidence): return evidence==[{'fixture':True}]
        task={'task_id':'T1','report_path':'report.json','knowledge_refs':self.store.get('math.topk-margin')['knowledge_refs']}
        (self.project/'report.json').write_text(json.dumps({'task_id':'T1','summary':'synthetic test','data':[{'kind':'synthetic','description':'fixture only'}]}))
        base=Handler()
        return task,base,ReportingHandler(base,self.project)

    def change_content(self):
        p=self.root/'entries/math.topk-margin.md';p.write_text(p.read_text()+'\nChanged premise.\n')

    def test_stale_refs_block_dispatch_and_post_execution(self):
        task,base,wrapper=self.fixture_handler()
        self.change_content()
        self.assertEqual(wrapper.run(task,{}).status,'blocked')
        self.assertEqual(base.calls,0)
        task['knowledge_refs']=KnowledgeStore(self.root).get('math.topk-margin')['knowledge_refs']
        with patch.object(base,'run',side_effect=lambda *_:(self.change_content(),Outcome('complete','x',[]))[1]):
            self.assertEqual(wrapper.run(task,{}).status,'blocked')

    def test_refs_checked_after_independent_verification(self):
        task,base,wrapper=self.fixture_handler()
        outcome=wrapper.run(task,{})
        self.assertTrue(wrapper.verify(task,outcome.evidence))
        with patch.object(base,'verify',side_effect=lambda *_:(self.change_content(),True)[1]):
            self.assertFalse(wrapper.verify(task,outcome.evidence))

    def test_bundle_exact_and_cli_without_repository(self):
        bundled=SKILL/'assets/knowledge'
        canonical={p.relative_to(ROOT/'knowledge') for p in (ROOT/'knowledge').rglob('*') if p.is_file()}
        mirrored={p.relative_to(bundled) for p in bundled.rglob('*') if p.is_file()}
        self.assertEqual(canonical,mirrored)
        for p in canonical: self.assertEqual((ROOT/'knowledge'/p).read_bytes(),(bundled/p).read_bytes())
        self.assertEqual((ROOT/'agent_runtime/knowledge.py').read_bytes(),(SKILL/'scripts/knowledge.py').read_bytes())
        isolated=self.project/'skill';shutil.copytree(SKILL,isolated)
        cmd=[sys.executable,'-I',str(isolated/'scripts/knowledge.py'),'--root',str(isolated/'assets/knowledge')]
        result=subprocess.run(cmd+['show','math.topk-margin'],cwd=self.project,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        refs=json.loads(result.stdout)['knowledge_refs']
        (self.project/'refs.json').write_text(json.dumps({'knowledge_refs':refs}))
        result=subprocess.run(cmd+['check-refs',str(self.project/'refs.json')],cwd=self.project,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        result=subprocess.run(cmd+['show','math.topk-margin','--version','99','--sha256','f'*64],cwd=self.project,capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertIn('stale',json.loads(result.stderr)['error'])

    def test_numerical_inner_product_and_uniform_error_counterexample(self):
        q=[3,4];error=[.06,.08]
        self.assertAlmostEqual(sum(a*b for a,b in zip(q,error)),.5)
        self.assertAlmostEqual(math.sqrt(sum(a*a for a in q))*math.sqrt(sum(a*a for a in error)),.5)
        errors=[0,2]
        self.assertGreater(max(errors),sum(errors)/len(errors))

    def test_topk_bound_and_failure_of_converse(self):
        scores=[.9,.7,.2];eps=.1
        for perturb in itertools.product((-eps,0,eps),repeat=3):
            changed=[s+e for s,e in zip(scores,perturb)]
            self.assertEqual(set(sorted(range(3),key=changed.__getitem__,reverse=True)[:2]),{0,1})
        self.assertLess(.501-.001,.500+.001)
        # A small gap permits reversal but zero perturbation also meets the bound.
        self.assertGreater(.501,.500)
        self.assertAlmostEqual(.7-.25,.2+.25)  # equality can create boundary ties

    def test_diagonal_svd_residual(self):
        singular=[5,2,.1];r=2
        residual=singular[r:]
        self.assertAlmostEqual(max(residual),.1)
        self.assertAlmostEqual(math.sqrt(sum(x*x for x in residual)),.1)
        self.assertGreater(3*.025*2,.10)
        self.assertLess(3*.025*2,.18)

    def test_group_action_and_counterexample(self):
        jobs=[2,4,7]
        for allocation in itertools.product(range(2),repeat=3):
            def cost(assign,speeds):
                return max(sum(jobs[j]/speeds[w] for j in range(3) if assign[j]==w) for w in range(2))
            flipped=tuple(1-w for w in allocation)
            self.assertEqual(cost(allocation,[1,1]),cost(flipped,[1,1]))
        self.assertNotEqual(2/1,2/2)

    def test_dimensionless_nullspace_and_missing_constant(self):
        # Columns T,l,g in rows length,time; exponents for T sqrt(g/l).
        D=[[0,1,1],[1,0,-2]];a=[1,-.5,.5]
        self.assertEqual([sum(x*y for x,y in zip(row,a)) for row in D],[0,0])
        wrong=[0,1,-1]
        self.assertEqual([sum(x*y for x,y in zip(row,wrong)) for row in D],[0,2])
        # Scaling length and g by the same unit conversion preserves the period scale.
        self.assertAlmostEqual(math.sqrt(2/9.8),math.sqrt(200/980))


if __name__=='__main__': unittest.main()
