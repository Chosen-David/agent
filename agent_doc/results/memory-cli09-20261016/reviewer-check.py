import contextlib, hashlib, io, json, pathlib, sqlite3, subprocess, sys, tempfile
from agent_runtime.project_memory import MemoryLedger, main, _load_document_refs
from agent_runtime.project_docs import migrate, snapshot_project_docs
checks=[]
def check(name): checks.append(name)
def state(path):
 with sqlite3.connect(path) as db:
  return {t:db.execute('SELECT * FROM '+t+' ORDER BY rowid').fetchall() for t in ['entries','dependencies','document_dependencies','events','sqlite_sequence']}
def args(root, cmd, f):
 x=['--root',str(root)]
 if cmd=='add': x+=['add','--id','new','--kind','claim','--content','hello','--source','review']
 else: x+=['correct','--id','old','--new-id','rev','--content','hello','--reason','review','--source','review']
 return x+['--document-refs',str(f)]
with tempfile.TemporaryDirectory() as d:
 root=pathlib.Path(d); ledger=MemoryLedger(root,create=True); ledger.add('old','claim','old','review')
 f=root/'refs.json'
 for cmd in ['add','correct']:
  for data in [b'{',b'\xff']:
   f.write_bytes(data); before=state(ledger.path)
   proc=subprocess.run([sys.executable,'-m','agent_runtime.project_memory',*args(root,cmd,f)],capture_output=True,text=True)
   assert proc.returncode==2 and not proc.stdout and isinstance(json.loads(proc.stderr)['error'],str)
   assert state(ledger.path)==before
   check('subprocess '+cmd+' '+data.hex())
 # Existing legacy add may upgrade schema before malformed decoding, preserving all business rows.
 with sqlite3.connect(ledger.path) as db: db.execute('DROP INDEX memory_events_entry'); db.execute('DROP INDEX memory_dependencies_parent')
 before=state(ledger.path); f.write_bytes(b'{')
 with contextlib.redirect_stderr(io.StringIO()): assert main(args(root,'add',f))==2
 assert state(ledger.path)==before
 with sqlite3.connect(ledger.path) as db: assert db.execute("SELECT count(*) FROM sqlite_master WHERE type='index' AND name IN ('memory_events_entry','memory_dependencies_parent')").fetchone()[0]==2
 check('legacy add schema upgrade before decode without business changes')
 # Valid current bindings still work for both commands.
 (root/'TASK.md').write_text('## 2026-10-16\n- [ ] [T1] Review\n'); migrate(root,'2026-10-16')
 f.write_text(json.dumps(snapshot_project_docs(root)))
 for cmd in ['add','correct']:
  out=io.StringIO();err=io.StringIO()
  with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err): assert main(args(root,cmd,f))==0
  assert not err.getvalue() and json.loads(out.getvalue())
  check('valid binding '+cmd)
 # Genuine stored scope corruption must not be relabelled by input-file helper.
 with sqlite3.connect(ledger.path) as db: db.execute("UPDATE entries SET scope='{' WHERE id='new'")
 before=state(ledger.path)
 for command in [['history','new'],['check','new'],['correct','--id','new','--new-id','next','--content','next','--source','review','--reason','review','--document-refs',str(f)]]:
  try: main(['--root',str(root),*command])
  except json.JSONDecodeError: pass
  else: raise AssertionError(command)
  assert state(ledger.path)==before
  check('real DB malformed scope propagation '+command[0])
 # Same boundary for database document JSON.
 with sqlite3.connect(ledger.path) as db:
  db.execute("UPDATE entries SET scope='[]' WHERE id='new'");db.execute("UPDATE document_dependencies SET snapshot='{' WHERE entry_id='new'")
 try: main(['--root',str(root),'history','new'])
 except json.JSONDecodeError: pass
 else: raise AssertionError('DB snapshot incorrectly caught')
 check('real DB malformed document snapshot propagation')
 assert _load_document_refs(None) is None and _load_document_refs('') is None
 check('falsy path compatibility')
with tempfile.TemporaryDirectory() as d:
 root=pathlib.Path(d);f=root/'bad.json';f.write_bytes(b'\xff')
 with contextlib.redirect_stderr(io.StringIO()): assert main(args(root,'add',f))==2
 p=root/'.agent-memory/memory.sqlite3'; assert p.exists(); assert not state(p)['entries']
 check('first add initialization retained')
print(json.dumps({'checks':checks,'count':len(checks),'source_sha256':hashlib.sha256(pathlib.Path('agent_runtime/project_memory.py').read_bytes()).hexdigest(),'test_sha256':hashlib.sha256(pathlib.Path('tests/test_memory_cli_input.py').read_bytes()).hexdigest()},indent=2))
