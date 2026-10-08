"""Bounded advisory packing for embarrassingly parallel single-GPU jobs.

Fractional GPU sharing: one GPU may host several jobs while summed memory
stays within usable memory; exclusive jobs reserve the whole GPU. Ready jobs
are placed longest-estimated-first (LPT) onto the feasible GPU with the
smallest projected serial load. Advisory only: this module never reserves,
connects, launches, or transfers anything. Completion IDs come from trusted
independent acceptance, never from worker self-reports.
"""
from __future__ import annotations

import hashlib
import json
import math


class PlanningError(ValueError):
    pass


def _need(ok, message):
    if not ok:
        raise PlanningError(message)


def _fields(obj, required, optional=()):
    _need(isinstance(obj, dict) and set(required) <= obj.keys()
          and obj.keys() <= set(required) | set(optional), 'missing/unknown fields')


def _text(value):
    return isinstance(value, str) and 0 < len(value) <= 512 and value.strip() == value


def _integer(value, low=0, high=2**63 - 1):
    return type(value) is int and low <= value <= high


def _real(value, low=0, high=1e15):
    return type(value) in (int, float) and low <= value <= high and math.isfinite(value)


def _strings(value, limit=4096):
    return (isinstance(value, list) and len(value) <= limit
            and all(_text(v) for v in value) and len(set(value)) == len(value))


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    allow_nan=False, separators=(',', ':')).encode()).hexdigest()


def validate_inventory(inventory, now):
    _fields(inventory, ('schema_version', 'observed_at', 'valid_for_seconds', 'hosts'))
    _need(inventory['schema_version'] == 'ep-inventory/v1', 'inventory version')
    _need(_real(now) and _real(inventory['observed_at'])
          and _real(inventory['valid_for_seconds'], 1, 300), 'invalid snapshot time')
    _need(0 <= now - inventory['observed_at'] < inventory['valid_for_seconds'],
          'stale/future inventory')
    hosts = inventory['hosts']
    _need(isinstance(hosts, list) and 1 <= len(hosts) <= 32, '1..32 hosts required')
    ids, uuids = set(), set()
    for host in hosts:
        _fields(host, ('host_id', 'gpus'))
        _need(_text(host['host_id']) and host['host_id'] not in ids, 'duplicate/invalid host')
        ids.add(host['host_id'])
        _need(isinstance(host['gpus'], list) and 1 <= len(host['gpus']) <= 64, 'GPU bound')
        for gpu in host['gpus']:
            _fields(gpu, ('uuid', 'model', 'usable_memory_bytes', 'in_use_memory_bytes',
                          'available', 'shared_ok'))
            _need(_text(gpu['uuid']) and gpu['uuid'] not in uuids, 'duplicate/invalid GPU UUID')
            _need(not gpu['uuid'].startswith('MIG-'), 'MIG not supported')
            uuids.add(gpu['uuid'])
            _need(_text(gpu['model']) and _integer(gpu['usable_memory_bytes'], 1)
                  and _integer(gpu['in_use_memory_bytes'])
                  and gpu['in_use_memory_bytes'] <= gpu['usable_memory_bytes']
                  and type(gpu['available']) is bool and type(gpu['shared_ok']) is bool,
                  'invalid GPU properties')
    return ids


def validate_jobs(jobs):
    _need(isinstance(jobs, list) and len(jobs) <= 4096, 'job bound')
    ids = set()
    for job in jobs:
        _fields(job, ('job_id', 'depends_on', 'priority', 'memory_bytes', 'exclusive',
                      'est_seconds', 'gpu_models'))
        _need(_text(job['job_id']) and job['job_id'] not in ids, 'duplicate job')
        ids.add(job['job_id'])
        _need(_strings(job['depends_on'], 256) and job['job_id'] not in job['depends_on'],
              'invalid dependencies')
        _need(_integer(job['priority'], 0, 100) and _integer(job['memory_bytes'], 1)
              and type(job['exclusive']) is bool
              and _real(job['est_seconds'], 0.001, 604800), 'invalid job request')
        _need(_strings(job['gpu_models'], 16), 'invalid gpu_models')
    remaining = {j['job_id']: set(j['depends_on']) & ids for j in jobs}
    while remaining:
        ready = {i for i, deps in remaining.items() if not deps}
        _need(bool(ready), 'dependency cycle')
        remaining = {i: deps - ready for i, deps in remaining.items() if i not in ready}
    return ids


