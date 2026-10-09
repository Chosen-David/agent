"""Independent public ACK boundary and concurrency properties."""
import hashlib, json, sqlite3, tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

def run(cls):
    checks=[]
    def ok(name,value):
        assert value,name
        checks.append(name)
    def reject(name,fn):
        try: fn()
        except (ValueError,sqlite3.Error): checks.append(name); return
        raise AssertionError(name)
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp); (root/'data').write_bytes(b'proof')
        ref=dict(id='d',path='data',sha256=hashlib.sha256(b'proof').hexdigest())
        def plan(run): return dict(schema_version=1,run_id=run,input_version='v1',max_events=100,max_message_bytes=8192,routes=[dict(sender='s',recipient='a',task_id='T',kind='artifact')])
        def event(run,i): return dict(event_id=str(i),run_id=run,input_version='v1',sender='s',task_id='T',kind='artifact',summary='proof',action='read',refs=[ref])
        p=plan('one'); b=cls(root/'db',p,root); other=cls(root/'db',plan('two'),root)
        usage=b.usage()
        for i,status in enumerate(('consumed','rejected','needs_revision')):
            seq=b.publish(event('one',i))['seq']; before=b.usage(); r=dict(status=status,reason='证据')
            ok('first_return_'+status,b.acknowledge('a',seq,r) is None)
            ok('first_status_'+status,b.status()[-1]['receipt']==r)
            ok('reordered_return_'+status,b.acknowledge('a',seq,dict(reason='证据',status=status)) is None)
            ok('unchanged_counters_'+status,b.usage()==before)
            reject('conflict_'+status,lambda:b.acknowledge('a',seq,dict(status=status,reason='changed')))
            reject('crossrun_'+status,lambda:other.acknowledge('a',seq,r))
            reject('unknown_recipient_'+status,lambda:b.acknowledge('other',seq,r))
            reject('oversized_'+status,lambda:b.acknowledge('a',seq,dict(status=status,reason='x'*9000)))
            invalid=[None,[],{},dict(status=status),dict(status=status,reason=''),dict(status=status,reason=' '),dict(status='bad',reason='x'),dict(status=status,reason='x',extra=1)]
            for j,r2 in enumerate(invalid): reject(f'invalid_{status}_{j}',lambda:b.acknowledge('a',seq,r2))
            reject('bool_seq_'+status,lambda:b.acknowledge('a',True,r))
        reject('missing_delivery',lambda:b.acknowledge('a',99999,dict(status='consumed',reason='x')))
        seq=b.publish(event('one','threads'))['seq']; before=b.usage(); r=dict(status='needs_revision',reason='thread')
        with ThreadPoolExecutor(max_workers=4) as pool: result=list(pool.map(lambda _:b.acknowledge('a',seq,r),range(8)))
        ok('concurrent_first_and_duplicates',result==[None]*8 and b.status()[-1]['receipt']==r)
        ok('thread_counters',b.usage()==before)
        old=b.status(); reopened=cls(root/'db',p,root)
        ok('reopen_status',reopened.status()==old)
        ok('reopen_counters',reopened.usage()==before)
        ok('reopen_duplicate',reopened.acknowledge('a',seq,dict(reason='thread',status='needs_revision')) is None and reopened.status()==old)
    return dict(ok=True,count=len(checks),checks=checks)
