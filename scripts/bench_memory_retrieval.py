"""Paired MemoryLedger list/check benchmark against pinned Git, synthetic only."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import random
import re
import sqlite3
import statistics
import subprocess
import tempfile
import time

from agent_runtime.project_memory import MemoryLedger
from agent_runtime.external_json import load_json


def validate_config(config):
    if not isinstance(config, dict):
        raise ValueError('benchmark config must be a JSON object')
    if config.get('operation', 'list') not in ('list', 'check'):
        raise ValueError('unsupported memory benchmark operation')
    if (not isinstance(config.get('baseline_revision'), str)
            or not re.fullmatch('[0-9a-f]{40}', config['baseline_revision'])
            or not isinstance(config.get('baseline_source_sha256'), str)
            or not re.fullmatch('[0-9a-f]{64}', config['baseline_source_sha256'])):
        raise ValueError('exact baseline revision/source hash required')
    for key, minimum, maximum in (('seed', 0, 2**63 - 1), ('repeats', 1, 10000)):
        value = config.get(key)
        if type(value) is not int or not minimum <= value <= maximum:
            raise ValueError('invalid benchmark field: ' + key)
    cases = config.get('cases')
    if not isinstance(cases, list) or not 1 <= len(cases) <= 1000:
        raise ValueError('1..1000 benchmark cases required')
    names = set()
    total_payload = 0
    total_scan_work = 0
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get('name'), str) or not case['name'] or case['name'] in names:
            raise ValueError('unique case name required')
        names.add(case['name'])
        for key, minimum, maximum in (('entries', 1, 1_000_000), ('active', 0, 1_000_000),
                                      ('content_bytes', 1, 256 * 1024 * 1024),
                                      ('match_every', 1, 1_000_000)):
            value = case.get(key)
            if type(value) is not int or not minimum <= value <= maximum:
                raise ValueError('invalid case field: ' + key)
        if case['active'] > case['entries'] or not (case.get('scope') is None or isinstance(case.get('scope'), str)):
            raise ValueError('invalid active count or scope')
        if case.get('dependency_shape', 'none') not in ('none', 'chain', 'star'):
            raise ValueError('unsupported dependency fixture')
        if config.get('operation', 'list') == 'check':
            offset, count = case.get('refs_offset'), case.get('refs_count')
            if (type(offset) is not int or type(count) is not int or offset < 0 or count < 1
                    or offset + count > case['active']):
                raise ValueError('check fixture requires nonempty active refs')
        payload = case['entries'] * case['content_bytes']
        if payload > 512 * 1024 * 1024:
            raise ValueError('case payload exceeds 512 MiB synthetic allocation bound')
        total_payload += payload
        total_scan_work += case['entries'] * (config['repeats'] + 1)
    if total_payload > 2 * 1024 * 1024 * 1024:
        raise ValueError('aggregate case payload exceeds 2 GiB bound')
    if total_scan_work > 50_000_000:
        raise ValueError('aggregate benchmark scan work exceeds 50000000 entry-visits')
    return config


def benchmark(config):
    operation = config.get('operation', 'list')
    if operation not in ('list', 'check'):
        raise ValueError('unsupported memory benchmark operation')
    revision = config['baseline_revision']
    if not re.fullmatch('[0-9a-f]{40}', revision):
        raise ValueError('baseline must be an exact Git commit')
    root = Path(__file__).resolve().parents[1]
    source = subprocess.check_output(
        ['git', 'show', revision + ':agent_runtime/project_memory.py'], cwd=root)
    before_hash = hashlib.sha256(source).hexdigest()
    if before_hash != config['baseline_source_sha256']:
        raise ValueError('baseline source hash mismatch')
    namespace = {'__name__': 'agent_runtime._memory_benchmark_before',
                 '__package__': 'agent_runtime'}
    exec(compile(source, revision + '/project_memory.py', 'exec'), namespace)
    Before = namespace['MemoryLedger']
    rng = random.Random(config['seed'])
    cases = []
    for case in config['cases']:
        with tempfile.TemporaryDirectory() as directory:
            after = MemoryLedger(directory, create=True)
            before = Before(directory)
            with after._connect(write=True) as db:
                for i in range(case['entries']):
                    db.execute('INSERT INTO entries VALUES(?,?,?,?,?,?,?,?)',
                               (f'm{i:06}', 'claim', 'x' * case['content_bytes'],
                                'synthetic fixture',
                                '["T1"]' if i % case['match_every'] == 0 else '["T10"]',
                                'verified', 'active' if i < case['active'] else 'stale',
                                '2026-10-16'))
                shape = case.get('dependency_shape', 'none')
                if shape not in ('none', 'chain', 'star'):
                    raise ValueError('unsupported dependency fixture')
                if shape != 'none':
                    for i in range(1, case['entries']):
                        parent = i - 1 if shape == 'chain' else 0
                        db.execute('INSERT INTO dependencies VALUES(?,?)',
                                   (f'm{i:06}', f'm{parent:06}'))
            digest = hashlib.sha256(after.path.read_bytes()).hexdigest()
            if operation == 'check':
                offset, count = case['refs_offset'], case['refs_count']
                if not (type(offset) is int and type(count) is int and
                        offset >= 0 and count > 0 and offset + count <= case['active']):
                    raise ValueError('check fixture requires nonempty active refs')
                refs = [f'm{i:06}' for i in range(offset, offset + count)]
                calls = {'before_ms': lambda: before.check(refs),
                         'after_ms': lambda: after.check(refs)}
            else:
                kwargs = {'status': 'active', 'scope': case['scope']}
                calls = {'before_ms': lambda: before.list(**kwargs),
                         'after_ms': lambda: after.list(**kwargs)}
            expected = calls['before_ms']()
            if calls['after_ms']() != expected:
                raise ValueError('packet mismatch before timing')
            for fn in calls.values():
                fn()
            samples = {key: [] for key in calls}
            orders = []
            for _ in range(config['repeats']):
                order = list(calls)
                rng.shuffle(order)
                orders.append(order)
                for label in order:
                    start = time.perf_counter_ns()
                    value = calls[label]()
                    elapsed = (time.perf_counter_ns() - start) / 1e6
                    if value != expected:
                        raise ValueError('measured packet mismatch')
                    samples[label].append(elapsed)
            if hashlib.sha256(after.path.read_bytes()).hexdigest() != digest:
                raise ValueError('measurement changed database')
            med = {key: statistics.median(values) for key, values in samples.items()}
            cases.append(dict(case, database_sha256=digest, returned=len(expected),
                              samples=samples, orders=orders, median=med,
                              reduction=1 - med['after_ms'] / med['before_ms']))
    return {'scope': f'full {operation} entry, warm local SQLite, synthetic, no model/KV',
            'config': config, 'baseline_source_sha256': before_hash,
            'candidate_source_sha256': hashlib.sha256(
                (root / 'agent_runtime/project_memory.py').read_bytes()).hexdigest(),
            'environment': {'python': platform.python_version(),
                            'compiler': platform.python_compiler(),
                            'platform': platform.platform(), 'sqlite': sqlite3.sqlite_version},
            'cases': cases}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        config = validate_config(load_json(args.config, max_bytes=2 * 1024 * 1024))
    except ValueError as exc:
        print(json.dumps({'status': 'invalid', 'reason': str(exc)}))
        return 2
    result = benchmark(config)
    # A measurement is immutable evidence, never silently replace a previous run.
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps([dict(case=c['name'], median=c['median'], reduction=c['reduction'],
                           returned=c['returned']) for c in result['cases']], indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
