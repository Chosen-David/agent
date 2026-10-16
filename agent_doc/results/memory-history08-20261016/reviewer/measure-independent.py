"""Frozen single-candidate full history/API measurement, baseline checkout only."""
import sys,json,sqlite3,shutil,tempfile,random,statistics,time,hashlib,re,platform
from pathlib import Path
from datetime import datetime
from unittest.mock import patch
sys.path.insert(0,str(Path.cwd()))
from agent_runtime.project_memory import MemoryLedger,MemoryError
OUT=Path(__file__).resolve().parent
PLAN=json.loads((OUT.parent/'plan.json').read_text())
DDL='CREATE INDEX memory_events_entry ON events(entry_id)'
QUERY='SELECT * FROM events WHERE entry_id=? ORDER BY sequence'
TABLES=('entries','dependencies','document_dependencies','events','sqlite_sequence')
def sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def snap(p):
 with sqlite3.connect(p) as db:
  db.row_factory=sqlite3.Row
  return {t:[dict(r) for r in db.execute('SELECT * FROM '+t+' ORDER BY rowid')] for t in TABLES}
def normalized(s,old):
 raw=[]
 for t,key in [('entries','id'),('events','sequence')]:
  oldrows={r[key]:r for r in old[t]}
  for r in s[t]:
   k=r[key]
   if k in oldrows:assert r['created_at']==oldrows[k]['created_at']
   else:
    assert k in ('revision','new-entry') if t=='entries' else k>max(oldrows,default=0)
    ts=r['created_at'];assert re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z',ts)
    datetime.fromisoformat(ts.replace('Z','+00:00'));raw.append([t,k,'created_at',ts]);r['created_at']='<new-clock>'
 return s,raw
def result_norm(r,op):
 if op=='correct':r['revision']['created_at']='<new-clock>'
 if op=='add':r['created_at']='<new-clock>'
 return r
def seed(root,cfg,cls=MemoryLedger):
 l=cls(root,create=True)
 with l._connect(write=True) as db:
  db.executemany('INSERT INTO entries VALUES(?,?,?,?,?,?,?,?)',[(f'n{i:05}','claim','x'*128,'synthetic:seed','[]','verified','stale' if cfg['id']=='history_many512' else 'active','2000-01-01T00:00:00.000Z') for i in range(cfg['nodes'])])
  if cfg['op']=='correct':db.executemany('INSERT INTO dependencies VALUES(?,?)',[(f'n{i:05}',f'n{i-1:05}') for i in range(1,16)])
  db.executemany('INSERT INTO events(entry_id,action,reason,source,created_at) VALUES(?,?,?,?,?)',[(f'n{0 if cfg["nodes"]==1 else i:05}','created' if cfg['nodes']>1 or i==0 else 'stale','fixture','synthetic:seed','2000-01-01T00:00:00.000Z') for i in range(cfg['events'])])
 return l.path

def clone(seedpath,root,index=False):
 p=root/'.agent-memory'/'memory.sqlite3';p.parent.mkdir(parents=True);shutil.copyfile(seedpath,p)
 before=p.stat().st_size;t=time.perf_counter_ns()
 if index:
  db=sqlite3.connect(p);db.execute(DDL);db.commit();db.close()
 return p,{'wall_ns':time.perf_counter_ns()-t if index else 0,'bytes_before':before,'bytes_after':p.stat().st_size}

def call(l,cfg):
 if cfg['op']=='history':return l.history(cfg['target'])
 if cfg['op']=='add':return l.add('new-entry','claim','new','synthetic:experiment',evidence='verified')
 return l.correct('n00000','revision','corrected','synthetic:user','fixture correction')

def validate():
 checks=[]
 with tempfile.TemporaryDirectory(prefix='agent-event-correct-',dir=OUT) as td:
  for arm in (0,1):
   l=MemoryLedger(Path(td)/str(arm),create=True)
   l.add('a','claim','a','test',evidence='verified')
   for k in ('b','c'):l.add(k,'claim',k,'test',deps=['a'],evidence='verified')
   l.correct('b','b2','new b','test','correction')
   if arm:
    with sqlite3.connect(l.path) as db:db.execute(DDL)
   before=snap(l.path)
   try:l.correct('a','bad','bad','test','reason',deps=['c'])
   except MemoryError as e:assert 'invalidated lineage' in str(e)
   else:raise AssertionError('pre-insert must fail')
   assert snap(l.path)==before
   original=MemoryLedger._event;hit=[]
   def fail(db,entry_id,action,*args):
    if action=='stale':hit.append(entry_id);raise sqlite3.OperationalError('injected')
    return original(db,entry_id,action,*args)
   with patch.object(MemoryLedger,'_event',side_effect=fail):
    try:l.correct('a','a2','new a','test','reason')
    except MemoryError as e:assert 'injected' in str(e)
    else:raise AssertionError('post-write must fail')
   assert hit==['c'] and snap(l.path)==before
   l.correct('a','a2','new a','test','reason')
   assert l.history('b')['entry']['status']=='superseded'
   assert l.history('c')['entry']['status']=='stale'
   assert l.history('b2')['entry']['status']=='active'
   assert [r['action'] for r in l.history('a')['events']]==['created','corrected']
   checks.append({'arm':arm,'preinsert_rollback':True,'postwrite_rollback':True,'history_superseded':True,'hit':hit})
 return checks

