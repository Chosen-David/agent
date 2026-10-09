#!/usr/bin/env python3
"""Synthetic local mailbox scaling benchmark; no model/token/network claims.

Run from repository root. Legacy histories are seeded outside timing using the
old append-only schema. Measured publishes use the complete production API.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import random
import shutil
import sqlite3
import statistics
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from agent_runtime.communication import Mailbox, canonical


def load_baseline(path):
    spec = importlib.util.spec_from_file_location('agent_runtime._benchmark_baseline', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Mailbox


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def timed(function):
    start = time.perf_counter_ns()
    result = function()
    return (time.perf_counter_ns() - start) / 1e6, result


def scan_usage(path, run):
    with sqlite3.connect(path) as db:
        bodies = db.execute('SELECT seq,body FROM communication_events WHERE run_id=?', (run,)).fetchall()
        counts = dict(db.execute('SELECT seq,COUNT(*) FROM communication_deliveries GROUP BY seq'))
    return dict(events=len(bodies), envelope_bytes=sum(len(b.encode()) for _, b in bodies),
                deliveries=sum(counts.get(s, 0) for s, _ in bodies),
                delivery_bytes=sum(len(b.encode()) * counts.get(s, 0) for s, b in bodies))


def run_case(root, baseline, backlog, fanout, budget, config, rng):
    case = f'n{backlog}-f{fanout}-budget{int(budget)}'
    recipients = [f'consumer-{i}' for i in range(fanout)]
    plan = dict(schema_version=1, run_id=case, input_version='fixed-v1', max_events=backlog+1000,
                routes=[dict(sender='producer', recipient=r, task_id='task', kind='question') for r in recipients])
    if budget:
        plan['max_delivery_bytes'] = 10**12
    data = 'fixed public synthetic question\n'.encode()
    (root/'question.txt').write_bytes(data)
    event = dict(event_id='seed', run_id=case, input_version='fixed-v1', sender='producer',
                 task_id='task', kind='question', summary='a'*config['summary_chars']+'中文', action='inspect reference',
                 refs=[dict(id='question', path='question.txt', sha256=hashlib.sha256(data).hexdigest())])
    seed_path = root/'seed.sqlite'
    old = baseline(seed_path, plan, root)
    with old.connect() as db:
        db.execute('BEGIN IMMEDIATE')
        for i in range(backlog):
            value = dict(event, event_id=f'seed-{i:08d}')
            seq = db.execute('INSERT INTO communication_events(run_id,event_id,body) VALUES (?,?,?)',
                             (case, value['event_id'], canonical(value))).lastrowid
            db.executemany('INSERT INTO communication_deliveries(seq,recipient) VALUES (?,?)',
                           [(seq, r) for r in recipients])
    arms = {}
    initializations = {}
    plans = {}
    storage = {}
    for name in config['arms']:
        path = root/f'{name}.sqlite'
        shutil.copyfile(seed_path, path)
        cls = Mailbox if name == 'candidate' else baseline
        if name == 'indexed_scan':
            def index():
                with sqlite3.connect(path) as db:
                    db.execute('CREATE INDEX communication_covering ON communication_events(run_id,seq,body)')
            elapsed, _ = timed(index)
            initializations['indexed_scan_index_build_ms'] = elapsed
        elapsed, box = timed(lambda: cls(path, plan, root))
        initializations[f'{name}_initial_open_ms'] = elapsed
        storage[name] = path.stat().st_size
        arms[name] = box
        with box.connect() as db:
            plans[name] = {'journal_mode': db.execute('PRAGMA journal_mode').fetchone()[0],
                           'synchronous': db.execute('PRAGMA synchronous').fetchone()[0],
                           'scan_query_plan': [list(r) for r in db.execute('''EXPLAIN QUERY PLAN
                               SELECT SUM(length(CAST(e.body AS BLOB))) FROM communication_events e
                               JOIN communication_deliveries d ON e.seq=d.seq WHERE e.run_id=?''', (case,))]}
    samples = {name: {operation: [] for operation in ['publish_ms', 'usage_ms', 'reopen_ms']} for name in arms}
    orders = []
    for repeat in range(config['warmups'] + config['repeats']):
        order = list(arms)
        rng.shuffle(order)
        orders.append(order)
        measured_event = dict(event, event_id=f'measured-{repeat:08d}')
        for name in order:
            box = arms[name]
            publish_ms, sent = timed(lambda: box.publish(measured_event))
            if sent['duplicate'] or sent['recipients'] != sorted(recipients):
                raise AssertionError('unexpected publish result')
            usage_ms, usage = timed(box.usage)
            cls = Mailbox if name == 'candidate' else baseline
            reopen_ms, _ = timed(lambda: cls(box.path, plan, root))
            if repeat >= config['warmups']:
                for op, value in [('publish_ms', publish_ms), ('usage_ms', usage_ms), ('reopen_ms', reopen_ms)]:
                    samples[name][op].append(value)
    final = {}
    for name, box in arms.items():
        expected = scan_usage(box.path, case)
        actual = box.usage()
        if any(actual[k] != v for k, v in expected.items()):
            raise AssertionError(f'{name}: accounting mismatch')
        final[name] = expected
    if len({canonical(value) for value in final.values()}) != 1:
        raise AssertionError('arms produced different counts/bytes')
    return dict(case=case, backlog=backlog, fanout=fanout, byte_budget=budget, samples=samples,
                initializations=initializations, database_bytes_after_init=storage,
                sqlite=plans, order_including_warmups=orders, final_accounting=final)


def summarize(cases):
    rows = []
    for case in cases:
        stats = {}
        for arm, ops in case['samples'].items():
            stats[arm] = {op: dict(median=statistics.median(v), p95=sorted(v)[math.ceil(.95*len(v))-1],
                                   minimum=min(v), maximum=max(v)) for op, v in ops.items()}
        rows.append(dict(case=case['case'], stats=stats,
                         publish_speedup=stats['baseline']['publish_ms']['median']/stats['candidate']['publish_ms']['median'],
                         indexed_publish_speedup=stats['indexed_scan']['publish_ms']['median']/stats['candidate']['publish_ms']['median'],
                         usage_speedup=stats['baseline']['usage_ms']['median']/stats['candidate']['usage_ms']['median']))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--backlogs', type=int, nargs='+', help='Independent reproduction subset; recorded explicitly')
    args = parser.parse_args()
    if args.out.exists():
        parser.error('output already exists; preserve raw observations and use a new path')
    plan = json.loads(args.plan.read_text())
    config = dict(plan['matrix'])
    if args.backlogs is not None:
        config['backlog'] = args.backlogs
    baseline = load_baseline(args.baseline)
    rng = random.Random(config['seed'])
    cases = []
    environment = dict(python=sys.version, sqlite=sqlite3.sqlite_version, platform=platform.platform(),
                       cpu_count=os.cpu_count(), clock=time.get_clock_info('perf_counter').__dict__)
    cpuinfo = Path('/proc/cpuinfo')
    if cpuinfo.exists():
        environment['cpu_model'] = next((l.split(':', 1)[1].strip() for l in cpuinfo.read_text().splitlines() if l.startswith('model name')), 'unknown')
    with tempfile.TemporaryDirectory(prefix='communication-bench-') as tmp:
        environment['temp_filesystem'] = str(Path(tmp).parent)
        for backlog in config['backlog']:
            for fanout in config['fanout']:
                for budget in config['byte_budget']:
                    path = Path(tmp)/f'{backlog}-{fanout}-{budget}'
                    path.mkdir()
                    cases.append(run_case(path, baseline, backlog, fanout, budget, config, rng))
    raw = dict(scope=plan['scope'], command=sys.argv, config=config, environment=environment,
               code_hashes={str(p.relative_to(ROOT)): digest(p) for p in [ROOT/'agent_runtime/communication.py', ROOT/'scripts/validate_handoff.py', ROOT/'agent_runtime/project_docs.py', Path(__file__).resolve()]},
               baseline_sha256=digest(args.baseline), plan_sha256=digest(args.plan), cases=cases)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(raw, indent=2, ensure_ascii=False)+'\n')
    summary = args.out.with_name(args.out.stem+'-summary.json')
    summary.write_text(json.dumps(summarize(cases), indent=2)+'\n')
    print(json.dumps({'raw': str(args.out), 'summary': str(summary), 'cases': len(cases)}))


if __name__ == '__main__':
    main()
