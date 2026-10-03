#!/usr/bin/env python3
"""Optional trusted Python runner adapter. CLI only plans or generates a scaffold."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import csv
import hashlib
import io
import json
import math
import os
import re
from pathlib import Path
import time

import experiment


class Blocked(RuntimeError):
    pass


class BatchOOM(RuntimeError):
    """Adapter translates only an identified device allocation OOM to this type."""


def inventory(observation, now=None, max_age=10):
    """Fail closed on stale, incomplete, or unsupported nvidia-smi observations."""
    now = time.time() if now is None else now
    if type(observation) is not dict or type(observation.get('observed_at')) not in (int, float):
        raise Blocked('missing observation time')
    age = now - observation['observed_at']
    if not math.isfinite(age) or not 0 <= age <= max_age:
        raise Blocked('stale or future resource observation')
    gpu = observation.get('gpu')
    if type(gpu) is not dict or any(type(gpu.get(k)) is not dict or gpu[k].get('status') != 'observed' for k in ('devices', 'processes')):
        raise Blocked('device/process visibility unavailable')
    def table(key, headers):
        text = gpu[key].get('csv')
        if type(text) is not str:
            raise ValueError()
        rows = [[v.strip() for v in row] for row in csv.reader(io.StringIO(text))]
        if not rows or rows[0] != headers:
            raise ValueError()
        return rows[1:]
    def number(value, unit):
        if not re.fullmatch(r'[0-9]+(?:\.[0-9]+)? ' + re.escape(unit), value):
            raise ValueError()
        return float(value.split()[0])
    try:
        devices = {}
        for row in table('devices', ['uuid','name','driver_version','utilization.gpu [%]','memory.used [MiB]','memory.total [MiB]']):
            uuid, name, driver, util, used, total = row
            numbers = [number(util, '%'), number(used, 'MiB'), number(total, 'MiB')]
            if not uuid.startswith('GPU-') or uuid in devices or any(not math.isfinite(v) for v in numbers):
                raise ValueError()
            if not 0 <= numbers[0] <= 100 or not 0 <= numbers[1] <= numbers[2]:
                raise ValueError()
            devices[uuid] = dict(uuid=uuid, name=name, driver=driver, utilization=numbers[0],
                                 free_mib=numbers[2]-numbers[1], pids=[])
        for row in table('processes', ['gpu_uuid','pid','used_gpu_memory [MiB]']):
            uuid, pid, memory = row
            if uuid not in devices or not pid.isdecimal() or int(pid) <= 0:
                raise ValueError()
            number(memory, 'MiB')
            devices[uuid]['pids'].append(int(pid))
        if not devices:
            raise ValueError()
    except (ValueError, KeyError, TypeError, csv.Error):
        raise Blocked('unsupported or incomplete GPU inventory (including MIG); use scheduler-specific adapter') from None
    return devices


def request(value):
    required = {'mode', 'authorized_devices', 'sample_ids', 'seed', 'batch_size', 'min_free_mib', 'max_utilization', 'protocol_sha256', 'warmup', 'repeats'}
    if type(value) is not dict or set(value) != required:
        raise ValueError('request must contain exactly ' + ', '.join(sorted(required)))
    r = dict(value)
    if r['mode'] not in ('accuracy', 'performance'):
        raise ValueError('invalid mode')
    for key, lo, hi in [('seed', 0, 2**32-1), ('batch_size', 1, 4096), ('min_free_mib', 1, 1000000), ('max_utilization', 0, 100), ('warmup', 1, 100), ('repeats', 2, 1000)]:
        if type(r[key]) is not int or not lo <= r[key] <= hi:
            raise ValueError('invalid ' + key)
    for key in ('authorized_devices', 'sample_ids'):
        xs = r[key]
        if type(xs) is not list or not xs or len(xs) > (16 if key == 'authorized_devices' else 100000):
            raise ValueError('invalid ' + key)
        if any(type(x) is not str or not x or len(x) > 200 for x in xs) or len(set(xs)) != len(xs):
            raise ValueError('invalid/duplicate ' + key)
    if type(r['protocol_sha256']) is not str or len(r['protocol_sha256']) != 64 or any(c not in '0123456789abcdef' for c in r['protocol_sha256']):
        raise ValueError('protocol_sha256 required')
    if r['mode'] == 'performance' and len(r['authorized_devices']) != 1:
        raise ValueError('performance adapter supports one device; no concurrent baselines')
    return r


def plan(value, observation):
    r = request(value)
    try:
        devices = inventory(observation)
        eligible = [u for u in r['authorized_devices'] if u in devices and not devices[u]['pids']
                    and devices[u]['free_mib'] >= r['min_free_mib'] and devices[u]['utilization'] <= r['max_utilization']]
        if r['mode'] == 'performance' and eligible != r['authorized_devices']:
            raise Blocked('performance device is busy, unavailable, or outside memory budget')
        if not eligible:
            raise Blocked('no eligible authorized device')
        eligible = eligible[:len(r['sample_ids'])]
        shards = {u: r['sample_ids'][i::len(eligible)] for i, u in enumerate(eligible)}
        return {'status': 'planned_not_reserved', 'request': r, 'shards': shards,
                'requires': 'trusted runner, current authorization, live pre/post probes; performance also scheduler exclusion',
                'reservation': 'none', 'visibility': 'compute_processes_only; not proof of idle GPU', 'evidence': observation}
    except Blocked as exc:
        return {'status': 'blocked', 'reason': str(exc), 'shards': {}}


@contextmanager
def cooperative_lease(directory, devices):
    """Same-host flock, same directory only; never excludes nonparticipants."""
    try:
        import fcntl
    except ImportError:
        raise Blocked('local cooperative lease requires POSIX flock') from None
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    handles = []
    try:
        for uuid in sorted(devices):
            path = root / (hashlib.sha256(uuid.encode()).hexdigest() + '.lock')
            fd = os.open(path, os.O_CREAT | os.O_RDWR | getattr(os, 'O_NOFOLLOW', 0), 0o600)
            handles.append(fd)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise Blocked('cooperating job already holds ' + uuid) from None
        yield
    finally:
        for fd in reversed(handles):
            os.close(fd)
        # Never unlink: another process may already be waiting on this inode.


def run(value, adapter, lease_dir, observe=None):
    """Explicit host API only. Adapter is trusted code, never imported from request JSON.

    Required adapter methods: authorize(request, uuids), capabilities(),
    owns_exclusive_allocation(uuids), verify_admission(request, uuids),
    known_pids(), evaluate(uuid, ids, seeds, batch),
    run_variant(uuid, variant, seed), synchronize(uuid), equivalent(a, b).
    Only the methods for the chosen mode are called. Callbacks are host evidence,
    not user-supplied booleans. Deadlines/cancellation belong to the host runner.
    """
    r = request(value)
    observe = observe or (lambda: experiment.probe(gpu=True))
    # No probing or allocation until a live host authorization check passes.
    if adapter.authorize(r, r['authorized_devices']) is not True:
        raise Blocked('host authorization unavailable')
    caps = adapter.capabilities()
    if (type(caps) is not dict or caps.get('ready') is not True
            or r['mode'] not in caps.get('modes', [])
            or caps.get('protocol_sha256') != r['protocol_sha256']
            or not isinstance(caps.get('id'), str) or not caps['id']):
        raise Blocked('runner capability unavailable')
    p = plan(r, observe())
    if p['status'] == 'blocked':
        raise Blocked(p['reason'])
    uuids = list(p['shards'])
    checks = []
    def guard(start=False):
        if adapter.authorize(r, uuids) is not True:
            raise Blocked('authorization revoked')
        if r['mode'] == 'performance' and adapter.owns_exclusive_allocation(uuids) is not True:
            raise Blocked('performance requires verified external scheduler exclusion')
        admission = adapter.verify_admission(r, uuids)
        if (type(admission) is not dict or admission.get('allowed') is not True
                or not isinstance(admission.get('source'), str) or not admission['source']
                or type(admission.get('observed_at')) not in (int, float)
                or not 0 <= time.time() - admission['observed_at'] <= 10):
            raise Blocked('full resource visibility/admission unavailable or stale')
        observed = observe()
        current = inventory(observed)
        own = set() if start else set(adapter.known_pids())
        for u in uuids:
            if u not in current or set(current[u]['pids']) - own:
                raise Blocked('external process or missing device during run')
            if start and (current[u]['free_mib'] < r['min_free_mib'] or current[u]['utilization'] > r['max_utilization']):
                raise Blocked('resource changed before execution')
        checks.append({'observation': observed, 'host_admission': admission,
                       'scheduler_exclusion_checked': r['mode'] == 'performance'})
    with cooperative_lease(lease_dir, uuids):
        guard(start=True)  # Close the cooperative planner/acquire race with a fresh observation.
        events = []
        if r['mode'] == 'accuracy':
            def shard(u):
                ids = p['shards'][u]
                rows, retries = [], []
                size = r['batch_size']
                while len(rows) < len(ids):
                    guard()
                    pending = ids[len(rows):len(rows)+size]
                    seeds = [int(hashlib.sha256((str(r['seed'])+'\0'+sid).encode()).hexdigest()[:8], 16) for sid in pending]
                    try:
                        got = adapter.evaluate(u, pending, seeds, size)
                    except BatchOOM:
                        retries.append({'device': u, 'event': 'identified_oom', 'batch_size': size})
                        if size == 1:
                            raise
                        size = max(1, size//2)
                        continue
                    if type(got) is not list or any(type(x) is not dict or set(x) != {'id', 'prediction'} for x in got):
                        raise ValueError('runner output schema mismatch')
                    if [x['id'] for x in got] != pending:
                        raise ValueError('runner output ID/order/coverage mismatch')
                    json.dumps(got, allow_nan=False)
                    rows.extend(got)
                return rows, retries
            with ThreadPoolExecutor(max_workers=len(uuids)) as pool:
                results = list(pool.map(shard, uuids))
            by_id = {row['id']:row for rows, _ in results for row in rows}
            output = {'rows': [by_id[i] for i in r['sample_ids']]}
            events = [event for _, retries in results for event in retries]
        else:
            u = uuids[0]
            pairs = []
            for i in range(r['warmup'] + r['repeats']):
                guard()
                values, elapsed = {}, {}
                for variant in (('baseline', 'candidate') if i%2 == 0 else ('candidate', 'baseline')):
                    adapter.synchronize(u)
                    start = time.perf_counter_ns()
                    values[variant] = adapter.run_variant(u, variant, r['seed'])
                    adapter.synchronize(u)
                    elapsed[variant] = time.perf_counter_ns()-start
                if adapter.equivalent(values['baseline'], values['candidate']) is not True:
                    raise ValueError('baseline/candidate correctness failed')
                if i >= r['warmup']:
                    pairs.append(elapsed)
            output = {'steady_pairs_ns': pairs, 'timing': 'synchronized wallclock; runner scope, not kernel-only CUDA events'}
        guard()
    return {'status': 'completed', 'request': r, 'request_sha256': experiment.digest(r),
            'runner': caps, 'plan': p, 'output': output, 'events': events, 'resource_checks': checks,
            'resource_limit': 'cooperative same-host lease; snapshots cannot exclude between-probe external activity',
            'claim': 'runner output; host must validate metrics, exclusion and workload protocol before scientific claims'}


SCAFFOLD = '''# Generated integration stub, not an executable model implementation.
# Fill this in using the project's existing runner; never load untrusted adapters.
from gpu_adapter import run, BatchOOM

class ProjectAdapter:
    def authorize(self, request, uuids):
        return False  # Bind current host authorization, including cancellation/deadline.
    def capabilities(self):
        return {"ready": False, "modes": [], "reason": "project runner not configured"}
    def owns_exclusive_allocation(self, uuids):
        return False  # Verify live scheduler allocation, not a local lock or idle snapshot.
    def verify_admission(self, request, uuids):
        return {"allowed": False, "source": "full process visibility/quota/memory admission not configured", "observed_at": 0}
    def known_pids(self):
        return []  # Only verified processes owned by this run.
    def evaluate(self, uuid, ids, seeds, batch_size):
        raise NotImplementedError("Return ordered {id, prediction}; translate only known OOM to BatchOOM")
    def synchronize(self, uuid):
        raise NotImplementedError("Use runner/device-specific synchronization")
    def run_variant(self, uuid, variant, seed):
        raise NotImplementedError("Same immutable workload for baseline/candidate")
    def equivalent(self, baseline, candidate):
        raise NotImplementedError("Independent task-specific correctness/tolerance")

if __name__ == "__main__":
    raise SystemExit("blocked: configure a trusted project runner and invoke the host API explicitly")
'''


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['plan', 'scaffold'])
    p.add_argument('--request', type=Path)
    p.add_argument('--snapshot', type=Path)
    p.add_argument('--output', type=Path)
    a = p.parse_args()
    if a.action == 'scaffold':
        if not a.output:
            p.error('--output required')
        with a.output.open('x') as f:
            f.write(SCAFFOLD)
    else:
        if not a.request or not a.snapshot:
            p.error('--request and --snapshot required (no implicit GPU probe)')
        print(json.dumps(plan(experiment.load(a.request), experiment.load(a.snapshot)), indent=2))


if __name__ == '__main__':
    main()
