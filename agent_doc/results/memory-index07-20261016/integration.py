"""Full real CLI add (parser/init/commit/JSON); independent baseline globals."""
import importlib.util,io,contextlib,json,random,statistics,time,tempfile,shutil
from pathlib import Path
import probe
spec=importlib.util.spec_from_file_location('agent_runtime._index_baseline',probe.OUT/'baseline.py')
baseline=importlib.util.module_from_spec(spec);spec.loader.exec_module(baseline)
from agent_runtime import project_memory as candidate
assert baseline.MemoryLedger is not candidate.MemoryLedger
rng=random.Random(71407);results={}
with tempfile.TemporaryDirectory(prefix='agent-index-cli-') as tmp:
 tmp=Path(tmp);seedroot=tmp/'seed';l=baseline.MemoryLedger(seedroot,create=True)
 with l._connect(write=True) as db:
  db.executemany('INSERT INTO entries VALUES(?,?,?,?,?,?,?,?)',[(f'n{i:05}','claim','x'*128,'synthetic:seed','[]','verified','active','2000-01-01T00:00:00.000Z') for i in range(5000)])
  db.executemany('INSERT INTO dependencies VALUES(?,?)',[(f'n{i:05}',f'n{i-1:05}') for i in range(1,5000) if i%16])
  db.executemany('INSERT INTO events(entry_id,action,reason,source,created_at) VALUES(?,?,?,?,?)',[(f'n{i:05}','created','verified','synthetic:seed','2000-01-01T00:00:00.000Z') for i in range(5000)])
 old=probe.snap(l.path);input_hash=probe.digest(old)
 for scenario in ('steady_cli_add','first_upgrade_cli_add','constructor_upgrade','constructor_repeat'):
  samples=[]
  for pair in range(-3,21):
   order=[0,1];rng.shuffle(order);outputs={};states={}
   for arm in order:
    root=tmp/f'{scenario}{pair}{arm}';p,_=probe.copy_arm(l.path,root,False)
    mod=(baseline,candidate)[arm]
    if scenario in ('steady_cli_add','constructor_repeat') and arm:
     candidate.MemoryLedger(root,create=True)
    assert probe.digest(probe.snap(p))==input_hash
    before_bytes=p.stat().st_size;buf=io.StringIO()
    with contextlib.redirect_stdout(buf):
     start=time.perf_counter_ns()
     if 'cli_add' in scenario:
      status=mod.main(['--root',str(root),'add','--id','new-entry','--kind','claim','--content','new','--source','synthetic:experiment','--dep','n00000','--evidence','verified'])
     else:mod.MemoryLedger(root,create=True);status=0
     elapsed=time.perf_counter_ns()-start
    assert status==0
    state,ts=probe.normalize(probe.snap(p),old)
    answer=probe.norm_result(json.loads(buf.getvalue()),'add') if 'cli_add' in scenario else None
    outputs[arm]=answer;states[arm]=state
    if 'cli_add' not in scenario:assert state==old
    if arm:
     import sqlite3
     with sqlite3.connect(p) as db:
      assert [r[2] for r in db.execute('PRAGMA index_info(memory_dependencies_parent)')]==['parent','child']
    if pair>=0:samples.append({'pair':pair,'arm':arm,'order':order,'wall_ns':elapsed,'bytes_before':before_bytes,'bytes_after':p.stat().st_size,'timestamps':ts,'output_hash':probe.digest(answer),'state_hash':probe.digest(state)})
    shutil.rmtree(root)
   assert outputs[0]==outputs[1] and states[0]==states[1]
  med={str(a):statistics.median(s['wall_ns'] for s in samples if s['arm']==a) for a in (0,1)}
  results[scenario]={'input_hash':input_hash,'samples':samples,'median_ns':med,'reduction':1-med['1']/med['0']}
  print(scenario,med,results[scenario]['reduction'],flush=True)
results['steady_gate']=results['steady_cli_add']['reduction']>=-.15
(probe.OUT/'integration.json').write_text(json.dumps(results,indent=2)+'\n')
assert results['steady_gate']
