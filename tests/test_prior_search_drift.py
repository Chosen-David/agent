"""Protected CPU producer chains retain review inputs across harmless scans."""
import copy
import hashlib
import json
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch

from agent_runtime.core import Engine, Outcome, Store
from agent_runtime.result_store import ResultStore
from agent_runtime.result_validation import ResultValidationHandler
from agent_runtime.plan_review import plan_sha256
from agent_runtime.task_manifest import ReportingHandler, atomic_json, _prior_search_comparison
from tests import test_plan_review_independent as review_fixture
from tests import test_result_validation as numerical_fixture


class PriorSearchDriftTests(unittest.TestCase):
    def setUp(self):
        self.case = review_fixture.IndependentPlanReviewTests()
        self.case.setUp()
        self.addCleanup(self.case.doCleanups)
        self.root = self.case.root
        self.calls = []
        self.verified = []
        self.contracts = {}
        self.manifests = {}
        for label in ('alpha', 'beta'):
            folder = self.root / label
            contract = numerical_fixture.make_fixture(folder)
            manifest = json.loads((folder / 'manifest.json').read_text())
            base = 'agent_doc/results/produced-' + label
            contract.update(result_id='result-' + label, producer_task_id=label,
                            producer_actor='actor-' + label,
                            manifest_path=base + '/manifest.json',
                            validation_plan=dict(contract['validation_plan'],
                                                 path=label + '/validation-plan.json'))
            manifest.update({k: contract[k] for k in ('result_id', 'producer_task_id',
                                                     'producer_actor', 'validation_plan')})
            manifest['run_id'] = 'produced-' + label
            for refs in manifest['artifacts'].values():
                for ref in refs:
                    ref['path'] = label + '/' + ref['path']
            for role, name in (('raw_data', 'raw.json'), ('outputs', 'output.json')):
                manifest['artifacts'][role][0]['path'] = base + '/' + name
            atomic_json(folder / 'manifest.json', manifest)
            self.contracts[label] = contract
            self.manifests[label] = manifest
        self.plan = self.case.make_plan('dual-producer')
        template = self.plan['tasks'][0]
        tasks = []
        for label in ('alpha', 'beta'):
            task = copy.deepcopy(template)
            task.update(task_id=label, owner='actor-' + label, action='produce_fixture',
                        explicit_reproduction=True, new_claim=True,
                        depends_on=[] if label == 'alpha' else ['verify-alpha'],
                        experiment_result=self.contracts[label], result_storage='central', outputs=[],
                        allowed_writes=[label + '/', 'reports/' + label + '.json',
                                        'agent_doc/results/produced-' + label + '/'],
                        report_path='reports/' + label + '.json',
                        inputs={'goal': 'zqx' + label + 'target'},
                        prior_result_review={'decision': 'rerun', 'record_refs': [],
                                             'reason': 'Bounded declared CPU reproduction.'})
            task['prior_result_search'] = ResultStore(self.root).search(task['inputs']['goal'])
            if label == 'beta':
                task['required_result_refs'] = [self.contracts['alpha']]
            gate = copy.deepcopy(task)
            gate.pop('experiment_result')
            gate.update(task_id='verify-' + label, action='verify_experiment_result',
                        owner='independent-numerical-controller', depends_on=[label],
                        result_validation=self.contracts[label],
                        report_path='reports/verify-' + label + '.json', allowed_writes=[])
            atomic_json(self.root / gate['report_path'], {
                'task_id': gate['task_id'], 'summary': 'Independent bounded CPU arithmetic gate',
                'data': [{'kind': 'synthetic', 'description': 'Exact formula and original-file checks.'}]})
            tasks.extend((task, gate))
        self.plan['tasks'] = tasks
        self.case.approve(self.plan)
        self.store = Store(self.root / 'dual.sqlite')
        self.store.create(self.plan, project_root=self.root)
        self.frozen = self.store.snapshot(self.plan['run_id'])['plan']
        self.engine = self.restart()

    def verifier(self, root, manifest, plan):
        label = manifest['producer_task_id']
        proof = numerical_fixture.independent_verify(root / label, manifest, plan)
        for check in proof['checks'].values():
            for ref in check['evidence']:
                ref['path'] = label + '/' + ref['path']
        self.verified.append(label)
        return proof

    def restart(self):
        outer = self
        class Producer:
            idempotent = False
            required_capabilities = ()
            def run(self, task, context):
                label = task['task_id']
                subprocess.run([sys.executable, 'code.py'], cwd=outer.root / label,
                               check=True, capture_output=True, timeout=10)
                base = outer.root / 'agent_doc/results' / ('produced-' + label)
                base.mkdir(parents=True)
                for name in ('raw.json', 'output.json'):
                    shutil.copyfile(outer.root / label / name, base / name)
                atomic_json(base / 'manifest.json', outer.manifests[label])
                outer.calls.append(copy.deepcopy(task))
                atomic_json(outer.root / task['report_path'], {
                    'task_id': label, 'summary': 'Executed frozen deterministic CPU code',
                    'data': [{'kind': 'synthetic', 'description': 'Integer square-sum observations.'}]})
                return Outcome('complete', evidence=[label])
            def verify(self, task, evidence):
                return evidence == [task['task_id']]
        handlers = {
            'produce_fixture': ReportingHandler(Producer(), self.root, result_verifier=self.verifier),
            'verify_experiment_result': ReportingHandler(
                ResultValidationHandler(self.root, self.verifier), self.root,
                result_verifier=self.verifier)}
        return Engine(Store(self.store.path), handlers, authorize=lambda *_: True,
                      project_root=self.root, plan_review_verifier=self.case.session.verify,
                      clock=lambda: self.case.now)

    def first_result(self):
        for event in ('produce-alpha', 'verify-alpha'):
            state = self.engine.tick(self.plan['run_id'], event)
        self.assertEqual(state['tasks']['verify-alpha']['status'], 'done', state)
        self.assertTrue((self.root / 'agent_doc/results/produced-alpha/record.json').is_file())
        return state

    def test_second_producer_runs_after_unrelated_result_registration(self):
        self.first_result()
        before = self.plan['tasks'][2]['prior_result_search']
        current = ResultStore(self.root).search('zqxbetatarget')
        self.assertEqual(before['scanned'], 0)
        self.assertEqual(current['scanned'], 1)
        self.assertEqual({k: v for k, v in before.items() if k != 'scanned'},
                         {k: v for k, v in current.items() if k != 'scanned'})
        for event in ('produce-beta', 'verify-beta'):
            state = self.engine.tick(self.plan['run_id'], event)
        self.assertEqual(state['status'], 'done', state)
        self.assertEqual([t['task_id'] for t in self.calls], ['alpha', 'beta'])
        self.assertEqual(self.calls, [self.frozen['tasks'][i] for i in (0, 2)])
        self.assertEqual(self.calls[1]['prior_result_search'], before)
        self.assertTrue(all(state['tasks']['verify-' + label]['status'] == 'done'
                            for label in ('alpha', 'beta')))
        self.assertEqual(set(self.verified), {'alpha', 'beta'})
        persisted = self.store.snapshot(self.plan['run_id'])['plan']
        self.assertEqual(persisted, self.frozen)
        self.assertEqual(plan_sha256(persisted), plan_sha256(self.frozen))
        self.assertEqual(persisted['plan_review_receipt'], self.frozen['plan_review_receipt'])
        with self.store.transaction() as db:
            rows = [json.loads(row[0]) for row in db.execute(
                "SELECT detail FROM journal WHERE kind='prior_result_scan_only'")]
        self.assertEqual(rows, [{'task_id': 'beta', 'reviewed_scanned': 0, 'observed_scanned': 1}])

    def test_restart_preserves_reviewed_input_and_journals_fresh_scan(self):
        self.first_result()
        self.engine = self.restart()
        state = self.engine.tick(self.plan['run_id'], 'after-restart')
        self.assertEqual(state['tasks']['beta']['status'], 'done', state)
        self.assertEqual(self.calls[-1]['prior_result_search'], self.plan['tasks'][2]['prior_result_search'])
        with self.store.transaction() as db:
            rows = [json.loads(row[0]) for row in db.execute(
                "SELECT detail FROM journal WHERE kind='prior_result_search'")]
        observed = next(r['search'] for r in rows if r['task_id'] == 'beta')
        self.assertEqual(observed['scanned'], 1)
        self.assertEqual(len(self.case.host.requests), 1)

    def test_new_relevant_candidate_still_blocks_without_new_review(self):
        self.first_result()
        path = 'alpha/output.json'
        ResultStore(self.root).register_history('relevant', 'zqxbetatarget', [{
            'path': path, 'sha256': hashlib.sha256((self.root / path).read_bytes()).hexdigest()}])
        state = self.engine.tick(self.plan['run_id'], 'new-candidate')
        self.assertEqual(state['tasks']['beta']['status'], 'blocked')
        self.assertEqual([t['task_id'] for t in self.calls], ['alpha'])

    def test_new_incomplete_directory_still_blocks(self):
        self.first_result()
        (self.root / 'agent_doc/results/not-registered').mkdir()
        state = self.engine.tick(self.plan['run_id'], 'new-gap')
        self.assertEqual(state['tasks']['beta']['status'], 'blocked')
        self.assertEqual(len(self.calls), 1)

    def block_changed_search(self, change):
        self.first_result()
        current = ResultStore(self.root).search('zqxbetatarget')
        observed = dict(current, **change)
        with patch('agent_runtime.task_manifest._prior_result_search', return_value=observed) as lookup:
            state = self.engine.tick(self.plan['run_id'], 'negative')
        lookup.assert_called_once()
        self.assertEqual(state['tasks']['beta']['status'], 'blocked')
        self.assertEqual(len(self.calls), 1)
        with self.store.transaction() as db:
            rows = [json.loads(row[0]) for row in db.execute(
                "SELECT detail FROM journal WHERE kind='prior_result_search'")]
        self.assertEqual(next(r['search'] for r in rows if r['task_id'] == 'beta'), observed)

    def test_partial_still_blocks(self):
        self.block_changed_search({'partial': True})

    def test_unknown_field_still_blocks(self):
        self.block_changed_search({'unknown_adapter_field': 1})

    def test_boolean_scan_count_still_blocks(self):
        self.block_changed_search({'scanned': True})

    def test_negative_scan_count_still_blocks(self):
        self.block_changed_search({'scanned': -1})

    def test_classification_log_failure_prevents_producer_and_replay(self):
        self.first_result()
        original = Store.log
        def fail_log(store, db, run_id, now, kind, detail):
            if kind == 'prior_result_scan_only':
                raise OSError('classification journal unavailable')
            return original(store, db, run_id, now, kind, detail)
        with patch.object(Store, 'log', fail_log):
            state = self.engine.tick(self.plan['run_id'], 'journal-failure')
        self.assertEqual(state['tasks']['beta']['status'], 'blocked')
        self.assertIn('classification journal unavailable', state['tasks']['beta']['reason'])
        self.engine = self.restart()
        state = self.engine.tick(self.plan['run_id'], 'journal-restored')
        self.assertEqual(state['tasks']['beta']['status'], 'blocked')
        self.assertEqual([t['task_id'] for t in self.calls], ['alpha'])


