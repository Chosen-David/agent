"""Pending-heavy ordered-pull companion using existing communication benchmark helpers."""
import argparse
import json
from pathlib import Path
import platform
import sqlite3
import statistics
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_runtime.communication import Mailbox, canonical
from scripts.benchmark_communication_inbox import load_baseline, timed, vm_steps, overhead


def fixture(cls, root, total, layout):
    plan=dict(schema_version=1,run_id='target',input_version='v1',max_events=30000,
              routes=[dict(sender='code',recipient='reader',task_id='T1',kind='artifact')])
    box=cls(root/'mailbox.db',plan,root)
    events=[];deliveries=[];expected=[]
    for i in range(1,total+1):
        if layout=='single':run='target'
        elif layout=='interleaved':run='target' if i%4==0 else 'other-'+str(i%4)
        elif layout=='last':run='target' if i>total-5 else 'other-'+str(i%3)
        else:run='other-'+str(i%3)
        event=dict(event_id=str(i),run_id=run,payload='界'*32)
        events.append((i,run,str(i),canonical(event)))
        deliveries.extend([(i,'reader',None),(i,'unrelated',None)])
        if run=='target' and len(expected)<20:expected.append(dict(seq=i,event=event))
    with box.connect() as db:
        db.executemany('INSERT INTO communication_events VALUES (?,?,?,?)',events)
        db.executemany('INSERT INTO communication_deliveries VALUES (?,?,?)',deliveries)
    return box,expected


def observed_query_plan(box):
    traces=[]
    original=box.connect
    # Trace the real public-method SQL only, then EXPLAIN outside timing.
    from contextlib import contextmanager
    @contextmanager
    def traced():
        with original() as db:
            db.set_trace_callback(traces.append)
            try:yield db
            finally:db.set_trace_callback(None)
    box.connect=traced
    try:box.inbox('reader')
    finally:box.connect=original
    statements=[q for q in traces if 'SELECT e.seq,e.body' in q]
    assert len(statements)==1
    with box.connect() as db:
        return dict(sql=statements[0],plan=[list(r) for r in db.execute('EXPLAIN QUERY PLAN '+statements[0])])


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--baseline',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--repeats',type=int,default=21)
    args=ap.parse_args()
    if not 3<=args.repeats<=101:ap.error('repeats must be3..101')
    baseline=load_baseline(args.baseline)
    report=dict(environment=dict(python=sys.version,sqlite=sqlite3.sqlite_version,platform=platform.platform()),
                config=dict(total=[100,1000,20000],layouts=['single','interleaved','last','absent'],
                            warmups=3,repeats=args.repeats,units='ms',seed='deterministic'),cases=[])
    with tempfile.TemporaryDirectory() as tmp:
        for total in report['config']['total']:
            for layout in report['config']['layouts']:
                boxes={};expected=None
                for name,cls in [('baseline',baseline),('candidate',Mailbox)]:
                    root=Path(tmp)/f'{total}-{layout}-{name}';root.mkdir()
                    box,value=fixture(cls,root,total,layout);boxes[name]=box
                    if expected is None:expected=value
                    assert expected==value
                case=dict(total=total,layout=layout,expected=expected,raw=[],vm={},queries={})
                for name,box in boxes.items():
                    steps,value=vm_steps(box);assert value==expected
                    case['vm'][name]=steps;case['queries'][name]=observed_query_plan(box)
                for i in range(args.repeats+3):
                    pair={}
                    for name in (['baseline','candidate'] if i%2==0 else ['candidate','baseline']):
                        ms,value=timed(lambda:boxes[name].inbox('reader'));assert value==expected
                        pair[name]=ms
                    if i>=3:case['raw'].append(pair)
                case['median_ms']={n:statistics.median(r[n] for r in case['raw']) for n in boxes}
                case['range_ms']={n:[min(r[n] for r in case['raw']),max(r[n] for r in case['raw'])] for n in boxes}
                if total in (100,20000):case['overhead']=overhead(boxes,args.repeats)
                report['cases'].append(case)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(dict(cases=len(report['cases']),out=str(args.out))))

if __name__=='__main__':main()
