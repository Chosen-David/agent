"""Bounded, deterministic multi-host placement advice. Never reserves or launches.

Inventory/cache claims come from a trusted host snapshot, not from an LLM.
The executor must revalidate and atomically reserve the ENTIRE proposed gang.
SQLite Engine/Mailbox remain local control ledgers, not a network transport.
"""
from __future__ import annotations

import hashlib
from itertools import combinations, islice
import json
import math
import os
from pathlib import Path
import stat


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


def _integer(value, low=0, high=2**63-1):
    return type(value) is int and low <= value <= high


def _real(value, low=0, high=1e15):
    # Compare integer bounds before float conversion inside isfinite: JSON may
    # contain a perfectly valid integer too large to convert to a C double.
    return type(value) in (int, float) and low <= value <= high and math.isfinite(value)


def _strings(value, limit=256):
    return (isinstance(value, list) and len(value) <= limit
            and all(_text(v) for v in value) and len(set(value)) == len(value))


def _sha(value):
    return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    allow_nan=False, separators=(',', ':')).encode()).hexdigest()


def validate_inventory(inventory, now):
    _fields(inventory, ('schema_version', 'observed_at', 'valid_for_seconds', 'hosts', 'links', 'artifacts'))
    _need(inventory['schema_version'] == 'cluster-inventory/v1', 'inventory version')
    _need(_real(now) and _real(inventory['observed_at'])
          and _real(inventory['valid_for_seconds'], 1, 300), 'invalid snapshot time')
    _need(0 <= now - inventory['observed_at'] < inventory['valid_for_seconds'], 'stale/future inventory')
    hosts = inventory['hosts']
    _need(isinstance(hosts, list) and 1 <= len(hosts) <= 32, '1..32 hosts required')
    ids, uuids = set(), set()
    for host in hosts:
        _fields(host, ('host_id', 'cpu_slots', 'ram_bytes', 'disk_bytes', 'gpus', 'capabilities', 'cache'))
        _need(_text(host['host_id']) and host['host_id'] not in ids, 'duplicate/invalid host')
        ids.add(host['host_id'])
        _need(_integer(host['cpu_slots'], 0, 65536) and _integer(host['ram_bytes'])
              and _integer(host['disk_bytes']), 'invalid host capacity')
        _need(_strings(host['capabilities']) and isinstance(host['cache'], dict)
              and len(host['cache']) <= 256, 'invalid capabilities/cache')
        _need(isinstance(host['gpus'], list) and len(host['gpus']) <= 64, 'GPU bound')
        for gpu in host['gpus']:
            _fields(gpu, ('uuid', 'model', 'usable_memory_bytes', 'available', 'fabric'))
            _need(_text(gpu['uuid']) and gpu['uuid'] not in uuids, 'duplicate/invalid GPU UUID')
            _need(not gpu['uuid'].startswith('MIG-'), 'MIG not supported; do not double-count parent devices')
            uuids.add(gpu['uuid'])
            _need(_text(gpu['model']) and _text(gpu['fabric']) and _integer(gpu['usable_memory_bytes'])
                  and type(gpu['available']) is bool, 'invalid GPU properties')
    artifacts = inventory['artifacts']
    _need(isinstance(artifacts, dict) and len(artifacts) <= 256, 'artifact bound')
    for aid, artifact in artifacts.items():
        _fields(artifact, ('sha256', 'size_bytes', 'source_hosts'))
        _need(_text(aid) and _sha(artifact['sha256']) and _integer(artifact['size_bytes'])
              and _strings(artifact['source_hosts'], 32)
              and set(artifact['source_hosts']) <= ids, 'invalid artifact')
    for host in hosts:
        _need(all(a in artifacts and _sha(s) for a, s in host['cache'].items()), 'unknown cache artifact')
        # An advertised source must have the advertised immutable bytes.
        for aid, artifact in artifacts.items():
            if host['host_id'] in artifact['source_hosts']:
                _need(host['cache'].get(aid) == artifact['sha256'], 'source hash mismatch')
    links = inventory['links']
    _need(isinstance(links, list) and len(links) <= 992, 'link bound')
    pairs = set()
    for link in links:
        _fields(link, ('source', 'destination', 'bytes_per_second', 'latency_seconds', 'transport'))
        pair = (link['source'], link['destination'])
        _need(all(_text(x) and x in ids for x in pair) and pair[0] != pair[1]
              and pair not in pairs, 'unknown/duplicate link')
        pairs.add(pair)
        _need(_real(link['bytes_per_second'], 1) and _real(link['latency_seconds'])
              and link['transport'] in ('tcp', 'rdma'), 'invalid link measurement')


