"""Run only after diagnostic acceptance and production DDL implementation."""
import importlib.util,contextlib,io,json,random,statistics,time,tempfile,shutil,sqlite3
from pathlib import Path
import measure
spec=importlib.util.spec_from_file_location('agent_runtime._history_index_baseline',measure.OUT/'baseline.py')
baseline=importlib.util.module_from_spec(spec);spec.loader.exec_module(baseline)
from agent_runtime import project_memory as candidate
assert baseline.MemoryLedger is not candidate.MemoryLedger
assert baseline.main.__globals__['MemoryLedger'] is baseline.MemoryLedger
rng=random.Random(81602);data={'source_sha256':__import__('hashlib').sha256(Path('agent_runtime/project_memory.py').read_bytes()).hexdigest(),'script_sha256':__import__('hashlib').sha256(Path(__file__).read_bytes()).hexdigest(),'fixtures':{},'pending_independent_review':True}
with tempfile.TemporaryDirectory(prefix='agent-history-cli-') as td:
 td=Path(td);cfg=next(x for x in measure.PLAN['fixtures'] if x['id']=='add50000')
 src=measure.seed(td/'seed',cfg,baseline.MemoryLedger);old=measure.snap(src);input_hash=measure.sha(old)
 for scenario in ('steady_cli_add','first_upgrade_cli_add','constructor_upgrade','constructor_repeat'):
  samples=[]
  for pair in range(-3,21):
   order=[0,1];rng.shuffle(order);answers={};states={}
   for arm in order:
    root=td/f'{scenario}{pair}a{arm}';p,_=measure.clone(src,root)
    if arm and scenario in ('steady_cli_add','constructor_repeat'):candidate.MemoryLedger(root,create=True)
    assert measure.sha(measure.snap(p))==input_hash
    before=p.stat().st_size;mod=(baseline,candidate)[arm];buf=io.StringIO()
    with contextlib.redirect_stdout(buf):
     t=time.perf_counter_ns()
     if 'cli' in scenario:
      rc=mod.main(['--root',str(root),'add','--id','new-entry','--kind','claim','--content','new','--source','synthetic:experiment','--evidence','verified'])
     else:mod.MemoryLedger(root,create=True);rc=0
     elapsed=time.perf_counter_ns()-t
    assert rc==0
    state,clocks=measure.normalized(measure.snap(p),old)
    answer=measure.result_norm(json.loads(buf.getvalue()),'add') if 'cli' in scenario else None
    if 'cli' not in scenario:assert state==old
    if arm:
     with sqlite3.connect(p) as db:
      info=db.execute('PRAGMA index_xinfo(memory_events_entry)').fetchall()
      assert info[0][2]=='entry_id' and info[1][1]==-1
    answers[arm]=answer;states[arm]=state
    if pair>=0:samples.append({'pair':pair,'arm':arm,'order':order,'wall_ns':elapsed,'bytes_before':before,'bytes_after':p.stat().st_size,'new_timestamps':clocks,'output_sha256':measure.sha(answer),'state_sha256':measure.sha(state)})
    shutil.rmtree(root)
   assert answers[0]==answers[1] and states[0]==states[1]
  med={str(a):statistics.median(s['wall_ns'] for s in samples if s['arm']==a) for a in (0,1)}
  data['fixtures'][scenario]={'input_hash':input_hash,'samples':samples,'median_ns':med,'reduction':1-med['1']/med['0']}
  (measure.OUT/'integration.json').write_text(json.dumps(data,indent=2)+'\n');print(scenario,med,data['fixtures'][scenario]['reduction'],flush=True)
data['steady_gate']=data['fixtures']['steady_cli_add']['reduction']>=-.15
(measure.OUT/'integration.json').write_text(json.dumps(data,indent=2)+'\n')
assert data['steady_gate']
