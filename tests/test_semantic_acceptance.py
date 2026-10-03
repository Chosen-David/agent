"""Synthetic trusted-controller controls; no receipts here attest actual roles."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import test_paper_delivery as fixture_module
from semantic_acceptance import canonical_record_sha256


class SemanticAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixture_module.PaperDeliveryTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        self.record = self.fixture.good
        self.acceptance = fixture_module.synthetic_acceptance(self.record)

    def errors(self, acceptance=True):
        return fixture_module.m.validate(self.record, self.root,
            acceptance=self.acceptance if acceptance else None)

    def assert_reject(self, fragment, acceptance=True):
        errors = self.errors(acceptance)
        self.assertTrue(any(fragment in error for error in errors), errors)

    def rewrite_event(self, field, **changes):
        binding = self.record['bindings'][1]
        item = binding[field]
        path = self.root/item['path']
        event = json.loads(path.read_text()); event.update(changes)
        path.write_text(json.dumps(event))
        item['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        # A controller trusting new bytes still cannot bypass event shape/identity.
        self.acceptance = fixture_module.synthetic_acceptance(self.record)

    def test_positive_external_acceptance_and_reordered_json(self):
        self.assertEqual(self.errors(), [])
        reordered = dict(reversed(list(self.record.items())))
        self.assertEqual(canonical_record_sha256(reordered),self.acceptance['record_sha256'])
        self.assertEqual(fixture_module.m.validate(reordered,self.root,acceptance=self.acceptance),[])

    def test_absent_and_forged_inline_acceptance_fail_closed(self):
        self.assert_reject('external trusted',False)
        self.record['acceptance'] = copy.deepcopy(self.acceptance)
        self.assert_reject('external trusted',False)

    def test_record_and_snapshot_staleness(self):
        old_target=self.record['target']
        self.record['target'] += ' changed target'
        self.assert_reject('stale record hash')
        self.record['target'] = old_target
        self.acceptance = fixture_module.synthetic_acceptance(self.record)
        self.acceptance['versions'][0]['snapshot_sha256']='0'*64
        self.assert_reject('stale snapshot hash')

    def test_file_content_and_coverage_binding(self):
        path=self.root/self.record['versions'][0]['snapshot']['path']
        path.write_text('Replacement manuscript after independent review')
        self.assert_reject('stale file')
        self.acceptance['file_hashes']={}
        self.assert_reject('file hash coverage mismatch')

    def test_self_review_and_unobserved_reviewer(self):
        for actor in ('research-write','unobserved-reviewer'):
            with self.subTest(actor=actor):
                self.acceptance['reviewer_actor']=actor
                self.assert_reject('reviewer must match')

    def test_disguised_audit_and_copy_need_independent_pass(self):
        for criterion in ('artifact_fit','originality'):
            with self.subTest(criterion=criterion):
                self.acceptance=fixture_module.synthetic_acceptance(self.record)
                self.acceptance['versions'][0]['checks'][criterion].update(
                    verdict='fail',evidence=['paper.pdf p1: independent synthetic reviewer rejects artifact'])
                self.assert_reject(criterion+': independent pass required')

    def test_evidence_and_language_coverage(self):
        self.acceptance['versions'][0]['checks']['originality']['evidence']=[]
        self.assert_reject('evidence locations required')
        self.acceptance=fixture_module.synthetic_acceptance(self.record)
        self.acceptance['versions'].pop()
        self.assert_reject('language coverage mismatch')

    def test_dispatch_and_queued_start_are_not_execution(self):
        self.rewrite_event('start_receipt',kind='dispatch',status='queued')
        self.assert_reject('expected start event')
        self.rewrite_event('start_receipt',kind='start',status='queued')
        self.assert_reject('cannot be queued')

    def test_completion_status_and_identity_holdouts(self):
        self.rewrite_event('result_receipt',status='blocked')
        self.assert_reject('produced status')
        for key in ('actor','role','revision','run_id','task_id'):
            with self.subTest(key=key):
                binding=self.record['bindings'][1]
                self.rewrite_event('result_receipt',status='produced',actor=binding['actor'],
                                   role=binding['role'],revision=binding['revision'],
                                   run_id=binding['run_id'],task_id=binding['task_id'])
                self.rewrite_event('result_receipt',**{key:'different-'+key})
                self.assert_reject('receipt '+key+' does not match')

    def test_event_id_reuse_and_nonjson_receipt_holdouts(self):
        start=self.record['bindings'][1]['start_receipt']
        event=json.loads((self.root/start['path']).read_text())
        self.rewrite_event('result_receipt',event_id=event['event_id'])
        self.assert_reject('event IDs must be unique')
        path=self.root/start['path']; path.write_text('not JSON')
        start['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
        self.acceptance=fixture_module.synthetic_acceptance(self.record)
        self.assert_reject('invalid observed start_receipt')

    def test_synthetic_and_mock_receipts_cannot_certify_actual_execution(self):
        for fields in ({'synthetic':True}, {'fixture_only':True}, {'adapter':'mock'},
                       {'synthetic':1}, {'synthetic':'true'}, {'fixture_only':'yes'},
                       {'synthetic':None}, {'synthetic':0}):
            with self.subTest(fields=fields):
                self.rewrite_event('start_receipt',synthetic=False,fixture_only=False,adapter='host')
                self.rewrite_event('start_receipt',**fields)
                self.assert_reject('synthetic/mock receipt')

    def test_attempt_pairing_and_missing_start_status_holdout(self):
        for attempt in (2,0,True,'1'):
            with self.subTest(attempt=attempt):
                self.rewrite_event('result_receipt',attempt=attempt)
                self.assert_reject('positive binding attempt')
        self.rewrite_event('result_receipt',attempt=1)
        self.rewrite_event('start_receipt',status=None)
        self.assert_reject('must have started status')
        self.rewrite_event('start_receipt',status='fixture_only')
        self.assert_reject('must have started status')

    def test_malformed_acceptance_fails_without_crash(self):
        for value in (None,[],{}, {'schema_version':True},
                      dict(self.acceptance,versions=[None]),dict(self.acceptance,reviewer_actor=[])):
            with self.subTest(value=value):
                self.assertTrue(fixture_module.m.validate(self.record,self.root,acceptance=value))

    def test_cli_requires_explicit_external_acceptance(self):
        record=self.root/'record.json'; record.write_text(json.dumps(self.record))
        external=tempfile.TemporaryDirectory(); self.addCleanup(external.cleanup)
        acceptance=Path(external.name)/'trusted-controller.json'; acceptance.write_text(json.dumps(self.acceptance))
        command=[sys.executable,str(fixture_module.ROOT/'scripts/validate_paper_delivery.py'),str(record),'--root',str(self.root)]
        missing=subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(missing.returncode,1)
        self.assertFalse(json.loads(missing.stdout)['declarations_valid'])
        self.assertEqual(json.loads(missing.stdout)['completion_status'],'unverified')
        present=subprocess.run(command+['--acceptance',str(acceptance)],capture_output=True,text=True)
        self.assertEqual(present.returncode,0,present.stdout+present.stderr)
        self.assertTrue(json.loads(present.stdout)['declarations_valid'])
        self.assertEqual(json.loads(present.stdout)['completion_status'],'verified')
        inline=self.root/'forged-controller.json'; inline.write_text(json.dumps(self.acceptance))
        rejected=subprocess.run(command+['--acceptance',str(inline)],capture_output=True,text=True)
        self.assertEqual(rejected.returncode,1)
        self.assertIn('outside the worker artifact root',rejected.stdout)


if __name__ == '__main__': unittest.main()