def validate_tasks(tasks, inventory):
    _need(isinstance(tasks, list) and len(tasks) <= 256, 'task bound')
    ids = set()
    host_ids = {h['host_id'] for h in inventory['hosts']}
    for task in tasks:
        _fields(task, ('task_id', 'depends_on', 'priority', 'nodes', 'gpus_per_node', 'gpu_models',
                       'gpu_memory_bytes', 'cpu_slots_per_node', 'ram_bytes_per_node', 'scratch_bytes_per_node',
                       'required_capabilities', 'gpu_fabric', 'min_link_bytes_per_second', 'artifacts',
                       'runtime_seconds', 'startup_seconds'))
        _need(_text(task['task_id']) and task['task_id'] not in ids, 'duplicate task')
        ids.add(task['task_id'])
        _need(_strings(task['depends_on']) and task['task_id'] not in task['depends_on'], 'invalid dependencies')
        _need(_integer(task['priority'], 0, 100) and _integer(task['nodes'], 1, 32)
              and _integer(task['gpus_per_node'], 0, 64), 'invalid request cardinality')
        for field in ('gpu_memory_bytes', 'cpu_slots_per_node', 'ram_bytes_per_node', 'scratch_bytes_per_node'):
            _need(_integer(task[field]), 'invalid request capacity')
        _need(task['cpu_slots_per_node'] > 0, 'positive CPU request required')
        _need(_strings(task['gpu_models']) and _strings(task['required_capabilities'])
              and _strings(task['artifacts']) and _text(task['gpu_fabric']), 'invalid request lists')
        _need(set(task['artifacts']) <= inventory['artifacts'].keys(), 'unknown input artifact')
        _need(_real(task['min_link_bytes_per_second'], 1), 'link threshold required')
        _need(isinstance(task['runtime_seconds'], dict) and task['runtime_seconds'].keys() <= host_ids
              and all(_real(v, 0.001, 604800) for v in task['runtime_seconds'].values()), 'runtime estimates required')
        _need(_real(task['startup_seconds'], 0, 604800), 'invalid startup estimate')
        if task['gpus_per_node']:
            _need(task['gpu_memory_bytes'] > 0, 'explicit per-GPU memory required')
        else:
            _need(task['nodes'] == 1 and task['gpu_memory_bytes'] == 0, 'CPU-only multi-node unsupported')
    # External dependencies may be supplied as independently verified IDs.
    remaining = {t['task_id']: set(t['depends_on']) & ids for t in tasks}
    while remaining:
        ready = {i for i, deps in remaining.items() if not deps}
        _need(bool(ready), 'dependency cycle')
        remaining = {i: deps - ready for i, deps in remaining.items() if i not in ready}


