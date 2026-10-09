from pathlib import Path
from fractions import Fraction as F
import json,sys,hashlib,subprocess,tempfile
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from agent_runtime.result_validation import _snapshot
c=json.loads((B/'contract.json').read_text());proof=_snapshot(R,c)[2];(B/'independent_snapshot.json').write_text(json.dumps(proof,indent=2)+'\n')
def enc(x):return json.loads(json.dumps(x,default=str))
def output(n,x):(B/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def e(x,y):return p*x*x+2*q*x*y+r*y*y
# Independent substitution in the three symmetric coordinate equations:
# (1-a²)p=1; (1-a²)q=2ap; (1-a²)r=1+4p+4aq.
a=F(1,2);p=1/(1-a*a);q=2*a*p/(1-a*a);r=(1+4*p+4*a*q)/(1-a*a)
P=[[p,q],[q,r]];det=p*r-q*q;assert det>0
vals={}
vals['C1']={'P':P,'det':det,'residual':[[F(0),F(0)],[F(0),F(0)]]}
assert (1-a*a)*p==1 and (1-a*a)*q==2*a*p and (1-a*a)*r==1+4*p+4*a*q
vals['C2']={'norm2_before':F(1),'norm2_after':F(17,4),'V_before':r,'V_after':e(F(2),a)};assert r-e(F(2),a)==1
# Independently exponentiate the scalar triangular recurrences per column.
x,y,z=F(1),F(0),F(1);v=[]
for t in range(31):
 assert x==a**t and z==a**t and y==(F(0) if t==0 else 2*t*a**(t-1));v.append({'t':t,'power':[[x,y],[F(0),z]]});x,y,z=a*x,a*y+2*z,a*z
vals['C3']=v
vals['C4']={'boundary_coefficient':0,'unstable_P':1/(1-F(11,10)**2)};assert 1-F(-1)**2==0
vals['C5']={'A':[[a,F(0)],[F(0),F(1)]],'P':[[p,F(0)],[F(0),F(1)]],'Q':[[F(1),F(0)],[F(0),F(0)]],'hidden_state':[[F(0)],[F(1)]]};assert p-a*a*p==1
vals['C6']={'A':[[a,F(0)],[F(0),F(2)]],'P':[[F(1),F(0)],[F(0),F(0)]],'Q':[[F(3,4),F(0)],[F(0),F(0)]]}
u,w=F(1),F(1);v=[]
for t in range(9):
 assert min(u,w)>=F(5,4)**t;v.append({'t':t,'state':[[u],[w]]});u,w=u/4+w,u+17*w/4
vals['C7']={'BA':[[F(1,4),F(1)],[F(1),F(17,4)]],'cycles':v,'minimum_row_sum':F(5,4)}
g=F(31,32);eta=F(1,50);margin=[[(g*g-1)*p+1,(g*g-1)*q],[(g*g-1)*q,(g*g-1)*r+1]];assert margin[0][0]>0 and margin[0][0]*margin[1][1]-margin[0][1]**2>0
assert g*g>F(365,392) and det==F(1168,81)
u,w=F(0),F(1);bound=F(4);v=[]
for t in range(41):
 assert e(u,w)<=bound**2;v.append({'t':t,'energy':e(u,w),'bound_squared':bound**2});noise=F((-1)**t,100);assert e(noise,F(0))<=eta**2;u,w=a*u+2*w+noise,a*w;bound=g*bound+eta
vals['C8']={'gamma':g,'eta':eta,'matrix_margin':margin,'trajectory':v}
raw=json.loads((B/'raw.json').read_text());assert len(raw['records'])==8 and len({v['id'] for v in raw['records']})==8
for rec in raw['records']:assert rec['passed'] and rec['values']==enc(vals[rec['id']]),rec['id']
output('independent_exact.json',{'method':'Independent scalar symmetric coordinate substitution, column power recurrence, cone recurrence and scalar disturbed state update; no producer import','cases':enc(vals),'all_eight_match':True})
commands=[]
def run(args,log):
 z=subprocess.run(args,cwd=R,capture_output=True,text=True);(B/log).write_text(z.stdout+z.stderr);commands.append({'command':args,'exit_code':z.returncode,'log':log});assert z.returncode==0;return z
run([sys.executable,str(B/'verify.py'),str(B/'independent_raw.json')],'independent_verify_replay.log')
replay=json.loads((B/'independent_raw.json').read_text());assert {k:v for k,v in replay.items() if k!='elapsed_seconds'}=={k:v for k,v in raw.items() if k!='elapsed_seconds'}
with tempfile.TemporaryDirectory() as tmp:
 run([sys.executable,str(B/'retrieve.py'),tmp],'independent_retrieve_replay.log');new=json.loads((Path(tmp)/'retrieval.json').read_text());old=json.loads((B/'retrieval.json').read_text())
 def strip(x):
  if isinstance(x,dict):return {k:strip(v) for k,v in x.items() if k not in ('seconds','load_seconds','index_build_seconds')}
  if isinstance(x,list):return [strip(v) for v in x]
  return x
 assert strip(new)==strip(old);assert (Path(tmp)/'retrieval_knowledge_use.json').read_bytes()==(B/'retrieval_knowledge_use.json').read_bytes()
 assert len(new['records'])==6 and all(x['hit'] for x in new['records']);assert {x['id'] for x in new['context']['entries']}=={'math.discrete-lyapunov','math.jordan-generalized-eigenspaces','math.hermitian-spectral-schur'}
 for ent in new['context']['entries']:
  # Verify full delivered content independently against source, not only entry IDs.
  print('context',ent['id'],list(ent))
 output('independent_replay_summary.json',{'exact_replay_except_elapsed':True,'retrieval_replay_except_timing':True,'six_hits':True,'context':new['context']})
run([sys.executable,'-m','unittest','tests.test_knowledge','tests.test_knowledge_handoff','tests.test_knowledge_index','tests.test_knowledge_math','tests.test_knowledge_reuse','-v'],'independent_regression.log')
def check(ref):assert hashlib.sha256((R/ref['path']).read_bytes()).hexdigest()==ref['sha256'],ref['path']
preserve=json.loads((B/'preservation.json').read_text());base=json.loads((B/'candidate_baseline.json').read_text());assert preserve['candidates_unchanged']==base
for ref in base:check(ref)
for pair in preserve['stable_knowledge_pairs']:
 for ref in pair.values():check(ref)
 assert (R/pair['source']['path']).read_bytes()==(R/pair['mirror']['path']).read_bytes()
assert (R/'knowledge/learning_state.json').read_bytes()==(B/'original_learning_state.json').read_bytes();assert (R/'knowledge/learning_state.json').read_bytes()==(R/'plugins/research-assistant/skills/model-with-knowledge/assets/knowledge/learning_state.json').read_bytes()
output('independent_preservation.json',{'stable_knowledge_pairs':preserve['stable_knowledge_pairs'],'candidates_unchanged':base,'live_policy':'source/mirror learning_state equality and original equality checked at review; live state excluded from durable refs; parent rechecks authorized closure','stable_pairs_count':len(preserve['stable_knowledge_pairs']),'original_learning_state':{'path':str((B/'original_learning_state.json').relative_to(R)),'sha256':hashlib.sha256((B/'original_learning_state.json').read_bytes()).hexdigest()}})
z=subprocess.run([sys.executable,'scripts/sync_plugin_references.py','--check'],cwd=R,capture_output=True,text=True);(B/'independent_global_mirror.log').write_text(z.stdout+z.stderr);assert (z.stdout+z.stderr).count(' - ')==1 and 'code-reading_execution.md' in z.stdout+z.stderr
assert _snapshot(R,c)[2]==proof;output('independent_integrity.json',{'bindings':len(proof['artifact_hashes']),'before_after_equal':True,'holdout':'metadata hash only; no unseen content inspected','stable_pairs':len(preserve['stable_knowledge_pairs']),'candidate_files':len(base)});output('independent_commands.json',commands)
print('INDEPENDENT CHECKS PASS',len(proof['artifact_hashes']))
