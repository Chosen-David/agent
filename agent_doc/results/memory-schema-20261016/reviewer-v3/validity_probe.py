import json,sqlite3,sys,tempfile
from pathlib import Path
import agent_runtime.project_memory as m
from agent_runtime.project_docs import snapshot_project_docs
OUT=Path('.agent-runs/memory-schema-20261016/reviewer-v3')
with tempfile.TemporaryDirectory(dir=OUT) as tmp:
 root=Path(tmp);(root/'TASK.md').write_text('## 2026-10-16\n- [ ] [T1] Original task\n')
 ledger=m.MemoryLedger(root,create=True);snap=snapshot_project_docs(root)
 for name,deps in [('n0',[]),('n1',['n0']),('n2',['n0']),('n3',['n1','n2'])]:
  ledger.add(name,'claim',name,'synthetic',deps=deps,evidence='verified',document_refs=snap)
 events=[]
 def profile(frame,event,arg):
  if event=='call' and frame.f_code is m.check_document_refs.__code__:events.append(dict(root=str(frame.f_locals['root']),refs=frame.f_locals['refs']))
  return profile
 sys.setprofile(profile)
 try:first=ledger.check(['n3','n0'])
 finally:sys.setprofile(None)
 assert len(events)==4
 first[0]['document_refs']['task_index']['sha256']='mutated'
 second=ledger.check(['n3'])
 assert second[0]['document_refs']==snap
 (root/'TASK.md').write_text('## 2026-10-16\n- [ ] [T1] Changed task\n')
 try:ledger.check(['n3'])
 except m.MemoryError as exc:error=str(exc)
 else:raise AssertionError('document change accepted')
 assert 'stale project document dependencies' in error
 # Failed hydration repaired on same ledger: fresh traversal state and complete revalidation.
 with ledger._connect(write=True) as db:
  db.execute('DELETE FROM document_dependencies')
  db.execute("UPDATE entries SET scope='bad' WHERE id='n0'")
 try:ledger.check(['n3'])
 except json.JSONDecodeError:pass
 else:raise AssertionError('bad scope accepted')
 with ledger._connect(write=True) as db:db.execute("UPDATE entries SET scope='[]' WHERE id='n0'")
 assert ledger.check(['n3'])[0]['id']=='n3'
 report=dict(native_document_check_calls=len(events),document_checks_preserved=True,nested_mutation_isolated=True,document_edit_rejected=error,failed_hydration_repaired=True)
(OUT/'validity.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
