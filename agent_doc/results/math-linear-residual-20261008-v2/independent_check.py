from fractions import Fraction as F
from pathlib import Path
import json,hashlib,sys,subprocess,time
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2];sys.path.insert(0,str(ROOT))
def decode(x):
 if isinstance(x,str):
  try:return F(x)
  except ValueError:return x
 if isinstance(x,list):return [decode(y) for y in x]
 if isinstance(x,dict):return {k:decode(v) for k,v in x.items()}
 return x
def mult(A,B):
 assert A and B and all(len(r)==len(A[0]) for r in A) and all(len(r)==len(B[0]) for r in B) and len(A[0])==len(B)
 return [[sum(A[i][k]*B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]
def trans(A):return [[A[i][j] for i in range(len(A))] for j in range(len(A[0]))]
def minus(A,B):return [[A[i][j]-B[i][j] for j in range(len(A[0]))] for i in range(len(A))]
def moment(samples,x,y):return [[sum(z['p']*z[x][i]*z[y][j] for z in samples) for j in range(len(samples[0][y]))] for i in range(len(samples[0][x]))]
def solve_row(C,r):
 assert C==trans(C) and C[0][0]>0
 if len(C)==1:return [r[0]/C[0][0]]
 assert len(C)==2;d=C[0][0]*C[1][1]-C[1][0]*C[0][1];assert d>0
 return [(r[0]*C[1][1]-r[1]*C[1][0])/d,(r[1]*C[0][0]-r[0]*C[0][1])/d]
def psd(C):
 assert C==trans(C) and all(C[i][i]>=0 for i in range(len(C)))
 if len(C)==2:assert C[0][0]*C[1][1]>=C[1][0]*C[0][1]
def residual(T,a,b):return [b[i]-sum(T[i][j]*a[j] for j in range(len(a))) for i in range(len(b))]
r=decode(json.loads((BASE/'raw.json').read_text()));ids=set();laws={}
for rec in r['records']:
 assert rec['id'] not in ids;ids.add(rec['id']);ss=rec['samples'];s=len(ss[0]['a']);h=len(ss[0]['b'])
 assert s>=1 and h>=1 and sum(z['p'] for z in ss)==1 and all(z['p']>0 and len(z['a'])==s and len(z['b'])==h for z in ss)
 assert len(rec['T'])==h and all(len(row)==s for row in rec['T'])
 C=moment(ss,'a','a');D=moment(ss,'b','a');E=moment(ss,'b','b');B=[solve_row(C,row) for row in D];S=minus(E,mult(B,trans(D)))
 assert (C,D,E,B,S)==tuple(rec[k] for k in ['Caa','Cba','Cbb','B','S']);psd(S)
 er=[{'p':z['p'],'a':z['a'],'b':residual(rec['T'],z['a'],z['b'])} for z in ss];M=moment(er,'b','b');diff=minus(M,S);psd(diff)
 assert M==rec['residual_moment'] and diff==rec['PSD_difference'];assert sum(M[i][i] for i in range(h))==rec['reconstruction_MSE'];assert sum(S[i][i] for i in range(h))==rec['minimum_MSE']
 risk=F(0)
 for u,v in rec['queries']:
  assert len(u)==s and len(v)==h;fold=[u[j]+sum(rec['T'][i][j]*v[i] for i in range(h)) for j in range(s)]
  for z in ss:
   e=residual(rec['T'],z['a'],z['b']);score=sum(u[j]*z['a'][j] for j in range(s))+sum(v[i]*z['b'][i] for i in range(h));assert score==sum(fold[j]*z['a'][j] for j in range(s))+sum(v[i]*e[i] for i in range(h));risk+=z['p']*sum(v[i]*e[i] for i in range(h))**2/len(rec['queries'])
 assert risk==rec['independent_score_MSE']==rec['trace_score_MSE'];laws[rec['id'].split('-')[0]]=ss
assert len(ids)==25 and len(laws)==5
loss=[]
for T in [F(0),F(1)]:loss.append((sum(x['p']*(x['b']-T*x['a'])**2 for x in r['paired_samples']),sum(x['p']*(x['v']*(x['b']-T*x['a']))**2 for x in r['paired_samples'])))
assert loss==[(1,F(1,2)),(2,0)]
assert all(x['b'][0]==x['a'][0]**2 for x in laws['nonlinear']) and r['nonlinear_mse']==0
assert next(x for x in r['records'] if x['id']=='nonlinear-1')['minimum_MSE']==F(17,2)
R=r['rotation']['R'];I=r['rotation']['B'];assert mult(R,I)==mult(I,R) and mult(trans(R),I)!=mult(I,R) and R!=I
try:solve_row([[F(1),F(1)],[F(1),F(1)]],[F(1),F(1)]);raise RuntimeError('singular accepted')
except AssertionError:pass
assert r['sensor']=={'B':2,'conductance_S':3,'drop_MSE_A2':45,'predict_MSE_A2':9,'shift_MSE_V2':16}
from agent_runtime.knowledge import KnowledgeStore
from agent_runtime.knowledge_index import build_index,indexed_search
store=KnowledgeStore(ROOT/'knowledge');cfg=json.loads((BASE/'retrieval_protocol.json').read_text());orig=json.loads((BASE/'retrieval.json').read_text());db=BASE/'independent_index.sqlite';build_index(store,db);observed=[]
for old in orig['records']:
 result=store.search(old['query'],domain=cfg['domain'],limit=cfg['cutoff']) if old['backend']=='files-lexical-v1' else indexed_search(store,db,old['query'],domain=cfg['domain'],limit=cfg['cutoff'])
 actual=[x['id'] for x in result['results']];assert actual==old['actual'];observed.append({'backend':old['backend'],'case':old['case'],'actual':actual})
ctx=store.context(store.search(cfg['queries'][0],domain=cfg['domain'],limit=1),**cfg['context']);assert ctx==orig['context'];assert store.snapshot==orig['snapshot'];db.unlink()
sourcechecks=[]
for src in json.loads((BASE/'sources.json').read_text()):
 p=Path(src['scratch_download']);assert hashlib.sha256(p.read_bytes()).hexdigest()==src['sha256'];sourcechecks.append({'kind':src['kind'],'sha256':src['sha256'],'extent':src['read_extent']})
commands=[['python','-m','unittest','tests.test_knowledge','tests.test_knowledge_index','tests.test_knowledge_math','tests.test_knowledge_handoff','tests.test_knowledge_reuse','-v'],['python','scripts/sync_plugin_references.py','--check']];runs=[]
for cmd in commands:
 p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,timeout=35);runs.append({'command':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr});assert p.returncode==0
out={'exact_records':len(ids),'finite_laws':len(laws),'paired_losses':[[str(x) for x in pair] for pair in loss],'retrieval':observed,'context_ids':[e['id'] for e in ctx['entries']],'source_hash_checks':sourcechecks,'reruns':runs,'reviewer':'/root/linear_residual_result_review','limitations':['Fixed generated fixtures have valid dimensions/normalized probabilities and SPD retained moments; producer helpers use zip and are not a general input-validating covariance API.','First producer attempt failed Fraction tuple serialization and no v1 raw exists; v2 is independently recalculated here.','No model/GPU/Lean/heldout capability/performance/token evidence.']}
(BASE/'independent_checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'cases':25,'laws':5,'retrieval_checks':6,'tests_rc':[x['returncode'] for x in runs]}))