def main():
 start=time.time();rng=random.Random(81601)
 data={'source_sha256':hashlib.sha256(Path('agent_runtime/project_memory.py').read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'plan_sha256':hashlib.sha256((OUT.parent/'plan.json').read_bytes()).hexdigest(),'sqlite':sqlite3.sqlite_version,'python':platform.python_version(),'fixtures':{},'pending_independent_review':True}
 with tempfile.TemporaryDirectory(prefix='agent-event-index-',dir=OUT) as td:
  td=Path(td)
  for cfg in PLAN['fixtures']:
   fid=cfg['id'];source=seed(td/(fid+'seed'),cfg);old=snap(source);input_hash=sha(old)
   assert len(old['entries'])==cfg['nodes'] and len(old['events'])==cfg['events']
   r={'input_hash':input_hash,'plans':{},'samples':[],'ddl':[]}
   for arm in (0,1):
    p,_=clone(source,td/(fid+'plan'+str(arm)),arm)
    with sqlite3.connect(p) as db:
     r['plans'][str(arm)]={'eqp':db.execute('EXPLAIN QUERY PLAN '+QUERY,(cfg.get('target','n00000'),)).fetchall(),'pragma':{q:db.execute('PRAGMA '+q).fetchall() for q in ('automatic_index','journal_mode','page_size','page_count','index_list(events)','index_xinfo(memory_events_entry)')},'schema':db.execute('SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY name').fetchall(),'files':[x.name for x in p.parent.iterdir()]}
   for pair in range(-3,21):
    order=[0,1];rng.shuffle(order);answers={};states={}
    for arm in order:
     root=td/f'{fid}{pair}a{arm}';p,ddl=clone(source,root,arm)
     assert sha(snap(p))==input_hash
     before=hashlib.sha256(p.read_bytes()).hexdigest();l=MemoryLedger(root)
     t=time.perf_counter_ns();answer=call(l,cfg);elapsed=time.perf_counter_ns()-t
     state,clocks=normalized(snap(p),old)
     if cfg['op']=='history':
      assert hashlib.sha256(p.read_bytes()).hexdigest()==before
      expected=[e for e in old['events'] if e['entry_id']==cfg['target']]
      assert answer['events']==expected and state==old
     if cfg['op']=='correct':
      assert answer['affected']==[f'n{i:05}' for i in range(1,16)]
      status={e['id']:e['status'] for e in state['entries']}
      assert status['n00000']=='superseded' and status['revision']=='active'
      assert all(status[f'n{i:05}']=='stale' for i in range(1,16))
      assert all(status[f'n{i:05}']=='active' for i in range(16,cfg['nodes']))
     answer=result_norm(answer,cfg['op']);answers[arm]=answer;states[arm]=state
     if pair>=0:
      r['samples'].append({'pair':pair,'arm':arm,'order':order,'wall_ns':elapsed,'output_sha256':sha(answer),'state_sha256':sha(state),'new_timestamps':clocks})
      if arm:r['ddl'].append(ddl)
     shutil.rmtree(root)
    assert answers[0]==answers[1] and states[0]==states[1]
    assert time.time()-start<1500
   med={str(a):statistics.median(s['wall_ns'] for s in r['samples'] if s['arm']==a) for a in (0,1)}
   r['median_ns']=med;r['reduction']=1-med['1']/med['0'];data['fixtures'][fid]=r
   (OUT/'raw.json').write_text(json.dumps(data,indent=2)+'\n');print(fid,med,r['reduction'],flush=True)
 data['validation']=validate()
 data['gates']={k:v['reduction']>=(.30 if k in ('history_first50000','history_last50000') else -.15) for k,v in data['fixtures'].items()}
 data['elapsed_seconds']=time.time()-start
 (OUT/'raw.json').write_text(json.dumps(data,indent=2)+'\n');print('gates',data['gates'],flush=True)
if __name__=='__main__':main()
