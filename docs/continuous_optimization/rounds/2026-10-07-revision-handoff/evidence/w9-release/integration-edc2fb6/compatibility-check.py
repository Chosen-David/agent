from pathlib import Path
import json,hashlib,sqlite3,sys,subprocess
r=Path('/workspace/scratch/c12f3d9f92bd/agent');w=r.parent;sys.path.insert(0,str(r))
from agent_runtime.communication import Mailbox
from agent_runtime.handoff_basis import check_handoff_basis,basis_context
from scripts import agent_eval_pipeline as p
rd=r/'docs/continuous_optimization/rounds/2026-10-07-revision-handoff';e=rd/'evidence/w9-release/integration-edc2fb6'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
root=rd/'evidence/w9-release/handoff';original=w/'revision-w9-handoff-private/messages.sqlite';private=w/'revision-w9-edc2-private';private.mkdir(mode=0o700,exist_ok=True);copy=private/'messages.sqlite';before=sha(original)
with sqlite3.connect(f'file:{original}?mode=ro',uri=True) as a,sqlite3.connect(copy) as b:a.backup(b)
request=read(root/'review-final/consumer-request.json');box=Mailbox(copy,read(root/'plan.json'),root);status=box.status();ctx=box.prepare_context('research-review',3,request,max_chars=20000);old=read(rd/'evidence/w9-release/integration-6248c54/root-context-preparation.json')['context']
assert ctx['payload']==old['payload'];assert ctx['selection'] is None and ctx['usage']['tokens'] is None
assert box.status()==status and sha(original)==before
save(e/'default-context-compatibility.json',dict(base='edc2fb6cff64f5e400a77c3f130feef5f032d3e0',context=ctx,payload_identical=True,original_db_unchanged=True,receipts_unchanged=True,basis_persistence='owned backup only',scope='Actual current API compatibility of same legacy payload; no new model task, publish, ACK or closure'))
records=[]
for suffix,iv in [('8411705','w9-knowledge-'),('final','w9-final-')]:
 run=w/('revision-w9-'+suffix+'-run');manifest=read(run/'manifest.json')
 for cid in manifest['cases']:
  out=run/'cases'/cid/'attempts/0001/outputs';h=read(out/'handoff.json')
  # Task binding is independently fixed by frozen task metadata, and not supplied by producer.
  task=read(run/'cases'/cid/'task.json') if (run/'cases'/cid/'task.json').exists() else None
  req={'schema_version':1,'input_version':(read(w/'revision-w9-8411705-controller/dispatch-input-bindings.json')['cases'][cid]['input_version'] if suffix=='8411705' else iv+cid),'tasks':[{'task_id':'REV-03','allow_skip':False}],'knowledge_root':'snapshot/plugins/research-assistant/skills/model-with-knowledge/assets/knowledge','knowledge_refs':[]}
  if h['input_version']!=req['input_version']:
   # Abort: inspect actual host binding instead of copying producer version.
   raise ValueError((cid,req['input_version'],h['input_version']))
  gate=check_handoff_basis(run,h,req);current=basis_context(run,h,req,max_chars=200000)
  code="import sys,json;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from agent_runtime.handoff_basis import basis_context;print(json.dumps(basis_context(Path(sys.argv[2]),json.load(open(sys.argv[3])),json.loads(sys.argv[4]),max_chars=200000)))"
  # Final41914 snapshot has baseline basis_context; compare all records on this same old implementation.
  z=subprocess.run(['python','-B','-c',code,str(w/'revision-w9-final-run/snapshot'),str(run),str(out/'handoff.json'),json.dumps(req)],capture_output=True,text=True);assert z.returncode==0,z.stderr;prior=json.loads(z.stdout)
  assert current['payload']==prior['payload'],cid
  records.append(dict(run=suffix,role=cid,handoff_sha256=sha(out/'handoff.json'),basis_passed=True,default_payload_identical=True,chars=current['usage']['chars'],claims=len(gate['claims'])))
save(e/'role-default-compatibility.json',records)
m=read(w/'revision-w9-final-run/manifest.json');diff={s:{'frozen':h,'current':sha(r/s)} for s,h in m['snapshot_hashes'].items() if sha(r/s)!=h};save(e/'dependency-impact.json',dict(total=len(m['snapshot_hashes']),unchanged=len(m['snapshot_hashes'])-len(diff),changed=diff,scope='Historical task versions retained; defaultcontext exact comparisons plus impact review justify scoped reuse'))
print('compatibility',len(records),'dependencychanges',len(diff))
