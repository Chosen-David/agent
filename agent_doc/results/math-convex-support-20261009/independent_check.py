import json,hashlib,itertools,subprocess,runpy,time,resource
from fractions import Fraction as F
from pathlib import Path
from agent_runtime.result_validation import inspect_result
root=Path.cwd(); d=root/'agent_doc/results/math-convex-support-20261009'
def save(name,x):(d/name).write_text(json.dumps(x,indent=2)+'\n')
contract=json.loads((d/'controller_contract.json').read_text()); before=inspect_result(root,contract); assert before['proof'] and before['proof']['manifest_sha256']=='2b7f1b9fc8003708098beeae956ac71eeabd8bf59ab160f4db9cb7ac1e045c3c',before
proof=before['proof']; cases=json.loads((d/'cases.json').read_text()); raw=json.loads((d/'raw.json').read_text())
def det(a):
 if len(a)==1:return a[0][0]
 return sum((-1)**j*a[0][j]*det([r[:j]+r[j+1:] for r in a[1:]]) for j in range(len(a)))
def rank(a):
 for k in range(min(len(a),len(a[0])),0,-1):
  if any(det([[a[i][j] for j in cc] for i in rr]) for rr in itertools.combinations(range(len(a)),k) for cc in itertools.combinations(range(len(a[0])),k)):return k
 return 0
def out(v,w):return [sum(x*y[j] for x,y in zip(w,v)) for j in range(len(v[0]))]
obs=[]
assert [c['id'] for c in cases]==[c['id'] for c in raw['cases']] and len(cases)==8
for c,r in zip(cases,raw['cases']):
 v=[[F(x) for x in row] for row in c['values']];w=list(map(F,c['weights'])); target=out(v,w)
 if c.get('expect')=='reject':assert any(x<0 for x in w) and r['rejected'];obs.append({'id':c['id'],'refused_nonconvex':True,'output':list(map(str,target))});continue
 m=[[p[j] for p in v] for j in range(len(v[0]))]+[[F(1)]*len(v)];rk=rank(m)
 assert r['affine_dimension']==rk-1 and list(map(F,r['output']))==target
 prev=w
 for step in r['trace']:
  w2=list(map(F,step['weights'])); assert len(w2)==len(w) and all(x>=0 for x in w2) and sum(w2)==1 and out(v,w2)==target
  assert sum(x>0 for x in w2)<sum(x>0 for x in prev) and all(not(x==0 and y>0) for x,y in zip(prev,w2)) and F(step['theta'])>0;prev=w2
 final=list(map(F,r['weights']));assert final==prev and sum(x>0 for x in final)==r['support']<=rk
 obs.append({'id':c['id'],'augmented_rank':rk,'output':list(map(str,target)),'support':r['support'],'trace_verified':len(r['trace'])})
# Independent exact tightness: solve triangle equations directly. Each nonzero target coordinate requires its corresponding vertex; remaining mass is 1/3.
assert raw['cases'][5]['weights']==['1/3']*3 and rank([[F(0),F(1),F(0)],[F(0),F(0),F(1)],[F(1)]*3])==3
z=F(1,3)+3*F(1,6); rw=3*F(5,18); wrong=3*F(1,6)/(F(1,2)+F(1,6));assert z==rw==F(5,6) and wrong==F(3,4) and z-wrong==F(1,12)
assert raw['counterexample']==dict(full=str(z),reweighted=str(rw),original_subset=str(wrong),error=str(z-wrong))
# Projected versus raw output independently computed.
assert out([[F(0),F(0)],[F(0),F(2)]],[F(1,2)]*2)==[0,1] and out([[F(0)],[F(0)]],[F(1,2)]*2)==[0]
save('independent_exact.json',{'cases':obs,'counterexample':raw['counterexample'],'bindings_count':len(proof['artifact_hashes']),'reference':'determinant minors, direct vector sums, direct simplex equations; no producer reducer imported'})
replay=d/'independent_replay';replay.mkdir(exist_ok=True)
for name in ['cases.json','retrieval_protocol.json']:(replay/name).write_bytes((d/name).read_bytes())
for name in ['validate.py','retrieve.py']:
 env=runpy.run_path(str(d/name)); env['main'].__globals__['BASE']=replay;env['main']()
r2=json.loads((replay/'raw.json').read_text());r2.pop('seconds');r1=dict(raw);r1.pop('seconds');assert r1==r2
ret1=json.loads((d/'retrieval.json').read_text());ret2=json.loads((replay/'retrieval.json').read_text())
for r in [ret1,ret2]:
 for k in ['load_seconds','index_build_seconds']:r.pop(k)
 for x in r['records']:x.pop('seconds')
assert ret1==ret2 and len(ret2['records'])==6 and all(x['hit'] for x in ret2['records'])
save('independent_replay_comparison.json',{'exact_semantic_match':True,'retrieval_semantic_match':True,'hits':6,'context_chars':ret2['context']['budget'],'timing_fields_ignored':'diagnostic only'})
mods=['tests.test_knowledge','tests.test_knowledge_index','tests.test_knowledge_math','tests.test_knowledge_handoff','tests.test_knowledge_reuse']
commands=[['python','-m','unittest',*mods,'-v'],['python','scripts/sync_plugin_references.py','--check']];results=[]
for i,cmd in enumerate(commands):
 t=time.monotonic();p=subprocess.run(cmd,capture_output=True,text=True,timeout=80);(d/f'independent_command_{i}.log').write_text(p.stdout+p.stderr);results.append({'command':cmd,'exit_code':p.returncode,'seconds':time.monotonic()-t});assert p.returncode==0
save('independent_commands.json',results)
after=inspect_result(root,contract);assert before==after;save('independent_bindings.json',{'proof':proof,'unchanged_before_after':True,'cpu_seconds':resource.getrusage(resource.RUSAGE_SELF).ru_utime})
print('independent data/code replay and regressions passed',len(proof['artifact_hashes']))
