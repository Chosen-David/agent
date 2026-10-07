"""Contract tests: real SQLite/process I/O; synthetic adapters and clocks where named.

No paid models, network scheduler or deployed daemon. The subprocess smoke test
runs only a bounded foreground service and validates actual artifact hashes.
"""
import copy
import hashlib
import json
import multiprocessing
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor

from agent_runtime.core import ArtifactHandler, Engine, Outcome, Store, interval, validate
from agent_runtime.scheduler import LocalScheduler, arm


ROOT = Path(__file__).resolve().parents[1]


def task(name='a', deps=(), action='synthetic', attempts=3):
    return {'task_id': name, 'depends_on': list(deps), 'action': action,
            'owner': 'test', 'done_when': {'contract': 'synthetic verifier'},
            'max_attempts': attempts, 'estimated_seconds': 20, 'risk': 'low'}


def plan(*tasks):
    return {'schema_version': 'task-dag/v1', 'run_id': 'test-run',
            'user_goal': 'verify durable task contract',
            'authorization_reference': 'synthetic local test authorization',
            'supervision': {'min_seconds': 1, 'max_seconds': 60,
                            'rationale': 'synthetic bounded estimate'},
            'tasks': list(tasks or (task(),))}


class SyntheticClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


class SyntheticHandler:
    idempotent = True
    required_capabilities = frozenset({'synthetic'})

    def __init__(self, outcome=None, verified=True):
        self.calls = []
        self.outcome = outcome or Outcome('complete', evidence=[{'synthetic': True}])
        self.verified = verified

    def run(self, task, context):
        self.calls.append((task['task_id'], context))
        return copy.deepcopy(self.outcome)

    def verify(self, task, evidence):
        return self.verified


class GateHandler(SyntheticHandler):
    def __init__(self, idempotent=True):
        super().__init__()
        self.idempotent = idempotent
        self.entered = threading.Event()
        self.release = threading.Event()

    def run(self, task, context):
        self.calls.append((task['task_id'], context))
        self.entered.set()
        if not self.release.wait(8):
            raise RuntimeError('test gate timeout')
        return copy.deepcopy(self.outcome)


class ProcessHandler(SyntheticHandler):
    """Synthetic actor; shared count proves real process claim exclusion."""
    def __init__(self, count, entered, release):
        super().__init__()
        self.count, self.entered, self.release = count, entered, release

    def run(self, task, context):
        with self.count.get_lock():
            self.count.value += 1
        self.entered.set()
        if not self.release.wait(8):
            raise RuntimeError('test process gate timeout')
        return copy.deepcopy(self.outcome)


def process_tick(db_path, count, entered, release, event_id):
    handler = ProcessHandler(count, entered, release)
    Engine(Store(db_path), {'synthetic': handler}, authorize=lambda *_: True, allow_legacy=True).tick('test-run', event_id)


