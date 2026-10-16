"""Private, single-candidate diagnostic. No production schema mutation."""
import sys, json, sqlite3, shutil, tempfile, random, statistics, time, hashlib, platform, re
from pathlib import Path
from datetime import datetime, timezone
sys.path.insert(0, str(Path.cwd()))
from agent_runtime.project_memory import MemoryLedger, MemoryError
from unittest.mock import patch
OUT=Path(__file__).resolve().parent
PLAN=json.loads((OUT/'plan-v2.json').read_text())
SQL='''WITH RECURSIVE affected(id) AS (
 SELECT child FROM dependencies WHERE parent=?
 UNION SELECT d.child FROM dependencies d JOIN affected a ON d.parent=a.id)
 SELECT id FROM affected ORDER BY id'''
DDL='CREATE INDEX memory_dependencies_parent ON dependencies(parent,child)'
TABLES=('entries','dependencies','document_dependencies','events','sqlite_sequence')
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def snap(path):
    with sqlite3.connect(path) as db:
        db.row_factory=sqlite3.Row
        return {t:sorted([dict(r) for r in db.execute('SELECT * FROM '+t)],key=lambda x:json.dumps(x,sort_keys=True)) for t in TABLES}
def normalize(s, old):
    s=json.loads(json.dumps(s)); raw=[]
    for t in ('entries','events'):
        keys={r['id'] if t=='entries' else r['sequence']:r for r in old[t]}
        for r in s[t]:
            k=r['id'] if t=='entries' else r['sequence']
            if k in keys:
                assert r['created_at']==keys[k]['created_at']
            else:
                assert (k in ('revision','new-entry')) if t=='entries' else k>max(keys,default=0)
                ts=r['created_at'];assert re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z',ts)
                datetime.fromisoformat(ts.replace('Z','+00:00'))
                raw.append([t,k,'created_at',ts]);r['created_at']='<new-clock>'
    return s,raw
def call(ledger,op):
    if op=='impact':return ledger.impact('n00000')
    if op=='correct':return ledger.correct('n00000','revision','corrected','synthetic:user','fixture correction')
    return ledger.add('new-entry','claim','new','synthetic:experiment',deps=['n00000'],evidence='verified')
def norm_result(r,op):
    r=json.loads(json.dumps(r))
    if op=='correct':r['revision']['created_at']='<new-clock>'
    elif op=='add':r['created_at']='<new-clock>'
    return r
def seed(root,cfg):
    l=MemoryLedger(root,create=True)
    with l._connect(write=True) as db:
        db.executemany('INSERT INTO entries VALUES(?,?,?,?,?,?,?,?)',[(f'n{i:05}','claim','x'*128,'synthetic:seed','[]','verified','active','2000-01-01T00:00:00.000Z') for i in range(cfg['nodes'])])
        edges=[(f'n{i:05}',f'n{0 if "wide" in cfg else i-1:05}') for i in range(1,cfg['nodes']) if 'wide' in cfg or i%16]
        db.executemany('INSERT INTO dependencies VALUES(?,?)',edges)
        db.executemany('INSERT INTO events(entry_id,action,reason,source,created_at) VALUES(?,?,?,?,?)',[(f'n{i:05}','created','verified','synthetic:seed','2000-01-01T00:00:00.000Z') for i in range(cfg['nodes'])])
    return l.path

def copy_arm(seedpath,root,index):
    p=root/'.agent-memory'/'memory.sqlite3';p.parent.mkdir(parents=True);shutil.copyfile(seedpath,p)
    before=p.stat().st_size;elapsed=0
    if index:
        t=time.perf_counter_ns();db=sqlite3.connect(p);db.execute(DDL);db.commit();db.close();elapsed=time.perf_counter_ns()-t
    return p,{'ns':elapsed,'bytes_before':before,'bytes_after':p.stat().st_size}