def plan_packing(inventory, jobs, *, verified_job_ids, now, max_placements=4096):
    """Pack one ready set of independent single-GPU jobs onto fractional slots.

    LPT order (long est_seconds first, then priority, then id); each job goes
    to the feasible GPU with the smallest projected serial load
    (in_use_seconds is not observable here, so load counts this wave only).
    Exclusive jobs require an untouched GPU; shared jobs require shared_ok and
    summed memory within usable. Estimates assume the caller's per-job
    exclusive-execution seconds; co-location slowdown is NOT modeled and must
    be calibrated by the executor.
    """
    validate_inventory(inventory, now)
    job_ids = validate_jobs(jobs)
    _need(_strings(verified_job_ids), 'verified ID list required')
    _need(_integer(max_placements, 1, 4096), 'invalid placement bound')
    verified = set(verified_job_ids)
    gpus = []  # (host_id, gpu dict)
    for host in sorted(inventory['hosts'], key=lambda h: h['host_id']):
        for gpu in sorted(host['gpus'], key=lambda g: g['uuid']):
            gpus.append((host['host_id'], gpu))
    load = {g['uuid']: 0.0 for _, g in gpus}          # 本波次分配串行秒
    mem = {g['uuid']: g['in_use_memory_bytes'] for _, g in gpus}
    share = {g['uuid']: 0 for _, g in gpus}           # 本波次共享 job 数
    exclusive_taken = set()
    placements, blocked = [], []
    ready = [j for j in jobs if j['job_id'] not in verified]
    for job in sorted(ready, key=lambda j: (-j['est_seconds'], -j['priority'], j['job_id'])):
        jid = job['job_id']
        if not set(job['depends_on']) <= verified:
            blocked.append({'job_id': jid, 'reason': 'dependencies-unverified'})
            continue
        if len(placements) >= max_placements:
            blocked.append({'job_id': jid, 'reason': 'wave-limit'})
            continue
        best = None
        for host_id, gpu in gpus:
            uid = gpu['uuid']
            if not gpu['available'] or (job['gpu_models'] and gpu['model'] not in job['gpu_models']):
                continue
            if job['exclusive']:
                if uid in exclusive_taken or share[uid] or mem[uid] > 0:
                    continue
                projected = mem[uid] + job['memory_bytes']
            else:
                if not gpu['shared_ok'] or uid in exclusive_taken:
                    continue
                projected = mem[uid] + job['memory_bytes']
                if projected > gpu['usable_memory_bytes']:
                    continue
            if job['memory_bytes'] > gpu['usable_memory_bytes']:
                continue
            key = (load[uid], uid)
            if best is None or key < best[0]:
                best = (key, host_id, gpu, projected)
        if best is None:
            exceeds = all(job['memory_bytes'] > g['usable_memory_bytes'] for _, g in gpus)
            blocked.append({'job_id': jid,
                            'reason': 'memory-exceeds-any-gpu' if exceeds else 'no-feasible-gpu'})
            continue
        _, host_id, gpu, projected = best
        uid = gpu['uuid']
        if job['exclusive']:
            exclusive_taken.add(uid)
        mem[uid] = projected
        load[uid] += job['est_seconds']
        share[uid] += 1
        placements.append({'job_id': jid, 'host_id': host_id, 'gpu_uuid': uid,
                           'share_group_size': share[uid], 'exclusive': job['exclusive'],
                           'gpu_serial_seconds': round(load[uid], 3),
                           'gpu_memory_bytes': mem[uid]})
    return {'schema_version': 'ep-placement/v1', 'status': 'advisory-only',
            'inventory_sha256': digest(inventory), 'jobs_sha256': digest(jobs),
            'verified_job_ids_sha256': digest(sorted(verified_job_ids)),
            'planned_at': now,
            'expires_at': inventory['observed_at'] + inventory['valid_for_seconds'],
            'placements': placements, 'blocked': blocked,
            'limitations': ['No reservations, remote jobs or transfers executed; atomic slot admission is the executor\'s duty.',
                            'LPT heuristic over one ready wave; not a makespan guarantee.',
                            'est_seconds are exclusive-execution estimates; co-location slowdown is NOT modeled.',
                            'Idle-looking GPUs may serve jobs outside this wave; executor must re-probe before submit.']}
