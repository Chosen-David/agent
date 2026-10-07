# Legacy fixture: exercises pre-dual-main invariants; independent review is tested separately.
"""Real files + independent arithmetic checks; no model/GPU/performance claim."""
import copy
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest

from agent_runtime.core import ArtifactHandler, Engine, Store
from agent_runtime.task_manifest import ReportingHandler, atomic_json, prepare, review, validate_contract
from agent_runtime.result_validation import (ARTIFACT_ROLES, CHECKS, ResultValidationHandler,
    canonical_sha256, check_task_results, inspect_result, validate_result_plan)


def save(root, path, value):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    return ref(root, path)


def ref(root, path):
    return {'path': path, 'sha256': hashlib.sha256((root / path).read_bytes()).hexdigest()}


def make_fixture(root):
    """Produce bounded CPU integer data; returns a controller-owned contract."""
    root.mkdir(parents=True, exist_ok=True)
    source = ('def measure(n):\n'
              '    if type(n) is not int or n < 0: raise ValueError("nonnegative integer required")\n'
              '    return sum(i*i for i in range(n))\n'
              '\nif __name__ == "__main__":\n'
              '    import json\n'
              '    from pathlib import Path\n'
              '    inputs = json.loads(Path("inputs.json").read_text())["n"]\n'
              '    config = json.loads(Path("config.json").read_text())\n'
              '    raw = [{"n": n, "repeat": r, "value": measure(n)} for r in range(config["repeats"]) for n in inputs]\n'
              '    Path("raw.json").write_text(json.dumps({"samples": raw}, indent=2) + "\\n")\n'
              '    Path("output.json").write_text(json.dumps({"sum": sum(x["value"] for x in raw)}, indent=2) + "\\n")\n')
    (root / 'code.py').write_text(source)
    inputs = [0, 1, 2, 7, 19]
    save(root, 'inputs.json', {'n': inputs})
    save(root, 'config.json', {'repeats': 3, 'seeds': [0], 'unit': 'dimensionless'})
    subprocess.run([sys.executable, 'code.py'], cwd=root, check=True, capture_output=True, timeout=10)
    raw = json.loads((root / 'raw.json').read_text())['samples']
    save(root, 'environment.json', {'python': sys.version, 'device': 'CPU', 'timed': False})
    scope = 'Exact integer square sums for frozen CPU synthetic cases; no performance claim'
    criteria = {name: {'procedure': 'independent fixture check for ' + name,
                       'acceptance': 'exact equality and complete frozen sample IDs',
                       'allow_not_applicable': name == 'measurement_validity'} for name in CHECKS}
    criteria['implementation']['acceptance'] = 'read implementation and test negative/type boundaries'
    criteria['measurement_validity']['acceptance'] = 'no time/speed claims; timing N/A must be explicit'
    protocol = save(root, 'validation-plan.json', {'schema_version': 'experiment-validation-plan/v1',
                    'scope': scope, 'criteria': criteria})
    contract = {'result_id': 'cpu-result-1', 'producer_task_id': 'produce',
                'producer_actor': 'implementation-agent', 'manifest_path': 'manifest.json',
                'validation_plan': protocol, 'scope': scope}
    manifest = {**{k: contract[k] for k in ('result_id', 'producer_task_id', 'producer_actor', 'scope')},
                'schema_version': 'experiment-result/v1', 'validation_plan': protocol,
                'run_id': 'cpu-run-1', 'code_revision': 'fixture-v1+file-sha256',
                'execution': {'command': [sys.executable, 'code.py'], 'exit_code': 0, 'seeds': [0], 'repeats': 3,
                              'environment_description': 'local CPU synthetic integer fixture'},
                'artifacts': {role: [ref(root, path)] for role, path in zip(ARTIFACT_ROLES,
                             ('code.py', 'inputs.json', 'config.json', 'raw.json', 'output.json', 'environment.json'))},
                'metrics': [{'name': 'sum', 'value': sum(x['value'] for x in raw), 'unit': 'dimensionless'}]}
    save(root, contract['manifest_path'], manifest)
    save(root, 'contract.json', contract)
    return contract


