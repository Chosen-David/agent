"""Bounded paired SQLite fixture benchmark; no LLM or token-cost measurements."""
import argparse
from contextlib import contextmanager
import importlib.util
import json
from pathlib import Path
import platform
import sqlite3
import statistics
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_runtime.communication import Mailbox, canonical


def load_baseline(path):
    spec = importlib.util.spec_from_file_location('agent_runtime._inbox_baseline', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Mailbox


def timed(fn):
    start = time.perf_counter_ns()
    value = fn()
    return (time.perf_counter_ns() - start) / 1e6, value


def fixture(cls, root, history, pending, runs):
    plan = dict(schema_version=1, run_id='target', input_version='v1',
                max_events=30000, routes=[dict(sender='code', recipient='reader',
                                              task_id='T1', kind='artifact')])
    box = cls(root/'mailbox.db', plan, root)
    events, deliveries, expected = [], [], []
    # Deterministic history seeding, not a publish throughput measurement.
    for i in range(1, history + pending + 1):
        run = 'target' if i > history or runs == 1 or i % runs == 0 else 'other-'+str(i % runs)
        event = dict(event_id=str(i), run_id=run, payload='界' * 32)
        events.append((i, run, str(i), canonical(event)))
        # Other runs keep a subset pending to stress recipient-only indexing.
        receipt = None if i > history or (run != 'target' and i % 17 == 0) else '{}'
        deliveries.append((i, 'reader', receipt))
        deliveries.append((i, 'unrelated', None))
        if run == 'target' and receipt is None:
            expected.append(dict(seq=i, event=event))
    with box.connect() as db:
        db.executemany('INSERT INTO communication_events VALUES (?,?,?,?)', events)
        db.executemany('INSERT INTO communication_deliveries VALUES (?,?,?)', deliveries)
    return box, expected


def vm_steps(box):
    count = [0]
    original = box.connect
    @contextmanager
    def counted():
        with original() as db:
            db.set_progress_handler(lambda: count.__setitem__(0, count[0]+1) or 0, 1)
            try:
                yield db
            finally:
                db.set_progress_handler(None, 0)
    box.connect = counted
    try:
        value = box.inbox('reader')
    finally:
        box.connect = original
    return count[0], value


def query_plan(box):
    with box.connect() as db:
        return [list(r) for r in db.execute('''EXPLAIN QUERY PLAN
          SELECT e.seq,e.body FROM communication_events e
          JOIN communication_deliveries d ON e.seq=d.seq
          WHERE e.run_id=? AND d.recipient=? AND d.receipt IS NULL
          ORDER BY e.seq LIMIT ?''', ('target','reader',20))]


def overhead(boxes, repeats):
    import hashlib
    data=b'fixture'
    ref=dict(id='artifact',path='artifact',sha256=hashlib.sha256(data).hexdigest())
    for box in boxes.values(): (box.root/'artifact').write_bytes(data)
    samples={name:[] for name in boxes}
    for i in range(repeats+3):
        event=dict(event_id='overhead:'+str(i),run_id='target',input_version='v1',
                   sender='code',task_id='T1',kind='artifact',summary='fixture',
                   action='read',refs=[ref])
        for name in (['baseline','candidate'] if i%2==0 else ['candidate','baseline']):
            box=boxes[name]
            publish,sent=timed(lambda:box.publish(event))
            ack,_=timed(lambda:box.acknowledge('reader',sent['seq'],dict(status='consumed',reason='fixture')))
            if i>=3: samples[name].append(dict(publish_ms=publish,ack_ms=ack))
    return samples


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--baseline',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--repeats',type=int,default=21)
    args=ap.parse_args()
    if not 3 <= args.repeats <= 101: ap.error('repeats must be 3..101')
    baseline=load_baseline(args.baseline)
    report=dict(environment=dict(python=sys.version,sqlite=sqlite3.sqlite_version,
                  platform=platform.platform(),cpu=platform.processor()),
                config=dict(history=[0,1000,20000],pending=[0,5],runs=[1,4],
                            warmups=3,repeats=args.repeats,units='ms',seed='deterministic'),cases=[])
    with tempfile.TemporaryDirectory() as tmp:
        for h in [0,1000,20000]:
            for p in [0,5]:
                for runs in [1,4]:
                    boxes={}; expected=None
                    for name,cls in [('baseline',baseline),('candidate',Mailbox)]:
                        root=Path(tmp)/f'{h}-{p}-{runs}-{name}';root.mkdir()
                        boxes[name],expect=fixture(cls,root,h,p,runs)
                        if expected is None: expected=expect
                        assert expected==expect
                    case=dict(history=h,pending=p,runs=runs,expected=expected,raw=[],vm={},query_plans={})
                    for name,box in boxes.items():
                        steps,actual=vm_steps(box);assert actual==expected
                        case['vm'][name]=steps;case['query_plans'][name]=query_plan(box)
                    for i in range(args.repeats+3):
                        pair={}
                        for name in (['baseline','candidate'] if i%2==0 else ['candidate','baseline']):
                            ms,actual=timed(lambda:boxes[name].inbox('reader'));assert actual==expected
                            pair[name]=ms
                        if i>=3: case['raw'].append(pair)
                    case['median_ms']={name:statistics.median(r[name] for r in case['raw']) for name in boxes}
                    # Same pre-existing history, migration measured before any overhead writes.
                    old=boxes['baseline']; before=old.path.stat().st_size
                    migration,migrated=timed(lambda:Mailbox(old.path,old.plan,old.root))
                    assert migrated.inbox('reader')==expected
                    reopen,_=timed(lambda:Mailbox(old.path,old.plan,old.root))
                    case['migration']=dict(ms=migration,reopen_ms=reopen,before_bytes=before,after_bytes=old.path.stat().st_size)
                    # Use independent fixture for baseline writes: migration above changes its schema.
                    write_root=Path(tmp)/f'{h}-{p}-{runs}-write';write_root.mkdir()
                    write_baseline,_=fixture(baseline,write_root,h,p,runs)
                    case['overhead']=overhead({'baseline':write_baseline,'candidate':boxes['candidate']},args.repeats)
                    report['cases'].append(case)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'cases':len(report['cases']),'out':str(args.out)}))

if __name__=='__main__': main()
