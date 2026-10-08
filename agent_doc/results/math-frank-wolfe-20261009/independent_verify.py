from pathlib import Path
from fractions import Fraction as Q
import json,hashlib,subprocess,runpy,io,contextlib
from unittest.mock import patch
from agent_runtime.result_validation import _snapshot
R=Path.cwd(); B=R/'agent_doc/results/math-frank-wolfe-20261009'
def save(n,x): (B/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
c=json.loads((B/'contract.json').read_text());m,pl,pf=_snapshot(R,c)
assert pf['manifest_sha256']=='a11826341ea0953750024f277e77c28eaf52de05e4ecee17a0905c49a0af52a8'
save('independent_snapshot.json',pf)
# Read every actual bound file; coverage includes recursively nested corpus and mirror.
read=[]
for path,digest in pf['artifact_hashes'].items():
 p=R/path;data=p.read_bytes();assert hashlib.sha256(data).hexdigest()==digest
 read.append({'path':path,'sha256':digest,'bytes':len(data)})
for root in ['knowledge','plugins/research-assistant/skills/model-with-knowledge/assets/knowledge']:
 actual={str(p.relative_to(R)) for p in (R/root).rglob('*') if p.is_file()}
 assert actual-set(pf['artifact_hashes']) <= {root+'/learning_state.json'},actual-set(pf['artifact_hashes'])
# Independent optimum coordinates: interval clamp, orthogonal segment foot,
# triangle symmetry boundary x+y=1, fixed duplicate/singleton, triangle interior.
ys={'F1':[Q(5,6)],'F2':[Q(1)],'F3':[Q(1),Q(0)],'F4':[Q(1,2),Q(1,2)],'F5':[Q(1)],'F6':[Q(3),Q(4)],'F7':[Q(1,4),Q(1,4)],'F8':[Q(4)]}
def inner(a,b):return sum((x*y for x,y in zip(a,b)),Q(0))
def diff(a,b):return [x-y for x,y in zip(a,b)]
def square(a):return inner(a,a)
def string(a):
 if isinstance(a,Q):return str(a)
 if isinstance(a,list):return [string(x) for x in a]
 if isinstance(a,dict):return {k:string(v) for k,v in a.items()}
 return a
cfg=json.loads((B/'cases.json').read_text());raw=json.loads((B/'raw.json').read_text())
assert cfg['steps']==12 and cfg['policies']==['schedule','line-search']
assert [x['id'] for x in cfg['cases']]==[x['id'] for x in raw['records']]==['F'+str(i) for i in range(1,11)]
checked=[];count=0
for case,row in zip(cfg['cases'],raw['records']):
 kid=case['id'];points=[[Q(x) for x in v] for v in case['v']];target=list(map(Q,case['z']))
 if kid=='F9':assert not points and row=={'id':kid,'rejected':'empty'};checked.append({'id':kid,'empty_refusal':True});continue
 if kid=='F10':assert min(case['beta'])<0 and row=={'id':kid,'rejected':'signed'};checked.append({'id':kid,'signed_refusal':True});continue
 optimum=ys[kid];res=diff(target,optimum);fstar=square(res)/2
 # Optimality proved by direct full vertex inequalities, independent of claimed opt.
 assert all(inner(res,diff(v,optimum))<=0 for v in points)
 assert Q(case['opt'])==Q(row['opt'])==fstar
 diam=max(square(diff(a,b)) for a in points for b in points);assert Q(row['D2'])==diam
 for policy in cfg['policies']:
  trajectory=row['policies'][policy];assert len(trajectory)==13
  gammas=[];chosen=[];previous_f=None
  for t,state in enumerate(trajectory):
   # Closed-form expansion of all past updates, not producer beta/mix helpers.
   weights=[Q(0)]*len(points);prod=Q(1)
   for k in range(t-1,-1,-1):
    weights[chosen[k]]+=gammas[k]*prod;prod*=1-gammas[k]
   weights[0]+=prod
   y=[sum((w*v[a] for w,v in zip(weights,points)),Q(0)) for a in range(len(target))]
   r=diff(target,y);value=square(r)/2;errors=value-fstar
   scores=[inner(r,v) for v in points];idx=min(range(len(points)),key=lambda j:(-scores[j],j));direction=diff(points[idx],y)
   gap=max(scores)-inner(r,y)
   expected={'step':t,'y':string(y),'beta':string(weights),'f':str(value),'h':str(errors),'gap':str(gap),'oracle':idx}
   assert {k:v for k,v in state.items() if k!='gamma'}==expected,(kid,policy,t)
   assert sum(weights)==1 and all(w>=0 for w in weights) and sum(w>0 for w in weights)<=t+1
   assert 0<=errors<=gap
   if t:assert errors<=2*diam/Q(t+2)
   if policy=='line-search' and previous_f is not None:assert value<=previous_f
   previous_f=value
   if t==12:continue
   step=Q(2,t+2);length=square(direction)
   # Independent minimization of exact 1D quadratic with endpoint clipping.
   if policy=='schedule':gamma=step
   elif length==0:gamma=Q(0)
   else:
    candidates=[Q(0),Q(1),min(Q(1),max(Q(0),gap/length))]
    gamma=min(candidates,key=lambda a:value-a*gap+a*a*length/2)
   assert Q(state['gamma'])==gamma
   next_y=[a+gamma*d for a,d in zip(y,direction)];next_value=square(diff(target,next_y))/2
   assert next_value==value-gamma*gap+gamma*gamma*length/2
   assert next_value-fstar <=(1-step)*errors+step*step*diam/2
   gammas.append(gamma);chosen.append(idx);count+=1
 if kid=='F1':
  assert Q(row['policies']['schedule'][0]['f'])==Q(25,72)
  assert Q(row['policies']['schedule'][1]['f'])==Q(169,72)
  assert Q(row['policies']['line-search'][1]['f'])==0
 if kid=='F8':
  r=[Q(2)];partial=max(inner(r,v) for v in points[:2])-Q(4);full=max(inner(r,v) for v in points)-Q(4)
  assert partial==0 and full==4 and square(r)/2==2
  assert row['sampled_false_stop']=={'y':['2'],'gap_partial':'0','gap_full':'4','eta':'4','h':'2'}
 checked.append({'id':kid,'analytic_optimum':string(optimum),'fstar':str(fstar),'full_vertex_optimality_certificate':True,'policies':2,'steps':12})
assert count==raw['transition_count']==192 and raw['case_count']==10
save('independent_exact.json',{'cases':checked,'transitions':count,'method':'Independent analytic output optima certified by all vertex inequalities and closed-form accumulated weight reconstruction; no producer helpers imported','F1_schedule_increase':['25/72','169/72'],'F8_partial_gap_false_stop':{'partial':0,'full':4,'suboptimality':2}})
# Frozen-code replay separately from reference; redirect every producer result write.
original=Path.write_text
allowed={'raw.json':'independent_replay_raw.json','retrieval.json':'independent_replay_retrieval.json','retrieval_knowledge_use.json':'independent_replay_knowledge_use.json'}
def redirect(p,data,*a,**kw):
 assert p.parent==B and p.name in allowed,str(p)
 return original(B/allowed[p.name],data,*a,**kw)
logs=[]
for script in ['validate.py','retrieve.py']:
 code=runpy.run_path(str(B/script));output=io.StringIO()
 with patch.object(Path,'write_text',redirect),contextlib.redirect_stdout(output):code['main']()
 logs.append({'script':script,'stdout':output.getvalue()})
replay=json.loads((B/'independent_replay_raw.json').read_text());assert {k:v for k,v in raw.items() if k!='seconds_diagnostic'}=={k:v for k,v in replay.items() if k!='seconds_diagnostic'}
a=json.loads((B/'retrieval.json').read_text());b=json.loads((B/'independent_replay_retrieval.json').read_text())
assert len(a['records'])==len(b['records'])==6
for x,y in zip(a['records'],b['records']):assert {k:v for k,v in x.items() if k!='seconds'}=={k:v for k,v in y.items() if k!='seconds'}
for key in ['scope','snapshot','protocol_sha256','context','token_cost','holdouts_metadata_sha256']:assert a[key]==b[key]
assert a['context']['status']=='partial' and a['context']['budget']['used_chars']==11417
assert {e['id'] for e in a['context']['entries']}=={'math.frank-wolfe-output-solver','math.convex-projection-certificate','math.dual-certificates'}
assert all(s['selection_reason']=='related' for s in a['context']['skipped'])
assert json.loads((B/'retrieval_knowledge_use.json').read_text())==json.loads((B/'independent_replay_knowledge_use.json').read_text())
# Preserved failed first run differs only in assertion acceptance.
old=(B/'failed_attempt1/retrieve.py').read_text();new=(B/'retrieve.py').read_text()
assert old.replace("context['status']=='ready'","context['status'] in ('ready','partial')")==new
failed=json.loads((B/'failed_attempt1/retrieval.json').read_text())
for key in ['snapshot','protocol_sha256','context','token_cost','holdouts_metadata_sha256']:assert failed[key]==a[key]
save('independent_replay_summary.json',{'scripts':logs,'identical_except_diagnostic_seconds':True,'structural_checks':6,'all_hits':all(x['hit'] for x in a['records']),'context':'partial: complete three-card strong closure; two optional related skips','failed_attempt1_preserved_only_status_assertion_changed':True})
commands=[['python','-m','unittest','tests.test_knowledge','tests.test_knowledge_index','tests.test_knowledge_math','tests.test_knowledge_handoff','tests.test_knowledge_reuse','-v'],['python','scripts/sync_plugin_references.py','--check']]
results=[]
for i,cmd in enumerate(commands):
 p=subprocess.run(cmd,cwd=R,capture_output=True,text=True,timeout=90)
 (B/f'independent_command_{i}.log').write_text(p.stdout+p.stderr)
 results.append({'command':cmd,'exit_code':p.returncode});assert p.returncode==0
assert 'Ran 53 tests' in (B/'independent_command_0.log').read_text()
save('independent_commands.json',results)
sources=json.loads((B/'sources.json').read_text());assert sha(Path('/tmp/jaggi.pdf'))==sources[0]['pdf_sha256'];assert sha(Path('/tmp/alcalde.pdf'))==sources[1]['pdf_sha256']
assert _snapshot(R,c)[2]==pf,'bound files changed'
save('independent_integrity.json',{'manifest_sha256':pf['manifest_sha256'],'artifact_count':len(pf['artifact_hashes']),'all_bound_files_read_and_hashed':read,'full_recursive_corpus_and_mirror_coverage':True,'before_after_identical':True,'source_pdf_sha256_checked':[sources[0]['pdf_sha256'],sources[1]['pdf_sha256']]})
print(json.dumps({'independent_exact_transitions':count,'case_count':10,'retrieval_checks':6,'regressions':53,'all_bound_hashes':len(pf['artifact_hashes']),'before_after_identical':True}))
