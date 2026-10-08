from pathlib import Path
from fractions import Fraction as Q
import json, hashlib, subprocess, runpy, contextlib, io, sys, time
from unittest.mock import patch
ROOT=Path.cwd(); B=ROOT/'agent_doc/results/math-convex-projection-20261009'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,x): (B/name).write_text(json.dumps(x,indent=2)+'\n')
from agent_runtime.result_validation import inspect_result
contract=json.loads((B/'controller_contract.json').read_text()); pending=inspect_result(ROOT,contract); assert pending['status']=='pending',pending
assert pending['proof']['manifest_sha256']=='58e4e9c35a17c8ce891778028e731bbdeb0c4effa076fe47fafd266fcbab49ac'
write('independent_pending_snapshot.json',pending)
cases=json.loads((B/'cases.json').read_text()); raw=json.loads((B/'raw.json').read_text()); assert len(cases)==len(raw['cases'])==12
assert [x['id'] for x in cases]==[x['id'] for x in raw['cases']]==['P'+str(i) for i in range(1,13)]
# Independent analytical geometry: intervals clamp z, singleton fixed, segment orthogonal foot,
# triangle exterior symmetry x+y=1, interior target itself. No producer project/solve imports.
reference={'P1':['5/6'],'P2':['1'],'P3':['1','0'],'P4':['1/2','1/2'],'P5':['1'],'P6':['3','4'],'P7':['1/4','1/4'],'P10':['2'],'P11':['4'],'P12':['0']}
def scalar(a,b):return sum((x*y for x,y in zip(a,b)),Q(0))
def independent_cert(v,z,b):
 assert len(b)==len(v) and all(q>=0 for q in b) and sum(b)==1
 y=[sum(b[i]*v[i][j] for i in range(len(v))) for j in range(len(z))];r=[x-y0 for x,y0 in zip(z,y)]
 scores=[scalar(r,p) for p in v];P=scalar(r,r);g=max(scores)-scalar(r,y)
 assert g>=0
 return dict(y=y,residual=r,P=P,gap=g,D=P-2*g,clipped_lower=max(Q(0),P-2*g),vertex_scores=scores)
def canon(o):
 if isinstance(o,Q):return str(o)
 if isinstance(o,list):return [canon(x) for x in o]
 if isinstance(o,dict):return {k:canon(v) for k,v in o.items()}
 return o
results=[]
for c,row in zip(cases,raw['cases']):
 v=[[Q(x) for x in p] for p in c['values']]; z=[Q(x) for x in c['target']]
 if c['id']=='P9': assert not v and row['rejected']; results.append(dict(id=c['id'],empty_refusal=True));continue
 if c['id']=='P8':assert any(Q(x)<0 for x in c['proposal']) and row['rejected'];results.append(dict(id=c['id'],signed_refusal=True));continue
 original_v,original_z=v,z
 if 'W' in c:
  W=[[Q(x) for x in p] for p in c['W']];v=[[scalar(w,p) for w in W] for p in v];z=[scalar(w,z) for w in W]
 cert=independent_cert(v,z,[Q(x) for x in row['weights']]);assert canon(cert)==row['optimal']
 assert cert['y']==list(map(Q,reference[c['id']])) and cert['gap']==0 and cert['P']==Q(c['expected_squared'])
 if 'proposal' in row:
  pc=independent_cert(v,z,list(map(Q,c['proposal'])));assert canon(pc)==row['proposal']; assert pc['D']<=cert['P']<=pc['P'];assert pc['P']-cert['P']<=2*pc['gap']
 if c['id']=='P12':
  rc=independent_cert(original_v,original_z,list(map(Q,row['weights'])));assert rc['P']==1 and row['raw_squared']=='1' and canon(rc['y'])==row['raw_y']
 results.append(dict(id=c['id'],independent_certificate=canon(cert),analytical_output=reference[c['id']]))
v=[[Q(0)],[Q(2)],[Q(4)]];z=[Q(4)];full=independent_cert(v,z,[Q(0),Q(1),Q(0)]);r=[Q(2)];falsegap=max(scalar(r,p) for p in v[:2])-Q(4);falseD=Q(4)-2*falsegap
assert falseD==4>0 and full['gap']==4 and full['D']==-4 and raw['incomplete_max']=={'false_lower':'4','actual_optimum':'0'}
assert raw['affine_relaxation']=={'weights':['-1','2'],'error_squared':'0','simplex_error_squared':'1'}
write('independent_exact.json',dict(cases=results,incomplete_max=dict(full=canon(full),false_lower=str(falseD)),method='Independent analytic geometry and direct Fraction recomputation, no producer helpers'))
# Execute frozen producer code only for reproduction, redirect output writes, never use as reference.
orig_write=Path.write_text
allowed={'raw.json':'independent_replay_raw.json','retrieval.json':'independent_replay_retrieval.json','retrieval_knowledge_use.json':'independent_replay_knowledge_use.json'}
def redirected(p,data,*args,**kwargs):
 assert p.parent==B and p.name in allowed, str(p)
 return orig_write(B/allowed[p.name],data,*args,**kwargs)
replay=[]
for name in ['validate.py','retrieve.py']:
 gl=runpy.run_path(str(B/name));out=io.StringIO()
 with patch.object(Path,'write_text',redirected),contextlib.redirect_stdout(out):gl['main']()
 replay.append(dict(script=name,stdout=out.getvalue()))
rr=json.loads((B/'independent_replay_raw.json').read_text()); assert {k:v for k,v in rr.items() if k!='seconds'}=={k:v for k,v in raw.items() if k!='seconds'}
a=json.loads((B/'retrieval.json').read_text());b=json.loads((B/'independent_replay_retrieval.json').read_text())
assert len(a['records'])==len(b['records'])==6
for x,y in zip(a['records'],b['records']): assert {k:v for k,v in x.items() if k!='seconds'}=={k:v for k,v in y.items() if k!='seconds'}
for k in ['scope','snapshot','protocol_sha256','context','token_cost','holdouts_metadata_sha256']:assert a[k]==b[k]
assert a['context']['status']=='ready' and len(a['context']['entries'])==2 and a['context']['budget']['used_chars']<=12000
write('independent_replay_summary.json',dict(replay=replay,exact_equality_excluding_diagnostic_seconds=True,structural_checks=6))
commands=[['python','-m','unittest','tests.test_knowledge','tests.test_knowledge_index','tests.test_knowledge_math','tests.test_knowledge_handoff','tests.test_knowledge_reuse','-v'],['python','scripts/sync_plugin_references.py','--check']]
logs=[]
for i,cmd in enumerate(commands):
 p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=90);(B/f'independent_command_{i}.log').write_text(p.stdout+p.stderr);logs.append(dict(command=cmd,exit_code=p.returncode));assert p.returncode==0
assert 'Ran 53 tests' in (B/'independent_command_0.log').read_text()
write('independent_commands.json',logs)
assert inspect_result(ROOT,contract)['proof']==pending['proof'],'bound artifacts changed'
source=json.loads((B/'sources.json').read_text());assert digest(Path('/tmp/boyd_projection.pdf'))==source['classic']['pdf_sha256'];assert digest(Path('/tmp/wildcat.pdf'))==source['recent']['pdf_sha256']
write('independent_integrity.json',dict(manifest_sha256=digest(B/'manifest.json'),artifact_count=len(pending['proof']['artifact_hashes']),before_after_identical=True,source_pdf_digests_verified=True,case_ids=[x['id'] for x in cases],retrieval_records=6))
print('Independent exact/replay/integrity/regression checks completed')
