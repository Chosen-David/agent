"""Deep claim validation preserves evidence and legacy rejection behavior."""
from copy import deepcopy
import unittest
from unittest.mock import patch

from agent_runtime.handoff_basis import claim_graph


def chain(n):
    return {'artifacts': [{'id': 'proof'}], 'evidence_claims': [
        dict(id=f'c{i}', status='supported', knowledge_ids=[], memory_ids=[],
             artifact_ids=['proof'], depends_on=[f'c{i-1}'] if i else [], assumptions=[])
        for i in range(n)]}


class ClaimResidualTests(unittest.TestCase):
    def test_complete_deep_graph_identity_and_no_mutation(self):
        for n in (0, 1, 65, 66, 67, 1200):
            record = chain(n)
            original = deepcopy(record)
            with self.subTest(n=n):
                graph = claim_graph(record)
                self.assertEqual(list(graph), [c['id'] for c in record['evidence_claims']])
                self.assertTrue(all(graph[c['id']] is c for c in record['evidence_claims']))
                self.assertEqual(record, original)

    def test_deep_invalid_dependencies_remain_rejected(self):
        for mode, message in [('unknown', 'unknown parent claim'),
                              ('unsupported', 'supported claim depends on unsupported claim'),
                              ('cycle', 'cyclic claim dependencies')]:
            record = chain(100)
            if mode == 'unknown':
                record['evidence_claims'][60]['depends_on'].append('missing')
            elif mode == 'unsupported':
                record['evidence_claims'][60]['status'] = 'candidate'
            else:
                record['evidence_claims'][98]['depends_on'] = ['c99']
            before = deepcopy(record)
            with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, message):
                claim_graph(record)
            self.assertEqual(record, before)

    def test_custom_objects_retain_legacy_observable_operations(self):
        events = []
        class TracedString(str):
            def __hash__(self):
                events.append(('hash', str(self)))
                return super().__hash__()
            def __eq__(self, other):
                events.append(('eq', str(self), str(other)))
                return super().__eq__(other)
        class TracedList(list):
            def __iter__(self):
                events.append('iterate')
                return super().__iter__()
        class TracedDict(dict):
            def __getitem__(self, key):
                events.append(('getitem', key))
                return super().__getitem__(key)
        for mode in ('id', 'parent', 'status', 'list', 'dict'):
            record = chain(100)
            if mode == 'id':
                record['evidence_claims'][0]['id'] = TracedString('c0')
            elif mode == 'parent':
                record['evidence_claims'][60]['depends_on'] = [TracedString('c59')]
            elif mode == 'status':
                record['evidence_claims'][60]['status'] = TracedString('supported')
            elif mode == 'list':
                record['evidence_claims'][60]['depends_on'] = TracedList(['c59'])
            else:
                record['evidence_claims'][60] = TracedDict(record['evidence_claims'][60])
            events.clear()
            with patch('agent_runtime.handoff_basis._valid_claim_residual', return_value=False):
                expected = claim_graph(record)
            legacy_events = events[:]
            events.clear()
            actual = claim_graph(record)
            actual_events = events[:]
            with self.subTest(mode=mode):
                self.assertEqual(actual_events, legacy_events)
                self.assertEqual(actual, expected)

    def test_multiple_errors_keep_legacy_diagnostic(self):
        record = chain(100)
        record['evidence_claims'][30]['status'] = 'candidate'
        record['evidence_claims'][60]['depends_on'].append('missing')
        record['evidence_claims'][98]['depends_on'] = ['c99']
        def error():
            try:
                claim_graph(record)
            except ValueError as exc:
                return type(exc), str(exc)
            self.fail('invalid graph accepted')
        with patch('agent_runtime.handoff_basis._valid_claim_residual', return_value=False):
            expected = error()
        self.assertEqual(error(), expected)


if __name__ == '__main__':
    unittest.main()
