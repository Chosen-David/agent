"""Actual fresh host child /root/batch_verify; evidence-only independent checks."""
import ast,copy,difflib,hashlib,importlib.util,io,json,math,platform,sqlite3,statistics,subprocess,sys,tempfile,threading,unittest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[3];D=Path(__file__).parent;sys.path.insert(0,str(ROOT))
from agent_runtime.result_validation import _snapshot,_review
from scripts.benchmark_communication_candidates_v2 import load

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p))
def module(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def state(b):
 with b.connect() as db:return {t:[list(r) for r in db.execute('SELECT * FROM '+t+' ORDER BY 1,2')] for t in ['communication_events','communication_deliveries','communication_usage_v1','communication_basis','sqlite_sequence']}

def own(cls):
 checks=[]
 def ok(n,v):assert v,n;checks.append(n)
 with tempfile.TemporaryDirectory() as tmp:
  r=Path(tmp);(r/'proof').write_bytes('证据'.encode());rr=dict(id='e',path='proof',sha256=digest(r/'proof'))
  p=dict(schema_version=1,run_id='r',input_version='v',routes=[dict(sender='s',recipient=x,task_id='T',kind='artifact') for x in ['b','a']])
  b=cls(r/'db',p,r);p=b.plan
  def e(i,**kw):return dict(dict(event_id=str(i),run_id='r',input_version='v',sender='s',task_id='T',kind='artifact',summary='😀界',action='read',refs=[dict(rr)]),**kw)
  def reject(n,es):
   before=state(b)
   try:b.publish_many(es)
   except (ValueError,sqlite3.Error):pass
   else:raise AssertionError(n+' accepted')
   ok(n,state(b)==before)
  for bad in [[],{},tuple([e(1)]),[e(i) for i in range(101)]]:reject('bounded_list',bad)
  for bad in [None,e(2,sender='wrong'),e(2,refs=[]),e(2,input_version='stale'),e(2,summary=''),dict(e(2),extra=1),e(1,summary='conflict')]:reject('midbatch_atomic',[e(1),bad])
  es=[e(1),e(2),e(1)];rows=b.publish_many(es)
  ok('ordered_duplicate',[(x['seq'],x['duplicate']) for x in rows]==[(1,False),(2,False),(1,True)])
  ok('list_oracle',b.inbox('a')==[dict(seq=i+1,event=x) for i,x in enumerate(es[:2])])
  size=sum(len(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()) for x in es[:2]);u=b.usage()
  ok('unicode_ledger',(u['events'],u['envelope_bytes'],u['deliveries'],u['delivery_bytes'],u['tokens'])==(2,size,4,size*2,None))
  (r/'proof').write_bytes(b'stale');reject('duplicate_ref',[e(1)]);(r/'proof').write_bytes('证据'.encode())
  old=copy.deepcopy(p['routes']);p['routes']=[dict(x,task_id='else') for x in old];reject('current_route',[e(1)]);p['routes']=old
  p['max_events']=3;reject('cumulative_events',[e(3),e(4)]);p.pop('max_events')
  p['max_delivery_bytes']=u['delivery_bytes']+1;reject('cumulative_bytes',[e(3)]);p.pop('max_delivery_bytes')
  p['max_message_bytes']=1;reject('message_bytes',[e(3)]);p.pop('max_message_bytes')
  with ThreadPoolExecutor(max_workers=4) as pool:rs=list(pool.map(lambda _:b.publish_many([e(3),e(4)]),range(4)))
  ok('thread_retry',sum(not x['duplicate'] for row in rs for x in row)==2 and b.usage()['events']==4)
  reject('rollback_after_existing',[e(5),e(1,summary='conflict')]);ok('connection_recovery',not b.publish_many([e(5)])[0]['duplicate'])
  ok('cap100',len(b.publish_many([e(i) for i in range(1000,1100)]))==100)
  # Pause after first INSERT while reader uses a separate connection; observe zero partial events.
  for mode in ['WAL','DELETE']:
   bb=cls(r/('visible-'+mode),p,r)
   with sqlite3.connect(bb.path) as db:ok('journal_'+mode,db.execute('PRAGMA journal_mode='+mode).fetchone()[0].upper()==mode)
   entered=threading.Event();release=threading.Event();orig=bb._store_publish
   def paused(db,event,body,recipients):
    result=orig(db,event,body,recipients)
    if event['event_id']=='800':entered.set();assert release.wait(5)
    return result
   bb._store_publish=paused
   with ThreadPoolExecutor(max_workers=1) as pool:
    future=pool.submit(bb.publish_many,[e(800),e(801)])
    try:
     assert entered.wait(5)
     with sqlite3.connect(bb.path) as reader:ok('reader_no_partial_'+mode,reader.execute('SELECT count(*) FROM communication_events').fetchone()[0]==0)
    finally:release.set()
    ok('reader_complete_'+mode,len(future.result())==2 and len(bb.inbox('a'))==2)
 return dict(ok=True,count=len(checks),checks=checks)

def properties():
 oracle=module(D.parent/'comm20-20261009/independent_properties.py','batch_public')
 for label in ['baseline','candidate']:
  cls=load(D/(label+'.py')).Mailbox;out=oracle.run(cls);assert out['count']==61
  (D/('independent_properties_'+label+'.json')).write_text(json.dumps(out,indent=2)+'\n')
  m=module(ROOT/'tests/test_communication_regressions.py','batch_reg_'+label);m.Mailbox=cls;stream=io.StringIO();r=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(m))
  (D/('independent_regressions_'+label+'.log')).write_text(stream.getvalue());assert r.wasSuccessful() and r.testsRun==2
 C=load(D/'candidate.py').Mailbox
 out=own(C);(D/'independent_batch_oracles.json').write_text(json.dumps(out,indent=2)+'\n')
 m=module(D/'batch_tests.py','batch_frozen');m.Mailbox=C;names=[n for n in unittest.defaultTestLoader.getTestCaseNames(m.BatchTests) if 'cli' not in n];stream=io.StringIO();r=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.TestSuite(m.BatchTests(n) for n in names))
 (D/'independent_frozen_tests.log').write_text(stream.getvalue());assert r.wasSuccessful() and r.testsRun==7
 bench=module(D/'benchmark_v2.py','batch_bench_ref');S=bench.atomic_reference(load(D/'baseline.py').Mailbox)
 with tempfile.TemporaryDirectory() as tmp:
  b,e=bench.make(S,Path(tmp)/'ref',3);es=[dict(e,event_id=str(i)) for i in range(8)];rows=b.publish_many(es);assert len(rows)==8 and b.usage()['events']==8
  before=state(b)
  try:b.publish_many([dict(e,event_id='new'),dict(e,event_id='bad',refs=[])])
  except ValueError:pass
  else:raise AssertionError('reference failed to reject')
  assert state(b)==before and b._batch_db is None
 (D/'independent_atomic_reference.json').write_text(json.dumps(dict(ok=True,valid_events=8,fanout=3,invalid_midbatch_rollback=True,borrowed_reset=True),indent=2)+'\n')

