"""Portable command interface; no arbitrary plan-provided shell execution."""
import argparse
import json
from pathlib import Path
import signal
import uuid

from .core import ArtifactHandler, Engine, Store
from .scheduler import LocalScheduler, arm


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', required=True)
    parser.add_argument('--legacy-unprotected', action='store_true', help='explicit trusted compatibility; no independent main review')
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('init'); p.add_argument('plan')
    for command in ('status', 'arm', 'cancel', 'wake', 'tick'):
        p = sub.add_parser(command); p.add_argument('run_id')
        if command in ('cancel', 'wake'):
            p.add_argument('--reference', required=True)
        if command == 'tick':
            p.add_argument('--artifact-root', required=True)
            p.add_argument('--event-id', default=None)
    sub.add_parser('capabilities')
    p = sub.add_parser('serve')
    p.add_argument('--artifact-root', required=True)
    p.add_argument('--max-seconds', type=float, default=None)
    args = parser.parse_args()
    store = Store(args.db)
    scheduler = LocalScheduler(store)
    if args.command in ('tick', 'serve'):
        # CLI only authorizes the read-only built-in inside the explicit root.
        # Adding capabilities to a task JSON cannot authorize commands/tools.
        handler = ArtifactHandler(args.artifact_root)
        engine = Engine(store, {'verify_artifacts': handler},
                        authorize=lambda plan, task, adapter: adapter is handler, allow_legacy=args.legacy_unprotected)
    if args.command == 'init':
        result = {'run_id': store.create(json.loads(Path(args.plan).read_text()))}
    elif args.command == 'status':
        result = store.snapshot(args.run_id)
        if result['monitor']:
            result['monitor'] = scheduler.read(result['monitor']['id'])
    elif args.command == 'capabilities':
        result = scheduler.capabilities()
    elif args.command == 'arm':
        result = arm(scheduler, args.run_id)
    elif args.command == 'cancel':
        store.cancel(args.run_id, args.reference)
        result = store.snapshot(args.run_id)
    elif args.command == 'wake':
        scheduler.wake(args.run_id, args.reference)
        result = store.snapshot(args.run_id)
    elif args.command == 'tick':
        result = engine.tick(args.run_id, args.event_id or 'manual:' + uuid.uuid4().hex)
    else:
        stopped = []
        signal.signal(signal.SIGTERM, lambda *_: stopped.append(True))
        signal.signal(signal.SIGINT, lambda *_: stopped.append(True))
        scheduler.serve(engine, lambda: bool(stopped), args.max_seconds)
        result = {'status': 'serve_stopped', 'capabilities': scheduler.capabilities()}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
