import json,sqlite3,tempfile,copy,hashlib
from pathlib import Path
from unittest.mock import patch
from agent_runtime.project_memory import MemoryLedger,MemoryError
from agent_runtime.project_docs import snapshot_project_docs
OUT=Path(__file__).resolve().parent
DDL='CREATE INDEX memory_events_entry ON events(entry_id)'
TABLES=['entries','dependencies','document_dependencies','events','sqlite_sequence']
def snapshot(path):
 with sqlite3.connect(path) as db:return {t:db.execute('SELECT * FROM '+t+' ORDER BY rowid').fetchall() for t in TABLES}
def outcome(fn):
 try:return dict(value=fn())
 except Exception as e:return dict(error=type(e).__name__,message=str(e))
checks=[]
with tempfile.TemporaryDirectory(dir=OUT) as td:
 root=Path(td)/'ordered';root.mkdir();(root/'TASK.md').write_text('## 2026-10-16\n- [ ] [T1] History evidence\n');refs=snapshot_project_docs(root)
 l=MemoryLedger(root,create=True)
 l.add('a','claim','a','fixture',evidence='verified',document_refs=refs);l.add('b','claim','b','fixture',evidence='verified')
 inserted=[(19,'a','fourth','2000-01-01T00:00:00.000Z'),(-5,'a','first','2026-01-01T00:00:00.000Z'),(100,'a','last','1999-01-01T00:00:00.000Z'),(77,'b','other','2020-01-01T00:00:00.000Z'),(0,'a','second','2025-01-01T00:00:00.000Z'),(4,'a','third','2024-01-01T00:00:00.000Z')]
 with l._connect(write=True) as db:
  db.execute('DELETE FROM events')
  db.executemany('INSERT INTO events(sequence,entry_id,action,reason,source,related_id,created_at) VALUES(?,?,?,?,?,?,?)',[(i,e,a,'reason:'+a,'source:'+a,'related:'+a,t) for i,e,a,t in inserted])
  db.execute("UPDATE entries SET status='stale' WHERE id='a'")
 old=snapshot(l.path);physical=l.path.read_bytes();before=l.history('a');assert l.path.read_bytes()==physical
 with sqlite3.connect(l.path) as db:db.execute(DDL)
 metadata=None
 with sqlite3.connect(l.path) as db:
  metadata=dict(schema=db.execute("SELECT sql FROM sqlite_master WHERE name='memory_events_entry'").fetchone()[0],index_list=db.execute('PRAGMA index_list(events)').fetchall(),xinfo=db.execute('PRAGMA index_xinfo(memory_events_entry)').fetchall(),eqp=db.execute('EXPLAIN QUERY PLAN SELECT * FROM events WHERE entry_id=? ORDER BY sequence',('a',)).fetchall())
 physical=l.path.read_bytes();after=l.history('a');assert l.path.read_bytes()==physical and snapshot(l.path)==old
 assert before==after and [x['sequence'] for x in after['events']]==[-5,0,4,19,100]
 assert [x['action'] for x in after['events']]==['first','second','third','fourth','last']
 assert after['entry']['status']=='stale' and after['entry']['document_refs']==refs
 assert metadata['xinfo']==[(0,1,'entry_id',0,'BINARY',1),(1,-1,None,0,'BINARY',0)]
 assert all('COVERING' not in r[3] for r in metadata['eqp']) and any('USING INDEX memory_events_entry' in r[3] for r in metadata['eqp'])
 assert all('TEMP B-TREE' not in r[3] for r in metadata['eqp'])
 # Audit history hydration preserves document metadata, without turning into check().
 (root/'TASK.md').write_text('## 2026-10-16\n- [ ] [T1] Changed history evidence\n')
 assert l.history('a')==after
 checks.append(dict(case='sequence_and_audit',negative_gapped_out_of_order=True,backwards_timestamps_preserved=True,complete_packets_equal=True,stale_and_document_binding_preserved=True,physical_unchanged=True,metadata=metadata))
 # Public correction, rollback and exact ordered history after correction.
 for arm in (0,1):
  l=MemoryLedger(Path(td)/f'rollback{arm}',create=True)
  l.add('a','claim','a','fixture',evidence='verified')
  for k in ['b','c']:l.add(k,'claim',k,'fixture',deps=['a'],evidence='verified')
  l.correct('b','b2','new b','fixture','replacement')
  if arm:
   with sqlite3.connect(l.path) as db:db.execute(DDL)
  state=snapshot(l.path)
  pre=outcome(lambda:l.correct('a','invalid','invalid','fixture','reason',deps=['c']));assert pre.get('error')=='MemoryError' and 'invalidated lineage' in pre['message'] and snapshot(l.path)==state
  orig=MemoryLedger._event;hit=[]
  def fail(db,eid,action,*args):
   if action=='stale':hit.append(eid);raise sqlite3.OperationalError('independent history rollback')
   return orig(db,eid,action,*args)
  with patch.object(MemoryLedger,'_event',side_effect=fail):post=outcome(lambda:l.correct('a','a2','new','fixture','reason'))
  assert hit==['c'] and post.get('error')=='MemoryError' and 'independent history rollback' in post['message'] and snapshot(l.path)==state
  result=l.correct('a','a2','new','fixture','reason');assert result['affected']==['b','c']
  assert {k:l.history(k)['entry']['status'] for k in ['a','a2','b','b2','c']}==dict(a='superseded',a2='active',b='superseded',b2='active',c='stale')
  assert [e['action'] for e in l.history('a')['events']]==['created','corrected']
  assert [e['action'] for e in l.history('c')['events']]==['created','stale']
  checks.append(dict(case='rollback',arm=arm,preinsert=True,postwrite=True,history_and_superseded=True))
 # Existing hydration and error priority for both table layouts, not just happy packets.
 errors=[]
 for case in ['unknown','scope','document','event_utf8','other_event_utf8','missing_events','unknown_and_missing_events']:
  pair=[]
  for arm in (0,1):
   l=MemoryLedger(Path(td)/f'{case}{arm}',create=True);l.add('a','claim','a','s',evidence='verified');l.add('b','claim','b','s',evidence='verified')
   with l._connect(write=True) as db:
    if arm:db.execute(DDL)
    if case=='scope':db.execute("UPDATE entries SET scope='broken' WHERE id='a'")
    if case=='document':db.execute("INSERT INTO document_dependencies VALUES('a','broken')")
    if case in ['event_utf8','other_event_utf8']:db.execute("UPDATE events SET reason=CAST(X'FF' AS TEXT) WHERE entry_id=?",('a' if case=='event_utf8' else 'b',))
    if case in ['missing_events','unknown_and_missing_events']:db.execute('DROP TABLE events')
   pair.append(outcome(lambda:l.history('missing' if case in ['unknown','unknown_and_missing_events'] else 'a')))
  # Created timestamps differ across independently seeded DBs; compare error class/text, or stable packet fields.
  if 'value' in pair[0]:
   for r in pair:
    r['value']['entry']['created_at']='<clock>'
    for e in r['value']['events']:e['created_at']='<clock>'
  assert pair[0]==pair[1];errors.append(dict(case=case,outcome=pair[0]))
 checks.append(dict(case='hydration_errors',cases=errors))
(OUT/'semantics.json').write_text(json.dumps(dict(checks=checks,all_passed=True),indent=2)+'\n')
print(json.dumps(dict(boundary_groups=len(checks),all_passed=True)))
