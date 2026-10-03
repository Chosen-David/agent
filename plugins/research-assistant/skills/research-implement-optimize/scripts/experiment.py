#!/usr/bin/env python3
"""Portable experiment admission and CPU synthetic receipts; no external job launcher."""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import statistics
import subprocess
import time


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def parse(text):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def load(path):
    return parse(Path(path).read_text())


def probe(gpu=False):
    """Observation is not ownership, reservation, idle proof, or execution permission."""
    result = {'observed_at': time.time(), 'python': platform.python_version(),
              'platform': ' '.join([platform.system(), platform.release(), platform.machine()]), 'cpu_count': os.cpu_count(),
              'affinity_count': len(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else os.cpu_count(),
              'load_average': list(os.getloadavg()) if hasattr(os, 'getloadavg') else None,
              'ownership': 'unknown', 'reservation': 'none', 'gpu': 'not_queried'}
    if gpu:
        result['gpu'] = {}
        for name, query in [('devices', '--query-gpu=uuid,name,driver_version,utilization.gpu,memory.used,memory.total'),
                            ('processes', '--query-compute-apps=gpu_uuid,pid,used_gpu_memory')]:
            try:
                p = subprocess.run(['nvidia-smi', query, '--format=csv'], capture_output=True,
                                   text=True, timeout=5, check=False)
                result['gpu'][name] = {'status': 'observed' if p.returncode == 0 else 'unknown',
                                       'csv': p.stdout if p.returncode == 0 else '', 'returncode': p.returncode}
            except (OSError, subprocess.TimeoutExpired):
                result['gpu'][name] = {'status': 'unknown'}
    return result


DEFAULT = {'mode': 'accuracy', 'device': 'cpu', 'workers': 1, 'samples': 16,
           'size': 1000, 'seed': 7, 'warmup': 2, 'repeats': 10, 'batch_size': 4}


def config(value):
    if type(value) is not dict or set(value) - set(DEFAULT):
        raise ValueError('unknown config field or non-object')
    c = DEFAULT | value
    if c['mode'] not in ('accuracy', 'performance') or c['device'] not in ('cpu', 'gpu'):
        raise ValueError('unsupported mode/device')
    for key, lo, hi in [('workers', 1, 8), ('samples', 1, 1000), ('size', 1, 100000),
                        ('seed', 0, 2**32-1), ('warmup', 1, 100), ('repeats', 2, 1000), ('batch_size', 1, 1000)]:
        if type(c[key]) is not int or not lo <= c[key] <= hi:
            raise ValueError('invalid ' + key)
    if c['samples'] * c['size'] > 10000000 or c['size'] * (c['repeats'] + c['warmup']) > 10000000:
        raise ValueError('synthetic work budget exceeded')
    if c['mode'] == 'performance' and c['workers'] != 1:
        raise ValueError('performance requires serial paired measurement')
    return c


def plan(c, observation):
    c = config(c)
    workers = min(c['workers'], observation.get('affinity_count') or 1, c['samples'])
    return {'config': c, 'config_sha256': digest(c), 'workers': workers,
            'status': 'synthetic_cpu_only' if c['device'] == 'cpu' else 'blocked',
            'reason': 'GPU requires authorized scheduler lease and workload adapter; neither is implemented here' if c['device'] == 'gpu' else None,
            'performance_claim': 'uncontrolled_cpu_observation' if c['mode'] == 'performance' else 'none',
            'resource_note': 'worker ceiling is an explicit budget, not proof of idle CPUs; CPU quota/memory require external admission',
            'gpu_shards': [], 'reservation': 'none'}


def sample(args):
    sample_id, size, seed = args
    start = (seed + sample_id * 104729) % 1009
    actual = sum(i * i for i in range(start, start + size))
    def squares(n):
        return n * (n + 1) * (2 * n + 1) // 6
    expected = squares(start + size - 1) - squares(start - 1)
    return {'id': sample_id, 'value': actual, 'expected': expected}


def batches(items, batch_size, invoke):
    """Retry only uncommitted batch on MemoryError; other failures propagate."""
    cursor = 0
    events = []
    while cursor < len(items):
        current = items[cursor:cursor + batch_size]
        try:
            rows = list(invoke(current))
        except MemoryError:
            events.append({'event': 'oom_backoff', 'from_batch_size': batch_size})
            if batch_size == 1:
                raise
            batch_size = max(1, batch_size // 2)
            continue
        if len(rows) != len(current):
            raise ValueError('incomplete batch')
        yield rows, list(events)
        events.clear()
        cursor += len(current)


def validate_rows(rows, c, complete=False):
    if type(rows) is not list:
        raise ValueError('rows must be a list')
    seen = set()
    for row in rows:
        if type(row) is not dict or set(row) != {'id', 'value', 'expected'}:
            raise ValueError('invalid sample record')
        sid = row['id']
        if type(sid) is not int or sid in seen or not 0 <= sid < c['samples']:
            raise ValueError('duplicate/out-of-range sample')
        start = (c['seed'] + sid * 104729) % 1009
        end = start + c['size'] - 1
        expected = end*(end+1)*(2*end+1)//6 - (start-1)*start*(2*start-1)//6
        if any(type(row[k]) is not int for k in row) or row['value'] != expected or row['expected'] != expected:
            raise ValueError('sample does not match protocol/reference')
        seen.add(sid)
    if complete and seen != set(range(c['samples'])):
        raise ValueError('missing samples')
    return seen


def performance(c):
    n = c['size']
    def baseline():
        return sum(i*i for i in range(n))
    def candidate():
        return (n-1)*n*(2*n-1)//6
    expected = sum(i*i for i in range(n))
    functions = {'baseline': baseline, 'candidate': candidate}
    def pair(index):
        row = {}
        for name in (('baseline', 'candidate') if index % 2 == 0 else ('candidate', 'baseline')):
            t = time.perf_counter_ns()
            value = functions[name]()
            row[name] = time.perf_counter_ns() - t
            if value != expected:
                raise ValueError('correctness failed')
        return row
    first = pair(0)
    for i in range(c['warmup']):
        pair(i)
    raw = [pair(i) for i in range(c['repeats'])]
    summaries = {k: {'median_ns': statistics.median(r[k] for r in raw),
                     'stdev_ns': statistics.stdev(r[k] for r in raw)} for k in functions}
    return {'first_call_ns': first, 'first_call_note': 'not process cold-start; interpreter already running',
            'steady_pairs_ns': raw, 'summary': summaries,
            'timing': 'CPU perf_counter_ns around function; reference check outside interval',
            'jit_compiler_cache': 'not_applicable_python_integer_fixture',
            'claim': 'synthetic_uncontrolled_cpu_only; no GPU/system speedup inference'}


def save_new(path, value):
    with path.open('x') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')


def run(c, root, run_id, resume=None):
    c = config(c)
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', run_id):
        raise ValueError('invalid run ID')
    observation = probe()
    admission = plan(c, observation)
    if admission['status'] == 'blocked':
        raise ValueError(admission['reason'])
    rows = []
    parent = None
    if resume:
        if c['mode'] != 'accuracy':
            raise ValueError('performance resume prohibited: rerun all paired measurements')
        resume_bytes = Path(resume).read_bytes()
        prior = parse(resume_bytes)
        if type(prior) is not dict or prior.get('schema') != 1 or type(prior.get('schema')) is not int:
            raise ValueError('resume schema mismatch')
        if (prior.get('config') != c or prior.get('config_sha256') != digest(c)
                or prior.get('runner_sha256') != hashlib.sha256(Path(__file__).read_bytes()).hexdigest()):
            raise ValueError('resume protocol mismatch')
        rows = prior['rows']
        validate_rows(rows, c)
        if prior.get('rows_sha256') != digest(rows):
            raise ValueError('resume checksum mismatch')
        parent = {'path': str(resume), 'sha256': hashlib.sha256(resume_bytes).hexdigest()}
    out = Path(root) / run_id
    out.mkdir(parents=True, exist_ok=False)
    base = {'schema': 1, 'run_id': run_id, 'config': c, 'config_sha256': digest(c),
            'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'environment': observation, 'admission': admission, 'resumed_from': parent}
    save_new(out / 'manifest.json', base)
    # Each committed checkpoint is new; interrupted writes cannot overwrite an earlier checkpoint.
    events = []
    try:
        measurements = None
        if c['mode'] == 'accuracy':
            done = validate_rows(rows, c)
            todo = [(i, c['size'], c['seed']) for i in range(c['samples']) if i not in done]
            with concurrent.futures.ProcessPoolExecutor(max_workers=admission['workers']) as pool:
                for chunk, backoff in batches(todo, c['batch_size'], lambda xs: pool.map(sample, xs)):
                    rows = sorted(rows + chunk, key=lambda r: r['id'])
                    validate_rows(rows, c)
                    events.extend(backoff)
                    save_new(out / ('checkpoint-%04d.json' % len(rows)),
                             base | {'rows': rows, 'rows_sha256': digest(rows), 'events': events})
            validate_rows(rows, c, complete=True)
        else:
            measurements = performance(c)
        result = base | {'status': 'completed', 'rows': rows, 'rows_sha256': digest(rows),
                         'events': events, 'measurements': measurements,
                         'metric': {'name': 'exact_integer_match', 'correct': len(rows), 'total': c['samples']} if c['mode'] == 'accuracy' else None,
                         'resource_end': probe(), 'next': 'review receipt; real workload/hardware remains untested'}
        save_new(out / 'result.json', result)
        return result
    except BaseException as exc:
        save_new(out / 'failure.json', {'status': 'failed', 'type': type(exc).__name__, 'completed_ids': [r['id'] for r in rows]})
        raise


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['probe', 'plan', 'run'])
    p.add_argument('--config', type=Path)
    p.add_argument('--gpu', action='store_true', help='read-only nvidia-smi query; never allocation')
    p.add_argument('--output', type=Path, default=Path('results'))
    p.add_argument('--run-id')
    p.add_argument('--resume-from', type=Path)
    args = p.parse_args()
    try:
        if args.action == 'probe':
            result = probe(args.gpu)
        else:
            c = config(load(args.config) if args.config else {})
            if args.action == 'plan':
                result = plan(c, probe(args.gpu))
            else:
                if not args.run_id:
                    raise ValueError('--run-id required')
                if args.gpu:
                    raise ValueError('--gpu is probe/plan only')
                result = run(c, args.output, args.run_id, args.resume_from)
        print(json.dumps(result, indent=2, allow_nan=False))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        p.exit(2, str(exc) + '\n')


if __name__ == '__main__':
    main()