def main():
    begin=time.time();rng=random.Random(71406);output={'plan_hash':hashlib.sha256((OUT/'plan-v2.json').read_bytes()).hexdigest(),'source_hash':hashlib.sha256(Path('agent_runtime/project_memory.py').read_bytes()).hexdigest(),'python':platform.python_version(),'sqlite':sqlite3.sqlite_version,'fixtures':{},'validation':[]}
    with tempfile.TemporaryDirectory(prefix='agent-reverse-index-') as tmp:
        tmp=Path(tmp)
        for cfg in PLAN['fixtures']:
            fid=cfg['id'];base=seed(tmp/(fid+'seed'),cfg);old=snap(base)
            assert len(old['entries'])==cfg['nodes']
            expected=512 if 'wide' in cfg else 15
            assert [x['id'] for x in MemoryLedger(base.parent.parent).impact('n00000')]==[f'n{i:05}' for i in range(1,expected+1)]
            rec={'input_hash':digest(old),'samples':[],'plans':{},'ddl':[]}
            # Inspect both query plans on their own disposable copies.
            for arm in (0,1):
                p,_=copy_arm(base,tmp/(fid+'explain'+str(arm)),arm)
                with sqlite3.connect(p) as db:
                    rec['plans'][str(arm)]={'eqp':db.execute('EXPLAIN QUERY PLAN '+SQL,('n00000',)).fetchall(),'pragma':{x:db.execute('PRAGMA '+x).fetchall() for x in ('automatic_index','journal_mode','page_size','page_count','index_list(dependencies)')},'schema':db.execute("SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY name").fetchall(),'index_info':db.execute('PRAGMA index_info(memory_dependencies_parent)').fetchall(),'side_files':[x.name for x in p.parent.iterdir()]}
            for pair in range(-3,21):
                order=[0,1];rng.shuffle(order);answers={};states={}
                for arm in order:
                    root=tmp/f'{fid}-{pair}-{arm}';p,ddl=copy_arm(base,root,arm)
                    assert digest(snap(p))==rec['input_hash']
                    before=hashlib.sha256(p.read_bytes()).hexdigest();l=MemoryLedger(root)
                    t=time.perf_counter_ns();ans=call(l,cfg['op']);elapsed=time.perf_counter_ns()-t
                    s=snap(p);normalized,timestamps=normalize(s,old)
                    if cfg['op']=='impact':assert hashlib.sha256(p.read_bytes()).hexdigest()==before
                    if cfg['op']=='correct':
                        status={r['id']:r['status'] for r in s['entries']}
                        assert status['n00000']=='superseded' and status['revision']=='active'
                        assert all(status[f'n{i:05}']=='stale' for i in range(1,expected+1))
                        assert all(status[f'n{i:05}']=='active' for i in range(expected+1,cfg['nodes']))
                        assert len(ans['affected'])==expected
                    answers[arm]=norm_result(ans,cfg['op']);states[arm]=normalized
                    if pair>=0:
                        rec['samples'].append({'pair':pair,'arm':arm,'order':order,'wall_ns':elapsed,'timestamps':timestamps,'output_hash':digest(answers[arm]),'state_hash':digest(normalized)})
                        if arm:rec['ddl'].append(ddl)
                    shutil.rmtree(root)
                assert answers[0]==answers[1] and states[0]==states[1]
            med={str(a):statistics.median(s['wall_ns'] for s in rec['samples'] if s['arm']==a) for a in (0,1)}
            rec['median_ns']=med;rec['reduction']=1-med['1']/med['0'];output['fixtures'][fid]=rec
            (OUT/'raw.json').write_text(json.dumps(output,indent=2)+'\n')
            print(fid,med,rec['reduction'],flush=True)
            assert time.time()-begin<1200
        # Independent oracle checks invalidation/history/rollback on small real APIs.
        for arm in (0,1):
            root=tmp/('validation'+str(arm));l=MemoryLedger(root,create=True)
            l.add('a','claim','a','test',evidence='verified');l.add('b','claim','b','test',deps=['a'],evidence='verified')
            l.correct('b','b2','new b','test','new')
            if arm:
                with sqlite3.connect(l.path) as db:db.execute(DDL)
            before=snap(l.path)
            try:l.correct('a','bad','bad','test','reason',deps=['b'])
            except MemoryError:pass
            else:raise AssertionError('lineage should fail')
            assert snap(l.path)==before
            original=MemoryLedger._event
            def fail(db,entry_id,action,*args):
                if action=='stale':raise sqlite3.OperationalError('injected')
                return original(db,entry_id,action,*args)
            with patch.object(MemoryLedger,'_event',side_effect=fail):
                try:l.correct('a','a2','new a','test','reason')
                except MemoryError:pass
                else:raise AssertionError('write rollback should fail')
            assert snap(l.path)==before
            l.correct('a','a2','new a','test','reason')
            assert l.history('b')['entry']['status']=='superseded'
            assert l.history('b2')['entry']['status']=='active'
            assert [r['id'] for r in l.impact('a')]==['b']
            output['validation'].append({'arm':arm,'lineage_rollback':True,'write_rollback':True,'preserve_superseded':True,'history':True})
    output['gates']={k:(v['reduction']>=.20 if 'sparse5000' in k else v['reduction']>=-.15) for k,v in output['fixtures'].items()}
    output['elapsed_seconds']=time.time()-begin;output['pending_independent_review']=True
    (OUT/'raw.json').write_text(json.dumps(output,indent=2)+'\n')
    print('gates',output['gates'],flush=True)
if __name__=='__main__':main()
