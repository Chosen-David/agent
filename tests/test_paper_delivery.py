"""Synthetic declarations; these tests do not score prose or live agent quality."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('paper_delivery', ROOT / 'scripts/validate_paper_delivery.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def synthetic_acceptance(record):
    """Explicit test-only controller assertion, never real reviewer provenance."""
    from semantic_acceptance import canonical_record_sha256, declared_file_hashes
    return dict(schema_version=1, record_sha256=canonical_record_sha256(record),
        reviewer_actor='research-review', file_hashes=declared_file_hashes(record),
        versions=[dict(language=v['language'], snapshot_sha256=v['snapshot']['sha256'],
            checks={c:dict(verdict='pass',evidence=['Synthetic fixture section 1; test controller assertion'])
                    for c in ('artifact_fit','originality')}) for v in record['versions']])


class PaperDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        def artifact(name):
            (self.root / name).write_text('synthetic fixture, not a real paper or execution: '+name)
            return {'path': name, 'sha256': hashlib.sha256((self.root/name).read_bytes()).hexdigest()}
        files = [artifact(n) for n in ('SKILL.md', 'execution.md', 'workflow.md', 'paper_delivery_contract.md', 'paper_exemplar_learning.md')]
        snapshot = artifact('paper.pdf')
        receipt = artifact('receipt.json')
        learning = dict(state='completed', completed_before_drafting=True,
            template=dict(verified=True, provisional=False, venue='Synthetic', year='2026', track='Research',
                          source_url='https://example.invalid/template', checked_at='2026-10-03', evidence=receipt),
            skills=dict(selection_notes=receipt), synthesis=receipt, blueprint=receipt, preflight_receipt=receipt,
            papers=[dict(identity=f'EX{i}', title=f'Synthetic example {i}', venue='Synthetic', year='2025',
                publication_url=f'https://example.invalid/{i}', selection_reason='fixture only', quality_reason='fixture only',
                published=True, access='full_text', pdf=artifact(f'exemplar-{i}.pdf'), page_count=2, read_pages=[1,2],
                read_receipt=receipt, notes=receipt, figure_inventory=['Fig1','Table1'], figures_read=['Fig1','Table1'],
                analysis={d:dict(location='p1-2', observation='synthetic observation', transfer='synthetic transfer')
                          for d in ('organization','claim_evidence','figures','rhetoric','content')}) for i in range(10)],
            decisions=[dict(dimension=d, source_ids=['EX0','EX1'], source_locations='p1', decision='adapt',
                rationale='synthetic choice', target_location='Introduction', own_evidence='OWN1')
                for d in ('organization','claim_evidence','figures','rhetoric','content')])
        self.good = dict(schema_version=1, run_id='synthetic-control-run', requested_artifact='submission_paper',
            delivered_artifact='submission_paper', target='A complete bilingual research submission',
            requested_languages=['en', 'zh'], status='submission_checks_complete', blockers=[],
            drafting_started=True, architecture_requested=False, data_visualization_requested=False, exemplar_learning=learning,
            bindings=[dict(role=r, actor=r, state='completed', mode='independent', loaded_before_execution=True,
                revision='fixture', read_scope='fixture instructions', files=files,
                start_receipt=receipt, result_receipt=receipt) for r in m.ROLES],
            versions=[dict(language=l, snapshot=snapshot, implementation_map=receipt, page_count=7, read_pages=list(range(1,8)),
                reader_snapshot_sha256=snapshot['sha256'], reviewer_snapshot_sha256=snapshot['sha256'], checks={c: dict(verdict='pass',
                location='synthetic section', reason='synthetic declaration only', evidence='fixture')
                for c in m.CRITERIA}) for l in ('en','zh')])

        for binding in self.good['bindings']:
            binding.update(run_id=self.good['run_id'], task_id=binding['role'], attempt=1)
            for field, kind in (('start_receipt','start'), ('result_receipt','complete')):
                path = self.root / (binding['role']+'-'+kind+'.json')
                event = dict(event_id=binding['role']+'-'+kind, kind=kind,
                             actor=binding['actor'], role=binding['role'], revision=binding['revision'],
                             run_id=binding['run_id'], task_id=binding['task_id'], attempt=binding['attempt'],
                             status='started')
                if kind == 'complete': event['status']='produced'
                path.write_text(json.dumps(event))
                binding[field] = dict(path=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest())

    def check_with_synthetic_trust(self):
        return m.validate(self.good, self.root, acceptance=synthetic_acceptance(self.good))

    def test_valid_declarations_only(self):
        self.assertEqual(self.check_with_synthetic_trust(), [])

    def test_ten_exemplars_must_be_distinct_and_fully_read(self):
        for change, fragment in [
            (lambda l:l['papers'].pop(), 'exactly 10'),
            (lambda l:l['papers'][1].update(identity='EX0'), 'duplicate/missing identity'),
            (lambda l:l['papers'][1].update(pdf=l['papers'][0]['pdf']), 'duplicate/missing PDF'),
            (lambda l:l['papers'][0].update(access='abstract_only'), 'cannot count as read'),
            (lambda l:l['papers'][0].update(access='access_blocked'), 'cannot count as read'),
            (lambda l:l['papers'][0].update(read_pages=[1]), 'full-text page coverage'),
            (lambda l:l['papers'][0].update(figures_read=['Fig1']), 'figure/table coverage'),
            (lambda l:l['papers'][0].pop('read_receipt'), 'read_receipt required')]:
            with self.subTest(fragment=fragment):
                r=copy.deepcopy(self.good)
                change(r['exemplar_learning'])
                self.reject(r,fragment)

    def test_template_and_learning_precede_drafting(self):
        for field,value,error in [('verified',False,'template verification'),
                                   ('provisional',True,'provisional template')]:
            r=copy.deepcopy(self.good)
            r['exemplar_learning']['template'][field]=value
            self.reject(r,error)
        self.good['exemplar_learning']['completed_before_drafting']=False
        self.reject(self.good,'completed too late')

    def test_ten_links_without_analysis_or_blueprint_fail(self):
        self.good['exemplar_learning']['papers'][0]['analysis'].pop('rhetoric')
        self.reject(self.good,'missing rhetoric analysis')
        self.good['exemplar_learning']['decisions']=[]
        self.reject(self.good,'five learning dimensions')

    def test_blueprint_must_use_own_evidence_and_reach_final_manuscript(self):
        self.good['exemplar_learning']['decisions'][0]['own_evidence']='EX0'
        self.reject(self.good,'cannot replace own scientific evidence')
        self.good['versions'][0]['checks']['blueprint_application'].update(verdict='fail',
            location='Introduction and Figure 2', reason='Blueprint says motivate before design but manuscript opens with file inventory',
            evidence='Independent source-to-blueprint-to-manuscript comparison; ten links do not establish transfer')
        self.reject(self.good,'blueprint_application')
        del self.good['versions'][0]['implementation_map']
        self.reject(self.good,'implementation evidence')

    def test_pending_learning_is_honest_but_cannot_start_drafting(self):
        self.test_limited_evidence_working_paper_remains_incomplete()
        self.good['drafting_started']=False
        self.good['exemplar_learning']={'state':'blocked','reason':'Two legal full texts unavailable; replace candidates'}
        self.assertEqual(self.check_with_synthetic_trust(),[])
        self.good['drafting_started']=True
        self.reject(self.good,'must precede drafting')

    def test_empty_figure_inventory_needs_justification(self):
        self.good['exemplar_learning']['papers'][0].update(figure_inventory=[],figures_read=[])
        self.reject(self.good,'no-figure claim')

    def visual_fixture(self):
        self.good['architecture_requested']=True
        receipt=self.good['exemplar_learning']['preflight_receipt']
        visual=dict(mode='independent', brief=receipt, reader_receipt=receipt, diagram_role_receipt=receipt,
            selection_evidence=receipt, reader_actor='visual-reader', diagram_actor='diagram-designer',
            source_figures=[dict(identity='EX0', figure_id='Fig1', page=1, pixel_read=True, receipt=receipt)],
            analysis={d:dict(source_location='EX0 Fig1 p1', observation='synthetic spatial comparison',
                            design_choice='original design decision for fixture') for d in
                      ('focus','hierarchy','abstraction','layout_flow','color_semantics','type_whitespace','panels')})
        self.good['exemplar_learning']['visual_design']=visual
        for v in self.good['versions']:
            for criterion in ('diagram_scientific_accuracy','diagram_visual_design'):
                v['checks'][criterion]=dict(verdict='pass',location='Fig1',reason='synthetic test only',evidence='fixture')
        return visual

    def data_fixture(self):
        self.good['data_visualization_requested']=True
        receipt=self.good['exemplar_learning']['preflight_receipt']
        data=dict(mode='independent', reader_actor='data-reader', visualization_actor='data-designer',
            brief=receipt, reader_receipt=receipt, visualization_role_receipt=receipt,
            selection_evidence=receipt, skill_selection=receipt,
            source_figures=[dict(identity='EX0',figure_id='Fig1',page=1,pixel_read=True,receipt=receipt)],
            analysis={d:dict(source_location='EX0 Fig1 p1', observation='synthetic comparison observation',
                design_choice='synthetic target-specific choice') for d in
                ('comparison_chart','axes_baselines','uncertainty','encoding_accessibility',
                 'palette_legend','typography','layout_density','panels')},
            charts=[dict(id='DATA1',source_kind='reported',presented_as='reported',source=receipt,
                         comparison_claim='descriptive',
                         exclusions=receipt,chart_type='bar',scale='linear',baseline='zero',
                         uncertainty=dict(available=False,shown=False,definition='not provided; omit intervals'))])
        self.good['exemplar_learning']['data_visual_design']=data
        for v in self.good['versions']:
            v['data_implementation_map']=receipt
            v['data_export_qa']=[dict(chart_id='DATA1',format='pdf',export=receipt,
                rendered_pixels=receipt,read_receipt=receipt,font_report=receipt,
                reviewed_sha256=receipt['sha256'],pixel_read=True,glyph_check='pass',font_check='pass')]
            for criterion in ('data_scientific_fidelity','data_visual_design'):
                v['checks'][criterion]=dict(verdict='pass',location='Fig2',reason='synthetic only',evidence='fixture')
        return data

    def test_png_success_cannot_replace_final_pdf_glyph_review(self):
        self.data_fixture()
        for change,error in [
            (lambda x:x.update(format='png'),'actual PDF'),
            (lambda x:x.update(pixel_read=False),'pixels/glyphs/fonts'),
            (lambda x:x.update(glyph_check='fail'),'pixels/glyphs/fonts'),
            (lambda x:x.pop('font_report'),'font_report required'),
            (lambda x:x.update(reviewed_sha256='old'),'stale data PDF')]:
            r=copy.deepcopy(self.good)
            change(r['versions'][1]['data_export_qa'][0])
            self.reject(r,error)
        self.good['versions'][1]['data_export_qa']=[]
        self.reject(self.good,'every chart/language')

    def test_data_exemplars_require_pixels_not_links_or_palette_words(self):
        self.data_fixture()
        self.assertEqual(self.check_with_synthetic_trust(),[])
        for change,error in [
            (lambda d:d.update(source_figures=[]),'pixel reading'),
            (lambda d:d['source_figures'][0].update(pixel_read=False),'pixel coverage'),
            (lambda d:d['source_figures'][0].update(figure_id='unknown'),'pixel coverage'),
            (lambda d:d.update(analysis={'palette_legend':'professional blue/orange'}),'concrete'),
            (lambda d:d.pop('visualization_role_receipt'),'visualization_role_receipt'),
            (lambda d:d.pop('skill_selection'),'skill_selection')]:
            with self.subTest(error=error):
                r=copy.deepcopy(self.good)
                change(r['exemplar_learning']['data_visual_design'])
                self.reject(r,error)
        self.good['exemplar_learning']['papers'][0]['access']='abstract_only'
        self.reject(self.good,'cannot count as read')

    def test_data_provenance_uncertainty_and_bars(self):
        self.data_fixture()
        for change,error in [
            (lambda c:c.update(baseline='truncated'),'baseline must be zero'),
            (lambda c:c.update(presented_as='measured'),'type misrepresented'),
            (lambda c:c.update(source_kind='placeholder',presented_as='placeholder'),'placeholder'),
            (lambda c:c['uncertainty'].update(shown=True),'cannot be invented'),
            (lambda c:c.pop('exclusions'),'exclusions evidence')]:
            with self.subTest(error=error):
                r=copy.deepcopy(self.good)
                change(r['exemplar_learning']['data_visual_design']['charts'][0])
                self.reject(r,error)

    def test_reported_uncertainty_is_allowed_with_traceable_definition(self):
        d=self.data_fixture()
        d['charts'][0]['uncertainty']=dict(available=True,shown=True,definition='SD reported by source',
            evidence=d['brief'],sample_size='5',sampling_unit='independent run')
        self.assertEqual(self.check_with_synthetic_trust(),[])

    def test_small_difference_without_uncertainty_cannot_claim_superiority(self):
        d=self.data_fixture()
        d['charts'][0]['comparison_claim']='superiority'
        self.reject(self.good,'superiority needs reviewer')
        d['charts'][0]['statistical_review']=d['brief']
        self.reject(self.good,'missing uncertainty')

    def test_data_aesthetics_cannot_override_scientific_failure_or_missing_map(self):
        self.data_fixture()
        self.good['versions'][0]['checks']['data_scientific_fidelity'].update(verdict='fail',
            reason='Negative results were removed solely to simplify the panel',evidence='Reader compares source rows and plotted rows')
        self.reject(self.good,'data_scientific_fidelity')
        self.good['versions'][1].pop('data_implementation_map')
        self.reject(self.good,'data design implementation')

    def test_staged_data_design_partial_and_malformed(self):
        self.test_limited_evidence_working_paper_remains_incomplete()
        d=self.data_fixture()
        d.update(mode='staged',reader_actor='one',visualization_actor='one',reason='no independent executor')
        self.assertEqual(self.check_with_synthetic_trust(),[])
        self.good.update(status='submission_checks_complete',blockers=[])
        self.reject(self.good,'staged data visual')
        for change in [lambda d:d.update(source_figures=[None]),
                       lambda d:d.update(charts=[None]),
                       lambda d:d['charts'][0].update(uncertainty=[]),
                       lambda d:d.update(analysis=['palette'])]:
            r=copy.deepcopy(self.good)
            change(r['exemplar_learning']['data_visual_design'])
            self.assertTrue(m.validate(r,self.root))

    def test_architecture_requires_pixels_role_result_and_concrete_design(self):
        visual=self.visual_fixture()
        self.assertEqual(self.check_with_synthetic_trust(),[])
        for change, error in [
            (lambda v:v['source_figures'][0].update(pixel_read=False), 'pixel coverage'),
            (lambda v:v.pop('diagram_role_receipt'), 'diagram_role_receipt'),
            (lambda v:v.update(diagram_actor='visual-reader'), 'collaboration'),
            (lambda v:v['analysis'].pop('hierarchy'), 'hierarchy analysis'),
            (lambda v:v['source_figures'][0].update(figure_id='unknown'), 'pixel coverage')]:
            with self.subTest(error=error):
                r=copy.deepcopy(self.good)
                change(r['exemplar_learning']['visual_design'])
                self.reject(r,error)

    def test_diagram_accuracy_does_not_replace_visual_quality(self):
        self.visual_fixture()
        self.good['versions'][0]['checks']['diagram_visual_design'].update(verdict='fail',
            location='Figure 1', reason='Equal emphasis obscures new contribution; arrows lack readable order',
            evidence='Reviewer compares brief and actual rendered figure, despite scientifically correct nodes')
        self.reject(self.good,'diagram_visual_design')

    def test_staged_visual_design_can_continue_partial_not_certify(self):
        self.test_limited_evidence_working_paper_remains_incomplete()
        visual=self.visual_fixture()
        visual.update(mode='staged',reader_actor='one-context',diagram_actor='one-context',
                      reason='No independent diagram executor; staged design only')
        self.assertEqual(self.check_with_synthetic_trust(),[])
        self.good.update(status='submission_checks_complete',delivered_artifact='submission_paper',blockers=[])
        self.reject(self.good,'staged visual design')

    def test_malformed_learning_no_crash(self):
        for change in [lambda l:l.update(papers=[None]*10),
                       lambda l:l['papers'][0].update(figure_inventory=[[]]),
                       lambda l:l.update(decisions=[{'dimension':[]}]),
                       lambda l:l.update(template=None)]:
            with self.subTest(change=change):
                r=copy.deepcopy(self.good)
                change(r['exemplar_learning'])
                self.assertTrue(m.validate(r,self.root))

    def reject(self, record, fragment):
        self.assertTrue(any(fragment in e for e in m.validate(record,self.root)))

    def test_audit_cannot_replace_submission(self):
        self.good['delivered_artifact']='technical_audit'
        self.reject(self.good,'audit cannot replace')

    def test_semantic_review_rejects_audit_even_with_headings_and_layout(self):
        self.good['versions'][0]['checks']['artifact_fit'].update(verdict='fail',
            location='Abstract; Evaluation', reason='Only enumerates files and audit discrepancies',
            evidence='Reviewer read: Introduction/Methods/Results headings mask an audit narrative')
        self.reject(self.good,'artifact_fit')

    def test_layout_only_is_not_completion(self):
        self.good['versions'][0]['checks']={'format':self.good['versions'][0]['checks']['format']}
        self.reject(self.good,'missing contribution')

    def test_unloaded_roles_fail(self):
        self.good['bindings'][1]['loaded_before_execution']=False
        self.reject(self.good,'not loaded before')

    def test_dispatch_is_not_execution_result(self):
        del self.good['bindings'][2]['result_receipt']
        self.reject(self.good,'actual result_receipt')

    def test_partial_read_or_stale_pdf_fail(self):
        for key,value,error in [('read_pages',[1,2,3,4,5,6],'page coverage'),
                                ('reader_snapshot_sha256','old','stale reader')]:
            with self.subTest(key=key):
                r=copy.deepcopy(self.good)
                r['versions'][0][key]=value
                self.reject(r,error)

    def test_no_data_result_assertion_fails(self):
        self.good['versions'][0]['checks']['evidence'].update(verdict='fail',
            reason='Abstract reports measured speedup but Section 5 only calculates ideal bandwidth')
        self.reject(self.good,'evidence')

    def test_limited_evidence_working_paper_remains_incomplete(self):
        self.good.update(status='validation_partial', delivered_artifact='working_paper', blockers=[
            dict(claim='end-to-end speedup', missing='real end-to-end trials', owner='experiment role',
                 next_action='run matched workload baseline', resume_when='raw trial logs available')])
        self.good['versions'][0]['checks']['evidence']['verdict']='unresolved'
        self.assertEqual(self.check_with_synthetic_trust(),[])

    def test_requested_language_missing(self):
        self.good['versions'].pop()
        self.reject(self.good,'language coverage')

    def test_staged_and_shared_actors_cannot_certify_completion(self):
        self.good['bindings'][2]['mode']='staged'
        self.reject(self.good,'independent review required')
        self.good['bindings'][3]['actor']='research-review'
        self.reject(self.good,'separate actors')

    def test_stale_scientific_review_fails(self):
        self.good['versions'][0]['reviewer_snapshot_sha256']='old'
        self.reject(self.good,'stale scientific review')

    def test_honest_pending_review_needs_no_fabricated_receipts(self):
        self.test_limited_evidence_working_paper_remains_incomplete()
        self.good['bindings'][2]={'role':'research-review', 'state':'not_run', 'reason':'draft incomplete'}
        self.assertEqual(self.check_with_synthetic_trust(),[])
        self.good['status']='submission_checks_complete'
        self.reject(self.good,'incomplete execution')

    def test_false_independence_and_instruction_tampering(self):
        self.good['bindings'][2]['actor']='research-write'
        self.reject(self.good,'independent actor')
        (self.root/'SKILL.md').write_text('changed')
        self.reject(self.good,'files/hash')

    def test_malformed_records_fail_without_crash(self):
        for r in [None, {}, {'bindings':[None], 'versions':[None]}, {'versions':[{'language':[]}]}]:
            with self.subTest(record=r):
                self.assertTrue(m.validate(r,self.root))
