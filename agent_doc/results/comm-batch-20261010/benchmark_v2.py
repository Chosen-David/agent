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

def trace_transaction(box,events,batch,record):
    sql=[];changes=[];original=box.connect
    record.update(sql=sql,changes=0,begins=0,commits=0,rollbacks=0,status='running')
    @contextmanager
    def observed():
        with original() as db:
            start=db.total_changes;db.set_trace_callback(sql.append)
            try:yield db
            finally:changes.append(db.total_changes-start)
        # Original context commits/closes while trace is still enabled.
    box.connect=observed
    try:
        record['results']=box.publish_many(events) if batch else [box.publish(e) for e in events]
        record['status']='complete'
    finally:
        box.connect=original
        record.update(changes=sum(changes),begins=sum(s=='BEGIN IMMEDIATE' for s in sql),
                      commits=sum(s=='COMMIT' for s in sql),rollbacks=sum(s=='ROLLBACK' for s in sql))
    return record

def run(baseline,candidate,out):
    B=load(baseline).Mailbox;C=load(candidate).Mailbox;S=atomic_reference(B)
    result=dict(environment=dict(python=sys.version,sqlite=sqlite3.sqlite_version,platform=platform.platform()),warmups=3,repeats=31,cases=[])
    out.mkdir(parents=True,exist_ok=False)
    result['status']='running'
    def checkpoint():
        (out/'raw.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    checkpoint()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            for n,f in [(1,1),(8,1),(32,3)]:
                row=dict(batch_size=n,fanout=f,samples=[],ack_samples=[],attempts=[])
                result['cases'].append(row);result['phase']=dict(stage='setup',batch_size=n,fanout=f);checkpoint()
                classes={'sequential_baseline':B,'sequential_candidate':C,'batch_candidate':C,'atomic_reference':S}
                boxes={};events={}
                for name,cls in classes.items():
                    box,event=make(cls,Path(tmp)/f'{n}-{f}-{name}',f);boxes[name]=box;events[name]=event
                    for i in range(100):box.publish(dict(event,event_id=f'seed-{i}'))
                for i in range(-3,31):
                    order=list(classes)
                    if i%2:order.reverse()
                    values={};times={};acks={}
                    attempt=dict(iteration=i,order=order,outputs=values,timing_ms=times,ack_ms=acks)
                    row['attempts'].append(attempt)
                    result['phase']=dict(stage='pair',batch_size=n,fanout=f,iteration=i);checkpoint()
                    for name in order:
                        es=[dict(events[name],event_id=f'{i}-{j}') for j in range(n)]
                        box=boxes[name]
                        fn=(lambda b=box,e=es:b.publish_many(e)) if name in ('batch_candidate','atomic_reference') else (lambda b=box,e=es:[b.publish(x) for x in e])
                        result['phase'].update(path=name,operation='publish')
                        values[name],times[name]=timed(fn)
                    assert all(v==values['sequential_baseline'] for v in values.values())
                    for name in order:
                        box=boxes[name];seq=values[name][0]['seq']
                        result['phase'].update(path=name,operation='ack')
                        _,acks[name]=timed(lambda b=box,s=seq:b.acknowledge('a',s,dict(status='consumed',reason='fixture')))
                    if i>=0:row['samples'].append(times);row['ack_samples'].append(acks)
                    attempt['status']='complete';checkpoint()
                result['phase']=dict(stage='state',batch_size=n,fanout=f)
                snaps={k:snapshot(b) for k,b in boxes.items()}
                row['state_hashes']={k:hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=False).encode()).hexdigest() for k,v in snaps.items()}
                if not all(v==snaps['sequential_baseline'] for v in snaps.values()):
                    row['failed_snapshots']=snaps
                    raise AssertionError('public outputs or database state differ')
                row['state_sha256']=hashlib.sha256(json.dumps(snaps['sequential_baseline'],sort_keys=True,ensure_ascii=False).encode()).hexdigest()
                checkpoint()
            observed={};result['observed']=observed
            for label,cls,batch in [('baseline',B,False),('candidate',C,True)]:
                box,event=make(cls,Path(tmp)/('trace-'+label))
                observed[label]={};result['phase']=dict(stage='trace',path=label);checkpoint()
                trace_transaction(box,[dict(event,event_id=str(i)) for i in range(8)],batch,observed[label]);checkpoint()
            assert observed['baseline']['begins']==observed['baseline']['commits']==8
            assert observed['candidate']['begins']==observed['candidate']['commits']==1
            assert observed['baseline']['changes']==observed['candidate']['changes']
            assert observed['baseline']['results']==observed['candidate']['results']
            checkpoint()
        result['status']='complete'
    except BaseException as exc:
        result['status']='failed'
        result['failure']=dict(type=type(exc).__name__,message=str(exc),phase=result.get('phase'))
        raise
    finally:
        checkpoint()
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();run(a.baseline,a.candidate,a.out);print('All paired samples and exact state retained.')
