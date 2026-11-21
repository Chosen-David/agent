from tests.document_fixture import DocumentFixtureCase
import os
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(os.environ["AGENT_TEST_PROJECT_ROOT"])))
from agent_runtime.plan_review import PlanReviewError, sha
from tests import test_plan_review as fixture_module


class ReviewEvidenceTests(DocumentFixtureCase):
    def setUp(self):
        self.fixture = fixture_module.PlanReviewTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def submit_modified(self, modify):
        original = self.fixture.session.reviewer

        def reviewer(request, plan, previous):
            response = original(request, plan, previous)
            modify(response['review'])
            self.fixture.records[response['proof']]['review_sha256'] = sha(response['review'])
            return response

        self.fixture.session.reviewer = reviewer
        return self.fixture.session.submit(self.fixture.plan)

    def test_authenticated_unknown_requirement_cannot_approve(self):
        with self.assertRaisesRegex(PlanReviewError, 'missing critical checks'):
            self.submit_modified(lambda r: r['verdict']['checks']['intent'].update(
                status='unknown', reason='Retry semantics require a human answer'))

    def test_empty_critique_does_not_mean_success(self):
        with self.assertRaisesRegex(PlanReviewError, 'full review missing'):
            self.submit_modified(lambda r: r.update(full_review=''))

    def test_approval_cannot_hide_a_blocking_counterexample(self):
        finding = dict(blocking=True, target='send after cancel',
                       feedback='A send follows cancellation in the trace',
                       requested_change='Stop before sending',
                       acceptance_check='Replay cancellation and observe zero sends')
        with self.assertRaisesRegex(PlanReviewError, 'blocking findings'):
            self.submit_modified(lambda r: r['verdict']['findings'].append(finding))

    def test_refusal_without_actionable_feedback_is_not_a_review(self):
        with self.assertRaisesRegex(PlanReviewError, 'actionable findings'):
            self.submit_modified(lambda r: r['verdict'].update(decision='revise'))

    def test_feedback_tampering_cannot_reuse_authentication(self):
        self.fixture.approve()
        receipt = copy.deepcopy(self.fixture.plan['plan_review_receipt'])
        receipt['review']['full_review'] += '\nChanged after authentication'
        with self.assertRaises(PlanReviewError):
            self.fixture.session.verify(self.fixture.root, receipt['request'],
                                        receipt['review'], receipt['proof'])


if __name__ == '__main__':
    unittest.main()
