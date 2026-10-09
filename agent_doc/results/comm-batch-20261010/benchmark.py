"""Frozen public batch vs sequential and atomic-reference comparison, all samples retained."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from scripts.benchmark_communication_candidates_v2 import load
from contextlib import contextmanager
import argparse,hashlib,json,platform,sqlite3,statistics,tempfile,time

def atomic_reference(base):
    class BeginOnce:
        def __init__(self,db):self.db=db
        def execute(self,sql,*args):
            if sql=='BEGIN IMMEDIATE':return None
            return self.db.execute(sql,*args)
        def __getattr__(self,name):return getattr(self.db,name)
    class Reference(base):
        @contextmanager
        def connect(self):
            if getattr(self,'_batch_db',None) is not None:
                yield BeginOnce(self._batch_db)
            else:
                with super().connect() as db:yield db
        def publish_many(self,events):
            if not isinstance(events,list) or not 1<=len(events)<=100:raise ValueError('bounded list required')
            # Single-caller reference only. Never deployed or shared across threads.
            with super().connect() as db:
                db.execute('BEGIN IMMEDIATE');self._batch_db=db
                try:return [super(Reference,self).publish(e) for e in events]
                finally:self._batch_db=None
    return Reference

def make(cls,root,fanout=1,**budgets):
    root.mkdir(parents=True);(root/'ref').write_bytes(b'evidence')
    plan=dict(schema_version=1,run_id='batch',input_version='v1',max_events=100000,
              routes=[dict(sender='s',recipient=chr(97+i),task_id='T',kind='artifact') for i in range(fanout)],**budgets)
    box=cls(root/'mail.db',plan,root)
    event=dict(run_id='batch',input_version='v1',sender='s',task_id='T',kind='artifact',summary='界'*128,
               action='Verify evidence',refs=[dict(id='ref',path='ref',sha256=hashlib.sha256(b'evidence').hexdigest())])
    return box,event

def snapshot(box):
    with box.connect() as db:
        return {t:[list(r) for r in db.execute('SELECT * FROM '+t+' ORDER BY 1,2')] for t in
                ['communication_events','communication_deliveries','communication_usage_v1','communication_basis','sqlite_sequence']}

def timed(fn):
    t=time.perf_counter_ns();v=fn();return v,(time.perf_counter_ns()-t)/1e6

def trace_transaction(box,events,batch):
    sql=[];changes=[];original=box.connect
    @contextmanager
    def observed():
        with original() as db:
            start=db.total_changes;db.set_trace_callback(sql.append)
            yield db
            changes.append(db.total_changes-start)
        # Original context commits/closes while trace is still enabled.
    box.connect=observed
    try:
        out=box.publish_many(events) if batch else [box.publish(e) for e in events]
    finally:box.connect=original
    return dict(sql=sql,changes=sum(changes),begins=sum(s=='BEGIN IMMEDIATE' for s in sql),commits=sum(s=='COMMIT' for s in sql),results=out)

def run(baseline,candidate,out):
    B=load(baseline).Mailbox;C=load(candidate).Mailbox;S=atomic_reference(B)
    result=dict(environment=dict(python=sys.version,sqlite=sqlite3.sqlite_version,platform=platform.platform()),warmups=3,repeats=31,cases=[])
    with tempfile.TemporaryDirectory() as tmp:
        for n,f in [(1,1),(8,1),(32,3)]:
            classes={'sequential_baseline':B,'sequential_candidate':C,'batch_candidate':C,'atomic_reference':S}
            boxes={};events={}
            for name,cls in classes.items():
                box,event=make(cls,Path(tmp)/f'{n}-{f}-{name}',f);boxes[name]=box;events[name]=event
                for i in range(100):box.publish(dict(event,event_id=f'seed-{i}'))
            row=dict(batch_size=n,fanout=f,samples=[],ack_samples=[])
            for i in range(-3,31):
                order=list(classes)
                if i%2:order.reverse()
                values={};times={}
                for name in order:
                    es=[dict(events[name],event_id=f'{i}-{j}') for j in range(n)]
                    box=boxes[name]
                    fn=(lambda b=box,e=es:b.publish_many(e)) if name in ('batch_candidate','atomic_reference') else (lambda b=box,e=es:[b.publish(x) for x in e])
                    values[name],times[name]=timed(fn)
                assert all(v==values['sequential_baseline'] for v in values.values())
                acks={}
                for name in order:
                    box=boxes[name];seq=values[name][0]['seq']
                    _,acks[name]=timed(lambda b=box,s=seq:b.acknowledge('a',s,dict(status='consumed',reason='fixture')))
                if i>=0:row['samples'].append(times);row['ack_samples'].append(acks)
            snaps={k:snapshot(b) for k,b in boxes.items()};assert all(s==snaps['sequential_baseline'] for s in snaps.values())
            row['state_sha256']=hashlib.sha256(json.dumps(snaps['sequential_baseline'],sort_keys=True,ensure_ascii=False).encode()).hexdigest()
            result['cases'].append(row)
        observed={}
        for label,cls,batch in [('baseline',B,False),('candidate',C,True)]:
            box,event=make(cls,Path(tmp)/('trace-'+label))
            observed[label]=trace_transaction(box,[dict(event,event_id=str(i)) for i in range(8)],batch)
        assert observed['baseline']['begins']==observed['baseline']['commits']==8
        assert observed['candidate']['begins']==observed['candidate']['commits']==1
        assert observed['baseline']['changes']==observed['candidate']['changes']
        assert observed['baseline']['results']==observed['candidate']['results']
        result['observed']=observed
    out.mkdir(parents=True,exist_ok=False);(out/'raw.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();run(a.baseline,a.candidate,a.out);print('All paired samples and exact state retained.')
