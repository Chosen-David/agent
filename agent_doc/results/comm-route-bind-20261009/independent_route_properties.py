"""Independent Python-list authorization oracle, seed fixed before execution."""
import hashlib,random,tempfile
from pathlib import Path

def run(cls):
    rng=random.Random(20261009); checks=[]
    def ok(name,v):assert v,name;checks.append(name)
    def rejects(name,fn):
        try:fn()
        except ValueError:checks.append(name);return
        raise AssertionError(name)
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp);(p/'ref').write_bytes(b'evidence');ref=dict(id='r',path='ref',sha256=hashlib.sha256(b'evidence').hexdigest())
        route=lambda s,t,k,r:dict(sender=s,task_id=t,kind=k,recipient=r)
        routes=[route('s','T','artifact',r) for r in ['z','a']]
        routes.extend([route('other','T','artifact','bad-s'),route('s','other','artifact','bad-t'),route('s','T','question','bad-k')])
        plan=dict(schema_version=1,run_id='one',input_version='v1',max_events=300,routes=routes)
        b=cls(p/'db',plan,p)
        def event(i,**kw):return dict(dict(event_id=str(i),run_id='one',input_version='v1',sender='s',task_id='T',kind='artifact',summary='read',action='verify',refs=[ref]),**kw)
        for i in range(80):
            current=[route(rng.choice(['s','x']),rng.choice(['T','X']),rng.choice(['artifact','question']),rng.choice(['a','b','z'])) for _ in range(rng.randrange(0,30))]
            b.plan['routes']=current;ev=event(i)
            expected=sorted(set(r['recipient'] for r in current if (r['sender'],r['task_id'],r['kind'])==('s','T','artifact')))
            before=b.usage()
            if expected:
                sent=b.publish(ev);ok('random_fanout_'+str(i),sent['recipients']==expected)
                for r in expected:ok('random_delivery_'+str(i)+'_'+r,any(x['seq']==sent['seq'] and x['event']==ev for x in b.inbox(r,limit=100)))
            else:
                rejects('random_unmatched_'+str(i),lambda:b.publish(ev));ok('random_atomic_'+str(i),b.usage()==before)
        b.plan['routes']=routes;ev=event('duplicate');sent=b.publish(ev);before=b.usage()
        ok('sorted_unique_all3keys',sent['recipients']==['a','z'])
        b.plan['routes']=[r for r in routes if r['recipient'].startswith('bad')]
        rejects('duplicate_liveplan_authority',lambda:b.publish(ev));ok('no_duplicate_mutation',b.usage()==before)
        b.plan['routes']=routes
        ok('duplicate_restored',b.publish(ev)==dict(seq=sent['seq'],recipients=['a','z'],duplicate=True))
        rejects('duplicate_immutable_body',lambda:b.publish(dict(ev,summary='changed')))
        for key in ['sender','task_id','kind']:
            bad=dict(ev,event_id='bad-'+key);bad[key]='nonmatching'
            rejects('independent_required_'+key,lambda:b.publish(bad))
        for name,bad in [('empty_sender',dict(ev,sender='')),('missing_kind',{k:v for k,v in ev.items() if k!='kind'}),('crossrun',dict(ev,run_id='other')),('stale',dict(ev,input_version='v0')),('extra',dict(ev,extra=1))]:rejects(name,lambda:b.publish(bad))
        (p/'ref').write_bytes(b'changed');rejects('duplicate_refs_revalidated',lambda:b.publish(ev))
        ok('failures_atomic',b.usage()==before)
    return dict(ok=True,count=len(checks),seed=20261009,checks=checks)
