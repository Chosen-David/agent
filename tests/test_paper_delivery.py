"""Synthetic declarations; these tests do not score prose or live agent quality."""
import copy
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('paper_delivery', ROOT / 'scripts/validate_paper_delivery.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class PaperDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        def artifact(name):
            (self.root / name).write_text('synthetic fixture, not a real paper or execution')
            return {'path': name, 'sha256': hashlib.sha256((self.root/name).read_bytes()).hexdigest()}
        files = [artifact(n) for n in ('SKILL.md', 'execution.md', 'workflow.md', 'paper_delivery_contract.md')]
        snapshot = artifact('paper.pdf')
        receipt = artifact('receipt.json')
        self.good = dict(schema_version=1, requested_artifact='submission_paper',
            delivered_artifact='submission_paper', target='A complete bilingual research submission',
            requested_languages=['en', 'zh'], status='submission_checks_complete', blockers=[],
            bindings=[dict(role=r, actor=r, state='completed', mode='independent', loaded_before_execution=True,
                revision='fixture', read_scope='fixture instructions', files=files,
                start_receipt=receipt, result_receipt=receipt) for r in m.ROLES],
            versions=[dict(language=l, snapshot=snapshot, page_count=7, read_pages=list(range(1,8)),
                reader_snapshot_sha256=snapshot['sha256'], reviewer_snapshot_sha256=snapshot['sha256'], checks={c: dict(verdict='pass',
                location='synthetic section', reason='synthetic declaration only', evidence='fixture')
                for c in m.CRITERIA}) for l in ('en','zh')])

    def test_valid_declarations_only(self):
        self.assertEqual(m.validate(self.good, self.root), [])

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
        self.assertEqual(m.validate(self.good,self.root),[])

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
        self.assertEqual(m.validate(self.good,self.root),[])
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
