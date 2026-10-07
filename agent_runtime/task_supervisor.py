"""tmux-managed TASK.md supervision. Start is detached even inside another tmux.

Trusted host adapters are explicit Python files, never commands in TASK.md.
The generic backend verifies artifacts; it cannot invent a main AI/model backend.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import shutil
import signal
import subprocess
import sys
import time
import uuid

from .core import ArtifactHandler, Engine, Store
from .scheduler import LocalScheduler, arm
from .project_docs import assert_ai_writable, guard_write_path, resolve_task_file
from .task_manifest import (ReportingHandler, atomic_json, prepare, review,
                            validate_contract)

CODE_ROOT = Path(__file__).resolve().parents[1]
TMUX_SOCKET = 'agent-supervisors'


def tmux(*args, check=True):
    return subprocess.run(['tmux', '-L', TMUX_SOCKET, '-f', '/dev/null', *args],
                          capture_output=True, text=True, check=check, timeout=10)


def load_backend(config, store):
    root = config['project_root']
    if config.get('adapter'):
        spec = importlib.util.spec_from_file_location('agent_host_adapter', config['adapter'])
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        backend = module.build(root, store, config['run_id'])
    else:
        handler = ArtifactHandler(root)
        backend = {'handlers': {'verify_artifacts': handler},
                   'authorize': lambda plan, task, candidate: candidate is handler}
    handlers = {name: ReportingHandler(h, root, backend.get('result_verifier')) for name, h in backend['handlers'].items()}
    authorize = backend['authorize']
    return (handlers, lambda plan, task, wrapper: authorize(plan, task, wrapper.handler),
            backend.get('maintain'), backend.get('result_verifier'), backend.get('plan_review_verifier'))



def submit_review(plan_path, project_root, state_dir, adapter, out):
    """Explicit host adapter submits one review, preserving revise/reject feedback.

    The adapter exposes build(root, store, run_id)['plan_review_session']; its
    ReviewSession has independently authenticated planner/reviewer callbacks.
    No callable, model identity or module path is obtained from plan JSON.
    """
    from .plan_review import ReviewSession
    root = Path(project_root).resolve()
    state_dir = assert_ai_writable(root, state_dir)
    out = assert_ai_writable(root, out)
    plan = json.loads(Path(plan_path).read_text())
    validate_contract(plan, root)
    if not adapter:
        raise ValueError('explicit trusted host adapter required for independent main review')
    spec = importlib.util.spec_from_file_location('agent_review_adapter', str(Path(adapter).resolve()))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    backend = module.build(str(root), Store(state_dir / 'review-host.sqlite'), plan['run_id'])
    session = backend.get('plan_review_session')
    if not isinstance(session, ReviewSession) or session.root != root:
        raise ValueError('host must supply plan_review_session with authentic separate invocations')
    plan.pop('plan_review_receipt', None)
    receipt = session.submit(plan)
    plan['plan_review_receipt'] = receipt
    atomic_json(out, plan)
    return {'status': receipt['review']['verdict']['decision'], 'plan': str(out),
            'request_id': receipt['request']['request_id'], 'cycle': receipt['request']['cycle'],
            'full_review': receipt['review']['full_review'], 'verdict': receipt['review']['verdict'],
            'authority': 'plan review only; not tool authorization or data acceptance'}


def publish(config, store, *, result_verifier=None, plan_review_verifier=None, **extra):
    report = review(store.snapshot(config['run_id']), config['project_root'], result_verifier, plan_review_verifier,
                    allow_legacy=config.get('allow_legacy') is True)
    report.update(updated_at=time.time(), **extra)
    atomic_json(Path(config['state_dir']) / 'progress.json', report)
    return report


class ManagedEngine(Engine):
    def __init__(self, config, *args, result_verifier=None, **kwargs):
        super().__init__(*args, project_root=config['project_root'],
                         allow_legacy=kwargs.pop('allow_legacy', config.get('allow_legacy') is True), **kwargs)
        self.config = config
        self.result_verifier = result_verifier

    def tick(self, run_id, event_id):
        # Re-read requirements before each dispatch; edits require explicit replan.
        snap = self.store.snapshot(run_id)
        validate_contract(snap['plan'], self.config['project_root'], check_adopted_advice=False)
        state = super().tick(run_id, event_id)
        publish(self.config, self.store, result_verifier=self.result_verifier,
                plan_review_verifier=self.plan_review_verifier, last_event=event_id)
        return state


def worker(config):
    if not os.environ.get('TMUX'):
        raise RuntimeError('managed supervisor must run inside tmux; use start')
    state_dir = assert_ai_writable(config['project_root'], config['state_dir'])
    # A DB has exactly one managed worker; duplicate starts cannot duplicate agents.
    with guard_write_path(state_dir / 'worker.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return 0
        store = Store(state_dir / 'state.sqlite')
        scheduler = LocalScheduler(store)
        handlers, authorize, maintain, result_verifier, plan_review_verifier = load_backend(config, store)
        engine = ManagedEngine(config, store, handlers, authorize, result_verifier=result_verifier,
                               plan_review_verifier=plan_review_verifier)
        service_id = 'tmux:' + uuid.uuid4().hex
        stopped = []
        signal.signal(signal.SIGTERM, lambda *_: stopped.append(True))
        signal.signal(signal.SIGINT, lambda *_: stopped.append(True))
        next_maintenance = 0
        monitor_id = 'local:' + config['run_id']
        try:
            while not stopped:
                scheduler.heartbeat(service_id)
                atomic_json(state_dir / 'live.json', {
                    'run_id': config['run_id'], 'session': config['session'],
                    'pid': os.getpid(), 'heartbeat_at': time.time(), 'service_id': service_id})
                report = publish(config, store, result_verifier=result_verifier, plan_review_verifier=plan_review_verifier)
                if report['runtime_status'] == 'cancelled':
                    return 0
                if report['runtime_status'] == 'done' and not report['source_error']:
                    # Fresh artifact verification after restart and before final delivery.
                    with store.transaction() as db:
                        plan, state = store.load(db, config['run_id'])
                        engine._check_done(plan, state)
                        engine._summary(plan, state)
                        store.save(db, config['run_id'], state)
                    report = publish(config, store, result_verifier=result_verifier, plan_review_verifier=plan_review_verifier)
                    if report['all_reportable']:
                        scheduler.stop(monitor_id)
                        monitor = store.snapshot(config['run_id'])['monitor']
                        final = publish(config, store, result_verifier=result_verifier, plan_review_verifier=plan_review_verifier, monitor=scheduler.read(monitor_id) if monitor else None)
                        atomic_json(state_dir / 'final-report.json', final)
                        return 0
                try:
                    if time.monotonic() >= next_maintenance:
                        snap = store.snapshot(config['run_id'])
                        next_maintenance = time.monotonic() + snap['state'].get(
                            'next_check_seconds', snap['plan']['supervision']['min_seconds'])
                        # Trusted main-AI adapter submits/polls maintenance, must not block.
                        # It may diagnose failed nodes, reconcile evidence or version a new
                        # recovery chain within existing authorization, never reset budgets.
                        if maintain:
                            maintain(report)
                    snap = store.snapshot(config['run_id'])
                    if not report['source_error'] and snap['state']['status'] not in ('done', 'failed', 'cancelled'):
                        if not snap['monitor']:
                            receipt = arm(scheduler, config['run_id'])
                            atomic_json(state_dir / 'monitor.json', receipt)
                            if receipt['status'] != 'started':
                                raise RuntimeError(receipt['reason'])
                        scheduler.drain_once(engine, config['run_id'])
                    # Failed/source-changed chains keep the owner alive for recovery;
                    # they never produce a success report or repeatedly run failed work.
                    publish(config, store, result_verifier=result_verifier, plan_review_verifier=plan_review_verifier, maintenance_available=maintain is not None)
                except Exception as exc:
                    publish(config, store, result_verifier=result_verifier, plan_review_verifier=plan_review_verifier, supervisor_error=f'{type(exc).__name__}: {exc}')
                    print(f'supervision error: {type(exc).__name__}: {exc}', flush=True)
                time.sleep(1)
            return 0
        finally:
            with store.transaction() as db:
                db.execute('DELETE FROM services WHERE id=?', (service_id,))
            guard_write_path(state_dir / 'live.json').unlink(missing_ok=True)


def guard(config_path):
    """Restart crashed worker in the owned tmux pane; keep all durable state."""
    if not os.environ.get('TMUX'):
        raise RuntimeError('guard requires tmux; use start')
    config = json.loads(Path(config_path).read_text())
    assert_ai_writable(config['project_root'], config['state_dir'])
    with guard_write_path(Path(config['state_dir']) / 'supervisor.log').open('a', buffering=1) as log:
        while True:
            if Store(Path(config['state_dir']) / 'state.sqlite').snapshot(config['run_id'])['state']['status'] == 'cancelled':
                return
            result = subprocess.run([sys.executable, '-m', 'agent_runtime.task_supervisor',
                                     '_worker', '--config', str(config_path)], cwd=CODE_ROOT,
                                    stdout=log, stderr=subprocess.STDOUT)
            if result.returncode == 0:
                return
            log.write(f'worker exit={result.returncode}; restart in 5 seconds\n')
            log.flush()
            time.sleep(5)


def status(config):
    state_dir = Path(config['state_dir'])
    store = Store(state_dir / 'state.sqlite')
    snap = store.snapshot(config['run_id'])
    pane = tmux('list-panes', '-t', '=' + config['session'], '-F', '#{pane_dead}', check=False)
    live = {}
    try:
        live = json.loads((state_dir / 'live.json').read_text())
    except (OSError, ValueError):
        pass
    alive = (pane.returncode == 0 and '0' in pane.stdout.splitlines()
             and live.get('run_id') == config['run_id']
             and live.get('session') == config['session']
             and 0 <= time.time() - live.get('heartbeat_at', 0) < 10)
    monitor = snap['monitor']
    if monitor:
        monitor = LocalScheduler(store).read(monitor['id'])
    return {'run_id': config['run_id'], 'session': config['session'],
            'live': alive, 'runtime_status': snap['state']['status'], 'monitor': monitor,
            'progress': str(state_dir / 'progress.json'),
            'final_report': str(state_dir / 'final-report.json') if (state_dir / 'final-report.json').exists() else None}


def start(plan_path, project_root, state_dir, adapter=None, *, allow_legacy=False):
    if not shutil.which('tmux'):
        raise RuntimeError('tmux unavailable; supervisor was NOT started (no foreground fallback)')
    plan = json.loads(Path(plan_path).read_text())
    root = Path(project_root).resolve()
    state_dir = assert_ai_writable(root, state_dir)
    validate_contract(plan, root)
    if any(t['action'] == 'configure_host_action' or t['done_when'].get('configure_acceptance') for t in plan['tasks']):
        raise ValueError('draft only: main AI must configure actions, dependencies and acceptance first')
    state_dir.mkdir(parents=True, exist_ok=True)
    # Serialize start/configuration changes, separate from the lifetime worker lock.
    with guard_write_path(state_dir / 'launch.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        config = {'run_id': plan['run_id'], 'project_root': str(root), 'state_dir': str(state_dir),
                  'adapter': str(Path(adapter).resolve()) if adapter else None,
                  'allow_legacy': allow_legacy is True,
                  'session': 'agent-' + hashlib.sha256(str(state_dir).encode()).hexdigest()[:16]}
        config_path = state_dir / 'launch.json'
        if config_path.exists() and json.loads(config_path.read_text()) != config:
            raise ValueError('state directory bound to different configuration; use a new version')
        store = Store(state_dir / 'state.sqlite')
        store.create(plan, project_root=root)
        # Backend code is selected only by this explicit host argument.
        _, _, _, _, plan_verifier = load_backend(config, store)
        from .plan_review import check_plan_review
        check_plan_review(plan, root, plan_verifier, allow_legacy=allow_legacy)
        source_bytes = (root / plan['task_source']['path']).read_bytes()
        if hashlib.sha256(source_bytes).hexdigest() != plan['task_source']['sha256']:
            raise ValueError('TASK.md changed during startup; reconcile before dispatch')
        atomic_json(state_dir / 'source-snapshot.json', {
            'sha256': plan['task_source']['sha256'], 'content': source_bytes.decode('utf-8'),
            'project_documents': plan.get('project_documents'),
            'guide_reviews': plan.get('guide_reviews'), 'advice_assessments': plan.get('advice_assessments')})
        validate_contract(plan, root)
        atomic_json(config_path, config)
        existing = tmux('has-session', '-t', '=' + config['session'], check=False).returncode == 0
        if not existing:
            guard_write_path(state_dir / 'final-report.json').unlink(missing_ok=True)
            guard_write_path(state_dir / 'live.json').unlink(missing_ok=True)
            command = 'exec ' + shlex.join([sys.executable, '-m', 'agent_runtime.task_supervisor',
                                           '_guard', '--config', str(config_path)])
            tmux('new-session', '-d', '-s', config['session'], '-c', str(CODE_ROOT), command)
        for _ in range(50):
            receipt = status(config)
            if receipt['final_report'] or receipt['runtime_status'] == 'cancelled':
                receipt['status'] = 'completed' if receipt['final_report'] else 'cancelled'
                break
            if (receipt['live'] and receipt['monitor'] and receipt['monitor']['live']
                    and receipt['monitor']['status'] == 'active'):
                receipt['status'] = 'started' if not existing else 'already_running'
                break
            time.sleep(.1)
        else:
            receipt['status'] = 'blocked'
            receipt['reason'] = 'no matching live monitor readback; inspect supervisor.log'
        atomic_json(state_dir / 'receipt.json', receipt)
        return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('prepare')
    p.add_argument('--task-file', help='canonical index or legacy TASK; defaults to project resolver')
    p.add_argument('--project-root', default='.')
    p.add_argument('--run-id', required=True)
    p.add_argument('--mode', choices=('auto', 'manual'), default='auto')
    p.add_argument('--authorization-reference', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--lineage-id', help='stable logical requirement lineage across revisions')
    p.add_argument('--legacy-unprotected', action='store_true', help='explicit compatibility only; no main-review protection')
    p = sub.add_parser('start')
    p.add_argument('--plan', required=True)
    p.add_argument('--project-root', required=True)
    p.add_argument('--state-dir', required=True)
    p.add_argument('--adapter', help='explicit trusted Python host adapter with build(root, store, run_id)')
    p.add_argument('--legacy-unprotected', action='store_true', help='trusted compatibility opt-in; never for protected requirements')
    p = sub.add_parser('review')
    p.add_argument('--plan', required=True)
    p.add_argument('--project-root', required=True)
    p.add_argument('--state-dir', required=True)
    p.add_argument('--adapter', required=True, help='explicit trusted host build with plan_review_session')
    p.add_argument('--out', required=True)
    for command in ('status', 'cancel', '_guard', '_worker'):
        p = sub.add_parser(command)
        p.add_argument('--config', required=True)
        if command == 'cancel':
            p.add_argument('--reference', required=True)
    args = parser.parse_args()
    if args.command == 'prepare':
        plan = prepare(args.task_file or resolve_task_file(args.project_root), args.run_id, args.mode, args.authorization_reference,
                       review_required=not args.legacy_unprotected, lineage_id=args.lineage_id)
        atomic_json(args.out, plan)
        result = {'status': 'draft', 'plan': str(Path(args.out).resolve()), 'tasks': len(plan['tasks'])}
    elif args.command == 'review':
        result = submit_review(args.plan, args.project_root, args.state_dir, args.adapter, args.out)
    elif args.command == 'start':
        result = start(args.plan, args.project_root, args.state_dir, args.adapter, allow_legacy=args.legacy_unprotected)
    elif args.command == '_guard':
        guard(args.config)
        return
    else:
        config = json.loads(Path(args.config).read_text())
        if args.command == '_worker':
            sys.exit(worker(config))
        if args.command == 'cancel':
            Store(Path(config['state_dir']) / 'state.sqlite').cancel(config['run_id'], args.reference)
        result = status(config)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get('status') == 'blocked':
        sys.exit(2)


if __name__ == '__main__':
    main()
