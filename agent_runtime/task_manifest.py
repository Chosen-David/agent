"""TASK.md coverage and evidence reports for the managed supervisor.

TASK.md describes requirements, never executable commands or permissions.
The main AI supplies actions, dependencies and independent acceptance handlers.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

from .core import Outcome, validate
from .project_memory import check_task_memory
from .knowledge import check_task_knowledge
from .result_validation import check_task_results, validate_result_plan
from .result_store import ResultStore, check_task_reuse, register_task_result
from .project_docs import (CANONICAL_TASK, assert_ai_writable, check_document_refs,
                           check_task_documents, guard_write_path, parse_requirements,
                           project_root_for_task, resolve_task_file, snapshot_project_docs,
                           task_document_refs, validate_advice_assessments, validate_guide_reviews)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_json(path, value):
    path = guard_write_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=path.name + '.')
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        guard_write_path(path)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def requirements(path):
    """Read stable IDs; canonical index additionally binds dates and details."""
    path = Path(path)
    return parse_requirements(path.read_text(encoding='utf-8'),
                              canonical=path.parts[-3:] == ('agent_doc', 'task', 'TASK.md'))



def _prior_result_search(store, query):
    """A failed lookup is unknown, never a claimed absence of earlier work."""
    try:
        return store.search(query)
    except (OSError, ValueError) as exc:
        return {'schema_version': 'project-result-search/v1', 'query': query,
                'status': 'unavailable', 'results': [], 'scanned': 0, 'partial': True,
                'errors': [{'error': str(exc)}], 'authority': 'lookup failed; no absence or reuse claim'}


def _review_prior_candidates(task, search):
    """Rationale is required before repeating data work; it is not acceptance."""
    producer = (task.get('experiment_result') is not None or task.get('produces_data') is True
                or task.get('task_type') == 'experiment')
    if not producer or not (search['results'] or search['partial'] or search['errors']):
        return
    assessment = task.get('prior_result_review')
    if (not isinstance(assessment, dict) or assessment.get('decision') not in ('rerun', 'verify_delta', 'reuse')
            or not isinstance(assessment.get('reason'), str) or not assessment['reason'].strip()
            or not isinstance(assessment.get('record_refs'), list)):
        raise ValueError('prior-result candidates/lookup gaps require an explicit planner review before data production')
    supplied = []
    for ref in assessment['record_refs']:
        if not isinstance(ref, dict) or not all(isinstance(ref.get(k), str) and ref[k]
                                               for k in ('run_id', 'record_sha256')):
            raise ValueError('prior-result review requires pinned record_refs')
        supplied.append((ref['run_id'], ref['record_sha256']))
    expected = {(hit['run_id'], hit['record_sha256']) for hit in search['results']}
    if len(set(supplied)) != len(supplied) or set(supplied) != expected:
        raise ValueError('prior-result review does not cover current lookup candidates; re-evaluate')
    if assessment['decision'] == 'reuse' and task['action'] != 'reuse_validated_result':
        raise ValueError('reuse decision requires explicit verified reuse action; do not rerun producer silently')

def prepare(task_file, run_id, mode, authorization_reference, *, review_required=True, lineage_id=None):
    task_file = Path(task_file)
    root = task_file.resolve() if task_file.is_dir() else project_root_for_task(task_file)
    task_file = resolve_task_file(root)
    items = requirements(task_file)
    documents = snapshot_project_docs(root)
    result_store = ResultStore(root)
    return {
        'schema_version': 'task-dag/v1', 'run_id': run_id,
        **({'plan_review': {'schema_version': 'main-plan-review/v1',
                            'lineage_id': lineage_id or 'requirements:' + hashlib.sha256(
                                ('\0'.join(sorted(item['id'] for item in items))).encode()).hexdigest(),
                            'evidence_refs': []}} if review_required else {}),
        'user_goal': 'Complete all TASK.md requirements with reportable evidence',
        'authorization_reference': authorization_reference,
        'task_source': {'path': str(task_file), 'sha256': digest(task_file), 'mode': mode},
        'project_documents': documents, 'guide_reviews': [], 'advice_assessments': [],
        'supervision': {'min_seconds': 30, 'max_seconds': 300,
                        'rationale': 'Main AI must refine ETA, risk and cadence before starting'},
        'tasks': [{'task_id': item['id'], 'task_refs': [item['id']], 'owner': 'main-ai',
                   'action': 'configure_host_action', 'depends_on': [], 'risk': 'low',
                   'document_refs': task_document_refs(documents, [item['id']]),
                   'prior_result_search': _prior_result_search(result_store, item['title']),
                   **({'result_storage': 'central'} if documents['layout'] == 'canonical' else {}),
                   'estimated_seconds': 120, 'max_attempts': 3, 'inputs': {'goal': item['title']},
                   'wait_policy': {'max_polls': 120, 'max_seconds': 3600,
                                   'diagnose_after_seconds': 300},
                   'outputs': [], 'done_when': {'configure_acceptance': True},
                   'report_path': f'.agent-runs/{hashlib.sha256(run_id.encode()).hexdigest()[:16]}/results/{item["id"]}.json'}
                  for item in items],
    }


def validate_contract(plan, root, *, check_adopted_advice=True, required_task_refs=None):
    validate(plan)
    validate_result_plan(plan)
    root = Path(root).resolve()
    source = plan['task_source']
    if source['mode'] not in ('auto', 'manual'):
        raise ValueError('task source mode must be auto or manual')
    path = (root / source['path']).resolve()
    if path != resolve_task_file(root):
        raise ValueError('the single task source must be agent_doc/task/TASK.md (legacy project-root TASK.md only before migration)')
    if not path.is_relative_to(root) or digest(path) != source['sha256']:
        raise ValueError('TASK.md missing, changed or outside project; reconcile and version the plan')
    items = requirements(path)
    documents = plan.get('project_documents')
    if documents is None:
        # Legacy serialized runs may only resume without new guide/advice inputs.
        current = snapshot_project_docs(root)
        if current['layout'] != 'legacy' or current['guides'] or current['advice']:
            raise ValueError('project document binding missing; explicitly replan legacy run')
    else:
        binding = documents if check_adopted_advice else {**documents, 'adopted_advice': {}}
        current = check_document_refs(root, binding)
        if set(documents['task_details']) != set(current['task_details']):
            raise ValueError('plan omits task detail planning dependencies')
        task_ids = {item['id'] for item in items}
        validate_guide_reviews(documents, plan.get('guide_reviews'), task_ids)
        adopted = validate_advice_assessments(documents, plan.get('advice_assessments'), task_ids)
        if adopted != documents.get('adopted_advice'):
            raise ValueError('adopted advice dependencies missing; bind assessed advice to draft')
    ids, covered = {item['id'] for item in items}, set()
    if required_task_refs is not None:
        if (not isinstance(required_task_refs, (list, tuple, set, frozenset)) or not required_task_refs
                or any(not isinstance(r, str) or r not in ids for r in required_task_refs)
                or len(set(required_task_refs)) != len(required_task_refs)):
            raise ValueError('trusted required_task_refs must name exact existing requirements')
        ids = set(required_task_refs)
    report_paths = set()
    for task in plan['tasks']:
        if (documents is not None and documents['layout'] == 'canonical' and
                task.get('experiment_result') is not None):
            contract_path = Path(task['experiment_result']['manifest_path'])
            if (task.get('result_storage') != 'central' or contract_path.is_absolute()
                    or '..' in contract_path.parts or contract_path.parts[:2] != ('agent_doc', 'results')):
                raise ValueError('new canonical data producers require central agent_doc/results/<run_id> storage')
        refs = task.get('task_refs')
        if not isinstance(refs, list) or not refs or not all(isinstance(r, str) and r in ids for r in refs):
            raise ValueError('each runtime task must map to known TASK.md IDs')
        covered.update(refs)
        if documents is not None and task.get('document_refs') != task_document_refs(
                documents, refs, plan['advice_assessments'], plan['guide_reviews']):
            raise ValueError('task document dependencies do not match current requirement/advice scope')
        assert_ai_writable(root, task['report_path'])
        for output in task.get('outputs', []):
            output_path = output if isinstance(output, str) else output.get('path') if isinstance(output, dict) else None
            if output_path:
                assert_ai_writable(root, output_path)
        report = (root / task['report_path']).resolve()
        if (not report.is_relative_to(root) or report in report_paths or report == path
                or report.is_relative_to(root / 'agent_doc/task')):
            raise ValueError('unique result report paths inside project required')
        report_paths.add(report)
    if covered != ids:
        raise ValueError('plan omits TASK.md requirements: ' + ', '.join(sorted(ids - covered)))
    return [item for item in items if item['id'] in ids]


def result_report(root, task, result_verifier=None):
    check_task_documents(root, task)
    check_task_memory(root, task)
    check_task_knowledge(root, task)
    path = (Path(root).resolve() / task['report_path']).resolve()
    if not path.is_relative_to(Path(root).resolve()):
        raise ValueError('result report outside project')
    # Reuse bounded, regular-file validation before parsing the exact bytes.
    # A report digest is a consistency binding, not independent scientific proof.
    flags = os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_NOFOLLOW', 0)
    import stat
    fd = os.open(path, flags)
    with os.fdopen(fd, 'rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError('result report must be a regular file')
        data = stream.read(1024 * 1024 + 1)
    if len(data) > 1024 * 1024:
        raise ValueError('result report exceeds 1 MiB')
    value = json.loads(data)
    if (value.get('task_id') != task['task_id'] or not isinstance(value.get('summary'), str)
            or not value['summary'].strip() or not isinstance(value.get('data'), list)
            or not value['data']):
        raise ValueError('report requires task_id, summary and nonempty data')
    for item in value['data']:
        if (not isinstance(item, dict) or item.get('kind') not in
                ('measured', 'derived', 'synthetic', 'not_applicable')
                or not isinstance(item.get('description'), str) or not item['description'].strip()):
            raise ValueError('each datum needs kind and description; distinguish measured/synthetic/N/A')
    result_proofs = check_task_results(root, task, result_verifier, report=value)
    reuse_proofs = check_task_reuse(root, task, result_verifier)
    check_task_documents(root, task)
    check_task_memory(root, task)
    check_task_knowledge(root, task)
    proof = {'path': task['report_path'], 'sha256': hashlib.sha256(data).hexdigest()}
    if result_proofs:
        proof['result_validation'] = result_proofs
    if reuse_proofs:
        proof['prior_result_reuse'] = reuse_proofs
    return value, proof


class ReportingHandler:
    """Completion requires both independent acceptance and a bound result report."""
    def __init__(self, handler, root, result_verifier=None):
        self.handler, self.root = handler, root
        self.result_verifier = result_verifier
        self._prior_searches = {}
        self.idempotent = handler.idempotent
        self.required_capabilities = handler.required_capabilities

    def run(self, task, context):
        try:
            check_task_documents(self.root, task)
            check_task_memory(self.root, task)
            check_task_knowledge(self.root, task)
            check_task_results(self.root, task, self.result_verifier)
            check_task_reuse(self.root, task, self.result_verifier)
            check_task_documents(self.root, task)
        except (OSError, ValueError) as exc:
            return Outcome('blocked', f'project documents/memory/knowledge/results reconciliation required: {exc}')
        # A real lookup precedes first dispatch (and repeats after restart), not
        # just drafts from prepare. Never read a persisted hit as authorization.
        search_key = getattr(context, 'idempotency_key', None) or hashlib.sha256(
            json.dumps(task, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        if search_key not in self._prior_searches:
            inputs, contract = task.get('inputs'), task.get('experiment_result')
            query = inputs.get('goal') if isinstance(inputs, dict) else None
            if not isinstance(query, str) or not query.strip():
                query = contract.get('scope') if isinstance(contract, dict) else None
            if not isinstance(query, str) or not query.strip():
                query = task['task_id']
            search = _prior_result_search(ResultStore(self.root), query)
            if context is not None and all(hasattr(context, key) for key in ('store', 'run_id', 'clock')):
                with context.store.transaction() as db:
                    context.store.log(db, context.run_id, context.clock(), 'prior_result_search',
                                      {'task_id': task['task_id'], 'search': search})
            self._prior_searches[search_key] = search
        try:
            _review_prior_candidates(task, self._prior_searches[search_key])
            check_task_documents(self.root, task)
        except (OSError, ValueError) as exc:
            return Outcome('blocked', f'prior-result planning review required: {exc}')
        dispatched_task = copy.deepcopy(task)
        protected = False
        if context is not None and hasattr(context, 'store'):
            try:
                protected = context.store.snapshot(context.run_id)['plan'].get('plan_review') is not None
            except KeyError:
                # Direct legacy wrapper use can log lookups without a managed DAG.
                # Engine always registers and gates a real plan before execution.
                protected = False
        if protected:
            # Do not replace a reviewed adapter input with unreviewed observations.
            producer = (task.get('experiment_result') is not None or task.get('produces_data') is True
                        or task.get('task_type') == 'experiment' or task.get('result_reuse') is not None)
            if producer and task.get('prior_result_search') != self._prior_searches[search_key]:
                return Outcome('blocked', 'prior-result evidence changed after main review; versioned replan required')
        else:
            dispatched_task['prior_result_search'] = copy.deepcopy(self._prior_searches[search_key])
        if context is not None and hasattr(context, 'current') and not context.current():
            return Outcome('blocked', 'claim no longer current after prior-result lookup')
        outcome = self.handler.run(dispatched_task, context)
        try:
            check_task_results(self.root, task, self.result_verifier)
            check_task_reuse(self.root, task, self.result_verifier)
            check_task_documents(self.root, task)
        except (OSError, ValueError) as exc:
            return Outcome('blocked', f'post-action document/result reconciliation required: {exc}')
        if outcome.status == 'complete':
            try:
                _, proof = result_report(self.root, task, self.result_verifier)
                register_task_result(self.root, task)
                check_task_documents(self.root, task)
            except (OSError, ValueError) as exc:
                return Outcome('blocked', f'result report required: {exc}')
            return Outcome('complete', outcome.reason, (outcome.evidence or []) + [{'task_report': proof}])
        return outcome

    def verify(self, task, evidence):
        if not evidence or not isinstance(evidence[-1], dict) or 'task_report' not in evidence[-1]:
            return False
        try:
            _, proof = result_report(self.root, task, self.result_verifier)
            accepted = (proof == evidence[-1]['task_report']
                        and self.handler.verify(task, evidence[:-1]))
            check_task_documents(self.root, task)
            check_task_memory(self.root, task)
            check_task_knowledge(self.root, task)
            check_task_results(self.root, task, self.result_verifier)
            check_task_reuse(self.root, task, self.result_verifier)
            check_task_documents(self.root, task)
            return accepted
        except (OSError, ValueError):
            return False


def review(snapshot, root, result_verifier=None, plan_review_verifier=None, *, allow_legacy=False):
    """Derived view only; checkbox marks never turn SQLite nodes into done."""
    plan, state = snapshot['plan'], snapshot['state']
    error = None
    plan_review_status = {'status': 'blocked'}
    try:
        from .plan_review import check_plan_review
        plan_review_status = check_plan_review(plan, root, plan_review_verifier, allow_legacy=allow_legacy)
        items = validate_contract(plan, root, check_adopted_advice=False)
    except (OSError, ValueError, KeyError) as exc:
        error = str(exc)
        try:
            items = requirements(Path(root) / plan['task_source']['path'])
        except (OSError, ValueError, KeyError):
            items = []
    rows = []
    for item in items:
        nodes = []
        for task in plan['tasks']:
            if item['id'] not in task.get('task_refs', []):
                continue
            node = state['tasks'][task['task_id']]
            entry = {'task_id': task['task_id'], 'status': node['status'],
                     'task_refs': task['task_refs'],
                     'owner': task['owner'], 'action': task['action'],
                     'depends_on': task.get('depends_on', []),
                     'reason': node.get('reason'), 'evidence': node['evidence'], 'result': None,
                     'next_step': {'todo': 'dispatch when dependencies and retry deadline allow',
                                   'doing': 'poll owned job and check lease',
                                   'blocked': 'main AI resolves the recorded blocker',
                                   'failed': 'main AI diagnoses and versions authorized recovery',
                                   'cancelled': 'respect cancellation', 'done': 'verified result available'}[node['status']]}
            entry['execution'] = {
                'attempts': node.get('attempts'), 'max_attempts': task['max_attempts'],
                'dispatches': node.get('dispatches'),
                'pending_polls': node.get('pending_polls', 0 if task.get('wait_policy') else None),
                'pending_since': node.get('pending_since'), 'last_pending_at': node.get('last_pending_at'),
                'next_at': node.get('next_at'), 'wait_policy': task.get('wait_policy'),
                'diagnosis_required': (node.get('diagnosis_required', False)
                                       and node['status'] not in ('done', 'cancelled')
                                       and state['status'] != 'cancelled'),
                'diagnosis_scope': 'Elapsed/poll observation only; cause and optimization benefit unknown.'}
            if (entry['execution']['diagnosis_required']
                    and (node['status'] in ('todo', 'doing') or node.get('reason_kind') == 'wait_budget')):
                entry['next_step'] = ('main AI inspects owned job progress, external waits and resource evidence; '
                                      'validate any authorized acceleration against the same inputs and acceptance')
            if node['status'] == 'done':
                try:
                    value, proof = result_report(root, task, result_verifier)
                    if not node['evidence'] or node['evidence'][-1].get('task_report') != proof:
                        raise ValueError('result report changed after acceptance')
                    entry['result'] = value
                except (OSError, ValueError, AttributeError) as exc:
                    entry.update(status='needs_review', reason=str(exc),
                                 next_step='main AI revalidates changed or missing result evidence')
            nodes.append(entry)
        rows.append({**item, 'done': bool(nodes) and all(n['status'] == 'done' for n in nodes), 'nodes': nodes})
    remaining = [r['id'] for r in rows if not r['done']]
    return {'run_id': plan['run_id'], 'source': plan['task_source'], 'source_error': error,
            'runtime_status': state['status'], 'requirements': rows, 'remaining': remaining,
            'plan_review': plan_review_status,
            'all_reportable': bool(rows) and not error and not remaining and state['status'] == 'done'}
