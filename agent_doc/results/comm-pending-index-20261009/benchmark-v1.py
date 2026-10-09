#!/usr/bin/env python3
"""Paired durable Mailbox benchmark; synthetic data, no model-performance claim.

Run from a git checkout. --baseline is an explicitly selected trusted local commit.
Setup uses the public baseline API; SQLite backups give both arms identical state.
"""
import argparse
from contextlib import contextmanager
import hashlib
import json
import math
from pathlib import Path
import platform
import sqlite3
import statistics
import subprocess
import sys
import tempfile
import time
import types

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from agent_runtime.communication import Mailbox, canonical


def digest(data):
    return hashlib.sha256(data).hexdigest()


def stats(values):
    return {'median': statistics.median(values),
            'p95': sorted(values)[math.ceil(.95 * len(values)) - 1]}


def measure(call):
    start = time.perf_counter_ns()
    value = call()
    return time.perf_counter_ns() - start, value


def run_case(case, baseline, repetitions, warmups):
    with tempfile.TemporaryDirectory(prefix='comm-inbox-') as tmp:
        root = Path(tmp)
        artifact = root / 'artifact.json'
        artifact.write_text('{}')
        ref = {'id': 'fixture', 'path': artifact.name, 'sha256': digest(artifact.read_bytes())}
        plans = [dict(schema_version=1, run_id=f'run{k}', input_version='v1',
                      max_events=case['events'] + repetitions + 10,
                      routes=[dict(sender='producer', recipient=f'reader{j}', task_id='T', kind='artifact')
                              for j in range(case['recipients'])]) for k in range(case['runs'])]
        base_path = root / 'base.sqlite'
        boxes = [baseline(base_path, p, root) for p in plans]
        receipt = dict(status='consumed', reason='fixture handled')
        ack_count = math.floor((case['events'] // case['runs']) * case['ack_fraction'])
        expected = []
        events = []
        for i in range(case['events']):
            run = i % case['runs']
            event = dict(event_id=str(i), run_id=f'run{run}', input_version='v1',
                         sender='producer', task_id='T', kind='artifact',
                         summary='Synthetic result available', action='Read fixture', refs=[ref])
            seq = boxes[run].publish(event)['seq']
            events.append((seq, event))
            if run == 0 and i // case['runs'] < ack_count:
                for j in range(case['recipients']):
                    boxes[run].acknowledge(f'reader{j}', seq, receipt)
            elif run == 0:
                expected.append(dict(seq=seq, event=event))
        candidate_path = root / 'candidate.sqlite'
        with sqlite3.connect(base_path) as src, sqlite3.connect(candidate_path) as dst:
            src.backup(dst)
        before_bytes = candidate_path.stat().st_size
        init_ns, candidate = measure(lambda: Mailbox(candidate_path, plans[0], root))
        indexed_bytes = candidate_path.stat().st_size
        old = boxes[0]
        boxes = [old, candidate]
        for box in boxes:
            for limit in (1, case['limit'], 100):
                assert box.inbox('reader0', limit=limit) == expected[:limit]
        for _ in range(warmups):
            for box in boxes:
                assert box.inbox('reader0', limit=case['limit']) == expected[:case['limit']]
        samples = [[], []]
        for i in range(repetitions):
            for arm in ((0, 1) if i % 2 == 0 else (1, 0)):
                elapsed, value = measure(lambda: boxes[arm].inbox('reader0', limit=case['limit']))
                assert value == expected[:case['limit']]
                samples[arm].append(elapsed)
        # Deterministic VM-work measurement is separate from latency samples.
        work = []
        query_plans = []
        for box in boxes:
            count = [0]
            original = box.connect
            @contextmanager
            def counted():
                with original() as db:
                    db.set_progress_handler(lambda: count.__setitem__(0, count[0]+1) or 0, 1)
                    yield db
            box.connect = counted
            try:
                box.inbox('reader0', limit=case['limit'])
            finally:
                box.connect = original
            work.append(count[0])
            with box.connect() as db:
                query_plans.append([list(row) for row in db.execute('''EXPLAIN QUERY PLAN
                    SELECT e.seq,e.body FROM communication_events e
                    JOIN communication_deliveries d ON e.seq=d.seq
                    WHERE e.run_id=? AND d.recipient=? AND d.receipt IS NULL
                    ORDER BY e.seq LIMIT ?''', ('run0', 'reader0', case['limit']))])
        # Actual public write costs, with equal added data in both arms.
        writes, acks = [[], []], [[], []]
        for i in range(repetitions):
            event = dict(events[0][1], event_id=f'write-{i}', run_id='run0')
            seqs = []
            for arm in ((0, 1) if i % 2 == 0 else (1, 0)):
                elapsed, result = measure(lambda: boxes[arm].publish(event))
                writes[arm].append(elapsed)
                seqs.append((arm, result['seq']))
            for arm, seq in seqs:
                elapsed, _ = measure(lambda: boxes[arm].acknowledge('reader0', seq, receipt))
                acks[arm].append(elapsed)
        assert old.status() == candidate.status()
        assert old.usage() == candidate.usage()
        result = dict(case=case, semantic_equivalence=True, pending_target=len(expected),
                      inbox_ns=samples, inbox_summary=[stats(v) for v in samples],
                      vm_steps=work, query_plans=query_plans,
                      publish_ns=writes, publish_summary=[stats(v) for v in writes],
                      ack_ns=acks, ack_summary=[stats(v) for v in acks],
                      candidate_first_open_ns=init_ns, db_bytes_before=before_bytes,
                      db_bytes_after_index=indexed_bytes,
                      fixture_sha256=digest(canonical(events).encode()))
        result['speedup'] = result['inbox_summary'][0]['median'] / result['inbox_summary'][1]['median']
        result['vm_reduction'] = 1 - work[1] / work[0]
        return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline', required=True)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--cases', nargs='*', help='Explicit subset for independent rerun')
    args = p.parse_args()
    if args.out.exists():
        p.error('output exists; preserve immutable previous data')
    config = json.loads(args.plan.read_text())
    source = subprocess.check_output(['git', 'show', args.baseline + ':agent_runtime/communication.py'], cwd=ROOT)
    module = types.ModuleType('agent_runtime._benchmark_baseline')
    exec(compile(source, '<trusted-git-baseline>', 'exec'), module.__dict__)
    cases = [c for c in config['workloads'] if not args.cases or c['name'] in args.cases]
    if args.cases and len(cases) != len(args.cases):
        p.error('unknown or duplicate case')
    report = dict(schema_version='communication-inbox-benchmark/v1',
                  baseline=args.baseline, baseline_sha256=digest(source),
                  candidate_sha256=digest((ROOT/'agent_runtime/communication.py').read_bytes()),
                  harness_sha256=digest(Path(__file__).read_bytes()), plan_sha256=digest(args.plan.read_bytes()),
                  environment=dict(python=sys.version, sqlite=sqlite3.sqlite_version,
                                   platform=platform.platform(), processor=platform.processor(),
                                   timer='perf_counter_ns', journal='DELETE', synchronous='SQLite default'),
                  command=sys.argv, cases=[])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    start = time.time()
    for c in cases:
        print('Running', c['name'], flush=True)
        result = run_case(c, module.Mailbox, config['measurement']['paired_repetitions'], config['measurement']['warmups'])
        report['cases'].append(result)
        # Checkpoint after each completed case, retained even if a later case fails.
        args.out.write_text(json.dumps(report, indent=2)+'\n')
        print(c['name'], 'speedup', round(result['speedup'], 2), 'VM', result['vm_steps'], flush=True)
    report['wall_seconds'] = time.time() - start
    report['completed'] = True
    args.out.write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    main()