def summarize(path):
 raw=json.loads(path.read_text());assert raw['status']=='complete' and raw['repeats']==31 and raw['warmups']==3
 assert [(c['batch_size'],c['fanout']) for c in raw['cases']]==[(1,1),(8,1),(32,3)]
 names=['sequential_baseline','sequential_candidate','batch_candidate','atomic_reference'];rows=[]
 for c in raw['cases']:
  assert len(c['samples'])==len(c['ack_samples'])==31 and len(c['attempts'])==34
  for i,a in zip(range(-3,31),c['attempts']):
   assert a['iteration']==i and a['status']=='complete' and a['order']==(names[::-1] if i%2 else names)
   assert set(a['outputs'])==set(names) and all(x==a['outputs']['sequential_baseline'] for x in a['outputs'].values())
   for k in ['timing_ms','ack_ms']:
    assert set(a[k])==set(names) and all(type(v) in (int,float) and math.isfinite(v) and v>0 for v in a[k].values())
   if i>=0:assert a['timing_ms']==c['samples'][i] and a['ack_ms']==c['ack_samples'][i]
  assert set(c['state_hashes'])==set(names) and set(c['state_hashes'].values())=={c['state_sha256']}
  med={n:statistics.median(x[n] for x in c['samples']) for n in names};ack={n:statistics.median(x[n] for x in c['ack_samples']) for n in names}
  def guard(x,y):return x<=1.25*y or x-y<.2
  guards=dict(legacy=guard(med['sequential_candidate'],med['sequential_baseline']),atomic=guard(med['batch_candidate'],med['atomic_reference']))
  if c['batch_size']==1:guards['B1']=guard(med['batch_candidate'],med['sequential_baseline'])
  guards.update({'ack_'+n:guard(ack[n],ack['sequential_baseline']) for n in names})
  gain=med['sequential_baseline']/med['batch_candidate'];delta=med['sequential_baseline']-med['batch_candidate']
  rows.append(dict(shape=[c['batch_size'],c['fanout']],median_ms=med,ack_ms=ack,speedup=gain,delta_ms=delta,primary=c['batch_size']>1,improved=gain>=2 and delta>=.5,guards=guards,guard=all(guards.values()),ranges_ms={n:[min(x[n] for x in c['samples']),max(x[n] for x in c['samples'])] for n in names}))
 o=raw['observed'];assert o['baseline']['begins']==o['baseline']['commits']==8 and o['candidate']['begins']==o['candidate']['commits']==1
 assert o['baseline']['changes']==o['candidate']['changes'] and o['baseline']['results']==o['candidate']['results'] and o['baseline']['rollbacks']==o['candidate']['rollbacks']==0
 return rows

