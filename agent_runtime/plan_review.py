"""Independent main-plan review at an explicit trusted host boundary.

The durable ledger is host-controlled application state, not a sandbox against its
filesystem owner. No JSON selects code or supplies actor identity. Each submit
calls one reviewer; revisions are separate immutable DAGs, never hidden loops.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import math
import os
from pathlib import Path
import sqlite3
import stat
import time
import uuid

from .project_docs import assert_ai_writable, guard_write_path

SCHEMA = 'main-plan-review/v1'
CHECKS = ('intent', 'guide', 'assumptions', 'prior_results', 'acceptance', 'risk', 'resources')
LIMIT = 1024 * 1024


class PlanReviewError(ValueError):
    pass


def _need(ok, message):
    if not ok:
        raise PlanReviewError(message)


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode('utf-8')


def sha(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def plan_sha256(plan):
    # Include unknown adapter-consumed fields. Only the detached receipt is omitted.
    return sha({k: v for k, v in plan.items() if k != 'plan_review_receipt'})


def project_identity(root):
    return hashlib.sha256(str(Path(root).resolve()).encode()).hexdigest()


def _refs(plan):
    return sorted({ref for task in plan.get('tasks', []) for ref in task.get('task_refs', [])})


def policy(plan):
    value = plan.get('plan_review')
    if value is None:
        return None
    _need(isinstance(value, dict) and value.get('schema_version') == SCHEMA,
          'invalid main-plan review policy; cannot downgrade protected plans')
    _need(_text(value.get('lineage_id')) and isinstance(value.get('evidence_refs'), list),
          'review requires logical lineage_id and explicit evidence_refs')
    return value


def _root(plan, root):
    if root is not None:
        return Path(root).resolve()
    # Compatibility discovery only. Protected execution still requires a verifier
    # installed by the host; a JSON source path is not an authorization grant.
    path = plan.get('task_source', {}).get('path')
    if path and Path(path).is_absolute():
        from .project_docs import project_root_for_task
        return project_root_for_task(path).resolve()
    return None


def _ledger_path(root):
    return assert_ai_writable(root, '.agent-runs/plan-review.sqlite')


def _db(root):
    path = _ledger_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    guard_write_path(path)
    db = sqlite3.connect(path, timeout=30)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA synchronous=FULL')
    db.execute('CREATE TABLE IF NOT EXISTS review_lineages (id TEXT PRIMARY KEY, project TEXT, refs TEXT, started REAL, max_cycles INTEGER, max_seconds REAL)')
    db.execute('CREATE TABLE IF NOT EXISTS review_requests (id TEXT PRIMARY KEY, lineage TEXT, cycle INTEGER, request TEXT, receipt TEXT, UNIQUE(lineage,cycle))')
    db.execute('CREATE TABLE IF NOT EXISTS review_protected (requirement TEXT PRIMARY KEY, lineage TEXT)')
    columns = {row['name'] for row in db.execute('PRAGMA table_info(review_lineages)')}
    if 'purpose' not in columns:
        db.execute("ALTER TABLE review_lineages ADD COLUMN purpose TEXT NOT NULL DEFAULT 'execution'")
    if 'publication_scope' not in columns:
        db.execute('ALTER TABLE review_lineages ADD COLUMN publication_scope TEXT')
    db.commit()
    return db


def protected_lineage(plan, root=None):
    root = _root(plan, root)
    if root is None or not _ledger_path(root).exists():
        return None
    with _db(root) as db:
        rows = db.execute('SELECT requirement,lineage FROM review_protected').fetchall()
    matches = {row['lineage'] for row in rows if row['requirement'] in _refs(plan)}
    _need(len(matches) <= 1, 'requirements cross protected lineages; host reconciliation required')
    return next(iter(matches), None)


def register_protection(plan, root=None, *, publication_task_refs=None):
    """Called on immutable Store creation, before any task can be dispatched."""
    value, root = policy(plan), _root(plan, root)
    existing = protected_lineage(plan, root)
    if value is None:
        _need(existing is None, 'protected logical requirements cannot downgrade to legacy')
        return
    _need(root is not None and _refs(plan), 'protected plans require project root and stable task_refs')
    # Validate all canonical documents and trusted coverage before reserving IDs.
    current_inputs(root, plan, publication_task_refs=publication_task_refs)
    _need(existing in (None, value['lineage_id']), 'protected lineage cannot change with run_id')
    with _db(root) as db:
        db.execute('BEGIN IMMEDIATE')
        scope = _scope(publication_task_refs)
        line = db.execute('SELECT * FROM review_lineages WHERE id=?', (value['lineage_id'],)).fetchone()
        _need(line is None or (line['purpose'] == ('publication' if scope is not None else 'execution') and
              line['publication_scope'] == (canonical(scope).decode() if scope is not None else None)),
              'existing review lineage purpose/scope cannot change')
        for ref in _refs(plan):
            row = db.execute('SELECT lineage FROM review_protected WHERE requirement=?', (ref,)).fetchone()
            _need(row is None or row['lineage'] == value['lineage_id'], 'protected lineage mismatch')
        for ref in _refs(plan):
            db.execute('INSERT OR IGNORE INTO review_protected VALUES (?,?)', (ref, value['lineage_id']))


def _bound(root, ref):
    from .legacy_result_paths import legacy_read_binding, relocated_digest_matches
    _need(isinstance(ref, dict) and set(ref) == {'path', 'sha256'} and _text(ref.get('path')),
          'review evidence requires exact path and sha256')
    raw = Path(ref['path'])
    _need(not raw.is_absolute() and '..' not in raw.parts, 'review evidence outside project')
    read_path, relocated_digest = legacy_read_binding(root, ref['path'])
    path = root / read_path
    for parent in (path, *path.parents):
        if parent == root:
            break
        _need(not parent.is_symlink(), 'review evidence symlink forbidden')
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0))
    with os.fdopen(fd, 'rb') as stream:
        _need(stat.S_ISREG(os.fstat(stream.fileno()).st_mode), 'review evidence must be regular')
        digest = hashlib.sha256()
        size = 0
        while chunk := stream.read(1024 * 1024):
            size += len(chunk)
            _need(size <= 256 * 1024 * 1024, 'review evidence exceeds 256 MiB; use bounded manifest')
            digest.update(chunk)
    _need(digest.hexdigest() == ref['sha256'], 'review evidence changed: ' + ref['path'])
    _need(relocated_digest_matches(digest.hexdigest(), relocated_digest),
          'relocated historical review evidence changed')


def current_inputs(root, plan, *, publication_task_refs=None):
    from .task_manifest import validate_contract
    validate_contract(plan, root, check_adopted_advice=True, required_task_refs=publication_task_refs)
    for ref in policy(plan)['evidence_refs']:
        _bound(root, ref)
    # Prior results are discovery evidence, not scientific acceptance. Bind exact
    # registry bytes nevertheless; new lookup candidates are checked at dispatch.
    refs = {}
    for task in plan['tasks']:
        search = task.get('prior_result_search', {})
        for hit in search.get('results', []):
            if 'record_path' in hit:
                refs[hit['record_path']] = hit['record_sha256']
        for hit in task.get('prior_result_review', {}).get('record_refs', []):
            refs['agent_doc/results/' + hit['run_id'] + '/record.json'] = hit['record_sha256']
        for contract in [task.get('experiment_result'), task.get('result_validation'),
                         *task.get('required_result_refs', [])]:
            if isinstance(contract, dict) and isinstance(contract.get('validation_plan'), dict):
                _bound(root, contract['validation_plan'])
    for path, digest in refs.items():
        _bound(root, {'path': path, 'sha256': digest})


def _review(value):
    _need(isinstance(value, dict) and set(value) == {'full_review', 'verdict'},
          'complete full_review and compact verdict required')
    _need(_text(value['full_review']) and len(canonical(value)) <= LIMIT,
          'full review missing or exceeds 1 MiB; never silently truncate')
    verdict = value['verdict']
    _need(isinstance(verdict, dict) and verdict.get('decision') in ('approve', 'revise', 'reject')
          and _text(verdict.get('summary')) and isinstance(verdict.get('findings'), list),
          'review verdict requires approve/revise/reject, summary and findings')
    checks = verdict.get('checks')
    _need(isinstance(checks, dict) and set(checks) == set(CHECKS), 'all critical review checks required')
    for check in checks.values():
        _need(isinstance(check, dict) and check.get('status') in ('pass', 'fail', 'unknown')
              and _text(check.get('reason')), 'critical check requires explicit status and reason')
    for finding in verdict['findings']:
        _need(isinstance(finding, dict) and type(finding.get('blocking')) is bool and
              all(_text(finding.get(k)) for k in ('target', 'feedback', 'requested_change', 'acceptance_check')),
              'findings must preserve actionable feedback and verification steps')
    if verdict['decision'] == 'approve':
        _need(all(c['status'] == 'pass' for c in checks.values()) and
              not any(f['blocking'] for f in verdict['findings']),
              'approval conflicts with blocking findings or missing critical checks')
    else:
        _need(bool(verdict['findings']), 'revise/reject requires actionable findings')
    return verdict


def _identity(value):
    _need(isinstance(value, dict) and all(_text(value.get(k)) for k in
          ('invocation_id', 'context_id', 'host_source')), 'trusted invocation/context identity required')
    return {k: value[k] for k in ('invocation_id', 'context_id', 'host_source')}


def _authenticate(callback, request, review, proof):
    _need(callable(callback), 'trusted plan-review verifier unavailable; no model backend is installed')
    try:
        observed = callback(deepcopy(request), deepcopy(review), deepcopy(proof))
    except Exception as exc:
        raise PlanReviewError('trusted review authentication unavailable: ' + type(exc).__name__) from exc
    _need(isinstance(observed, dict), 'trusted verifier must return authenticated bindings, not a boolean')
    _need(observed.get('request_sha256') == sha(request) and observed.get('review_sha256') == sha(review),
          'authenticated review does not bind exact nonce/plan/full response')
    planner, reviewer = _identity(observed.get('planner')), _identity(observed.get('reviewer'))
    _need(planner == request['planner'], 'authenticated planner identity mismatch')
    _need(planner['invocation_id'] != reviewer['invocation_id'] and
          planner['context_id'] != reviewer['context_id'] and observed.get('fresh_context') is True,
          'planner self-approval or non-independent reviewer context')
    _need(observed.get('budget_valid') is True, 'host review budget missing/exhausted; replan required')
    return observed


def check_plan_review(plan, root=None, verifier=None, *, allow_legacy=False,
                      purpose="execution", publication_task_refs=None):
    """Reauthenticate current receipt. Saved labels or old callback pass never suffice."""
    value, root = policy(plan), _root(plan, root)
    existing = protected_lineage(plan, root)
    if value is None:
        _need(publication_task_refs is None, 'scoped publication always requires independent review')
        _need(existing is None, 'protected logical requirements cannot downgrade to legacy')
        _need(allow_legacy is True, 'legacy-unprotected requires explicit trusted host opt-in')
        return {'status': 'legacy-unprotected', 'reason': 'historical DAG has no independent main review'}
    _need(root is not None, 'protected review requires current project root')
    _need(existing == value['lineage_id'], 'protected lineage was not registered by trusted host')
    _need(purpose in ('execution', 'publication'), 'unknown trusted review purpose')
    scope = _scope(publication_task_refs)
    _need((purpose == 'publication') == (scope is not None), 'publication review requires exact trusted scope')
    current_inputs(root, plan, publication_task_refs=scope)
    receipt = plan.get('plan_review_receipt')
    _need(isinstance(receipt, dict) and receipt.get('schema_version') == SCHEMA,
          'independent main review receipt missing; dispatch blocked')
    request = receipt.get('request')
    _need(isinstance(request, dict) and request.get('plan_sha256') == plan_sha256(plan)
          and request.get('project') == project_identity(root) and request.get('run_id') == plan['run_id']
          and request.get('lineage_id') == value['lineage_id'], 'stale/cross-project/replayed main review')
    _need(request.get('purpose', 'execution') == purpose and
          request.get('publication_task_refs') == scope, 'review purpose or trusted publication scope mismatch')
    verdict = _review(receipt.get('review'))
    _need(callable(verifier), 'trusted plan-review verifier unavailable; dispatch blocked')
    # A session verifies its durable request ledger and authenticates the model's
    # full response again. An alternate host verifier must provide the same facts.
    try:
        observed = verifier(root, deepcopy(request), deepcopy(receipt['review']), deepcopy(receipt.get('proof')))
    except Exception as exc:
        raise PlanReviewError('trusted review verification rejected/unavailable: ' + str(exc)) from exc
    _authenticate(lambda *_: observed, request, receipt['review'], receipt.get('proof'))
    _need(verdict['decision'] == 'approve', 'main review requires ' + verdict['decision'] + '; versioned replan required')
    current_inputs(root, plan, publication_task_refs=scope)
    return {'status': 'approved', 'plan_sha256': request['plan_sha256'], 'request_id': request['request_id'],
            'lineage_id': request['lineage_id'], 'cycle': request['cycle'],
            'review_sha256': sha(receipt['review']), 'purpose': purpose,
            'publication_task_refs': scope, 'verdict': deepcopy(verdict)}


def _scope(value):
    if value is None:
        return None
    _need(isinstance(value, (list, tuple, set, frozenset)) and value and
          all(_text(r) for r in value) and len(set(value)) == len(value),
          'trusted publication_task_refs must be a nonempty exact set')
    return sorted(value)


class ReviewSession:
    """One host-owned logical requirement lineage; budgets survive new run IDs.

    planner_identity(plan) authenticates the invocation which produced exact plan.
    reviewer(request, plan, previous_reviews) submits/polls ONE fresh review and
    returns {'review': {...}, 'proof': opaque_host_receipt}. It must obey deadline
    and idempotency request_id; this helper cannot interrupt arbitrary host code.
    authenticate(request, review, proof) freshly verifies host records/signatures
    and returns exact hash bindings plus observed planner/reviewer context IDs,
    fresh_context and budget_valid. Unknown hard cost/token budgets must block.
    """
    def __init__(self, root, lineage_id, *, planner_identity=None, reviewer=None,
                 authenticate=None, max_cycles=3, max_seconds=900, clock=time.time, publication_task_refs=None):
        self.root, self.lineage_id = Path(root).resolve(), lineage_id
        self.planner_identity, self.reviewer, self.authenticate = planner_identity, reviewer, authenticate
        self.clock = clock
        self.publication_task_refs = _scope(publication_task_refs)
        self.purpose = 'publication' if self.publication_task_refs is not None else 'execution'
        _need(_text(lineage_id) and type(max_cycles) is int and 1 <= max_cycles <= 20
              and type(max_seconds) in (int, float) and math.isfinite(max_seconds)
              and 1 <= max_seconds <= 86400, 'bounded review cycle/time budgets required')
        self.max_cycles, self.max_seconds = max_cycles, max_seconds

    def submit(self, plan):
        value = policy(plan)
        _need(value is not None and value['lineage_id'] == self.lineage_id, 'session lineage mismatch')
        _need(callable(self.planner_identity) and callable(self.reviewer) and callable(self.authenticate),
              'planner/reviewer/authentication host adapters unavailable; no review was run')
        current_inputs(self.root, plan, publication_task_refs=self.publication_task_refs)
        planner = _identity(self.planner_identity(deepcopy(plan)))
        now = self.clock()
        with _db(self.root) as db:
            db.execute('BEGIN IMMEDIATE')
            line = db.execute('SELECT * FROM review_lineages WHERE id=?', (self.lineage_id,)).fetchone()
            if line is None:
                db.execute('INSERT INTO review_lineages (id,project,refs,started,max_cycles,max_seconds,purpose,publication_scope) VALUES (?,?,?,?,?,?,?,?)',
                           (self.lineage_id, project_identity(self.root), canonical(_refs(plan)).decode(),
                            now, self.max_cycles, self.max_seconds, self.purpose,
                            canonical(self.publication_task_refs).decode() if self.publication_task_refs is not None else None))
                line = db.execute('SELECT * FROM review_lineages WHERE id=?', (self.lineage_id,)).fetchone()
            _need(line['project'] == project_identity(self.root) and
                  line['max_cycles'] == self.max_cycles and line['max_seconds'] == self.max_seconds and
                  line['purpose'] == self.purpose and
                  line['publication_scope'] == (canonical(self.publication_task_refs).decode() if self.publication_task_refs is not None else None),
                  'cannot reset logical review budget; explicit host reconciliation required')
            rows = db.execute('SELECT * FROM review_requests WHERE lineage=? ORDER BY cycle',
                              (self.lineage_id,)).fetchall()
            # No implicit retry after timeout/crash: prior request still consumed budget.
            _need(not rows or rows[-1]['receipt'] is not None,
                  'prior review outcome ambiguous; host reconciliation required, do not resubmit')
            _need(len(rows) < line['max_cycles'] and 0 <= now - line['started'] < line['max_seconds'],
                  'review budget exhausted; stop for replan, never mark done')
            previous = [json.loads(row['receipt']) for row in rows]
            request = {'schema_version': SCHEMA, 'request_id': uuid.uuid4().hex,
                       'project': project_identity(self.root), 'lineage_id': self.lineage_id,
                       'cycle': len(rows) + 1, 'run_id': plan['run_id'], 'plan_sha256': plan_sha256(plan),
                       'purpose': self.purpose, 'publication_task_refs': self.publication_task_refs,
                       'planner': planner, 'deadline': line['started'] + line['max_seconds'],
                       'previous_review_sha256': [sha(item['review']) for item in previous]}
            # Scope/budget/identity validation precedes atomic ownership reservation.
            for ref in _refs(plan):
                owner = db.execute('SELECT lineage FROM review_protected WHERE requirement=?', (ref,)).fetchone()
                _need(owner is None or owner['lineage'] == self.lineage_id,
                      'protected lineage cannot change with run_id')
            for ref in _refs(plan):
                db.execute('INSERT OR IGNORE INTO review_protected VALUES (?,?)', (ref, self.lineage_id))
            db.execute('INSERT INTO review_requests VALUES (?,?,?,?,NULL)',
                       (request['request_id'], self.lineage_id, request['cycle'], canonical(request).decode()))
        result = self.reviewer(deepcopy(request), deepcopy(plan), deepcopy(previous))
        return self.resolve(plan, request['request_id'], result)

    def resolve(self, plan, request_id, result):
        """Accept the authentic response to an existing ambiguous request once.

        No new model call, cycle refund, budget extension or approval is implied.
        The host must recover the original response/receipt before its deadline;
        an unavailable or expired response remains blocked, with history intact.
        """
        with _db(self.root) as db:
            row = db.execute('SELECT * FROM review_requests WHERE id=?', (request_id,)).fetchone()
        _need(row is not None and row['lineage'] == self.lineage_id,
              'no matching review request to reconcile')
        request = json.loads(row['request'])
        _need(policy(plan) is not None and policy(plan)['lineage_id'] == self.lineage_id and
              request['plan_sha256'] == plan_sha256(plan) and request['run_id'] == plan['run_id'] and
              request['project'] == project_identity(self.root) and request.get('purpose', 'execution') == self.purpose and
              request.get('publication_task_refs') == self.publication_task_refs, 'recovered review plan/project/scope mismatch')
        _need(isinstance(result, dict), 'reviewer returned no full response')
        review, proof = result.get('review'), result.get('proof')
        _review(review)
        _authenticate(self.authenticate, request, review, proof)
        _need(self.clock() <= request['deadline'], 'review time budget exhausted; stop for replan')
        current_inputs(self.root, plan, publication_task_refs=self.publication_task_refs)
        receipt = {'schema_version': SCHEMA, 'request': request, 'review': deepcopy(review), 'proof': deepcopy(proof)}
        with _db(self.root) as db:
            db.execute('BEGIN IMMEDIATE')
            current = db.execute('SELECT receipt FROM review_requests WHERE id=?', (request_id,)).fetchone()[0]
            _need(current is None or json.loads(current) == receipt, 'review response already frozen; cannot replace it')
            db.execute('UPDATE review_requests SET receipt=? WHERE id=? AND receipt IS NULL',
                       (canonical(receipt).decode(), request_id))
        return receipt

    def verify(self, root, request, review, proof):
        _need(Path(root).resolve() == self.root and request.get('lineage_id') == self.lineage_id and
              request.get('purpose', 'execution') == self.purpose and
              request.get('publication_task_refs') == self.publication_task_refs,
              'review session project/lineage mismatch')
        with _db(self.root) as db:
            row = db.execute('SELECT * FROM review_requests WHERE id=?', (request.get('request_id'),)).fetchone()
            line = db.execute('SELECT * FROM review_lineages WHERE id=?', (self.lineage_id,)).fetchone()
            _need(line is not None and line['purpose'] == self.purpose and
                  line['publication_scope'] == (canonical(self.publication_task_refs).decode() if self.publication_task_refs is not None else None),
                  'trusted publication scope changed after restart')
            latest = db.execute('SELECT MAX(cycle) FROM review_requests WHERE lineage=?', (self.lineage_id,)).fetchone()[0]
        expected = {'schema_version': SCHEMA, 'request': request, 'review': review, 'proof': proof}
        _need(row is not None and row['receipt'] is not None and json.loads(row['receipt']) == expected
              and json.loads(row['request']) == request and row['cycle'] == latest,
              'receipt absent/replayed/superseded in authoritative review ledger')
        return _authenticate(self.authenticate, request, review, proof)
