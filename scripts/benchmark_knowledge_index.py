"""Paired full-build_index benchmark; synthetic fixtures are not agent QA."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import sqlite3
import statistics
import subprocess
import sys
import tempfile
import time
import types

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from agent_runtime import knowledge_index as candidate
from agent_runtime.knowledge import KnowledgeStore

BASE = '8cf78b709f49e4ecaa3030b57a341940c3f780a1'
QUERIES = ['memory retrieval', 'low rank', '量纲', 'batch update', 'zzqxnonexistent']


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def baseline():
    source = subprocess.check_output(['git', 'show', BASE + ':agent_runtime/knowledge_index.py'], cwd=ROOT)
    module = types.ModuleType('agent_runtime._index_baseline')
    module.__package__ = 'agent_runtime'
    exec(compile(source, BASE, 'exec'), module.__dict__)
    return module, hashlib.sha256(source).hexdigest()


def snapshot(store):
    store.snapshot = digest([store.ref(k) for k in sorted(store.records)])
    return store


def corpus(size):
    store = KnowledgeStore(ROOT / 'knowledge')
    if size == 0:
        return store
    template = copy.deepcopy(next(d for d in store.records.values() if d['status'] == 'published'))
    store.records = {}
    for i in range(size):
        kid = f'bench.entry-{i:05d}'
        d = copy.deepcopy(template)
        d.update(id=kid, title=f'Memory {i % 17}', summary='batch update retrieval',
                 status='published', requires=[], aliases=['memory retrieval'], domains=['test'],
                 structures=['index'], assumptions=['synthetic'],
                 content=''.join(f'# {term}\n{term} category {i % 17} item {i}\n' for term in ('memory', 'retrieval', 'batch', 'update')))
        d['sha256'] = digest({k: v for k, v in d.items() if k != 'sha256'})
        store.records[kid] = d
    return snapshot(store)


def transition(store, mode):
    out = copy.deepcopy(store)
    ids = [k for k, d in out.records.items() if d['status'] == 'published']
    count = {'noop': 0, 'single': 1, 'partial': 64, 'b127': 127, 'b128': 128,
             'b129': 129, 'all': len(ids), 'rebuild': 0, 'delete': 0,
             'mixed': 64, 'migration': 0}[mode]
    for kid in ids[:count]:
        d = out.records[kid]
        d['content'] += '\nUpdated memory retrieval.\n'
        d['sha256'] = digest({k: v for k, v in d.items() if k != 'sha256'})
    if mode == 'delete':
        out.records = {}
    if mode == 'mixed':
        for kid in ids[64:128]:
            # Deprecation exercises published-only membership and leaves references valid.
            out.records[kid]['status'] = 'deprecated'
        for i, kid in enumerate(ids[:64]):
            d = copy.deepcopy(out.records[kid])
            d.update(id=f'bench.new-{i:05d}', requires=[])
            d['sha256'] = digest(d)
            out.records[d['id']] = d
    return snapshot(out)


def logical(path):
    with sqlite3.connect(path) as con:
        return {t: con.execute(f'SELECT {cols} FROM {t} ORDER BY {order}').fetchall()
                for t, cols, order in [('entries', '*', 'id'), ('meta', '*', 'key'),
                                       ('docs', 'rowid,*', 'rowid'), ('chunks', 'rowid,*', 'rowid')]}


def paired(size, mode, repeats=7):
    old, base_hash = baseline()
    store = corpus(size)
    target = transition(store, mode)
    config = dict(size=len(store.records), mode=mode, repeats=repeats, queries=QUERIES,
                  source_sha256=base_hash,
                  candidate_sha256=hashlib.sha256(Path(candidate.__file__).read_bytes()).hexdigest(),
                  input_sha256=digest(store.records), target_sha256=digest(target.records),
                  chunks=sum(len(old.sections(d)) for d in store.records.values() if d['status']=='published'),
                  content_bytes=sum(len(d['content'].encode()) for d in store.records.values()))
    samples = []
    with tempfile.TemporaryDirectory(prefix='fts-pair-') as tmp:
        root = Path(tmp)
        seed = root / 'seed.db'
        old.build_index(store, seed)
        if mode == 'migration':
            with sqlite3.connect(seed) as con:
                con.execute("UPDATE meta SET value='old-engine' WHERE key='engine_version'")
        config['seed_sha256'] = hashlib.sha256(seed.read_bytes()).hexdigest()
        for repeat in range(-1, repeats):
            outputs, states, searches, elapsed = {}, {}, {}, {}
            order = ('baseline', 'candidate') if repeat % 2 == 0 else ('candidate', 'baseline')
            for label in order:
                module = old if label == 'baseline' else candidate
                db = root / (label + '.db')
                shutil.copyfile(seed, db)
                start = time.perf_counter_ns()
                outputs[label] = module.build_index(target, db, rebuild=mode == 'rebuild')
                elapsed[label] = (time.perf_counter_ns() - start) / 1e6
                states[label] = logical(db)
                searches[label] = [module.indexed_search(target, db, q) for q in QUERIES]
            assert outputs['baseline'] == outputs['candidate'], (size, mode, 'return')
            assert states['baseline'] == states['candidate'], (size, mode, 'tables')
            assert searches['baseline'] == searches['candidate'], (size, mode, 'search')
            if repeat >= 0:
                samples.append(dict(pair=repeat, order=order, **elapsed))
        for module in (old, candidate):
            db = root / 'rollback.db'
            shutil.copyfile(seed, db)
            before = logical(db)
            original = module.sections
            def fail(record):
                raise RuntimeError('injected post-delete failure')
            module.sections = fail
            try:
                try:
                    module.build_index(transition(store, 'all'), db)
                except RuntimeError:
                    pass
                else:
                    raise AssertionError('failure not exercised')
                assert logical(db) == before, 'rollback changed logical state'
            finally:
                module.sections = original
    med = {key: statistics.median(s[key] for s in samples) for key in ('baseline', 'candidate')}
    required = size in (400, 1600) and mode in ('all', 'delete')
    threshold = med['baseline'] * .85 if required else max(med['baseline'] * 1.15, med['baseline'] + .5)
    return dict(config=config, samples_ms=samples, median_ms=med,
                speedup=med['baseline']/med['candidate'], threshold_ms=threshold,
                performance_pass=med['candidate'] <= threshold, parity=True, rollback=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sizes', nargs='+', type=int, default=[0, 400, 1600])
    parser.add_argument('--modes', nargs='+', default=['noop','single','partial','all','delete','rebuild',
                                                    'b127','b128','b129','mixed','migration'])
    parser.add_argument('--repeats', type=int, default=7)
    args = parser.parse_args()
    if os.environ.get('PYTHONHASHSEED') != '0':
        parser.error('run with PYTHONHASHSEED=0')
    assert args.repeats > 0 and all(n >= 0 for n in args.sizes)
    print(json.dumps(dict(environment=dict(python=sys.version, sqlite=sqlite3.sqlite_version,
                     platform=platform.platform(), cpu=platform.processor(),
                     lscpu=subprocess.check_output(['lscpu'], text=True),
                     hashseed=os.environ['PYTHONHASHSEED']), protocol='full build_index wall ms; one warm pair; AB/BA; ratio medians')), flush=True)
    for size in args.sizes:
        for mode in args.modes:
            print(json.dumps(paired(size, mode, args.repeats)), flush=True)


if __name__ == '__main__':
    main()
