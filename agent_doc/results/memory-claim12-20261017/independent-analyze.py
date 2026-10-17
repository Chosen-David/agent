from pathlib import Path
import hashlib,json,statistics,math,importlib.util,subprocess,time
R=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('check_mod',R/'check.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
allrows={}
for actor in ('producer','independent'):
 d=json.loads((R/(actor+'.json')).read_text());rows={}
 assert d['correctness_cases']==659
 for k,r in c.fixtures().items():
  b=d['benchmark'][k];ss=b['samples_ms'];assert len(ss)==21
  assert hashlib.sha256(json.dumps(r,sort_keys=True,separators=(',',':')).encode()).hexdigest()==b['input_sha256']
  assert all(set(x)=={'baseline','candidate'} and all(math.isfinite(v) and v>0 for v in x.values()) for x in ss)
  med={s:statistics.median(x[s] for x in ss) for s in ('baseline','candidate')}
  assert med==b['median_ms'];red=100*(1-med['candidate']/med['baseline']);assert abs(red-b['reduction_percent'])<1e-10
  assert red >= (25 if k=='chain512' else -15)
  rows[k]={'median_ms':med,'reduction_percent':red,'range_ms':{s:[min(x[s] for x in ss),max(x[s] for x in ss)] for s in med},'python_peak_bytes':b['python_peak_bytes_single_call']}
 allrows[actor]=rows
base=subprocess.run(['git','show','4e4199d789812c6964329c02231733472d65a700:agent_runtime/handoff_basis.py'],check=True,capture_output=True).stdout
assert base==(R/'baseline.py').read_bytes()
# All diagnostics retain21 pairs; errors are caught so full rejection cost is timed.
diag={}
for kind in ('unknown','unsupported','cycle'):
 r=c.chain(100)
 if kind=='unknown':r['evidence_claims'][60]['depends_on'].append('missing')
 elif kind=='unsupported':r['evidence_claims'][60]['status']='candidate'
 else:r['evidence_claims'][98]['depends_on']=['c99']
 def reject(fn):
  def run(record):
   try:fn(record)
   except ValueError:return
   raise AssertionError('invalid graph accepted')
  return run
 a=reject(c.baseline.claim_graph);b=reject(c.claim_graph)
 for _ in range(3):c.measure(a,r,1);c.measure(b,r,1)
 samples=[]
 for i in range(21):
  pair={}
  for label,fn in ([('baseline',a),('candidate',b)] if i%2==0 else [('candidate',b),('baseline',a)]):pair[label]=c.measure(fn,r,1)
  samples.append(pair)
 med={s:statistics.median(x[s] for x in samples) for s in ('baseline','candidate')}
 diag[kind]={'samples_ms':samples,'median_ms':med,'reduction_percent':100*(1-med['candidate']/med['baseline'])}
allrows['invalid_fallback_diagnostic']=diag
allrows['hashes']={str(p.relative_to(R.parent.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [R/'plan-v3.json',R/'validation-plan.json',R/'producer.json',R/'independent.json',R/'independent-supplement.py',R/'independent-supplement.json',R/'check.py',R/'baseline.py',R.parent.parent/'agent_runtime/handoff_basis.py',R.parent.parent/'tests/test_claim_graph_residual.py']}
(R/'independent-analysis.json').write_text(json.dumps(allrows,indent=2)+'\n')
print(json.dumps({a:{k:round(x['reduction_percent'],3) for k,x in v.items()} for a,v in allrows.items() if a in ('producer','independent','invalid_fallback_diagnostic')},indent=2))