class SearchComparisonTests(unittest.TestCase):
    def setUp(self):
        self.search = {'schema_version': 'project-result-search/v1', 'query': 'frozen query',
                       'status': 'no_hits', 'results': [], 'strategy': 'lexical', 'scanned': 0,
                       'partial': False, 'errors': [],
                       'authority': 'retrieval only; no applicability or acceptance proof'}
        self.hit = {'run_id': 'first', 'record_sha256': 'a' * 64, 'record_path': 'record.json',
                    'summary': 'candidate', 'origin': 'historical', 'score': 1,
                    'match': 'lexical', 'stored_validation': 'unknown', 'applicability': 'unchecked'}

    def test_count_only_in_both_directions_and_stable_candidates(self):
        for hits in ([], [self.hit]):
            old = dict(self.search, scanned=1, results=hits,
                       status='candidates' if hits else 'no_hits')
            new = dict(old, scanned=2)
            self.assertEqual(_prior_search_comparison(old, new), 'scan-only')
            self.assertEqual(_prior_search_comparison(new, old), 'scan-only')
            self.assertEqual(_prior_search_comparison(old, copy.deepcopy(old)), 'same')

    def test_changed_metadata_and_invalid_searches_are_not_scan_only(self):
        changes = [{'schema_version': 'project-result-search/v2'}, {'query': 'other'},
                   {'query': ''}, {'query': 'x' * 2001}, {'strategy': 'vector'},
                   {'status': 'candidates'}, {'partial': True}, {'partial': 0},
                   {'errors': ['incomplete']}, {'errors': ()}, {'authority': 'other'},
                   {'unknown': 1}, {'scanned': True}, {'scanned': 1.0}, {'scanned': -1},
                   {'scanned': 201}, {'results': ()}, {'results': [self.hit]},
                   {'scanned': float('nan')}, {'scanned': float('inf')}]
        for change in changes:
            with self.subTest(change=change):
                new = dict(self.search, scanned=1)
                new.update(change)
                self.assertIsNone(_prior_search_comparison(self.search, new))
        for key in self.search:
            new = dict(self.search, scanned=1)
            del new[key]
            with self.subTest(missing=key):
                self.assertIsNone(_prior_search_comparison(self.search, new))

    def test_candidate_changes_and_malformed_hits_are_rejected(self):
        old = dict(self.search, scanned=2, status='candidates',
                   results=[self.hit, dict(self.hit, run_id='second')])
        for field, value in [('record_sha256', 'b' * 64), ('score', 2), ('score', True),
                             ('score', 1.0), ('score', 0), ('record_sha256', 'Z' * 64),
                             ('match', 'other'), ('applicability', 'accepted'),
                             ('summary', ''), ('origin', 1), ('unknown', 1)]:
            new = copy.deepcopy(old)
            new['scanned'] = 3
            new['results'][0][field] = value
            with self.subTest(field=field, value=value):
                self.assertIsNone(_prior_search_comparison(old, new))
        for hits in (list(reversed(old['results'])), old['results'][:1], [self.hit] * 6):
            self.assertIsNone(_prior_search_comparison(old, dict(old, scanned=3, results=hits)))
        for key in self.hit:
            new = copy.deepcopy(old)
            new['scanned'] = 3
            del new['results'][0][key]
            with self.subTest(missing_hit=key):
                self.assertIsNone(_prior_search_comparison(old, new))

    def test_equal_but_incomplete_or_malformed_metadata_cannot_use_count_exception(self):
        invalid = [{'schema_version': 'future'}, {'strategy': 'vector'}, {'query': '   '},
                   {'query': ''}, {'query': 'x' * 2001}, {'partial': True}, {'partial': 0},
                   {'errors': ['gap']}, {'errors': ()}, {'authority': 'other'},
                   {'status': 'candidates'}, {'unknown': 1}, {'results': ()}]
        for change in invalid:
            old = dict(self.search, scanned=1)
            old.update(change)
            with self.subTest(change=change):
                self.assertIsNone(_prior_search_comparison(old, dict(old, scanned=2)))
        for change in ({'score': True}, {'score': 1.0}, {'score': 0}, {'summary': ''},
                       {'record_sha256': 'z' * 64}, {'match': 'other'}, {'unknown': 1}):
            old = dict(self.search, scanned=1, status='candidates', results=[dict(self.hit, **change)])
            with self.subTest(hit=change):
                self.assertIsNone(_prior_search_comparison(old, dict(old, scanned=2)))
        for old_count, new_count in ((True, False), (1.0, 2.0), (-1, -2), (201, 202)):
            with self.subTest(counts=(old_count, new_count)):
                self.assertIsNone(_prior_search_comparison(dict(self.search, scanned=old_count),
                                                           dict(self.search, scanned=new_count)))

    def test_identical_legacy_observations_keep_existing_exact_match_behavior(self):
        unknown = {'schema_version': 'future', 'unknown': True}
        self.assertEqual(_prior_search_comparison(unknown, copy.deepcopy(unknown)), 'same')
        self.assertIsNone(_prior_search_comparison(unknown, dict(unknown, unknown=1)))
        self.assertIsNone(_prior_search_comparison(dict(unknown, unknown=[]),
                                                   dict(unknown, unknown=())))
        self.assertIsNone(_prior_search_comparison(dict(unknown, unknown={'1': 'value'}),
                                                   dict(unknown, unknown={1: 'value'})))


if __name__ == '__main__':
    unittest.main()
