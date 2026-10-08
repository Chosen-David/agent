#!/usr/bin/env python3
"""Read-only single-GPU sweep packing advice. stdout is JSON; never submits jobs."""
import argparse
import json
import os
from pathlib import Path
import stat
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_runtime.ep_packing import PlanningError, plan_packing


def _read(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > 2 * 1024 * 1024:
            raise PlanningError('input must be regular file <=2MiB')
        raw = stream.read(2 * 1024 * 1024 + 1)
    if len(raw) > 2 * 1024 * 1024:
        raise PlanningError('input exceeds 2MiB')

    def pairs(items):
        obj = {}
        for k, v in items:
            if k in obj:
                raise PlanningError('duplicate JSON key')
            obj[k] = v
        return obj
    return json.loads(raw, object_pairs_hook=pairs)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    plan = commands = parser.add_subparsers(dest='command', required=True).add_parser('plan')
    plan.add_argument('--input', required=True, help='inventory/jobs/verified_job_ids JSON')
    plan.add_argument('--now', type=float, help='fixture replay timestamp; default current time')
    plan.add_argument('--max-placements', type=int, default=4096)
    args = parser.parse_args(argv)
    try:
        data = _read(args.input)
        if not isinstance(data, dict) or set(data) != {'inventory', 'jobs', 'verified_job_ids'}:
            raise PlanningError('expected inventory/jobs/verified_job_ids')
        result = plan_packing(**data, now=time.time() if args.now is None else args.now,
                              max_placements=args.max_placements)
    except (ValueError, OSError, TypeError, KeyError, RecursionError, OverflowError) as exc:
        print(json.dumps({'status': 'invalid', 'reason': str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
