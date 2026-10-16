import sys,json,tempfile,sqlite3,hashlib
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from agent_runtime import project_memory as m,handoff_basis as b
RUN=Path(__file__).parent
checks=[]
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);ledger=m.MemoryLedger(root,create=True)
 ledger.add('a','claim','ancestor','fixture',evidence='verified')
 ledger.add('z','claim','root','fixture',deps=['a'],evidence='verified')
 # Guards must reject customization before even validating refs or opening DB.
 for name,obj,attr,replacement in [
  ('connect',m.MemoryLedger,'_connect',lambda *a:None),
  ('document-check',m,'check_document_refs',lambda *a:None),
  ('sqlite-connect',sqlite3,'connect',lambda *a:None),
  ('sqlite-Row',sqlite3,'Row',lambda *a:None)]:
  with patch.object(obj,attr,replacement):
   if ledger._context_closure(['invalid/refs']) is not None:raise RuntimeError(name)
  checks.append(name)
 class Sub(m.MemoryLedger):pass
 if Sub(root)._context_closure(['invalid/refs']) is not None:raise RuntimeError('subclass')
 checks.append('subclass')
 for name in ('check','_check','_get','_connect'):
  ledger.__dict__[name]=lambda *a:None
  if ledger._context_closure(['invalid/refs']) is not None:raise RuntimeError('instance '+name)
  del ledger.__dict__[name]
  checks.append('instance-'+name)
 with sqlite3.connect(ledger.path) as db:db.execute('PRAGMA journal_mode=WAL')
 fired=[]
 def trace(frame,event,arg):
  if event!='return' or frame.f_code is not m._read_entry.__code__ or frame.f_locals.get('entry_id')!='z' or fired:return
  f=frame.f_back
  while f and f.f_code.co_name!='_context_closure':f=f.f_back
  if not f:return
  with sqlite3.connect(ledger.path) as db:db.execute("UPDATE entries SET status='stale' WHERE id='a'")
  fired.append('writer committed after closure root read')
 old=sys.getprofile()
 try:
  sys.setprofile(trace);closure=ledger._context_closure(['z'])
 finally:sys.setprofile(old)
 if not fired or {x['id']:x['status'] for x in closure}!={'a':'active','z':'active'}:raise RuntimeError(('snapshot',fired,closure))
 try:ledger._context_closure(['z'])
 except m.MemoryError as e:
  if str(e)!='memory a is stale; reconciliation required':raise
 else:raise RuntimeError('cross-call stale cache')
 checks.append('WAL concurrent writer: closure snapshot old state, subsequent call stale; not whole basis_context atomic')
print(json.dumps({'count':len(checks),'checks':checks,'scope':'helper snapshot only; filesystem document state is outside SQLite transaction'},indent=2))
(RUN/'boundaries.json').write_text(json.dumps({'count':len(checks),'checks':checks},indent=2))
