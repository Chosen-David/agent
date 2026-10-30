"""Structured intake: bounded confirmation, answer re-injection and re-check."""
import unittest

from agent_runtime.intake import IntakeError, apply_intake, build_intake


class IntakeTests(unittest.TestCase):
    def build(self):
        return build_intake([
            {'id': 'platform', 'question': 'Target platform?', 'options': ['cpu', 'gpu']},
            {'id': 'precision', 'question': 'Precision?',
             'options': ['fp32', 'fp16', 'bf16'], 'default': 'fp32'},
            {'id': 'note', 'question': 'Any extra note?',
             'options': ['none'], 'allow_free_text': True},
        ])

    def test_build_normalizes_and_marks_needs_confirmation(self):
        request = self.build()
        self.assertEqual(request['schema_version'], 'intake/v1')
        self.assertEqual(request['status'], 'NEEDS_CONFIRMATION')
        self.assertEqual([q['id'] for q in request['questions']],
                         ['platform', 'precision', 'note'])

    def test_options_capped_at_five_and_unique(self):
        with self.assertRaisesRegex(IntakeError, 'more than 5'):
            build_intake([{'id': 'a', 'question': 'q?', 'options': ['1', '2', '3', '4', '5', '6']}])
        with self.assertRaisesRegex(IntakeError, 'unique'):
            build_intake([{'id': 'a', 'question': 'q?', 'options': ['1', '1']}])

    def test_default_and_id_validation(self):
        with self.assertRaisesRegex(IntakeError, 'default is not one of its options'):
            build_intake([{'id': 'a', 'question': 'q?', 'options': ['x'], 'default': 'y'}])
        with self.assertRaisesRegex(IntakeError, 'ids must be unique'):
            build_intake([{'id': 'a', 'question': 'q?', 'options': ['x']},
                          {'id': 'a', 'question': 'r?', 'options': ['y']}])

    def test_partial_answers_report_missing_and_not_complete(self):
        result = apply_intake(self.build(), {'platform': 'cpu'})
        self.assertFalse(result['complete'])
        self.assertEqual(result['status'], 'NEEDS_CONFIRMATION')
        self.assertEqual(result['confirmed'], {'platform': 'cpu', 'precision': 'fp32'})
        self.assertEqual(result['missing'], ['note'])

    def test_complete_answers_with_free_text_and_default(self):
        result = apply_intake(self.build(), {'platform': 'gpu', 'note': 'fuse kernels'})
        self.assertTrue(result['complete'])
        self.assertEqual(result['status'], 'CONFIRMED')
        self.assertEqual(result['confirmed'],
                         {'platform': 'gpu', 'precision': 'fp32', 'note': 'fuse kernels'})

    def test_invalid_option_and_unknown_id_are_rejected(self):
        result = apply_intake(self.build(), {'platform': 'quantum', 'ghost': 'x'})
        self.assertFalse(result['complete'])
        reasons = {e['question']: e['reason'] for e in result['errors']}
        self.assertEqual(reasons['platform'], 'not in options')
        self.assertEqual(reasons['ghost'], 'unknown question id')

    def test_non_request_and_non_mapping_inputs_are_rejected(self):
        with self.assertRaisesRegex(IntakeError, 'intake/v1'):
            apply_intake({'schema_version': 'other'})
        with self.assertRaisesRegex(IntakeError, 'mapping'):
            apply_intake(self.build(), ['platform'])


class IntakeConsumerTests(unittest.TestCase):
    @staticmethod
    def question(qid='target'):
        return {'id': qid, 'question': 'Target?', 'options': ['yes'],
                'allow_free_text': False, 'default': 'yes'}

    def reject_without_mutation(self, questions):
        from copy import deepcopy
        request = {'schema_version': 'intake/v1', 'questions': questions}
        original = deepcopy(request)
        try:
            with self.assertRaises(IntakeError):
                apply_intake(request)
        finally:
            self.assertEqual(request, original)

    def test_apply_rejects_empty_and_oversized_question_sets(self):
        for questions in ([], [self.question(str(i)) for i in range(21)]):
            with self.subTest(count=len(questions)):
                self.reject_without_mutation(questions)

    def test_apply_rejects_duplicate_normalized_ids(self):
        for qid in ('target', ' target '):
            with self.subTest(second_id=qid):
                self.reject_without_mutation([self.question(), self.question(qid)])

    def test_apply_rejects_invalid_question_contract_fields(self):
        changes = ({'question': ''}, {'options': ['yes', 'yes']},
                   {'options': ['yes', '2', '3', '4', '5', '6']},
                   {'allow_free_text': 'true'}, {'default': 'not-an-option'})
        for change in changes:
            with self.subTest(change=change):
                self.reject_without_mutation([dict(self.question(), **change)])

    def test_roundtrip_preserves_answers_defaults_missing_and_inputs(self):
        import json
        from copy import deepcopy
        request = json.loads(json.dumps(build_intake([
            {'id': 'target', 'question': 'Target?', 'options': ['yes'], 'default': 'yes'},
            {'id': 'note', 'question': 'Note?', 'options': ['none'], 'allow_free_text': True},
        ])))
        before = deepcopy(request)
        missing = apply_intake(request)
        self.assertFalse(missing['complete'])
        self.assertEqual(missing['confirmed'], {'target': 'yes'})
        self.assertEqual(missing['missing'], ['note'])
        answers = {'note': '恢复 ✓'}
        answers_before = deepcopy(answers)
        complete = apply_intake(request, answers)
        self.assertTrue(complete['complete'])
        self.assertEqual(complete['confirmed'], {'target': 'yes', 'note': '恢复 ✓'})
        self.assertEqual(request, before)
        self.assertEqual(answers, answers_before)


if __name__ == '__main__':
    unittest.main()
