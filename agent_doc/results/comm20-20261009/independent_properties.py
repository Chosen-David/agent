"""Independent public list/byte oracle; no producer fixtures or assertions reused."""
import hashlib, json, sys, tempfile, sqlite3, types
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
def load(path):
    m=types.ModuleType('agent_runtime.independent_comm');m.__package__='agent_runtime'
    exec(compile(Path(path).read_text(),str(path),'exec'),m.__dict__);return m.Mailbox

def run(cls):
    checks=[]
    def ok(name,value):
        assert value,name;checks.append(name)
    def rejects(name,f):
        try:f()
        except (ValueError,sqlite3.Error):checks.append(name);return
        raise AssertionError(name)
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp);(root/'ref').write_bytes('证据'.encode());ref={'id':'data','path':'ref','sha256':hashlib.sha256((root/'ref').read_bytes()).hexdigest()}
        def plan(run):return {'schema_version':1,'run_id':run,'input_version':'v1','max_events':200,'max_message_bytes':8192,'routes':[{'sender':'s','recipient':r,'task_id':'T','kind':'artifact'} for r in ['a','z']]}
        boxes={r:cls(root/'db',plan(r),root) for r in ['one','two']};records=[];receipts={}
        def event(run,i):return dict(event_id=str(i),run_id=run,input_version='v1',sender='s',task_id='T',kind='artifact',summary='中文'+str(i),action='read',refs=[dict(ref)])
        for i in range(18):
            run='one' if i%3 else 'two';ev=event(run,i);ret=boxes[run].publish(ev);records.append((ret['seq'],run,ev));ok('fanout_'+str(i),ret['recipients']==['a','z'])
            if i%4==0:boxes[run].acknowledge('a',ret['seq'],{'status':'consumed','reason':'done'});receipts[(ret['seq'],'a')]={'status':'consumed','reason':'done'}
        for run,b in boxes.items():
            for recipient in ['a','z']:
                for limit in [1,3,20,100]:
                    expected=[{'seq':seq,'event':ev} for seq,r,ev in records if r==run and (seq,recipient) not in receipts][:limit]
                    ok(f'ordered_list_{run}_{recipient}_{limit}',b.inbox(recipient,limit=limit)==expected)
            status=[{'seq':seq,'recipient':recipient,'receipt':receipts.get((seq,recipient))} for seq,r,ev in records if r==run for recipient in ['a','z']]
            ok('exact_status_'+run,b.status()==status)
            bodies=[json.dumps(ev,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode() for seq,r,ev in records if r==run];u=b.usage()
            ok('unicode_usage_'+run,(u['events'],u['envelope_bytes'],u['deliveries'],u['delivery_bytes'],u['tokens'])==(len(bodies),sum(map(len,bodies)),2*len(bodies),2*sum(map(len,bodies)),None))
            for bad in [0,101,True,-1]:rejects('invalid_limit_'+str(bad),lambda:b.inbox('a',limit=bad))
            rejects('unknown_recipient',lambda:b.inbox('unknown'))
        seq,run,ev=records[0];b=boxes[run]
        rejects('crossrun_ack',lambda:boxes['one'].acknowledge('a',seq,{'status':'consumed','reason':'done'}))
        b.acknowledge('a',seq,{'status':'consumed','reason':'done'})
        rejects('immutable_ack',lambda:b.acknowledge('a',seq,{'status':'rejected','reason':'changed'}))
        rejects('root_identity',lambda:cls(root/'db',plan(run),root/'other'))
        rejects('crossrun_publish',lambda:boxes['one'].publish(ev))
        (root/'ref').write_bytes(b'mutated');rejects('duplicate_mutated_ref',lambda:b.publish(ev));(root/'ref').write_bytes('证据'.encode())
        ev2=event('one','parallel')
        with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(lambda _:boxes['one'].publish(ev2),range(6)))
        ok('concurrent_duplicates',len({x['seq'] for x in results})==1 and sum(not x['duplicate'] for x in results)==1)
        handoff={'schema_version':1,'run_id':'one','role':'s','input_version':'v1','status':'completed','limitations':[],'artifacts':[dict(ref)],'checks':[{'criterion':'verified','status':'pass','artifact_ids':['data']}],'tasks':[{'task_id':'T','status':'done','depends_on':[],'evidence':['data']}]}
        raw=json.dumps(handoff,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode();(root/'manifest').write_bytes(raw)
        manifest_ev=event('one','handoff');manifest_ev['refs']=[{'id':'handoff','path':'manifest','sha256':hashlib.sha256(raw).hexdigest()}]
        hseq=boxes['one'].publish(manifest_ev)['seq'];request={'schema_version':1,'input_version':'v1','tasks':[{'task_id':'T'}]}
        ok('valid_public_handoff',boxes['one'].consume_handoff('a',hseq,request)==handoff)
        handoff['limitations']=['changed valid document'];(root/'manifest').write_text(json.dumps(handoff))
        rejects('changed_valid_manifest',lambda:boxes['one'].consume_handoff('a',hseq,request))
        (root/'manifest').write_bytes(raw);(root/'ref').write_bytes(b'stale data')
        impact=boxes['one'].impact();ok('actual_stale_basis',len(impact)==1 and impact[0]['seq']==hseq and impact[0]['recipient']=='a' and impact[0]['stale'])
        (root/'ref').write_bytes('证据'.encode())
        # Real old schema simulation: drop cached usage marker/triggers; constructor must backfill.
        with sqlite3.connect(root/'db') as db:
            db.execute('DROP TRIGGER communication_usage_event_v1');db.execute('DROP TRIGGER communication_usage_delivery_v1');db.execute('DROP TABLE communication_usage_v1')
        old=boxes['one'].status();reopened=cls(root/'db',plan('one'),root);ok('migration_order',reopened.status()==old)
        with sqlite3.connect(root/'db') as db:
            scan=db.execute('SELECT count(*),sum(length(CAST(body AS BLOB))) FROM communication_events WHERE run_id=?',('one',)).fetchone()
        ok('migration_usage',(reopened.usage()['events'],reopened.usage()['envelope_bytes'])==scan)
        p=plan('budget');p['max_delivery_bytes']=1;tight=cls(root/'tight',p,root)
        rejects('atomic_budget',lambda:tight.publish(event('budget',1)));ok('no_partial_budget',tight.status()==[] and tight.usage()['events']==0)
    return {'ok':True,'checks':checks,'count':len(checks)}
if __name__=='__main__':
    print(json.dumps(run(load(sys.argv[1])),indent=2))
