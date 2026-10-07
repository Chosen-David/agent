"""Reported evidence must not silently replace required experiments or code checks."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from agent_runtime.knowledge import KnowledgeStore, KnowledgeError
from agent_runtime.knowledge_reuse import decision_support, validate_reuse
from scripts.knowledge_maintenance import next_due, SHANGHAI
from datetime import datetime

ROOT=Path(__file__).resolve().parents[1]


class ReuseChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.store=KnowledgeStore(ROOT/'knowledge')

    def card(self): return self.store.get('infra.speculative-acceptance')['reuse']

    def test_reported_prior_and_explicit_reproduction(self):
        context=self.card()['conditions']
        out=decision_support(self.store,'speculative decoding',context)
        row=next(r for r in out['results'] if r['id']=='infra.speculative-acceptance')
        self.assertEqual(row['disposition'],'reuse_for_planning')
        self.assertFalse(row['automatic_skip_authorized'])
        self.assertTrue(self.store.check_refs(out['knowledge_refs'])['valid'])
        explicit=decision_support(self.store,'speculative decoding',context,explicit_reproduction=True)
        self.assertTrue(all(r['disposition']=='run_requested_experiment' for r in explicit['results']))

    def test_missing_and_changed_hardware_are_visible(self):
        no=decision_support(self.store,'draft acceptance',{})['results'][0]
        self.assertEqual(no['disposition'],'insufficient_context')
        context=dict(self.card()['conditions'],hardware='H100')
        row=next(r for r in decision_support(self.store,'投机解码',context)['results']
                 if r['id']=='infra.speculative-acceptance')
        self.assertEqual(row['disposition'],'minimal_transfer_check')
        self.assertEqual(row['mismatched_conditions'][0]['field'],'hardware')
        self.assertFalse(row['automatic_skip_authorized'])

    def test_implementation_pointer_not_local_measurement(self):
        context=self.store.get('ds.fenwick-point-range')['reuse']['conditions']
        out=decision_support(self.store,'点更新 区间求和',context,purpose='implementation')
        row=next(r for r in out['results'] if r['id']=='ds.fenwick-point-range')
        self.assertEqual(row['disposition'],'evaluate_pinned_implementation')
        self.assertEqual(row['reuse']['code']['local_execution'],'not-run')
        self.assertTrue(all(r['reuse']['type']=='implementation' for r in out['results']))

    def test_schema_rejects_unpinned_code_and_relabelled_results(self):
        card=copy.deepcopy(self.card()); card['paper']['local_reproduction']='measured'
        with self.assertRaises(ValueError): validate_reuse(card)
        code=copy.deepcopy(self.store.get('ds.dsu-connectivity')['reuse'])
        code['code']['commit']='main'
        with self.assertRaises(ValueError): validate_reuse(code)
        for context in ([], {'batch':1}, {'hardware':None}):
            with self.assertRaises(ValueError): decision_support(self.store,'attention',context)

    def test_old_schema_unknown_fields_and_no_hits(self):
        old=copy.deepcopy(self.store.get('math.cauchy-schwarz'))
        for k in ('content','path','sha256','knowledge_refs'): old.pop(k)
        KnowledgeStore._validate(old)
        old['rogue']='value'
        with self.assertRaises(KnowledgeError): KnowledgeStore._validate(old)
        self.assertEqual(decision_support(self.store,'zzqxnotknown',{})['status'],'no_hits')

    def test_cli_and_standalone_have_same_decision(self):
        with tempfile.TemporaryDirectory() as temp:
            context=Path(temp)/'context.json'
            context.write_text(json.dumps(self.card()['conditions']),encoding='utf-8')
            commands=[['-m','agent_runtime.knowledge','--root','knowledge'],
                      [str(ROOT/'plugins/research-assistant/skills/model-with-knowledge/scripts/knowledge.py'),
                       '--root',str(ROOT/'plugins/research-assistant/skills/model-with-knowledge/assets/knowledge')]]
            outputs=[]
            for command in commands:
                run=subprocess.run([sys.executable,*command,'decision','投机解码','--context',str(context)],
                                   cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
                self.assertEqual(run.returncode,0,run.stderr)
                outputs.append(json.loads(run.stdout))
            self.assertEqual(outputs[0]['results'],outputs[1]['results'])

    def test_schedule_uses_shanghai_and_no_immediate_duplicate(self):
        monday=datetime(2026,10,5,7,59,tzinfo=SHANGHAI)
        self.assertEqual(datetime.fromtimestamp(next_due(monday.timestamp()),SHANGHAI).hour,8)
        due=datetime(2026,10,5,8,0,tzinfo=SHANGHAI)
        self.assertEqual(datetime.fromtimestamp(next_due(due.timestamp()),SHANGHAI).weekday(),2)


if __name__=='__main__': unittest.main()
