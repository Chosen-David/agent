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
import sqlite3
import statistics
import subprocess
import tempfile
import time
import tracemalloc

from agent_runtime import project_memory as candidate


def digest(data):
    return hashlib.sha256(data).hexdigest()


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    config_bytes = args.config.read_bytes()
    result = measure(json.loads(config_bytes))
    result['config_sha256'] = digest(config_bytes)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'gate': result['gate'], 'cases': [
        {'id': c['id'], 'wall_reduction': c['wall_summary']['reduction'],
         'peak_reduction': c['traced_summary']['reduction']} for c in result['cases']]}))
