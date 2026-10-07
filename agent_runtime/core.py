"""Durable, bounded task DAG. Trusted host adapters execute; plans never grant rights.

SQLite is the authoritative local ledger (not suitable for shared network FS).
Delivery is at-least-once: adapters must honor stable keys and fencing/cancellation.
No model, shell command, credentials, cloud service or daemon is auto-installed.
"""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import sqlite3
import stat
import time
from typing import Callable, Protocol
import uuid

from .project_docs import guard_write_path


def packed(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


def number(value, low, high):
    return (type(value) in (int, float) and math.isfinite(value)
            and low <= value <= high)


def validate(plan):
    if plan.get('schema_version') != 'task-dag/v1':
        raise ValueError('expected task-dag/v1')
    for field in ('run_id', 'user_goal', 'authorization_reference'):
        if not isinstance(plan.get(field), str) or not plan[field].strip():
            raise ValueError(f'missing {field}')
    tasks = plan.get('tasks', [])
    if not isinstance(tasks, list) or not 1 <= len(tasks) <= 1000:
        raise ValueError('1..1000 tasks required')
    ids = [t.get('task_id') for t in tasks]
    if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
        raise ValueError('unique nonempty task IDs required')
    for task in tasks:
        for field in ('action', 'owner', 'done_when'):
            if not task.get(field):
                raise ValueError(f'missing {field}')
        deps = task.get('depends_on', [])
        if not isinstance(deps, list) or any(d not in ids for d in deps):
            raise ValueError('unknown dependency')
        if type(task.get('max_attempts')) is not int or not 1 <= task['max_attempts'] <= 20:
            raise ValueError('max_attempts must be 1..20')
        if not number(task.get('estimated_seconds'), 1, 604800):
            raise ValueError('bounded estimated_seconds required')
        if task.get('risk') not in ('low', 'medium', 'high'):
            raise ValueError('risk required')
        if 'wait_policy' in task:
            wait = task['wait_policy']
            if (not isinstance(wait, dict)
                    or set(wait) != {'max_polls', 'max_seconds', 'diagnose_after_seconds'}
                    or type(wait.get('max_polls')) is not int
                    or not 1 <= wait['max_polls'] <= 100000
                    or not number(wait.get('max_seconds'), 1, 604800)
                    or not number(wait.get('diagnose_after_seconds'), 1, wait['max_seconds'])):
                raise ValueError('wait_policy requires bounded polls, elapsed time and diagnosis threshold')
    remaining, visited = {t['task_id']: set(t.get('depends_on', [])) for t in tasks}, set()
    while remaining:
        ready = {i for i, deps in remaining.items() if deps <= visited}
        if not ready:
            raise ValueError('dependency cycle')
        visited |= ready
        remaining = {i: deps for i, deps in remaining.items() if i not in ready}
    policy = plan.get('supervision', {})
    if not (number(policy.get('min_seconds'), 1, 86400)
            and number(policy.get('max_seconds'), policy['min_seconds'], 86400)
            and isinstance(policy.get('rationale'), str) and policy['rationale']):
        raise ValueError('bounded supervision policy with rationale required')
    packed(plan)


def interval(plan, state, changed=False):
    """AI supplies estimates/risk/rationale; deterministic clamp enforces limits."""
    policy = plan['supervision']
    outstanding = [t for t in plan['tasks'] if state['tasks'][t['task_id']]['status'] != 'done']
    estimate = min((t['estimated_seconds'] for t in outstanding), default=policy['min_seconds'])
    risky = any(t['risk'] == 'high' for t in outstanding)
    base = estimate * (0.1 if risky else 0.25)
    backoff = 1 if changed else 2 ** min(state.get('idle_ticks', 0), 10)
    return min(policy['max_seconds'], max(policy['min_seconds'], base * backoff))


def wait_limit(task, node, now):
    """Explicit opt-in observation budget; legacy plans retain attempt semantics."""
    policy = task.get('wait_policy')
    if policy is None or 'pending_since' not in node:
        return None
    if node.get('pending_polls', 0) >= policy['max_polls']:
        return 'pending observation budget exhausted; main AI diagnosis required'
    if now - node['pending_since'] >= policy['max_seconds']:
        return 'pending elapsed budget exhausted; main AI diagnosis required'
    return None


class Store:
    def __init__(self, path):
        self.path = str(guard_write_path(path))
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.transaction() as db:
            db.execute('CREATE TABLE IF NOT EXISTS chains (id TEXT PRIMARY KEY, plan TEXT, state TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS events (chain_id TEXT, event_id TEXT, at REAL, PRIMARY KEY(chain_id,event_id))')
            db.execute('CREATE TABLE IF NOT EXISTS journal (seq INTEGER PRIMARY KEY, chain_id TEXT, at REAL, kind TEXT, detail TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS monitors (id TEXT PRIMARY KEY, chain_id TEXT UNIQUE, status TEXT, due REAL)')
            if 'version' not in {row['name'] for row in db.execute('PRAGMA table_info(monitors)')}:
                db.execute('ALTER TABLE monitors ADD COLUMN version INTEGER NOT NULL DEFAULT 0')
            db.execute('CREATE TABLE IF NOT EXISTS services (id TEXT PRIMARY KEY, expires REAL)')

    @contextmanager
    def transaction(self):
        guard_write_path(self.path)
        db = sqlite3.connect(self.path, timeout=30, isolation_level=None)
        db.row_factory = sqlite3.Row
        try:
            db.execute('PRAGMA synchronous=FULL')
            db.execute('BEGIN IMMEDIATE')
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def load(self, db, run_id):
        row = db.execute('SELECT plan,state FROM chains WHERE id=?', (run_id,)).fetchone()
        if row is None:
            raise KeyError(run_id)
        return json.loads(row['plan']), json.loads(row['state'])

    def save(self, db, run_id, state):
        db.execute('UPDATE chains SET state=? WHERE id=?', (packed(state), run_id))

    def log(self, db, run_id, now, kind, detail):
        db.execute('INSERT INTO journal(chain_id,at,kind,detail) VALUES (?,?,?,?)',
                   (run_id, now, kind, packed(detail)))

    def create(self, plan, *, project_root=None):
        validate(plan)
        from .plan_review import register_protection
        register_protection(plan, project_root)
        state = {'status': 'active', 'idle_ticks': 0, 'tasks': {
            t['task_id']: {'status': 'todo', 'attempts': 0, 'next_at': 0,
                           'evidence': [], 'reason': None} for t in plan['tasks']}}
        with self.transaction() as db:
            # Sticky protection also survives a stripped source path in this Store.
            from .plan_review import PlanReviewError
            refs = {r for t in plan['tasks'] for r in t.get('task_refs', [])}
            for row in db.execute('SELECT plan FROM chains'):
                prior = json.loads(row['plan'])
                if prior.get('plan_review') and refs & {r for t in prior['tasks'] for r in t.get('task_refs', [])}:
                    if plan.get('plan_review', {}).get('lineage_id') != prior['plan_review']['lineage_id']:
                        raise PlanReviewError('protected logical requirements cannot change lineage or downgrade')
            old = db.execute('SELECT plan FROM chains WHERE id=?', (plan['run_id'],)).fetchone()
            if old:
                if old['plan'] != packed(plan):
                    raise ValueError('run_id already bound to a different immutable plan')
                return plan['run_id']
            db.execute('INSERT INTO chains VALUES (?,?,?)', (plan['run_id'], packed(plan), packed(state)))
        return plan['run_id']

    def snapshot(self, run_id):
        with self.transaction() as db:
            plan, state = self.load(db, run_id)
            row = db.execute('SELECT * FROM monitors WHERE chain_id=?', (run_id,)).fetchone()
            return {'plan': plan, 'state': state, 'monitor': dict(row) if row else None}

    def cancel(self, run_id, reference, now=None):
        if not reference:
            raise ValueError('cancellation instruction reference required')
        with self.transaction() as db:
            _, state = self.load(db, run_id)
            state['status'] = 'cancelled'
            for node in state['tasks'].values():
                if node['status'] != 'done':
                    node.update(status='cancelled', reason=reference, token=None, diagnosis_required=False)
            self.save(db, run_id, state)
            db.execute("UPDATE monitors SET status='stopped' WHERE chain_id=?", (run_id,))
            self.log(db, run_id, time.time() if now is None else now, 'cancel', reference)


@dataclass
class Outcome:
    status: str  # complete candidate / pending observation / retry / blocked / failed
    reason: str = ''
    evidence: list | None = None


@dataclass
class Context:
    store: Store
    run_id: str
    task_id: str
    token: str
    idempotency_key: str
    clock: Callable

    def current(self):
        snap = self.store.snapshot(self.run_id)['state']
        node = snap['tasks'][self.task_id]
        return (snap['status'] != 'cancelled' and node.get('token') == self.token
                and node['status'] == 'doing' and node['lease_until'] > self.clock())


class Handler(Protocol):
    # Trusted adapter metadata, never accepted from the model's plan.
    idempotent: bool
    required_capabilities: frozenset[str]

    def run(self, task: dict, context: Context) -> Outcome: ...
    def verify(self, task: dict, evidence: list) -> bool: ...


class Engine:
    def __init__(self, store, handlers, authorize=None, clock=time.time, lease_seconds=300,
                 *, project_root=None, plan_review_verifier=None, allow_legacy=False):
        if not number(lease_seconds, 1, 86400):
            raise ValueError('invalid lease')
        self.store, self.handlers = store, handlers
        self.authorize = authorize or (lambda plan, task, handler: False)
        self.clock, self.lease_seconds = clock, lease_seconds
        self.project_root, self.plan_review_verifier = project_root, plan_review_verifier
        self.allow_legacy = allow_legacy is True

    def _authorized(self, plan, task, handler):
        try:
            return self.authorize(plan, task, handler) is True
        except Exception:
            # An unavailable policy service must not grant rights or kill monitor.
            return False

    def _review_plan(self, plan):
        from .plan_review import check_plan_review, PlanReviewError
        try:
            return check_plan_review(plan, self.project_root, self.plan_review_verifier, allow_legacy=self.allow_legacy)
        except (ValueError, OSError, KeyError) as exc:
            raise PlanReviewError(str(exc)) from exc

    def _check_done(self, plan, state):
        try:
            self._review_plan(plan)
        except ValueError as exc:
            state.update(status='blocked', plan_review_error=str(exc))
            for node in state['tasks'].values():
                if node['status'] == 'done':
                    node.update(status='blocked', reason_kind='plan_review_after_effect', requires_reconciliation=True,
                                reason='review invalid after effect; explicit reconciliation required: ' + str(exc))
            return False
        # Fresh dependency/terminal evidence, not just an old success bit.
        for task in plan['tasks']:
            node = state['tasks'][task['task_id']]
            if node['status'] != 'done':
                continue
            handler = self.handlers.get(task['action'])
            try:
                valid = handler is not None and handler.verify(task, node['evidence'])
            except Exception:
                valid = False
            if not valid:
                node.update(status='failed', reason='previous completion evidence no longer valid')
        # Invalidation follows dependency closure, even when plan order is not
        # topological. A valid file cannot justify results built on invalid inputs.
        changed = True
        while changed:
            changed = False
            for task in plan['tasks']:
                node = state['tasks'][task['task_id']]
                if (node['status'] == 'done' and any(state['tasks'][d]['status'] != 'done'
                                                    for d in task.get('depends_on', []))):
                    node.update(status='failed', reason='completed result depends on invalid evidence')
                    changed = True

    def reconcile(self, run_id, task_id, evidence, reference):
        """Explicit host reconciliation of an ambiguous effect; no blind replay."""
        if not reference or not evidence:
            raise ValueError('reconciliation evidence and host reference required')
        with self.store.transaction() as db:
            plan, state = self.store.load(db, run_id)
            self._review_plan(plan)
            state.pop('plan_review_error', None)
            task = next(t for t in plan['tasks'] if t['task_id'] == task_id)
            node, handler = state['tasks'][task_id], self.handlers.get(task['action'])
            if state['status'] == 'cancelled' or node['status'] != 'blocked':
                raise ValueError('only blocked, non-cancelled tasks may be reconciled')
            if (handler is None or not self._authorized(plan, task, handler)
                    or not all(state['tasks'][d]['status'] == 'done' for d in task.get('depends_on', []))
                    or not handler.verify(task, evidence)):
                raise ValueError('reconciliation not authorized or not verified')
            node.update(status='done', token=None, evidence=evidence, reason=reference, reason_kind='reconciled',
                        diagnosis_required=False, requires_reconciliation=False)
            self._check_done(plan, state)
            self._summary(plan, state)
            self.store.save(db, run_id, state)
            if state['status'] == 'done':
                db.execute("UPDATE monitors SET status='stopped' WHERE chain_id=?", (run_id,))
            self.store.log(db, run_id, self.clock(), 'reconcile', {'task_id': task_id, 'reference': reference})
            return state

    def _summary(self, plan, state):
        if state['status'] == 'cancelled':
            return
        if state.get('plan_review_error'):
            state['status'] = 'blocked'
            return
        nodes = state['tasks']
        for task in plan['tasks']:
            node = nodes[task['task_id']]
            if node.get('requires_reconciliation'):
                node['status'] = 'blocked'
                continue
            if node['status'] in ('todo', 'blocked'):
                bad = [d for d in task.get('depends_on', [])
                       if nodes[d]['status'] in ('failed', 'blocked', 'cancelled')]
                if bad and node.get('reason_kind') not in ('permission', 'ambiguous', 'plan_review_after_effect'):
                    node.update(status='blocked', reason='dependencies: ' + ', '.join(bad), reason_kind='dependency')
                elif not bad and node.get('reason_kind') == 'dependency':
                    node.update(status='todo', reason=None, reason_kind=None)
        statuses = [n['status'] for n in nodes.values()]
        if all(s == 'done' for s in statuses):
            state['status'] = 'done'
        elif any(s in ('todo', 'doing') for s in statuses):
            state['status'] = 'active'
        elif 'failed' in statuses:
            state['status'] = 'failed'
        else:
            state['status'] = 'blocked'

    def tick(self, run_id, event_id):
        """Only trusted host wake-ups call this API. Event text in documents is not a trigger.

        One claim per tick bounds work; successor readiness is durable for next wake-up.
        An early/duplicate tick cannot bypass retry deadlines or active leases.
        """
        if not isinstance(event_id, str) or not event_id:
            raise ValueError('event ID required')
        now, claim = self.clock(), None
        # Before terminal fast paths and each actual claim, including restart.
        try:
            self._review_plan(self.store.snapshot(run_id)['plan'])
        except (ValueError, OSError, KeyError) as exc:
            with self.store.transaction() as db:
                _, state = self.store.load(db, run_id)
                if state['status'] != 'cancelled':
                    state['status'] = 'blocked'
                    for node in state['tasks'].values():
                        if not node.get('requires_reconciliation') and (node['status'] == 'todo' or
                                (node['status'] == 'blocked' and node.get('reason_kind') == 'plan_review')):
                            node.update(status='blocked', reason_kind='plan_review', reason=str(exc))
                    state['plan_review_error'] = str(exc)
                    self.store.save(db, run_id, state)
                    self.store.log(db, run_id, now, 'plan_review_blocked', str(exc))
                return state
        with self.store.transaction() as db:
            plan, state = self.store.load(db, run_id)
            state.pop('plan_review_error', None)
            for node in state['tasks'].values():
                if node.get('reason_kind') == 'plan_review' and not node.get('requires_reconciliation'):
                    node.update(status='todo', reason_kind=None, reason=None)
            if state['status'] in ('done', 'cancelled'):
                return state
            if db.execute('SELECT 1 FROM events WHERE chain_id=? AND event_id=?', (run_id, event_id)).fetchone():
                return state
            db.execute('INSERT INTO events VALUES (?,?,?)', (run_id, event_id, now))
            self._check_done(plan, state)
            for task in plan['tasks']:
                node = state['tasks'][task['task_id']]
                handler = self.handlers.get(task['action'])
                if node['status'] == 'doing' and node['lease_until'] <= now:
                    if handler and handler.idempotent:
                        node.update(status='todo' if node['attempts'] < task['max_attempts'] else 'failed',
                                    token=None, next_at=now, reason='expired lease; retry uses original idempotency key')
                    else:
                        node.update(status='blocked', token=None, reason_kind='ambiguous',
                                    reason='expired lease: external side effect unknown; reconciliation required')
                if node.get('reason_kind') in ('permission', 'adapter'):
                    node.update(status='todo', reason_kind=None)
                if (task.get('wait_policy') and 'pending_since' in node
                        and node['status'] in ('todo', 'doing', 'blocked')
                        and now - node['pending_since'] >= task['wait_policy']['diagnose_after_seconds']):
                    # Observation diagnostics must not wait for another action claim.
                    node['diagnosis_required'] = True
            self._summary(plan, state)
            tasks = plan['tasks']
            cursor = state.get('claim_cursor', 0) % len(tasks)
            for offset in range(len(tasks)):
                index = (cursor + offset) % len(tasks)
                task = tasks[index]
                node = state['tasks'][task['task_id']]
                if node['status'] != 'todo':
                    continue
                if not all(state['tasks'][d]['status'] == 'done' for d in task.get('depends_on', [])):
                    continue
                exhausted = wait_limit(task, node, now)
                if exhausted:
                    node.update(status='blocked', reason_kind='wait_budget', reason=exhausted,
                                diagnosis_required=True)
                    continue
                if node['next_at'] > now:
                    continue
                handler = self.handlers.get(task['action'])
                if handler is None:
                    node.update(status='blocked', reason_kind='adapter', reason='host action adapter unavailable')
                    continue
                if not self._authorized(plan, task, handler):
                    node.update(status='blocked', reason_kind='permission', reason='host authorization required')
                    continue
                token = uuid.uuid4().hex
                node.update(status='doing', attempts=node['attempts'] + 1, token=token,
                            lease_until=now + self.lease_seconds, reason=None, reason_kind=None,
                            dispatches=node.get('dispatches', 0) + 1)
                # Persist fairness across restarts and concurrent claimants.
                # Readiness, authorization and individual deadlines still gate each claim.
                state['claim_cursor'] = (index + 1) % len(tasks)
                key = hashlib.sha256((packed(plan) + '\0' + task['task_id']).encode()).hexdigest()
                claim = (task, handler, Context(self.store, run_id, task['task_id'], token, key, self.clock))
                break
            # Claims/permission rechecks are not progress. Only verified results
            # (or an explicit change event) reset backoff; pending/retry grows it.
            if not claim:
                state['idle_ticks'] += 1
            self._summary(plan, state)
            state['next_check_seconds'] = interval(plan, state)
            self.store.save(db, run_id, state)
            self.store.log(db, run_id, now, 'tick', {'event_id': event_id, 'claimed': claim[0]['task_id'] if claim else None})
        if claim:
            from .plan_review import PlanReviewError
            task, handler, context = claim
            executed, review_blocked, outcome, effect_observation = False, False, None, None
            try:
                if not context.current() or not self._authorized(plan, task, handler):
                    outcome = Outcome('blocked', 'authorization revoked or claim no longer current')
                else:
                    self._review_plan(plan)
                    executed = True
                    outcome = handler.run(task, context)
                    self._review_plan(plan)
                    if outcome.status == 'complete' and not (outcome.evidence and handler.verify(task, outcome.evidence)):
                        outcome = Outcome('failed', 'completion evidence rejected by verifier')
                    if outcome.status not in ('complete', 'pending', 'retry', 'blocked', 'failed'):
                        outcome = Outcome('failed', 'invalid adapter outcome')
            except PlanReviewError as exc:
                review_blocked = True
                if executed:
                    effect_observation = ({'status': outcome.status, 'reason': outcome.reason,
                                           'evidence': deepcopy(outcome.evidence)} if outcome is not None else
                                          {'status': 'unknown', 'reason': 'no outcome returned', 'evidence': []})
                outcome = Outcome('blocked', 'plan review invalid; explicit reconciliation required: ' + str(exc),
                                  outcome.evidence if outcome is not None else [])
            except Exception as exc:
                # Unknown side effects: only an explicitly idempotent adapter may retry.
                outcome = Outcome('retry' if handler.idempotent else 'blocked',
                                  f'adapter exception {type(exc).__name__}: {exc}')
            with self.store.transaction() as db:
                plan, state = self.store.load(db, run_id)
                node = state['tasks'][task['task_id']]
                if (node.get('token') == context.token and node['status'] == 'doing'
                        and node['lease_until'] > self.clock() and state['status'] != 'cancelled'):
                    status = {'complete': 'done', 'pending': 'todo', 'retry': 'todo'}.get(outcome.status, outcome.status)
                    reason_kind = ('plan_review_after_effect' if executed else 'plan_review') if review_blocked else 'adapter_result'
                    if outcome.status == 'pending' and task.get('wait_policy') is not None:
                        # Only a successfully returned observation refunds this claim.
                        # Crashes, unknown side effects and retry outcomes still cost attempts.
                        node['attempts'] -= 1
                        node['pending_polls'] = node.get('pending_polls', 0) + 1
                        node.setdefault('pending_since', now)
                        node['last_pending_at'] = self.clock()
                        node['diagnosis_required'] = (
                            self.clock() - node['pending_since'] >= task['wait_policy']['diagnose_after_seconds'])
                        exhausted = wait_limit(task, node, self.clock())
                        if exhausted:
                            status, reason_kind = 'blocked', 'wait_budget'
                            outcome.reason = exhausted
                            node['diagnosis_required'] = True
                    if status == 'todo' and node['attempts'] >= task['max_attempts']:
                        status = 'failed'
                        outcome.reason = 'attempt budget exhausted: ' + outcome.reason
                    if effect_observation is not None:
                        node.update(requires_reconciliation=True, effect_observation=effect_observation)
                    node.update(status=status, token=None, reason=outcome.reason,
                                evidence=outcome.evidence or [], reason_kind=reason_kind)
                    if status == 'done':
                        node['diagnosis_required'] = False
                    state['idle_ticks'] = state['idle_ticks'] + 1 if status == 'todo' else 0
                    delay = interval(plan, state, status == 'done')
                    node['next_at'] = self.clock() + delay
                    self._check_done(plan, state)
                    self._summary(plan, state)
                    state['next_check_seconds'] = interval(plan, state, status == 'done')
                    self.store.save(db, run_id, state)
                    self.store.log(db, run_id, self.clock(), 'outcome', {'task_id': task['task_id'], 'status': status, 'reason': outcome.reason})
                else:
                    self.store.log(db, run_id, self.clock(), 'stale_result_rejected', {'task_id': task['task_id']})
        with self.store.transaction() as db:
            _, state = self.store.load(db, run_id)
            if state['status'] in ('done', 'cancelled', 'failed'):
                db.execute("UPDATE monitors SET status='stopped' WHERE chain_id=?", (run_id,))
            return state


class ArtifactHandler:
    """Read-only, content-hash acceptance. Does not do semantic/LLM verification."""
    idempotent = True
    required_capabilities = frozenset({'read_artifacts'})

    def __init__(self, root):
        self.root = Path(root).resolve()

    def _evidence(self, task):
        results = []
        for item in task['done_when']['artifacts']:
            path = (self.root / item['path']).resolve()
            if not path.is_relative_to(self.root):
                raise ValueError('artifact outside authorized root')
            # A FIFO/device is not an artifact. Nonblocking open plus fstat avoids
            # blocking before validation; read(limit+1) also bounds concurrent growth.
            flags = os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_NOFOLLOW', 0)
            fd = os.open(path, flags)
            with os.fdopen(fd, 'rb') as stream:
                metadata = os.fstat(stream.fileno())
                if not stat.S_ISREG(metadata.st_mode):
                    raise ValueError('artifact must be a regular file')
                limit = 16 * 1024 * 1024
                if metadata.st_size > limit:
                    raise ValueError('artifact exceeds 16 MiB verification bound')
                content = stream.read(limit + 1)
                if len(content) > limit:
                    raise ValueError('artifact grew beyond verification bound')
            digest = hashlib.sha256(content).hexdigest()
            if digest != item['sha256']:
                raise ValueError('artifact digest does not match predeclared acceptance')
            results.append({'path': item['path'], 'sha256': digest})
        return results

    def run(self, task, context):
        try:
            return Outcome('complete', evidence=self._evidence(task))
        except FileNotFoundError:
            return Outcome('pending', 'artifact not yet present')

    def verify(self, task, evidence):
        return bool(evidence) and evidence == self._evidence(task)