def independent_verify(root, manifest, plan):
    """Trusted TEST adapter actually recomputes values with a distinct formula.

    runpy is confined to the test fixture's source; production verifier code must
    separately authorize any code execution. Runtime never executes this string.
    """
    inputs = json.loads((root / 'inputs.json').read_text())['n']
    config = json.loads((root / 'config.json').read_text())
    raw = json.loads((root / 'raw.json').read_text())['samples']
    output = json.loads((root / 'output.json').read_text())
    fn = runpy.run_path(str(root / 'code.py'))['measure']
    formula = lambda n: n * (n - 1) * (2*n - 1) // 6
    boundaries = all(fn(n) == formula(n) for n in (0, 1, 2, 17, 64))
    rejects = []
    for bad in (-1, 1.5, '2', True):
        try:
            fn(bad)
        except ValueError:
            rejects.append(bad)
        except Exception:
            pass  # Wrong exception semantics fails the boundary check.
    implementation = boundaries and len(rejects) == 4
    expected_ids = {(n, r) for n in inputs for r in range(config['repeats'])}
    actual_ids = [(row['n'], row['repeat']) for row in raw]
    integrity = len(actual_ids) == len(set(actual_ids)) and set(actual_ids) == expected_ids
    numerical = all(type(row['value']) is int and row['value'] == formula(row['n']) for row in raw)
    total = sum(formula(n) for n in inputs) * config['repeats']
    numerical = numerical and output['sum'] == total and manifest['metrics'][0]['value'] == total
    hashes = {r['path']: r['sha256'] for refs in manifest['artifacts'].values() for r in refs}
    hashes[manifest['validation_plan']['path']] = manifest['validation_plan']['sha256']
    verdicts = {'implementation': implementation, 'reference_boundary': boundaries,
                'data_integrity': integrity, 'numerical_sanity': numerical,
                'reproducibility': numerical and all(fn(n) == formula(n) for n in inputs)}
    checks = {name: {'verdict': 'pass' if verdicts.get(name) else 'fail',
                     'reason': 'Independent formula, boundary and sample-ID recomputation',
                     'evidence': [ref(root, 'raw.json'), ref(root, 'code.py'), ref(root, 'output.json')]}
              for name in CHECKS}
    checks['measurement_validity'] = {'verdict': 'not_applicable',
              'reason': 'These are exact integer observations, no timing or performance measurement or claim',
              'evidence': [ref(root, 'environment.json')]}
    return {'schema_version': 'experiment-validation/v1', 'manifest_sha256': ref(root, 'manifest.json')['sha256'],
            'artifact_hashes': hashes, 'validation_plan_sha256': manifest['validation_plan']['sha256'],
            'scope': manifest['scope'], 'verifier': {'actor': 'independent-test-controller', 'independent': True,
            'source': 'unit-test host executed closed-form and boundary checks', 'run_id': 'review-1',
            'method': 'independent integer formula, IDs, boundaries and re-execution'},
            'checks': checks, 'limitations': ['finite synthetic CPU cases only; not a proof of bug-free code']}


def dag(contract):
    common = {'task_refs': ['REQ'], 'max_attempts': 2, 'estimated_seconds': 1, 'risk': 'low',
              'done_when': {'independent': True}}
    return {'schema_version': 'task-dag/v1', 'run_id': 'test', 'user_goal': 'test validation',
            'authorization_reference': 'test host',
            'supervision': {'min_seconds': 1, 'max_seconds': 3, 'rationale': 'bounded test'},
            'tasks': [{**common, 'task_id': 'produce', 'owner': 'implementation-agent',
                       'action': 'produce_fixture', 'depends_on': [], 'experiment_result': contract},
                      {**common, 'task_id': 'verify', 'owner': 'independent-reviewer',
                       'action': 'verify_experiment_result', 'depends_on': ['produce'], 'result_validation': contract},
                      {**common, 'task_id': 'consume', 'owner': 'writer', 'action': 'consume_fixture',
                       'depends_on': ['verify'], 'required_result_refs': [contract]}]}


class ResultValidationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.contract = make_fixture(self.root)

    def result(self, verifier=independent_verify):
        return inspect_result(self.root, self.contract, verifier)

    def rewrite_manifest(self, mutate):
        value = json.loads((self.root / 'manifest.json').read_text())
        mutate(value)
        save(self.root, 'manifest.json', value)

    def test_actual_independent_recomputation_accepts_scoped_data(self):
        result = self.result()
        self.assertEqual(result['status'], 'usable-with-scope', result)
        self.assertIn('not a proof', result['proof']['limitations'][0])
        self.assertTrue(validate_result_plan(dag(self.contract)))
        proof = check_task_results(self.root, dag(self.contract)['tasks'][2], independent_verify)
        self.assertEqual(proof, [result['proof']])

    def test_missing_verifier_and_forged_worker_pass_remain_pending(self):
        self.rewrite_manifest(lambda m: m.update(status='passed', independent=True, reviewer='other-agent'))
        self.assertEqual(self.result(None)['status'], 'pending')
        self.assertEqual(self.result(lambda *_: None)['status'], 'pending')

    def test_producer_is_raw_pending_not_usable(self):
        task = dag(self.contract)['tasks'][0]
        result = check_task_results(self.root, task, report={'data': [{'kind': 'measured'}]})
        self.assertEqual(result[0]['status'], 'pending')
        with self.assertRaisesRegex(ValueError, 'contract'):
            check_task_results(self.root, {}, report={'data': [{'kind': 'measured'}]})

    def test_all_code_data_config_and_output_changes_invalidate(self):
        for role in ARTIFACT_ROLES:
            with self.subTest(role=role):
                make_fixture(self.root)
                manifest = json.loads((self.root / 'manifest.json').read_text())
                path = self.root / manifest['artifacts'][role][0]['path']
                path.write_bytes(path.read_bytes() + b' ')
                self.assertEqual(self.result()['status'], 'invalid')

    def test_fresh_hashes_do_not_hide_wrong_numerical_data(self):
        raw = json.loads((self.root / 'raw.json').read_text())
        raw['samples'][2]['value'] += 1
        save(self.root, 'raw.json', raw)
        self.rewrite_manifest(lambda m: m['artifacts'].update(raw_data=[ref(self.root, 'raw.json')]))
        result = self.result()
        self.assertEqual(result['status'], 'invalid')
        self.assertIn('repairs', result['next_action'])
        self.assertEqual(json.loads((self.root / 'raw.json').read_text()), raw)

    def test_duplicate_and_missing_samples_fail_independent_checks(self):
        raw = json.loads((self.root / 'raw.json').read_text())
        raw['samples'][0] = raw['samples'][1]
        save(self.root, 'raw.json', raw)
        self.rewrite_manifest(lambda m: m['artifacts'].update(raw_data=[ref(self.root, 'raw.json')]))
        self.assertEqual(self.result()['status'], 'invalid')

    def test_code_bug_caught_even_when_new_fingerprint_is_honest(self):
        (self.root / 'code.py').write_text('def measure(n):\n    return sum(i*i for i in range(n))\n')
        self.rewrite_manifest(lambda m: m['artifacts'].update(code=[ref(self.root, 'code.py')]))
        result = self.result()
        # Callback errors are a closed gate as well as a failed assertion.
        self.assertEqual(result['status'], 'invalid')

    def test_nonfinite_duplicate_keys_and_unit_omission_rejected(self):
        for mutation in ('nan', 'duplicate', 'unit'):
            with self.subTest(mutation=mutation):
                make_fixture(self.root)
                if mutation == 'nan':
                    text = (self.root / 'manifest.json').read_text().replace('"value": 21645', '"value": NaN')
                    # Use a direct deterministic substitution independent of fixture sum.
                    value = json.loads(text)
                    value['metrics'][0]['value'] = float('nan')
                    (self.root / 'manifest.json').write_text(json.dumps(value))
                elif mutation == 'duplicate':
                    text = (self.root / 'manifest.json').read_text()
                    (self.root / 'manifest.json').write_text(text.replace('{', '{"run_id":"forged",', 1))
                else:
                    self.rewrite_manifest(lambda m: m['metrics'][0].pop('unit'))
                self.assertEqual(self.result()['status'], 'invalid')

    def test_self_review_missing_checks_wrong_scope_and_illicit_na_rejected(self):
        mutations = [lambda r: r['verifier'].update(actor='implementation-agent'),
                     lambda r: r['checks'].pop('reference_boundary'),
                     lambda r: r.update(scope='all inputs are bug-free'),
                     lambda r: r['checks']['numerical_sanity'].update(verdict='not_applicable'),
                     lambda r: r['checks']['implementation'].update(evidence=[])]
        for mutate in mutations:
            def verifier(root, manifest, plan):
                review = independent_verify(root, manifest, plan)
                mutate(review)
                return review
            with self.subTest(mutation=mutate):
                self.assertEqual(self.result(verifier)['status'], 'invalid')

    def test_inconclusive_is_pending_never_usable(self):
        def verifier(*args):
            result = independent_verify(*args)
            result['checks']['numerical_sanity']['verdict'] = 'inconclusive'
            return result
        self.assertEqual(self.result(verifier)['status'], 'pending')

    def test_crashed_verifier_is_retriable_pending_not_an_uncaught_exception(self):
        def verifier(*_):
            raise RuntimeError('independent provider unavailable')
        result = self.result(verifier)
        self.assertEqual(result['status'], 'pending')
        self.assertIn('RuntimeError', result['errors'][0])
        self.assertIn('retry', result['next_action'])

    def test_mutation_during_callback_fails(self):
        def verifier(*args):
            result = independent_verify(*args)
            (self.root / 'code.py').write_text('# changed after review\n')
            return result
        self.assertEqual(self.result(verifier)['status'], 'invalid')

    def test_escaped_symlink_and_nonregular_evidence_rejected(self):
        self.rewrite_manifest(lambda m: m['artifacts']['code'][0].update(path='../escape.py'))
        self.assertEqual(self.result()['status'], 'invalid')
        make_fixture(self.root)
        (self.root / 'alias.py').symlink_to(self.root / 'code.py')
        self.rewrite_manifest(lambda m: m['artifacts']['code'][0].update(path='alias.py'))
        self.assertEqual(self.result()['status'], 'invalid')
        if hasattr(os, 'mkfifo'):
            make_fixture(self.root)
            (self.root / 'code.py').unlink()
            os.mkfifo(self.root / 'code.py')
            self.assertEqual(self.result()['status'], 'invalid')

    def test_plan_cannot_omit_gate_or_bypass_it_with_changed_flags(self):
        mutations = [lambda p: p['tasks'].pop(1),
                     lambda p: p['tasks'][2].update(depends_on=['produce']),
                     lambda p: p['tasks'][2].pop('required_result_refs'),
                     lambda p: p['tasks'][1].update(owner='implementation-agent'),
                     lambda p: p['tasks'][0].pop('experiment_result'),
                     lambda p: p['tasks'][0].update(produces_data=True, experiment_result=None)]
        for mutate in mutations:
            plan = dag(self.contract)
            mutate(plan)
            with self.subTest(mutation=mutate), self.assertRaises(ValueError):
                validate_result_plan(plan)
        task = dag(self.contract)['tasks'][2]
        task['produces_data'] = False
        with self.assertRaisesRegex(ValueError, 'pending'):
            check_task_results(self.root, task, report={'data': [{'kind': 'not_applicable'}]})

    def test_handler_real_engine_and_stale_evidence_after_restart(self):
        task = dag(self.contract)['tasks'][1]
        task['depends_on'] = []
        plan = dag(self.contract)
        plan['tasks'] = [task]
        store = Store(self.root / 'state.sqlite')
        store.create(plan)
        handler = ResultValidationHandler(self.root, independent_verify)
        engine = Engine(store, {'verify_experiment_result': handler}, authorize=lambda *_: True, allow_legacy=True)
        state = engine.tick('test', 'event-1')
        self.assertEqual(state['tasks']['verify']['status'], 'done')
        node = Store(self.root / 'state.sqlite').snapshot('test')['state']['tasks']['verify']
        self.assertTrue(handler.verify(task, node['evidence']))
        (self.root / 'raw.json').write_text('{}')
        self.assertFalse(handler.verify(task, node['evidence']))
        # Engine tick terminal shortcut is not acceptance: its explicit fresh
        # completion/recovery path uses this same independent verify method.
        with store.transaction() as db:
            plan, state = store.load(db, 'test')
            engine._check_done(plan, state)
            self.assertEqual(state['tasks']['verify']['status'], 'failed')

    def integrated_chain(self, verifier=independent_verify):
        (self.root / 'TASK.md').write_text('- [ ] [REQ] Validate measured fixture before conclusions\n')
        plan = prepare(self.root / 'TASK.md', 'integrated', 'auto', 'test host instruction', review_required=False)
        template = plan['tasks'][0]
        plan['tasks'] = dag(self.contract)['tasks']
        for task in plan['tasks']:
            task.update(document_refs=template['document_refs'],
                        report_path='reports/' + task['task_id'] + '.json', outputs=[])
            if task['task_id'] != 'verify':
                task['action'] = 'verify_artifacts'
                task['done_when'] = {'artifacts': [ref(self.root, 'output.json')]}
            atomic_json(self.root / task['report_path'], {'task_id': task['task_id'],
                        'summary': 'bounded fixture stage',
                        'data': [{'kind': 'measured' if task['task_id'] == 'produce' else 'derived',
                                  'description': 'integer fixture; scientific scope stays bounded'}]})
        validate_contract(plan, self.root)
        store = Store(self.root / 'integrated.sqlite')
        store.create(plan)
        handlers = {'verify_artifacts': ReportingHandler(ArtifactHandler(self.root), self.root,
                                                          result_verifier=verifier),
                    'verify_experiment_result': ReportingHandler(ResultValidationHandler(self.root, verifier),
                                                                 self.root, result_verifier=verifier)}
        engine = Engine(store, handlers, authorize=lambda *_: True, allow_legacy=True)
        return plan, store, engine, handlers

    def test_actual_reporting_runtime_producer_gate_consumer_and_live_review(self):
        plan, store, engine, handlers = self.integrated_chain()
        for number in range(3):
            engine.tick('integrated', 'stage-' + str(number))
        snapshot = store.snapshot('integrated')
        self.assertEqual(snapshot['state']['status'], 'done')
        producer = snapshot['state']['tasks']['produce']['evidence'][-1]['task_report']['result_validation'][0]
        self.assertEqual(producer['status'], 'pending')
        self.assertTrue(review(snapshot, self.root, result_verifier=independent_verify, allow_legacy=True)['all_reportable'])
        self.assertFalse(review(snapshot, self.root, allow_legacy=True)['all_reportable'])
        (self.root / 'config.json').write_text('{}')
        self.assertFalse(review(snapshot, self.root, result_verifier=independent_verify, allow_legacy=True)['all_reportable'])
        self.assertFalse(handlers['verify_artifacts'].verify(plan['tasks'][2],
                         snapshot['state']['tasks']['consume']['evidence']))

    def test_actual_reporting_runtime_blocks_gate_and_consumer_without_verifier(self):
        plan, store, engine, handlers = self.integrated_chain(None)
        engine.tick('integrated', 'producer')
        state = engine.tick('integrated', 'gate')
        self.assertEqual(state['tasks']['produce']['status'], 'done')
        self.assertEqual(state['tasks']['verify']['status'], 'blocked')
        self.assertNotEqual(state['tasks']['consume']['status'], 'done')
        # Direct wrapper invocation cannot launder an accepted-looking report,
        # or bypass with producer-controlled false/synthetic flags.
        consumer = plan['tasks'][2]
        consumer['produces_data'] = False
        outcome = handlers['verify_artifacts'].run(consumer, None)
        self.assertEqual(outcome.status, 'blocked')

    def test_cli_without_trusted_adapter_does_not_accept_pass_json(self):
        script = Path(__file__).resolve().parents[1] / 'scripts/validate_experiment_result.py'
        run = subprocess.run([sys.executable, str(script), '--root', str(self.root),
                              '--contract', str(self.root / 'contract.json')], capture_output=True, text=True)
        self.assertEqual(run.returncode, 2, run.stderr)
        self.assertEqual(json.loads(run.stdout)['status'], 'pending')


if __name__ == '__main__':
    unittest.main()