def plan_wave(inventory, tasks, *, verified_task_ids, now, max_inflight=8, candidate_limit=1024):
    """Place one ready wave. Caller supplies trusted verified IDs, NOT job pass flags.

    Per-host GPU selection is first-fit within each (model, fabric) group. Host
    combinations are capped; a cap hit blocks that task with search-limit, never
    reports infeasible or silently returns a purported optimal partial search.
    No shared staging-cache prediction or live resource lease is implied.
    """
    validate_inventory(inventory, now)
    validate_tasks(tasks, inventory)
    _need(_strings(verified_task_ids, 4096), 'verified ID list required')
    _need(_integer(max_inflight, 1, 256) and _integer(candidate_limit, 1, 4096), 'invalid planning bounds')
    verified = set(verified_task_ids)
    hosts = {h['host_id']: h for h in inventory['hosts']}
    links = {(l['source'], l['destination']): l for l in inventory['links']}
    free = {hid: {'cpu': h['cpu_slots'], 'ram': h['ram_bytes'], 'disk': h['disk_bytes']} for hid, h in hosts.items()}
    used, placements, blocked = set(), [], []
    for task in sorted(tasks, key=lambda t: (-t['priority'], t['task_id'])):
        tid = task['task_id']
        if tid in verified:
            continue
        if not set(task['depends_on']) <= verified:
            blocked.append({'task_id': tid, 'reason': 'dependencies-unverified'})
            continue
        if len(placements) >= max_inflight:
            blocked.append({'task_id': tid, 'reason': 'wave-limit'})
            continue
        groups = {}
        for hid, host in sorted(hosts.items()):
            if hid not in task['runtime_seconds'] or not set(task['required_capabilities']) <= set(host['capabilities']):
                continue
            if task['nodes'] > 1 and 'distributed' not in host['capabilities']:
                continue
            f = free[hid]
            if f['cpu'] < task['cpu_slots_per_node'] or f['ram'] < task['ram_bytes_per_node']:
                continue
            if not task['gpus_per_node']:
                groups.setdefault(('cpu', 'none'), {})[hid] = []
                continue
            local = {}
            for gpu in sorted(host['gpus'], key=lambda g: g['uuid']):
                if (gpu['available'] and gpu['uuid'] not in used
                        and gpu['usable_memory_bytes'] >= task['gpu_memory_bytes']
                        and (not task['gpu_models'] or gpu['model'] in task['gpu_models'])
                        and (task['gpu_fabric'] == 'any' or gpu['fabric'] == task['gpu_fabric'])):
                    local.setdefault((gpu['model'], gpu['fabric']), []).append(gpu['uuid'])
            for key, devices in local.items():
                if len(devices) >= task['gpus_per_node']:
                    groups.setdefault(key, {})[hid] = devices[:task['gpus_per_node']]
        candidates, scanned, exhausted = [], 0, False
        for key, options in sorted(groups.items()):
            combos = combinations(sorted(options), task['nodes'])
            for chosen in islice(combos, candidate_limit + 1):
                scanned += 1
                if scanned > candidate_limit:
                    exhausted = True
                    break
                if task['nodes'] > 1 and any((a, b) not in links or links[a, b]['transport'] != 'rdma'
                        or links[a, b]['bytes_per_second'] < task['min_link_bytes_per_second']
                        for a in chosen for b in chosen if a != b):
                    continue
                transfers, disk, staging = [], {}, 0.0
                feasible = True
                for hid in chosen:
                    disk[hid] = task['scratch_bytes_per_node']
                    for aid in task['artifacts']:
                        art = inventory['artifacts'][aid]
                        if hosts[hid]['cache'].get(aid) == art['sha256']:
                            continue
                        disk[hid] += art['size_bytes']
                        routes = [(links[s, hid]['latency_seconds'] + art['size_bytes'] / links[s, hid]['bytes_per_second'], s)
                                  for s in art['source_hosts'] if (s, hid) in links]
                        if not routes:
                            feasible = False
                            break
                        seconds, source = min(routes)
                        staging += seconds
                        transfers.append({'artifact_id': aid, 'sha256': art['sha256'], 'size_bytes': art['size_bytes'],
                                          'source_host': source, 'destination_host': hid, 'estimated_seconds': seconds})
                    if disk[hid] > free[hid]['disk']:
                        feasible = False
                    if not feasible:
                        break
                if not feasible:
                    continue
                estimate = max(task['runtime_seconds'][hid] for hid in chosen) + task['startup_seconds'] + staging
                candidates.append((estimate, chosen, key, transfers, disk, options))
            if exhausted:
                break
        if exhausted or not candidates:
            blocked.append({'task_id': tid, 'reason': 'search-limit' if exhausted else 'no-feasible-candidate',
                            'candidates_scanned': min(scanned, candidate_limit)})
            continue
        estimate, chosen, key, transfers, disk, options = min(candidates, key=lambda c: (c[0], c[1], c[2]))
        allocations = []
        for hid in chosen:
            devices = options[hid]
            used.update(devices)
            free[hid]['cpu'] -= task['cpu_slots_per_node']
            free[hid]['ram'] -= task['ram_bytes_per_node']
            free[hid]['disk'] -= disk[hid]
            allocations.append({'host_id': hid, 'gpu_uuids': list(devices), 'cpu_slots': task['cpu_slots_per_node'],
                                'ram_bytes': task['ram_bytes_per_node'], 'disk_bytes': disk[hid]})
        placements.append({'task_id': tid, 'allocations': allocations, 'transfers': transfers,
                           'estimated_seconds': estimate, 'gang': task['nodes'] * task['gpus_per_node'] > 1,
                           'gpu_model': key[0]})
    return {'schema_version': 'cluster-placement/v1', 'status': 'advisory-only',
            'inventory_sha256': digest(inventory), 'tasks_sha256': digest(tasks),
            'verified_task_ids_sha256': digest(verified_task_ids), 'planned_at': now,
            'expires_at': inventory['observed_at'] + inventory['valid_for_seconds'],
            'placements': placements, 'blocked': blocked,
            'limitations': ['No reservations, remote jobs or network transfers executed.',
                            'Greedy ready wave; first-fit devices; serial staging estimates; no optimality or makespan guarantee.',
                            'Whole GPUs only; distributed groups require homogeneous model/fabric and directed RDMA links.',
                            'Host must check permissions, versions, current capacity, data hashes and full gang admission before submit.']}


def verify_local_artifact(path, *, sha256, size_bytes, max_bytes=16 * 1024**3):
    """Stream a regular local file under a caller-selected byte cap, no fetch/exec.

    Use a host-owned staging directory; this check does not publish immutable
    cache state or protect against same-user writes after it returns.
    """
    _need(_sha(sha256) and _integer(size_bytes) and _integer(max_bytes, 1)
          and size_bytes <= max_bytes, 'invalid artifact bounds')
    path = Path(path).absolute()
    _need(not any(p.is_symlink() for p in (path, *path.parents)), 'symlink path rejected')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        before = os.fstat(stream.fileno())
        _need(stat.S_ISREG(before.st_mode) and before.st_size == size_bytes, 'not regular file or size mismatch')
        result, count = hashlib.sha256(), 0
        while chunk := stream.read(min(1024 * 1024, max_bytes - count + 1)):
            count += len(chunk)
            _need(count <= max_bytes, 'stream size bound exceeded')
            result.update(chunk)
        after = os.fstat(stream.fileno())
    _need(count == size_bytes and result.hexdigest() == sha256, 'artifact hash/size mismatch')
    _need((before.st_size, before.st_mtime_ns, before.st_ctime_ns) ==
          (after.st_size, after.st_mtime_ns, after.st_ctime_ns), 'artifact changed during verification')
    return {'sha256': sha256, 'size_bytes': count, 'status': 'bytes-verified'}
