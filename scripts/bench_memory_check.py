"""Full-call CPU memory-check benchmark; synthetic SQLite, no model KV claims.

Run from the repository root with PYTHONPATH=. Pass the frozen JSON protocol
and an output path. Baseline code is loaded from its immutable git revision.
"""
import argparse
import gc
import hashlib
import json
import platform
from pathlib import Path
import random
import re
import sqlite3
import statistics
import subprocess
import tempfile
import time
import tracemalloc

from agent_runtime import project_memory as candidate
from agent_runtime.external_json import regular_bytes, strict_json


def digest(data):
    return hashlib.sha256(data).hexdigest()


def validate_config(config):
    if not isinstance(config, dict):
        raise ValueError('benchmark config must be a JSON object')
    if not isinstance(config.get('baseline'), str) or not re.fullmatch('[0-9a-f]{40}', config['baseline']):
        raise ValueError('exact baseline commit required')
    fixtures, measurement = config.get('fixtures'), config.get('measurement')
    if not isinstance(fixtures, list) or not 1 <= len(fixtures) <= 1000:
        raise ValueError('1..1000 benchmark fixtures required')
    if not isinstance(measurement, dict):
        raise ValueError('measurement config required')
    for key, minimum, maximum in (('seed', 0, 2**63 - 1), ('wall_pairs', 1, 10000),
                                  ('traced_pairs', 1, 10000), ('warmup_each', 0, 10000)):
        value = measurement.get(key)
        if type(value) is not int or not minimum <= value <= maximum:
            raise ValueError('invalid measurement field: ' + key)
    seen = set()
    total_payload = 0
    for fixture in fixtures:
        if not isinstance(fixture, dict):
            raise ValueError('fixture object required')
        identifier = fixture.get('id')
        if not isinstance(identifier, str) or not identifier or identifier in seen:
            raise ValueError('unique fixture id required')
        seen.add(identifier)
        if not isinstance(fixture.get('shape'), str):
            raise ValueError('fixture shape required')
        for key, maximum in (('nodes', 1_000_000), ('content_bytes', 256 * 1024 * 1024)):
            value = fixture.get(key)
            if type(value) is not int or value < 1 or value > maximum:
                raise ValueError('invalid fixture field: ' + key)
        roots = fixture.get('roots')
        if not ((isinstance(roots, str) and roots) or
                isinstance(roots, list) and roots and all(type(item) is int and
                0 <= item < fixture['nodes'] for item in roots)):
            raise ValueError('fixture roots must be a bounded list or named ordering')
        payload = fixture['nodes'] * fixture['content_bytes']
        if payload > 512 * 1024 * 1024:
            raise ValueError('fixture payload exceeds 512 MiB synthetic allocation bound')
        total_payload += payload
    if total_payload > 2 * 1024 * 1024 * 1024:
        raise ValueError('aggregate fixture payload exceeds 2 GiB bound')
    calls = len(fixtures) * (measurement['wall_pairs'] + measurement['traced_pairs']) * 2
    if calls > 100_000:
        raise ValueError('aggregate measurement call count exceeds 100000')
    return config


def baseline_class(revision):
    source = subprocess.check_output(['git', 'show', revision + ':agent_runtime/project_memory.py'])
    module = {'__name__': 'agent_runtime._check_baseline', '__package__': 'agent_runtime'}
    exec(compile(source, revision + '/project_memory.py', 'exec'), module)
    return module['MemoryLedger'], digest(source)


def seed(root, spec):
    ledger = candidate.MemoryLedger(root, create=True)
    rows, edges = [], []
    for i in range(spec['nodes']):
        name = f'm{i:04d}'
        rows.append((name, 'claim', 'x' * spec['content_bytes'], 'synthetic',
                     '[]', 'verified', 'active', '2026-10-16'))
        if spec['shape'] == 'chain' and i:
            edges.append((name, f'm{i-1:04d}'))
        elif spec['id'] == 'wide' and i == 512:
            edges.extend((name, f'm{j:04d}') for j in range(512))
        elif spec['id'] == 'layered' and i >= 4:
            edges.extend((name, f'm{j:04d}') for j in range((i // 4 - 1)*4, (i // 4)*4))
    with ledger._connect(write=True) as db:
        db.executemany('INSERT INTO entries VALUES(?,?,?,?,?,?,?,?)', rows)
        db.executemany('INSERT INTO dependencies VALUES(?,?)', edges)
    roots = spec['roots']
    if isinstance(roots, str):
        roots = list(reversed(range(spec['nodes'])))
    refs = [f'm{i:04d}' for i in roots]
    payload = json.dumps({'rows': rows, 'edges': edges, 'refs': refs}, sort_keys=True).encode()
    return ledger, refs, digest(payload)


def measure(config):
    Before, before_hash = baseline_class(config['baseline'])
    rng = random.Random(config['measurement']['seed'])
    result = {'baseline': config['baseline'], 'baseline_source_sha256': before_hash,
              'candidate_source_sha256': digest(Path(candidate.__file__).read_bytes()),
              'python': platform.python_version(), 'platform': platform.platform(),
              'sqlite': sqlite3.sqlite_version, 'cases': []}
    for spec in config['fixtures']:
        with tempfile.TemporaryDirectory() as root:
            after, refs, input_hash = seed(root, spec)
            arms = {'before': Before(root), 'after': after}
            assert arms['before'].check(refs) == after.check(refs)
            for arm in arms.values():
                for _ in range(config['measurement']['warmup_each']):
                    arm.check(refs)
            case = {'id': spec['id'], 'input_sha256': input_hash, 'wall': [], 'traced': []}
            for kind, count in (('wall', config['measurement']['wall_pairs']),
                                ('traced', config['measurement']['traced_pairs'])):
                for _ in range(count):
                    order = ['before', 'after']
                    rng.shuffle(order)
                    pair = {'order': order}
                    for name in order:
                        gc.collect()
                        if kind == 'traced':
                            tracemalloc.start()
                            value = arms[name].check(refs)
                            _, peak = tracemalloc.get_traced_memory()
                            tracemalloc.stop()
                            pair[name] = peak
                        else:
                            start = time.perf_counter_ns()
                            value = arms[name].check(refs)
                            pair[name] = time.perf_counter_ns() - start
                        del value
                    case[kind].append(pair)
            for kind in ('wall', 'traced'):
                medians = {name: statistics.median(p[name] for p in case[kind]) for name in arms}
                case[kind + '_summary'] = {**medians, 'reduction': 1 - medians['after']/medians['before']}
            result['cases'].append(case)
    result['gate'] = {
        'peak': result['cases'][0]['traced_summary']['reduction'] >= .70,
        'wall': all(c['wall_summary']['reduction'] >= -.15 for c in result['cases'])}
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        config_bytes = regular_bytes(args.config, max_bytes=2 * 1024 * 1024)
        config = validate_config(strict_json(config_bytes))
    except ValueError as exc:
        print(json.dumps({'status': 'invalid', 'reason': str(exc)}))
        return 2
    result = measure(config)
    result['config_sha256'] = digest(config_bytes)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'gate': result['gate'], 'cases': [
        {'id': c['id'], 'wall_reduction': c['wall_summary']['reduction'],
         'peak_reduction': c['traced_summary']['reduction']} for c in result['cases']]}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
