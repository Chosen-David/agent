import sys,types,json,tempfile,random,sqlite3,hashlib
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from agent_runtime import handoff_basis as cb,project_memory as cm
RUN=Path(__file__).parent.parent

def load(name,path):
 m=types.ModuleType(name);m.__package__='agent_runtime';exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m
bm=load('agent_runtime._reviewbase10',RUN/'baseline_project_memory.py');bb=load('agent_runtime._reviewbasis10',RUN/'baseline_handoff_basis.py');bb.MemoryLedger=bm.MemoryLedger
checks=[]
def outcome(fun,root,r,q,opts):
 try:return ('ok',fun(root,r,q,**opts))
 except Exception as e:return ('error',type(e).__name__,str(e))
def equal(name,root,r,q={},**opts):
 a=outcome(bb.basis_context,root,r,q,opts);b=outcome(cb.basis_context,root,r,q,opts)
 if a!=b:raise RuntimeError((name,a,b))
 checks.append({'name':name,'result':a[0],'sha256':hashlib.sha256(repr(a).encode()).hexdigest()})
rng=random.Random(6610)
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);ledger=cm.MemoryLedger(root,create=True)
 for i in range(24):
  deps=sorted(rng.sample([f'n{x:02}' for x in range(i)],min(i,rng.randrange(4))))
  ledger.add(f'n{i:02}','claim',f'完整 evidence {i}', 'fixture', deps=deps,evidence='verified')
 for j in range(35):
  refs=rng.sample([f'n{x:02}' for x in range(24)],rng.randrange(1,5));r={'input_version':'v1','artifacts':[],'memory_refs':refs}
  equal('graph'+str(j),root,r,max_chars=200000,known_memory_ids=rng.sample([f'n{x:02}' for x in range(24)],rng.randrange(4)))
 r={'input_version':'v1','artifacts':[],'memory_refs':['n23','n22']}
 for label,sql in [('stale',"UPDATE entries SET status='stale' WHERE id='n00'"),('corrupt-scope',"UPDATE entries SET scope='{' WHERE id='n23'")]:
  with sqlite3.connect(ledger.path) as db:old=db.execute('SELECT status,scope FROM entries WHERE id=?',('n00' if label=='stale' else 'n23',)).fetchone();db.execute(sql)
  equal(label,root,r,max_chars=200000)
  with sqlite3.connect(ledger.path) as db:db.execute('UPDATE entries SET status=?,scope=? WHERE id=?',(*old,'n00' if label=='stale' else 'n23'))
 for label,snapshot in [('corrupt-doc','{'),('invalid-doc','{}')]:
  with sqlite3.connect(ledger.path) as db:db.execute('INSERT INTO document_dependencies VALUES (?,?)',('n23',snapshot))
  equal(label,root,r,max_chars=200000)
  with sqlite3.connect(ledger.path) as db:db.execute('DELETE FROM document_dependencies')
 equal('missing',root,dict(r,memory_refs=['absent']))
 equal('required-precedence',root,dict(r,memory_refs=['absent']),{'memory_refs':['missing-required']})
 equal('budget',root,r,max_chars=10)
 for field in ('check','_get','_check','_walk'):
  seen=[];orig=getattr(cm.MemoryLedger,field)
  def wrapped(*args,_orig=orig,**kwargs):seen.append(1);return _orig(*args,**kwargs)
  with patch.object(cm.MemoryLedger,field,wrapped if field=='check' else staticmethod(wrapped)):
   actual=cb.basis_context(root,r,{},max_chars=200000)
  expected=bb.basis_context(root,r,{},max_chars=200000)
  if actual!=expected or not seen:raise RuntimeError('custom '+field)
  checks.append({'name':'custom-'+field,'calls':len(seen)})
 for mod in (bb,cb):
  class Fake:
   calls=[]
   def __init__(self,root):self.delegate=ledger
   def check(self,refs):self.calls.append(list(refs));return ledger.check(refs)
  with patch.object(mod,'MemoryLedger',Fake):out=mod.basis_context(root,r,{},max_chars=200000)
  if mod is bb:fake_out,fake_calls=out,Fake.calls
  elif out!=fake_out or Fake.calls!=fake_calls:raise RuntimeError('fake mismatch')
 checks.append({'name':'fake-ledger','calls':fake_calls})
 # Explicit diamond with shared ancestor, multiple roots and claim selection.
 for mid,deps in [('d0',[]),('d1',['d0']),('d2',['d0']),('d3',['d1','d2'])]:
  ledger.add(mid,'claim',mid,'fixture',deps=deps,evidence='verified')
 dr={'input_version':'v1','artifacts':[],'memory_refs':['d3','d1']}
 equal('diamond',root,dr,max_chars=200000)
 equal('diamond-known-shared',root,dr,max_chars=200000,known_memory_ids=['d0','d3'])
 claims=[dict(id='c'+str(i),status='supported',knowledge_ids=[],memory_ids=[mid],artifact_ids=[],depends_on=[],assumptions=[]) for i,mid in enumerate(['d3','d1'])]
 equal('claim-selected',root,dict(dr,evidence_claims=claims),{'context_claim_ids':['c1']},max_chars=200000)
 from agent_runtime.project_docs import snapshot_project_docs
 (root/'TASK.md').write_text('## 2026-10-07\n- [ ] [T1] Validate result\n')
 ledger.add('docroot','claim','doc','fixture',deps=['d3'],evidence='verified',document_refs=snapshot_project_docs(root))
 docr=dict(dr,memory_refs=['docroot'])
 equal('valid-doc',root,docr,max_chars=200000)
 (root/'TASK.md').write_text('## 2026-10-07\n- [ ] [T1] Changed result\n')
 equal('stale-doc-known',root,docr,max_chars=200000,known_memory_ids=['docroot'])
value={'checks':checks,'count':len(checks),'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'agent_runtime/handoff_basis.py',ROOT/'agent_runtime/project_memory.py']}}
(RUN/'reviewer/verification.json').write_text(json.dumps(value,indent=2));print('Independent differential/boundary checks',len(checks))
