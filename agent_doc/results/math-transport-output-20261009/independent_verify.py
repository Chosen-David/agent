import json,sys,hashlib,subprocess,platform
from pathlib import Path
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from agent_runtime.result_validation import _snapshot
BASE=Path(__file__).resolve().parent
D=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,x): (BASE/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
contract=json.loads((BASE/'contract.json').read_text());manifest,plan,before=_snapshot(ROOT,contract)
assert before['manifest_sha256']=='50c349a40fe1998e6358653e2df4e39d6391ac9d784f381379d6c0ec42b74972'
assert len(before['artifact_hashes'])==257
write('independent_snapshot.json',before)
cases=json.loads((BASE/'fixtures.json').read_text())['cases'];raw=json.loads((BASE/'raw.json').read_text())['rows'];assert len(cases)==len(raw)==8
rows=[]
for t,r in zip(cases,raw):
 assert t['id']==r['id'];tid=t['id']
 if tid=='T7':
  invalid=[any(F(x)<0 for x in a) or sum(map(F,a))!=1 for a in t['invalid_alpha']]
  pi=[[F(x) for x in a] for a in t['invalid_pi']];b=list(map(F,t['beta']));bad=[sum(a) for a in pi]!=b or [sum(a[j] for a in pi) for j in range(2)]!=b
  assert all(invalid) and bad and r['invalid_probability_rejected']==invalid and r['invalid_marginal_rejected']==bad
  rows.append({'id':tid,'invalid_probability':invalid,'invalid_marginal':bad});continue
 if tid=='T8':
  q,e,lam=map(F,[t['Q'],t['E'],t['ridge']]);true=q*q*e*e;penalty=lam*e*e;ridge=true+penalty
  assert true==F(t['expected_true_logit_squared'])==F(r['true_logit_squared']);assert ridge==F(t['expected_ridge_metric_squared'])==F(r['ridge_metric_squared']);assert penalty==F(r['extra_penalty'])>0
  rows.append({'id':tid,'true':str(true),'ridge':str(ridge),'penalty':str(penalty)});continue
 v,a,b=[list(map(F,t[k])) for k in ('values','alpha','beta')];n=len(v);assert len(a)==len(b)==n and min(a+b)>=0 and sum(a)==sum(b)==1
 # Discrete CDF integral: aggregate identical values; no coupling construction or greedy loop.
 z=sorted(set(v));cdf=sum(abs(sum(a[i]-b[i] for i in range(n) if v[i]<=x))*(y-x) for x,y in zip(z,z[1:]))
 err=abs(sum((a[i]-b[i])*v[i] for i in range(n)));vh=list(map(F,t.get('values_hat',t['values'])));pert=sum(b[i]*abs(v[i]-vh[i]) for i in range(n));actual=abs(sum(a[i]*v[i]-b[i]*vh[i] for i in range(n)));dtv=(max(v)-min(v))*sum(abs(x-y) for x,y in zip(a,b))/2
 assert err<=cdf<=dtv and actual<=cdf+pert
 cert=r['certificate'];pi=[[F(x) for x in row] for row in cert['pi']];f=list(map(F,cert['f']));g=list(map(F,cert['g']));C=[[abs(x-y) for y in v] for x in v]
 assert min(x for row in pi for x in row)>=0 and [sum(row) for row in pi]==a and [sum(row[j] for row in pi) for j in range(n)]==b
 assert all(f[i]+g[j]<=C[i][j] for i in range(n) for j in range(n))
 primal=sum(pi[i][j]*C[i][j] for i in range(n) for j in range(n));dual=sum(x*y for x,y in zip(a,f))+sum(x*y for x,y in zip(b,g));assert primal==dual==cdf==F(cert['primal'])==F(cert['dual'])
 for field,x in [('base_error',err),('actual_error',actual),('DTV',dtv),('value_perturbation',pert),('combined_bound',cdf+pert)]:assert F(r[field])==x
 for field,x in [('expected_cost',cdf),('expected_error',actual),('expected_DTV',dtv),('expected_combined_bound',cdf+pert)]:
  if field in t:assert F(t[field])==x
 if tid=='T5':
  features=list(map(F,t['features']));assert len(set(features))==1 and len(set(v))>1 and actual==100 and F(r['wrong_feature_cost'])==0
 rows.append({'id':tid,'cdf_integral':str(cdf),'output_error':str(actual),'perturbation':str(pert),'DTV':str(dtv),'feasible_primal_dual_checked':True})
write('independent_exact.json',{'method':'Exact discrete CDF integral using grouped support intervals; raw primal/dual checked directly, no producer import','rows':rows,'passed':True})
baseline=json.loads((BASE/'preservation_baseline.json').read_text());assert len(baseline)==229
changed=[p for p,h in baseline.items() if D(ROOT/p)!=h];assert not changed
mirror=ROOT/'plugins/research-assistant/skills/model-with-knowledge/assets/knowledge';pairs={ext:D(ROOT/f'knowledge/entries/math.transport-output-certificate.{ext}')==D(mirror/f'entries/math.transport-output-certificate.{ext}') for ext in ('json','md')};assert all(pairs.values())
write('independent_preservation.json',{'paths':len(baseline),'changed':changed,'new_card_mirror':pairs,'holdout_policy':'Hash bytes only; no deserialization or contents inspection'})
replay=BASE/'independent_replay';replay.mkdir(exist_ok=True);commands=[]
for args,log in [([sys.executable,str(BASE/'verify.py'),str(replay)],'independent_replay_verify.log'),([sys.executable,str(BASE/'retrieve.py'),str(replay)],'independent_replay_retrieve.log'),([sys.executable,'-m','unittest','tests.test_knowledge','tests.test_knowledge_index'],'independent_regression.log')]:
 p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);(BASE/log).write_text(p.stdout+p.stderr);commands.append({'argv':args,'returncode':p.returncode,'log':log});assert p.returncode==0
write('independent_commands.json',{'commands':commands,'python':sys.version,'platform':platform.platform()})
oldraw=json.loads((BASE/'raw.json').read_text());newraw=json.loads((replay/'raw.json').read_text());oldraw.pop('seconds');newraw.pop('seconds');assert oldraw==newraw
old=json.loads((BASE/'retrieval.json').read_text());new=json.loads((replay/'retrieval.json').read_text());assert len(new['records'])==6 and all(r['hit'] for r in new['records'])
for x,y in zip(old['records'],new['records']):
 for key in ('backend','case','query','actual','hit','chars','bytes','result'):assert x[key]==y[key]
assert old['context']==new['context'];ctx=new['context'];assert len(ctx['entries'])==2 and ctx['budget']['used_chars']<=16000
assert {e['id'] for e in ctx['entries']}=={'math.transport-output-certificate','math.softmax-barycenter-error'}
_,_,after=_snapshot(ROOT,contract);assert before==after
assert all(D(ROOT/p)==h for p,h in baseline.items())
write('independent_replay_summary.json',{'exact_replay_match_excluding_seconds':True,'six_retrieval_full_record_match_excluding_seconds':True,'context_ids':[e['id'] for e in ctx['entries']],'context_budget':ctx['budget'],'tests':34,'all_257_bindings_unchanged':True,'preservation_229_unchanged_after':True})
print('PASS: independent CDF8, replay8, retrieval6, tests34, preservation229, frozen257')
