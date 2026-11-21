from tests.document_fixture import DocumentFixtureCase
import copy
import unittest

from lifecycle_cost import summarize


class LifecycleCostTests(DocumentFixtureCase):
    def record(self):
        return {'events': [{'phase': phase, 'text': phase} for phase in
                           ('creation', 'discovery', 'maintenance', 'diagnosis', 'execution')],
                'checks': [{'revision': 'a', 'case': 'bad', 'defective': True,
                            'outcome': 'detected', 'evidence': 'assertion failed'},
                           {'revision': 'b', 'case': 'good', 'defective': False,
                            'outcome': 'pass', 'evidence': 'passed'}]}

    def test_all_phases_are_charged(self):
        result = summarize(self.record(), len)
        self.assertEqual(result['payload_tokens'], 46)
        self.assertTrue(result['coverage_complete'])
        self.assertIsNone(result['end_to_end_savings'])

    def test_missing_maintenance_is_incomplete(self):
        record = self.record()
        record['events'] = record['events'][:2]
        self.assertIn('maintenance', summarize(record, len)['missing_phases'])

    def test_crash_is_not_detection(self):
        record = self.record()
        record['checks'][0]['outcome'] = 'error'
        result = summarize(record, len)
        self.assertEqual(result['detected'], 0)
        self.assertEqual(result['errors'], 1)
        self.assertIsNone(result['miss_rate'])
        self.assertEqual(result['unverified_defects'], 1)

    def test_surviving_mutation_is_miss(self):
        record = self.record()
        record['checks'][0]['outcome'] = 'pass'
        self.assertEqual(summarize(record, len)['miss_rate'], 1)

    def test_false_positive(self):
        record = self.record()
        record['checks'][1]['outcome'] = 'detected'
        self.assertEqual(summarize(record, len)['false_positives'], 1)

    def test_repeated_same_revision_does_not_become_longitudinal(self):
        record = self.record()
        record['checks'][1]['revision'] = 'a'
        self.assertFalse(summarize(record, len)['coverage_complete'])

    def test_duplicate_case_rejected(self):
        record = self.record()
        record['checks'].append(copy.deepcopy(record['checks'][0]))
        with self.assertRaises(ValueError):
            summarize(record, len)

    def test_invalid_input_rejected(self):
        for field, value in [('defective', 'false'), ('outcome', 'crash'), ('evidence', '')]:
            record = self.record()
            record['checks'][0][field] = value
            with self.assertRaises(ValueError):
                summarize(record, len)

    def test_empty_records_rejected(self):
        with self.assertRaises(ValueError):
            summarize({'events': [], 'checks': []}, len)