def validate():
 contract=json.loads((D/'contract.json').read_text());manifest,plan,proof=_snapshot(ROOT,contract);assert proof==json.loads((D/'independent_before_snapshot.json').read_text())
 base=(D/'baseline.py').read_text();cand=(D/'candidate.py').read_text();assert base.encode()==subprocess.check_output(['git','show','e6b3dc14ad9eb2c5d3c1cb09ccda5027a7d74019:agent_runtime/communication.py'],cwd=ROOT)
 def methods(code):
  t=ast.parse(code);box=next(n for n in t.body if isinstance(n,ast.ClassDef) and n.name=='Mailbox');return {n.name:ast.dump(n,include_attributes=False) for n in box.body if isinstance(n,ast.FunctionDef)}
 bm,cm=methods(base),methods(cand);assert all(cm[k]==v for k,v in bm.items() if k!='publish')
 # Extraction preserves every original validation/SQL statement in original order.
 bs=ast.parse(base);cs=ast.parse(cand);bb=next(n for n in bs.body if isinstance(n,ast.ClassDef) and n.name=='Mailbox');cb=next(n for n in cs.body if isinstance(n,ast.ClassDef) and n.name=='Mailbox');fm=lambda b,n:next(x for x in b.body if isinstance(x,ast.FunctionDef) and x.name==n)
 old=fm(bb,'publish');prep=fm(cb,'_prepare_publish');store=fm(cb,'_store_publish');assert [ast.dump(x) for x in old.body[:-1]]==[ast.dump(x) for x in prep.body[:-1]]
 assert [ast.dump(x) for x in old.body[-1].body[1:]]==[ast.dump(x) for x in store.body]
 (D/'independent_source.diff').write_text(''.join(difflib.unified_diff(base.splitlines(True),cand.splitlines(True))))
 cohorts={n:summarize(D/n/'raw.json') for n in ['producer','independent_replay']};assert json.loads((D/'producer/raw.json').read_text())['environment']==json.loads((D/'independent_replay/raw.json').read_text())['environment']
 keep=all(c['guard'] and (not c['primary'] or c['improved']) for rs in cohorts.values() for c in rs)
 decision=dict(keep=keep,cohorts=cohorts,reason='All frozen gates passed' if keep else 'Frozen performance gate failed; retain baseline')
 (D/'independent_decision.json').write_text(json.dumps(decision,indent=2)+'\n');(D/'independent_after_snapshot.json').write_text(json.dumps(proof,indent=2)+'\n')
 evidence=[ref(p) for p in sorted(D.glob('independent*')) if p.is_file() and p.name not in ['independent_validation.log','validation.json']]+[ref(D/'independent_replay/raw.json'),ref(D.parent/'comm20-20261009/independent_properties.py')]
 reasons=dict(implementation='Exact e6b3dc baseline, AST unchanged legacy methods; publish validation and SQL extracted in exact order; opt-in per-event validation and one call-local transaction; no ACK/route/DDL optimization.',reference_boundary='61 independent public oracle checks plus two old regressions each source; independent list/Unicode/ledger/cap/budget/duplicate/live-route/ref/thread rollback checks; independent reader visibility under WAL and DELETE; seven frozen API tests; strong original-publish atomic reference valid/failing fixture reviewed.',data_integrity='Frozen manifest and every native artifact hash unchanged before/after; all three shapes, four paths,34 ordered complete attempts,31 retained samples/ACKs and exact output/state equality; no replay retries.',numerical_sanity='All attempt timings positive finite ms; every31sample median/range/gain and absolute delta recomputed; all frozen guards checked in both cohorts; exact SQLite states and sequence hashes equal.',measurement_validity='Full public methods include validation, connection, commit; alternation and warmups fixed, diagnostic trace outside primary shows8vs1 BEGIN/COMMIT with identical logical changes/results; shared CPU synthetic boundary explicit.',reproducibility='Exactly one frozen independent31pair replay across all3shapes4paths plus independently executed functional/reference/visibility oracles; unchanged sources/config/thresholds; CLI eighth test deferred until actual integration.')
 review=dict(schema_version='experiment-validation/v1',**proof,verifier=dict(actor='batch-independent-verifier',independent=True,source='actual trusted host fresh child /root/batch_verify; parent authenticates dispatched task and returned completion',run_id='comm-batch-independent-20261010',method='Independent native snapshot, AST/read audit, exact single replay, separate public/list/atomic visibility oracle and recomputed metrics'),limitations=['Synthetic SQLite public API on shared CPU; no affinity or LLM/network/token benefit measured.','Ordinary caller-owned stable JSON values; no concurrent mutation guarantee.','Strong atomic reference single-caller only; never production or thread-safe claim.','Finite cases and hashes do not prove universal correctness or authenticate host reviewer; parent authenticates actual child.','CLI eighth test and full repository integration excluded until adoption.','Initial independent helper failure preserved in attempt1 log: it changed constructor caller plan rather than frozen Mailbox.plan, so current-route test wrongly expected rejection; helper-only correction targets actual live plan; no source, benchmark, gate or replay changed.'],checks={k:dict(verdict='pass',reason=v,evidence=evidence) for k,v in reasons.items()},decision=decision)
 assert _snapshot(ROOT,contract)[2]==proof;_review(ROOT,manifest,plan,proof,review);(D/'validation.json').write_text(json.dumps(review,indent=2)+'\n')
 print(json.dumps(dict(status='usable-with-scope',keep=keep,validation_sha256=digest(D/'validation.json'),failed=[dict(cohort=n,**c) for n,rs in cohorts.items() for c in rs if not c['guard'] or c['primary'] and not c['improved']])))
if __name__=='__main__':
 if sys.argv[1]=='properties':properties()
 elif sys.argv[1]=='validate':validate()
