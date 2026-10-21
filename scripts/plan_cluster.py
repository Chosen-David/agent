#!/usr/bin/env python3
"""Read-only cluster advice. stdout is JSON; never submits jobs or fetches data."""
import argparse
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_runtime.cluster_planning import PlanningError, plan_wave, verify_local_artifact
from agent_runtime.external_json import load_json


def _read(path):
    return load_json(path, max_bytes=2 * 1024 * 1024)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    plan = commands.add_parser('plan')
    plan.add_argument('--input', required=True, help='inventory/tasks/verified_task_ids JSON')
    plan.add_argument('--now', type=float, help='fixture replay timestamp; default current time')
    plan.add_argument('--max-inflight', type=int, default=8)
    plan.add_argument('--candidate-limit', type=int, default=1024)
    verify = commands.add_parser('verify-file')
    verify.add_argument('--path', required=True)
    verify.add_argument('--sha256', required=True)
    verify.add_argument('--size-bytes', type=int, required=True)
    verify.add_argument('--max-bytes', type=int, default=16 * 1024**3)
    args = parser.parse_args(argv)
    try:
        if args.command == 'plan':
            data = _read(args.input)
            if not isinstance(data, dict) or set(data) != {'inventory', 'tasks', 'verified_task_ids'}:
                raise PlanningError('expected inventory/tasks/verified_task_ids')
            result = plan_wave(**data, now=time.time() if args.now is None else args.now,
                               max_inflight=args.max_inflight, candidate_limit=args.candidate_limit)
        else:
            result = verify_local_artifact(args.path, sha256=args.sha256, size_bytes=args.size_bytes,
                                           max_bytes=args.max_bytes)
    except (ValueError, OSError, TypeError, KeyError, RecursionError, OverflowError) as exc:
        print(json.dumps({'status': 'invalid', 'reason': str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
