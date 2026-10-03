import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'plugins/research-assistant/skills/research-review/scripts/measurement_review.py'
spec = importlib.util.spec_from_file_location('measurement_review', SCRIPT)
m = importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
try:
    import scipy
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


def packet(delta=2):
    return {'claim_id':'REV-SYNTHETIC-001','unit':'score_points','direction':'higher',
      'design': {'kind':'accuracy','estimand':'equal_cluster_mean_paired_difference',
       'cluster_unit':'independently sampled synthetic source document',
       'independence_evidence':'synthetic independent document fixture, not real model data',
       'noise_sources':'example sampling; fixed scorer/decoding; no seed-generalization claim',
       'precision_plan':'independent pilot will determine fixed confirmation count for halfwidth <= .2 points; fixture count is not a power plan',
       'stopping_rule':'fixed_before_collection','planned_clusters':24,'target_halfwidth':.2,
       'protocol_reference':'synthetic-v1','outlier_rule':'retain all observations',
       'paired':True,'protocol_matched':True,'threshold_prespecified':True,'no_test_tuning':True,
       'family':'single_prespecified_primary','criterion':'superiority','margin':1,
       'dataset_sampling':'24 synthetic independent documents, 2 questions each; equal document weighting',
       'seed_decoding_scorer':'fixed deterministic synthetic scorer v1'},
      'rows':[{'id':f'{i}-{j}','cluster':str(i),'baseline':50+j,
               'candidate':50+j+delta+((i%7)-3)*.1} for i in range(24) for j in range(2)]}


class MeasurementReviewTests(unittest.TestCase):
    def test_single_summary_cannot_produce_ci(self):
        p=packet();p['rows']=[];p['summary']={'baseline':61.2,'candidate':61.3}
        r=m.review(p,True)
        self.assertIsNone(r['ci']);self.assertIsNone(r['criterion_met'])
        self.assertIn('raw_data',[i['code'] for i in r['issues']])
        self.assertTrue(r['redesign_tasks'])

    def test_repeated_timers_not_independent_trials(self):
        p=packet()
        for row in p['rows']:row['cluster']='one-session'
        r=m.review(p,True)
        self.assertEqual(r['independent_clusters_declared'],1)
        self.assertIsNone(r['ci'])

    def test_multiplicity_leakage_and_posthoc_margin(self):
        for key,value in [('family','best_of_40'),('no_test_tuning',False),('threshold_prespecified',False),('paired',False)]:
            p=packet();p['design'][key]=value
            r=m.review(p,True)
            self.assertEqual(r['status'],'needs_redesign');self.assertIsNone(r['ci'])

    def test_performance_configuration_required(self):
        p=packet();p['design']['kind']='performance'
        r=m.review(p)
        codes={i['code'] for i in r['issues']}
        self.assertTrue({'exclusion_evidence','synchronization','order','cold_or_steady'}.issubset(codes))
        for key in ('hardware_software_shapes_precision','warmup_compile_autotune','synchronization','cold_or_steady','exclusion_evidence','session_sampling'):
            p['design'][key]='synthetic declared protocol'
        p['design']['order']='randomized_paired'
        self.assertEqual(m.review(p)['status'],'contract_ready_not_verified')

    def test_equal_cluster_weight_not_loop_count(self):
        p=packet();p['rows']=[{'id':'a','cluster':'A','baseline':0,'candidate':3}]+[
            {'id':str(i),'cluster':'B','baseline':0,'candidate':0} for i in range(100)]+[
            {'id':'c','cluster':'C','baseline':0,'candidate':0}]
        self.assertEqual(m.review(p)['effect_candidate_minus_baseline'],1)

    def test_reject_invalid_and_duplicate_data(self):
        for change in [{'id':'0-0'}, {'baseline':True}, {'candidate':float('inf')}]:
            p=packet();p['rows'][1].update(change)
            with self.assertRaises(ValueError):m.review(p)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'p.json';p.write_text('{"rows":[],"rows":[]}')
            with self.assertRaises(ValueError):m.load(p)

    @unittest.skipUnless(HAS_SCIPY,'optional SciPy not installed')
    def test_positive_bounded_case_and_reproducibility(self):
        r=m.review(packet(),True);s=m.review(packet(),True)
        self.assertEqual(r['status'],'conditional_interval_only')
        self.assertTrue(r['criterion_met']);self.assertEqual(r['ci'],s['ci'])
        self.assertLess(r['ci']['low'],2);self.assertGreater(r['ci']['high'],1.8)
        self.assertNotIn('p_value',r)

    @unittest.skipUnless(HAS_SCIPY,'optional SciPy not installed')
    def test_tiny_delta_inconclusive_not_equivalent(self):
        r=m.review(packet(.01),True)
        self.assertFalse(r['criterion_met'])
        self.assertLess(r['ci']['low'],0);self.assertGreater(r['ci']['high'],0)
        self.assertEqual(r['redesign_tasks'][-1]['issue'],'criterion_or_precision_not_established')

    @unittest.skipUnless(HAS_SCIPY,'optional SciPy not installed')
    def test_constant_repetitions_do_not_fabricate_certainty(self):
        p=packet()
        for row in p['rows']:row['candidate']=row['baseline']+2
        r=m.review(p,True)
        self.assertIsNone(r['ci']);self.assertEqual(r['status'],'needs_redesign')

    @unittest.skipUnless(HAS_SCIPY,'optional SciPy not installed')
    def test_direction_and_margin_criteria(self):
        p=packet(-2);p['direction']='lower'
        self.assertTrue(m.review(p,True)['criterion_met'])
        p=packet(.01);p['design']['criterion']='equivalence'
        self.assertTrue(m.review(p,True)['criterion_met'])
        p['design']['margin']=.01
        self.assertFalse(m.review(p,True)['criterion_met'])
        p['design']['criterion']='noninferiority';p['design']['margin']=1
        self.assertTrue(m.review(p,True)['criterion_met'])

    def test_overflow_and_optional_stopping_block(self):
        for baseline,candidate in [(-1e308,1e308),(10**500,1)]:
            p=packet();p['rows'][0].update(baseline=baseline,candidate=candidate)
            with self.assertRaises(ValueError):m.review(p,True)
        p=packet();p['design']['stopping_rule']='stop_when_significant'
        self.assertIsNone(m.review(p,True)['ci'])
        p=packet();p['design']['planned_clusters']=25
        self.assertIn('planned_clusters',[i['code'] for i in m.review(p,True)['issues']])