class RuntimeContracts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db_path = str(Path(self.tmp.name) / 'ledger.sqlite')
        self.store = Store(self.db_path)
        self.clock = SyntheticClock()

    def engine(self, handler=None, authorize=None):
        return Engine(self.store, {'synthetic': handler or SyntheticHandler()},
                      authorize=authorize or (lambda *_: True), clock=self.clock, lease_seconds=5, allow_legacy=True)

    def state(self):
        return self.store.snapshot('test-run')['state']

    def test_dag_rejects_cycles_unknown_duplicate_and_unbounded(self):
        invalid = [plan(task('a', ['a'])), plan(task('a', ['b'])),
                   plan(task('a'), task('a')), plan(task('a', ['b']), task('b', ['a']))]
        p = plan(); p['tasks'][0]['max_attempts'] = 0; invalid.append(p)
        p = plan(); p['tasks'][0]['estimated_seconds'] = float('inf'); invalid.append(p)
        p = plan(); p['supervision']['min_seconds'] = 0; invalid.append(p)
        p = plan(); p['supervision']['max_seconds'] = 0; invalid.append(p)
        for p in invalid:
            with self.subTest(plan=p), self.assertRaises(ValueError):
                validate(p)

    def test_dependencies_restart_immutable_identity_and_duplicate_event(self):
        p = plan(task('child', ['parent']), task('parent'))
        self.store.create(p)
        handler = SyntheticHandler()
        first = self.engine(handler).tick('test-run', 'event-1')
        self.assertEqual(first['tasks']['parent']['status'], 'done')
        self.assertEqual(first['tasks']['child']['status'], 'todo')
        self.store = Store(self.db_path)  # Real SQLite close/reopen, not an in-memory mock.
        self.store.create(p)  # Same immutable plan is idempotent.
        duplicate = self.engine(handler).tick('test-run', 'event-1')
        self.assertEqual(duplicate['tasks']['child']['attempts'], 0)
        self.assertEqual(len(handler.calls), 1)
        self.assertEqual(self.engine(handler).tick('test-run', 'event-2')['status'], 'done')
        altered = copy.deepcopy(p); altered['user_goal'] = 'different'
        with self.assertRaises(ValueError):
            self.store.create(altered)

    def test_concurrent_threads_only_one_actor_owns_active_lease(self):
        self.store.create(plan())
        handler = GateHandler()
        with ThreadPoolExecutor(max_workers=6) as pool:
            owner = pool.submit(self.engine(handler).tick, 'test-run', 'owner')
            self.assertTrue(handler.entered.wait(4))
            try:
                rivals = [pool.submit(self.engine(handler).tick, 'test-run', f'rival-{i}') for i in range(5)]
                for rival in rivals:
                    self.assertEqual(rival.result(timeout=4)['tasks']['a']['attempts'], 1)
                self.assertEqual(len(handler.calls), 1)
            finally:
                handler.release.set()
            self.assertEqual(owner.result(timeout=4)['status'], 'done')

    def test_real_multiprocess_sqlite_claim_exclusion(self):
        self.store.create(plan())
        ctx = multiprocessing.get_context('spawn')
        count, entered, release = ctx.Value('i', 0), ctx.Event(), ctx.Event()
        first = ctx.Process(target=process_tick, args=(self.db_path, count, entered, release, 'p1'))
        rival = ctx.Process(target=process_tick, args=(self.db_path, count, entered, release, 'p2'))
        first.start()
        try:
            self.assertTrue(entered.wait(5))
            rival.start(); rival.join(5)
            self.assertEqual(rival.exitcode, 0)
            self.assertEqual(count.value, 1)
        finally:
            release.set(); first.join(5)
            for process in (first, rival):
                if process.pid and process.is_alive():
                    process.terminate(); process.join(3)
        self.assertEqual(first.exitcode, 0)
        self.assertEqual(self.state()['status'], 'done')

    def expired_case(self, idempotent):
        self.store.create(plan())
        old = GateHandler(idempotent=idempotent)
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(self.engine(old).tick, 'test-run', 'first')
            self.assertTrue(old.entered.wait(4))
            try:
                original_context = old.calls[0][1]
                self.clock.now += 6
                self.store = Store(self.db_path)
                replacement = SyntheticHandler(); replacement.idempotent = idempotent
                state = self.engine(replacement).tick('test-run', 'recovery')
                self.assertFalse(original_context.current())
                if idempotent:
                    self.assertEqual(state['status'], 'done')
                    self.assertEqual(state['tasks']['a']['attempts'], 2)
                    self.assertEqual(original_context.idempotency_key, replacement.calls[0][1].idempotency_key)
                    self.assertNotEqual(original_context.token, replacement.calls[0][1].token)
                else:
                    self.assertEqual(state['status'], 'blocked')
                    self.assertEqual(state['tasks']['a']['reason_kind'], 'ambiguous')
                    self.assertEqual(replacement.calls, [])
            finally:
                old.release.set()
            future.result(timeout=4)
        with self.store.transaction() as db:
            rejected = db.execute("SELECT count(*) FROM journal WHERE kind='stale_result_rejected'").fetchone()[0]
        self.assertEqual(rejected, 1)
        return self.state()

    def test_expired_idempotent_restarts_with_stable_key_and_fences_old_result(self):
        self.assertEqual(self.expired_case(True)['status'], 'done')

    def test_expired_nonidempotent_blocks_for_reconciliation(self):
        self.assertEqual(self.expired_case(False)['status'], 'blocked')

    def test_permission_block_does_not_stop_independent_branch(self):
        self.store.create(plan(task('restricted'), task('dependent', ['restricted']), task('independent')))
        handler = SyntheticHandler()
        engine = self.engine(handler, authorize=lambda _p, t, _h: t['task_id'] != 'restricted')
        state = engine.tick('test-run', 'permission')
        self.assertEqual(state['tasks']['restricted']['reason_kind'], 'permission')
        self.assertEqual(state['tasks']['dependent']['status'], 'blocked')
        self.assertEqual(state['tasks']['independent']['status'], 'done')
        self.assertNotEqual(state['status'], 'done')
        state = self.engine(handler).tick('test-run', 'approved')
        self.assertEqual(state['tasks']['restricted']['status'], 'done')
        self.assertEqual(self.engine(handler).tick('test-run', 'dependent-ready')['status'], 'done')

    def test_default_authorization_denies_and_plan_cannot_grant(self):
        p = plan(); p['authorization'] = {'synthetic': True}
        self.store.create(p)
        handler = SyntheticHandler()
        engine = Engine(self.store, {'synthetic': handler}, clock=self.clock, allow_legacy=True)
        self.assertEqual(engine.tick('test-run', 'untrusted-plan')['status'], 'blocked')
        self.assertEqual(handler.calls, [])

    def test_cancel_rejects_inflight_completion_and_stops_owned_monitor(self):
        self.store.create(plan())
        scheduler = LocalScheduler(self.store, self.clock)
        scheduler.heartbeat('synthetic-service'); monitor = arm(scheduler, 'test-run')['monitor_id']
        handler = GateHandler()
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(self.engine(handler).tick, 'test-run', 'start')
            self.assertTrue(handler.entered.wait(4))
            self.store.cancel('test-run', 'user stop', now=self.clock())
            handler.release.set(); future.result(timeout=4)
        self.assertEqual(self.state()['status'], 'cancelled')
        self.assertEqual(self.state()['tasks']['a']['status'], 'cancelled')
        self.assertEqual(scheduler.read(monitor)['status'], 'stopped')
        self.assertEqual(self.engine().tick('test-run', 'late')['status'], 'cancelled')

    def test_retry_budget_and_early_tick_are_bounded(self):
        self.store.create(plan(task(attempts=2)))
        handler = SyntheticHandler(Outcome('retry', 'synthetic transient error'))
        engine = self.engine(handler)
        state = engine.tick('test-run', 'first')
        self.assertEqual(state['tasks']['a']['attempts'], 1)
        engine.tick('test-run', 'too-early')
        self.assertEqual(len(handler.calls), 1)
        self.clock.now = state['tasks']['a']['next_at']
        state = engine.tick('test-run', 'retry-due')
        self.assertEqual(state['status'], 'failed')
        self.assertIn('budget exhausted', state['tasks']['a']['reason'])
        self.clock.now += 1000
        engine.tick('test-run', 'cannot-retry-terminal')
        self.assertEqual(len(handler.calls), 2)

    def test_evidence_missing_rejected_and_verifier_failure(self):
        for evidence, verified in (([], True), ([{'claim': 'done'}], False)):
            with self.subTest(evidence=evidence):
                p = plan(); p['run_id'] = str(verified)
                self.store.create(p)
                handler = SyntheticHandler(Outcome('complete', evidence=evidence), verified)
                state = self.engine(handler).tick(p['run_id'], 'proof')
                self.assertEqual(state['status'], 'failed')
                self.assertIn('evidence rejected', state['tasks']['a']['reason'])

    def test_interval_bounds_backoff_risk_and_change(self):
        p = plan(); s = {'tasks': {'a': {'status': 'todo'}}, 'idle_ticks': 0}
        self.assertEqual(interval(p, s), 5)
        s['idle_ticks'] = 99
        self.assertEqual(interval(p, s), 60)
        self.assertEqual(interval(p, s, changed=True), 5)
        p['tasks'][0]['risk'] = 'high'
        self.assertEqual(interval(p, s, changed=True), 2)
        p['tasks'][0]['estimated_seconds'] = 1
        self.assertEqual(interval(p, s, changed=True), 1)

    def test_artifact_hash_and_root_boundary_use_real_files(self):
        root = Path(self.tmp.name) / 'artifacts'; root.mkdir()
        (root / 'result').write_bytes(b'expected')
        t = task(action='verify_artifacts')
        t['done_when'] = {'artifacts': [{'path': 'result', 'sha256': hashlib.sha256(b'expected').hexdigest()}]}
        handler = ArtifactHandler(root)
        evidence = handler.run(t, None).evidence
        self.assertTrue(handler.verify(t, evidence))
        (root / 'result').write_bytes(b'changed')
        with self.assertRaises(ValueError):
            handler.verify(t, evidence)
        t['done_when']['artifacts'][0]['path'] = '../outside'
        with self.assertRaises(ValueError):
            handler.run(t, None)

    def test_scheduler_no_backend_readback_stop_and_restart(self):
        self.store.create(plan())
        scheduler = LocalScheduler(self.store, self.clock)
        self.assertFalse(scheduler.capabilities()['ready'])
        self.assertEqual(arm(scheduler, 'test-run')['status'], 'blocked')
        self.assertIsNone(self.store.snapshot('test-run')['monitor'])
        scheduler.heartbeat('synthetic-service')
        started = arm(scheduler, 'test-run')
        self.assertEqual(started['status'], 'started')
        self.assertTrue(started['readback']['live'])
        self.assertEqual(arm(scheduler, 'test-run')['monitor_id'], started['monitor_id'])
        reopened = LocalScheduler(Store(self.db_path), self.clock)
        self.assertEqual(reopened.read(started['monitor_id'])['chain_id'], 'test-run')
        reopened.stop(started['monitor_id'])
        self.assertEqual(reopened.read(started['monitor_id'])['status'], 'stopped')
        self.clock.now += 31
        self.assertFalse(reopened.capabilities()['ready'])

    def test_scheduler_rejects_id_without_readback(self):
        class SyntheticBadScheduler:
            def capabilities(self): return {'ready': True}
            def create(self, run_id): return 'issued-id'
            def read(self, monitor_id): return {'id': monitor_id, 'chain_id': 'wrong', 'status': 'active', 'live': True}
        result = arm(SyntheticBadScheduler(), 'test-run')
        self.assertEqual(result['status'], 'blocked')
        self.assertEqual(result['monitor_id'], 'issued-id')

    def test_scheduler_cancel_between_reservation_and_tick_is_safe(self):
        self.store.create(plan())
        scheduler = LocalScheduler(self.store, self.clock)
        scheduler.heartbeat('synthetic-service')
        monitor = arm(scheduler, 'test-run')['monitor_id']
        store = self.store
        class CancelDuringTick:
            def tick(self, run_id, event_id):
                store.cancel(run_id, 'injected user cancellation')
                return store.snapshot(run_id)['state']
        self.assertTrue(scheduler.drain_once(CancelDuringTick()))
        self.assertEqual(scheduler.read(monitor)['status'], 'stopped')
        self.assertEqual(self.state()['status'], 'cancelled')

    def test_real_worker_termination_recovers_persisted_lease(self):
        self.store.create(plan())
        ctx = multiprocessing.get_context('spawn')
        count, entered, release = ctx.Value('i', 0), ctx.Event(), ctx.Event()
        worker = ctx.Process(target=process_tick, args=(self.db_path, count, entered, release, 'crash'))
        worker.start()
        try:
            self.assertTrue(entered.wait(5))
            worker.terminate(); worker.join(4)
            self.assertFalse(worker.is_alive())
            self.store = Store(self.db_path)
            persisted = self.state()['tasks']['a']
            self.assertEqual(persisted['status'], 'doing')
            # A real dead process is not permission to replay before its lease.
            handler = SyntheticHandler()
            self.clock.now = persisted['lease_until'] - 0.01
            early = self.engine(handler).tick('test-run', 'restart-before-lease')
            self.assertEqual(handler.calls, [])
            self.assertEqual(early['tasks']['a']['status'], 'doing')
            self.assertEqual(early['tasks']['a']['attempts'], 1)
            # Real process death and SQLite reopen; only now expire the lease.
            self.clock.now = persisted['lease_until'] + 1
            state = self.engine(handler).tick('test-run', 'restart')
            self.assertEqual(state['status'], 'done')
            self.assertEqual(state['tasks']['a']['attempts'], 2)
        finally:
            # Do not touch multiprocessing synchronization after terminate:
            # its waiter may have died holding an internal condition lock.
            if worker.is_alive():
                worker.terminate(); worker.join(3)

    def test_changed_upstream_proof_prevents_downstream_dispatch(self):
        root = Path(self.tmp.name)
        (root / 'source').write_bytes(b'v1')
        a = task('source', action='verify_artifacts')
        a['done_when'] = {'artifacts': [{'path': 'source', 'sha256': hashlib.sha256(b'v1').hexdigest()}]}
        self.store.create(plan(a, task('consumer', ['source'])))
        consumer = SyntheticHandler()
        engine = Engine(self.store, {'verify_artifacts': ArtifactHandler(root), 'synthetic': consumer},
                        authorize=lambda *_: True, clock=self.clock, allow_legacy=True)
        engine.tick('test-run', 'produce')
        (root / 'source').write_bytes(b'v2')
        state = engine.tick('test-run', 'dispatch')
        self.assertEqual(state['tasks']['source']['status'], 'failed')
        self.assertEqual(state['tasks']['consumer']['status'], 'blocked')
        self.assertEqual(consumer.calls, [])
        self.assertNotEqual(state['status'], 'done')

    def test_reconcile_needs_host_authorization_evidence_and_stops_monitor(self):
        self.store.create(plan())
        handler = SyntheticHandler(Outcome('blocked', 'ambiguous effect'))
        engine = self.engine(handler)
        engine.tick('test-run', 'ambiguous')
        scheduler = LocalScheduler(self.store, self.clock)
        scheduler.heartbeat('synthetic-service')
        monitor = arm(scheduler, 'test-run')['monitor_id']
        for evidence, reference in (([], 'host'), ([{'proof': True}], '')):
            with self.assertRaises(ValueError):
                engine.reconcile('test-run', 'a', evidence, reference)
        with self.assertRaises(ValueError):
            self.engine(handler, authorize=lambda *_: False).reconcile('test-run', 'a', [{'proof': True}], 'host')
        handler.verified = False
        with self.assertRaises(ValueError):
            engine.reconcile('test-run', 'a', [{'proof': True}], 'host')
        handler.verified = True
        state = engine.reconcile('test-run', 'a', [{'proof': True}], 'host inspected external outcome')
        self.assertEqual(state['status'], 'done')
        self.assertEqual(len(handler.calls), 1)  # Reconciliation never replays effect.
        self.assertEqual(scheduler.read(monitor)['status'], 'stopped')

    def test_cancelled_chain_cannot_be_reconciled_to_done(self):
        self.store.create(plan())
        self.store.cancel('test-run', 'user stop')
        with self.assertRaises(ValueError):
            self.engine().reconcile('test-run', 'a', [{'proof': True}], 'host')
        self.assertEqual(self.state()['status'], 'cancelled')

    def test_adapter_exception_uses_idempotency_boundary(self):
        class Raises(SyntheticHandler):
            def run(self, task, context):
                raise RuntimeError('injected unknown effect')
        for safe in (True, False):
            p = plan(); p['run_id'] = str(safe); self.store.create(p)
            handler = Raises(); handler.idempotent = safe
            state = self.engine(handler).tick(p['run_id'], 'error')
            self.assertEqual(state['tasks']['a']['status'], 'todo' if safe else 'blocked')
            self.assertIn('injected unknown effect', state['tasks']['a']['reason'])

    def test_scheduler_respects_due_minimum_and_stops_only_owned_monitor(self):
        self.store.create(plan())
        other = plan(); other['run_id'] = 'other'; self.store.create(other)
        scheduler = LocalScheduler(self.store, self.clock)
        scheduler.heartbeat('synthetic-service')
        own_id = arm(scheduler, 'test-run')['monitor_id']
        other_id = arm(scheduler, 'other')['monitor_id']
        engine = self.engine(SyntheticHandler(Outcome('pending', 'waiting')))
        self.assertTrue(scheduler.drain_once(engine))
        own = scheduler.read(own_id)
        self.assertGreater(own['due'], self.clock())
        scheduler.wake('test-run', 'actual artifact changed')
        self.assertGreaterEqual(scheduler.read(own_id)['due'], self.clock() + 1)
        self.store.cancel('test-run', 'user stop')
        self.assertEqual(scheduler.read(own_id)['status'], 'stopped')
        self.assertEqual(scheduler.read(other_id)['status'], 'active')

    def test_invalid_proof_propagates_through_completed_dependency_closure(self):
        for reverse in (False, True):
            with self.subTest(non_topological=reverse):
                proof = Path(self.tmp.name) / ('proof-' + str(reverse))
                proof.write_bytes(b'original')
                a = task('a', action='verify_artifacts')
                a['done_when'] = {'artifacts': [{'path': proof.name, 'sha256': hashlib.sha256(b'original').hexdigest()}]}
                nodes = [a, task('b', ['a']), task('c', ['b'])]
                p = plan(*(list(reversed(nodes)) if reverse else nodes))
                p['run_id'] = 'closure-' + str(reverse)
                self.store.create(p)
                handler = SyntheticHandler()
                engine = Engine(self.store, {'synthetic': handler, 'verify_artifacts': ArtifactHandler(self.tmp.name)},
                                authorize=lambda *_: True, clock=self.clock, allow_legacy=True)
                engine.tick(p['run_id'], 'a-completes')
                state = engine.tick(p['run_id'], 'b-completes')
                self.assertEqual(state['tasks']['a']['status'], 'done')
                self.assertEqual(state['tasks']['b']['status'], 'done')
                self.assertEqual(state['tasks']['c']['attempts'], 0)
                proof.write_bytes(b'changed')
                state = engine.tick(p['run_id'], 'dependency-proof-invalidated')
                self.assertEqual(state['tasks']['a']['status'], 'failed')
                self.assertEqual(state['tasks']['b']['status'], 'failed')
                self.assertEqual(state['tasks']['c']['status'], 'blocked')
                self.assertEqual(state['tasks']['c']['attempts'], 0)
                self.assertEqual([name for name, _ in handler.calls], ['b'])
                self.assertNotEqual(state['status'], 'done')

    def test_repeated_retry_backoff_grows_despite_claims_and_waiting_descendants(self):
        for reverse in (False, True):
            with self.subTest(non_topological=reverse):
                nodes = [task('a', attempts=10), task('b', ['a']), task('c', ['b'])]
                p = plan(*(list(reversed(nodes)) if reverse else nodes))
                p['run_id'] = 'backoff-' + str(reverse)
                self.store.create(p)
                handler = SyntheticHandler(Outcome('retry', 'same transient condition'))
                engine = self.engine(handler)
                delays = []
                for i in range(4):
                    state = engine.tick(p['run_id'], 'retry-' + str(i))
                    delays.append(state['next_check_seconds'])
                    self.clock.now = state['tasks']['a']['next_at']
                    self.assertEqual(state['tasks']['b']['attempts'], 0)
                    self.assertEqual(state['tasks']['c']['attempts'], 0)
                self.assertLess(delays[0], delays[1])
                self.assertLess(delays[1], delays[2])
                self.assertEqual(delays[-1], p['supervision']['max_seconds'])
                self.assertEqual(len(handler.calls), 4)
                # A real verified result, unlike another claim, resets backoff.
                handler.outcome = Outcome('complete', evidence=[{'synthetic': True}])
                state = engine.tick(p['run_id'], 'verified-result')
                self.assertEqual(state['tasks']['a']['status'], 'done')
                self.assertEqual(state['idle_ticks'], 0)
                self.assertLess(state['next_check_seconds'], delays[-1])

    def test_permission_recheck_with_blocked_descendants_keeps_backoff(self):
        for reverse in (False, True):
            with self.subTest(non_topological=reverse):
                nodes = [task('a'), task('b', ['a']), task('c', ['b'])]
                p = plan(*(list(reversed(nodes)) if reverse else nodes))
                p['run_id'] = 'permission-backoff-' + str(reverse)
                self.store.create(p)
                handler = SyntheticHandler()
                engine = self.engine(handler, authorize=lambda *_: False)
                delays = []
                for i in range(4):
                    state = engine.tick(p['run_id'], 'recheck-' + str(i))
                    delays.append(state['next_check_seconds'])
                    self.clock.now += state['next_check_seconds']
                    self.assertEqual(state['tasks']['a']['status'], 'blocked')
                    self.assertTrue(all(n['attempts'] == 0 for n in state['tasks'].values()))
                self.assertLess(delays[0], delays[1])
                self.assertLess(delays[1], delays[2])
                self.assertEqual(delays[-1], p['supervision']['max_seconds'])
                self.assertEqual(handler.calls, [])
                LocalScheduler(self.store, self.clock).wake(p['run_id'], 'trusted authorization changed')
                state = self.store.snapshot(p['run_id'])['state']
                self.assertEqual(state['idle_ticks'], 0)
                self.assertLess(interval(p, state), delays[-1])

    def test_bounded_real_subprocess_serve_arm_artifact_convergence(self):
        root = Path(self.tmp.name) / 'output'; root.mkdir()
        t = task(action='verify_artifacts', attempts=10)
        t['done_when'] = {'artifacts': [{'path': 'proof.txt', 'sha256': hashlib.sha256(b'accepted').hexdigest()}]}
        p = plan(t); p['supervision']['max_seconds'] = 1
        self.store.create(p)
        command = [sys.executable, '-m', 'agent_runtime', '--legacy-unprotected', '--db', self.db_path]
        offline = subprocess.run(command + ['arm', 'test-run'], cwd=ROOT, capture_output=True, text=True, timeout=5, check=True)
        self.assertEqual(json.loads(offline.stdout)['status'], 'blocked')
        service = subprocess.Popen(command + ['serve', '--artifact-root', str(root), '--max-seconds', '8'], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            scheduler = LocalScheduler(self.store)
            deadline = time.monotonic() + 4
            while not scheduler.capabilities()['ready'] and time.monotonic() < deadline:
                time.sleep(.05)
            self.assertTrue(scheduler.capabilities()['ready'])
            started = subprocess.run(command + ['arm', 'test-run'], cwd=ROOT, capture_output=True, text=True, timeout=5, check=True)
            start = json.loads(started.stdout)
            self.assertEqual(start['status'], 'started')
            self.assertTrue(start['readback']['live'])
            (root / 'proof.txt').write_bytes(b'accepted')
            deadline = time.monotonic() + 5
            while self.state()['status'] != 'done' and time.monotonic() < deadline:
                time.sleep(.05)
            self.assertEqual(self.state()['status'], 'done')
            self.assertEqual(scheduler.read(start['monitor_id'])['status'], 'stopped')
            self.assertEqual(self.state()['tasks']['a']['evidence'][0]['sha256'], hashlib.sha256(b'accepted').hexdigest())
        finally:
            service.terminate()
            try:
                stdout, stderr = service.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                service.kill(); stdout, stderr = service.communicate(timeout=3)
        self.assertEqual(service.returncode, 0, stderr)
        self.assertEqual(json.loads(stdout)['status'], 'serve_stopped')
        self.assertFalse(LocalScheduler(self.store).capabilities()['ready'])


if __name__ == '__main__':
    unittest.main()
