"""Post-experiment acceptance at a trusted host boundary, not a bug-free oracle.

Raw production is separate from usability. A host-owned verifier actually checks
code and observations; worker-authored pass files are never acceptance. Hashes
bind that review to exact inputs. They do not authenticate actors or prove the
scientific adequacy of a test. No command/import specified by JSON is executed.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat

from .core import Outcome

CHECKS = ('implementation', 'reference_boundary', 'data_integrity',
          'numerical_sanity', 'measurement_validity', 'reproducibility')
ARTIFACT_ROLES = ('code', 'inputs', 'config', 'raw_data', 'outputs', 'environment')
LIMIT = 16 * 1024 * 1024
REPAIR = ('preserve raw data; main AI diagnoses, repairs within authorization, '
          'creates a new result/run and versioned plan, reruns and independently revalidates')


class ResultValidationError(ValueError):
    pass


def canonical_sha256(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _need(condition, message):
    if not condition:
        raise ResultValidationError(message)


def _path(root, value):
    _need(_text(value), 'nonempty relative artifact path required')
    raw = Path(value)
    _need(not raw.is_absolute() and '..' not in raw.parts, 'artifact path outside project')
    path = root / raw
    for part in (path, *path.parents):
        if part == root:
            break
        _need(not part.is_symlink(), 'artifact path must not contain symlinks')
    _need(path.resolve().is_relative_to(root), 'artifact path outside project')
    return path


def _bytes(root, value):
    path = _path(root, value)
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_NOFOLLOW', 0))
    with os.fdopen(fd, 'rb') as stream:
        info = os.fstat(stream.fileno())
        _need(stat.S_ISREG(info.st_mode), 'artifact must be a regular file')
        _need(info.st_size <= LIMIT, 'artifact exceeds 16 MiB bound; use bounded shard manifests')
        data = stream.read(LIMIT + 1)
    _need(len(data) <= LIMIT, 'artifact grew beyond verification bound')
    return data


def _json(data):
    def reject(value):
        raise ResultValidationError('nonfinite JSON value: ' + value)
    def pairs(items):
        result = {}
        for key, value in items:
            _need(key not in result, 'duplicate JSON key: ' + key)
            result[key] = value
        return result
    result = json.loads(data, parse_constant=reject, object_pairs_hook=pairs)
    _need(isinstance(result, dict), 'JSON object required')
    return result


def _ref(value):
    _need(isinstance(value, dict) and _text(value.get('path')) and
          isinstance(value.get('sha256'), str) and
          re.fullmatch('[0-9a-f]{64}', value['sha256']), 'path/sha256 binding required')
    raw = Path(value['path'])
    _need(not raw.is_absolute() and '..' not in raw.parts, 'binding outside project')
    return value


def _bound(root, ref):
    _ref(ref)
    data = _bytes(root, ref['path'])
    _need(hashlib.sha256(data).hexdigest() == ref['sha256'], 'stale artifact: ' + ref['path'])
    return data


def validate_contract(contract):
    _need(isinstance(contract, dict), 'experiment result contract required')
    for field in ('result_id', 'producer_task_id', 'producer_actor', 'manifest_path', 'scope'):
        _need(_text(contract.get(field)), 'result contract requires ' + field)
    _ref(contract.get('validation_plan'))
    path = Path(contract['manifest_path'])
    _need(not path.is_absolute() and '..' not in path.parts, 'manifest outside project')
    return contract


def validate_result_plan(plan):
    """Require explicit producer -> independent gate -> all downstream consumers.

    This validates declared data dependencies, not natural-language intent. The
    main planner must classify experiments, including synthetic experiments.
    """
    tasks = plan.get('tasks', [])
    by_id = {t['task_id']: t for t in tasks}
    producers, gates = {}, {}
    for task in tasks:
        producer = task.get('experiment_result')
        gate = task.get('result_validation')
        if task.get('task_type') == 'experiment' or task.get('produces_data') is True:
            _need(producer is not None, 'experiment/data producer requires experiment_result')
        _need(not (producer is not None and gate is not None), 'producer cannot verify its own result')
        if producer is not None:
            validate_contract(producer)
            _need(producer['producer_task_id'] == task['task_id'] and
                  producer['producer_actor'] == task['owner'], 'producer identity mismatch')
            _need(producer['result_id'] not in producers, 'duplicate result identity')
            producers[producer['result_id']] = task
        if gate is not None:
            validate_contract(gate)
            _need(task['action'] == 'verify_experiment_result', 'result gate requires verify_experiment_result action')
            _need(gate['result_id'] not in gates, 'duplicate result verification gate')
            _need(task['owner'] != gate['producer_actor'], 'independent verification owner required')
            gates[gate['result_id']] = task
        elif task.get('action') == 'verify_experiment_result':
            raise ResultValidationError('verification action requires result_validation contract')
        refs = task.get('required_result_refs', [])
        _need(isinstance(refs, list), 'required_result_refs must be a list')
        seen = set()
        for ref in refs:
            validate_contract(ref)
            _need(ref['result_id'] not in seen, 'duplicate consumer result reference')
            seen.add(ref['result_id'])
    _need(set(producers) == set(gates), 'every experiment needs exactly one independent post-data gate')

    def ancestors(task_id, seen=None):
        seen = set() if seen is None else seen
        for dep in by_id[task_id].get('depends_on', []):
            _need(dep in by_id, 'unknown result dependency')
            if dep not in seen:
                seen.add(dep)
                ancestors(dep, seen)
        return seen

    for result_id, producer in producers.items():
        gate, contract = gates[result_id], producer['experiment_result']
        _need(gate['result_validation'] == contract, 'producer/gate contract mismatch')
        _need(producer['task_id'] in gate.get('depends_on', []), 'verification must follow data production')
        for task in tasks:
            upstream = ancestors(task['task_id'])
            refs = task.get('required_result_refs', [])
            relevant = [r for r in refs if r['result_id'] == result_id]
            if producer['task_id'] in upstream and task['task_id'] != gate['task_id']:
                _need(gate['task_id'] in upstream and relevant == [contract],
                      'data consumer must depend on verification and bind its result contract')
            if relevant:
                _need(relevant == [contract] and gate['task_id'] in upstream,
                      'consumer result reference lacks matching gate dependency')
    for task in tasks:
        _need(all(r['result_id'] in producers for r in task.get('required_result_refs', [])),
              'consumer references unknown experiment')
    return True


def _snapshot(root, contract):
    validate_contract(contract)
    plan_bytes = _bound(root, contract['validation_plan'])
    plan = _json(plan_bytes)
    _need(plan.get('schema_version') == 'experiment-validation-plan/v1' and
          plan.get('scope') == contract['scope'], 'validation plan schema/scope mismatch')
    criteria = plan.get('criteria')
    _need(isinstance(criteria, dict) and set(criteria) == set(CHECKS), 'complete contextual check criteria required')
    for name, criterion in criteria.items():
        _need(isinstance(criterion, dict) and _text(criterion.get('procedure')) and
              _text(criterion.get('acceptance')) and type(criterion.get('allow_not_applicable')) is bool,
              'explicit procedure, acceptance and applicability required: ' + name)
    raw = _bytes(root, contract['manifest_path'])
    manifest = _json(raw)
    _need(manifest.get('schema_version') == 'experiment-result/v1', 'experiment-result/v1 required')
    for field in ('result_id', 'producer_task_id', 'producer_actor', 'scope'):
        _need(manifest.get(field) == contract[field], 'result identity/scope mismatch: ' + field)
    _need(manifest.get('validation_plan') == contract['validation_plan'], 'result validation plan mismatch')
    for field in ('run_id', 'code_revision'):
        _need(_text(manifest.get(field)), 'result requires ' + field)
    run = manifest.get('execution')
    _need(isinstance(run, dict) and isinstance(run.get('command'), list) and run['command'] and
          all(_text(s) for s in run['command']) and _text(run.get('environment_description')) and
          type(run.get('repeats')) is int and run['repeats'] > 0 and
          isinstance(run.get('seeds'), list) and run['seeds'] and
          all(type(s) in (str, int) for s in run['seeds']), 'command/environment/repeats/seeds required')
    artifacts = manifest.get('artifacts')
    _need(isinstance(artifacts, dict) and set(artifacts) == set(ARTIFACT_ROLES), 'all artifact roles required')
    bindings = {contract['validation_plan']['path']: contract['validation_plan']['sha256']}
    for role in ARTIFACT_ROLES:
        refs = artifacts[role]
        _need(isinstance(refs, list) and bool(refs), 'nonempty artifact bindings required: ' + role)
        for ref in refs:
            _ref(ref)
            _need(ref['path'] != contract['manifest_path'], 'manifest cannot be its own evidence')
            _need(ref['path'] not in bindings or bindings[ref['path']] == ref['sha256'], 'contradictory artifact hash')
            _bound(root, ref)
            bindings[ref['path']] = ref['sha256']
    metrics = manifest.get('metrics')
    _need(isinstance(metrics, list) and metrics, 'nonempty named metrics with units required')
    names = set()
    for metric in metrics:
        _need(isinstance(metric, dict) and _text(metric.get('name')) and _text(metric.get('unit')),
              'metric name/unit required (use dimensionless explicitly)')
        value = metric.get('value')
        _need(type(value) in (int, float) and math.isfinite(value), 'metric must be finite numeric data')
        _need(metric['name'] not in names, 'duplicate metric name')
        names.add(metric['name'])
    proof = {'result_id': contract['result_id'], 'manifest_path': contract['manifest_path'],
             'manifest_sha256': hashlib.sha256(raw).hexdigest(), 'artifact_hashes': bindings,
             'validation_plan_sha256': contract['validation_plan']['sha256'], 'scope': contract['scope']}
    return manifest, plan, proof


def _review(root, manifest, plan, proof, review):
    _need(isinstance(review, dict), 'trusted verifier has not supplied an independent review')
    _need(review.get('schema_version') == 'experiment-validation/v1', 'review schema mismatch')
    for key in ('manifest_sha256', 'artifact_hashes', 'validation_plan_sha256', 'scope'):
        _need(review.get(key) == proof[key], 'review binding mismatch: ' + key)
    provenance = review.get('verifier')
    _need(isinstance(provenance, dict) and all(_text(provenance.get(k)) for k in
          ('actor', 'source', 'run_id', 'method')), 'observed independent verifier provenance required')
    _need(provenance['actor'] != manifest['producer_actor'] and provenance.get('independent') is True,
          'producer self-review cannot accept experiment')
    _need(isinstance(review.get('limitations'), list) and review['limitations'] and
          all(_text(x) for x in review['limitations']), 'explicit validation limits required; no bug-free guarantee')
    checks = review.get('checks')
    _need(isinstance(checks, dict) and set(checks) == set(CHECKS), 'all independent check domains required')
    statuses, evidence_bindings = [], {}
    for name in CHECKS:
        check = checks[name]
        _need(isinstance(check, dict) and _text(check.get('reason')), 'check reason required: ' + name)
        verdict = check.get('verdict')
        _need(verdict in ('pass', 'fail', 'inconclusive', 'not_applicable'), 'unknown check verdict: ' + name)
        if verdict == 'not_applicable':
            _need(plan['criteria'][name]['allow_not_applicable'], 'required check cannot be skipped: ' + name)
        refs = check.get('evidence')
        _need(isinstance(refs, list) and refs, 'independent evidence required: ' + name)
        for ref in refs:
            _bound(root, ref)
            _need(ref['path'] not in evidence_bindings or evidence_bindings[ref['path']] == ref['sha256'],
                  'contradictory review evidence')
            evidence_bindings[ref['path']] = ref['sha256']
        statuses.append(verdict)
    return statuses, evidence_bindings


def inspect_result(root, contract, verifier=None):
    """Read-only gate. Callback is host code, never data from a worker report.

    The callback must authenticate observed reviewer events, perform/retrieve the
    contextual independent checks and honor current host authorization. This
    module cannot authenticate a callback or stop a dishonest trusted host.
    """
    root = Path(root).resolve()
    base = {'status': 'pending', 'scope': contract.get('scope') if isinstance(contract, dict) else None,
            'errors': [], 'next_action': 'obtain independent post-data validation', 'proof': None}
    try:
        manifest, plan, proof = _snapshot(root, contract)
        base['proof'] = dict(proof, status='pending')
        if verifier is None:
            base['errors'] = ['trusted host verifier unavailable; worker pass JSON is not acceptance']
            return base
        _need(callable(verifier), 'verifier must be supplied by trusted host code')
        # Protect snapshot identity from accidental mutation by callback code.
        try:
            review = verifier(root, deepcopy(manifest), deepcopy(plan))
        except Exception as exc:
            base.update(errors=[f'trusted verifier unavailable or crashed: {type(exc).__name__}: {exc}'],
                        next_action='repair/retry the independent verifier; do not consume these results')
            return base
        if review is None:
            base['errors'] = ['independent review is pending']
            return base
        statuses, evidence = _review(root, manifest, plan, proof, review)
        _, _, after = _snapshot(root, contract)
        _need(after == proof, 'experiment changed during independent validation')
        for path, digest in evidence.items():
            _bound(root, {'path': path, 'sha256': digest})
        if 'fail' in statuses:
            base.update(status='invalid', errors=['independent check failed'], next_action=REPAIR)
        elif 'inconclusive' in statuses:
            base.update(errors=['independent evidence insufficient'], next_action=REPAIR)
        else:
            base.update(status='usable-with-scope', next_action='consume only within validated scope',
                        proof=dict(proof, status='usable-with-scope',
                                   review_sha256=canonical_sha256(review),
                                   review_evidence=evidence, verifier=review['verifier'],
                                   limitations=review['limitations']))
    except FileNotFoundError as exc:
        base.update(errors=['validation input missing: ' + str(exc)])
    except (OSError, ValueError, TypeError, KeyError, OverflowError, RecursionError) as exc:
        base.update(status='invalid', errors=[str(exc)], next_action=REPAIR)
    return base


def check_task_results(root, task, verifier=None, report=None):
    """Consumer/runtime hook; raw producers remain explicitly unaccepted.

    Returned proofs belong in the durable completion evidence. The host must
    supply its verifier again on resume/review, never recover trust from JSON.
    """
    if report is not None:
        data = report.get('data', [])
        if any(isinstance(d, dict) and d.get('kind') == 'measured' for d in data):
            _need(task.get('experiment_result') or task.get('result_validation') or task.get('required_result_refs'),
                  'measured result requires explicit experiment and independent validation contract')
    proofs = []
    producer = task.get('experiment_result')
    if producer is not None and report is not None:
        _, _, proof = _snapshot(Path(root).resolve(), producer)
        proofs.append(dict(proof, status='pending', limitations=['raw production only; not accepted data']))
    contracts = list(task.get('required_result_refs', []))
    if task.get('result_validation') is not None:
        contracts.append(task['result_validation'])
    for contract in contracts:
        result = inspect_result(root, contract, verifier)
        _need(result['status'] == 'usable-with-scope',
              f"experiment result {result['status']}: {'; '.join(result['errors'])}; {result['next_action']}")
        proofs.append(result['proof'])
    return proofs


class ResultValidationHandler:
    """Explicit trusted-handler entry; authorization still belongs to the host."""
    idempotent = True
    required_capabilities = frozenset({'read_artifacts', 'independent_result_validation'})

    def __init__(self, root, verifier=None):
        self.root, self.verifier = Path(root).resolve(), verifier

    def run(self, task, context):
        result = inspect_result(self.root, task.get('result_validation'), self.verifier)
        if result['status'] == 'usable-with-scope':
            return Outcome('complete', 'scoped independent acceptance; not a bug-free proof', [result['proof']])
        return Outcome('failed' if result['status'] == 'invalid' else 'pending',
                       '; '.join(result['errors']) + '; ' + result['next_action'])

    def verify(self, task, evidence):
        result = inspect_result(self.root, task.get('result_validation'), self.verifier)
        return result['status'] == 'usable-with-scope' and evidence == [result['proof']]
