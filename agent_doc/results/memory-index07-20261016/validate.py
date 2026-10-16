"""Correct the diagnostic oracle fixture; preserve original producer and failed log."""
import sys,json,sqlite3
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import probe
from unittest.mock import patch
from tempfile import TemporaryDirectory
from agent_runtime.project_memory import MemoryLedger,MemoryError
checks=[]
with TemporaryDirectory(prefix='agent-index-validation-') as tmp:
 for arm in (0,1):
  root=Path(tmp)/str(arm);l=MemoryLedger(root,create=True)
  l.add('a','claim','a','test',evidence='verified')
  l.add('b','claim','b','test',deps=['a'],evidence='verified')
  l.add('c','claim','c','test',deps=['a'],evidence='verified')
  l.correct('b','b2','new b','test','new')
  if arm:
   with sqlite3.connect(l.path) as db:db.execute(probe.DDL)
  before=probe.snap(l.path)
  try:l.correct('a','bad','bad','test','reason',deps=['c'])
  except MemoryError as e:assert 'invalidated lineage' in str(e)
  else:raise AssertionError('lineage must fail before insert')
  assert probe.snap(l.path)==before
  original=MemoryLedger._event
  triggered=[]
  def fail(db,entry_id,action,*args):
   if action=='stale':
    triggered.append(entry_id);raise sqlite3.OperationalError('injected write')
   return original(db,entry_id,action,*args)
  with patch.object(MemoryLedger,'_event',side_effect=fail):
   try:l.correct('a','a2','new a','test','reason')
   except MemoryError as e:assert 'injected write' in str(e)
   else:raise AssertionError('rollback must fail after mutation')
  assert triggered==['c'] and probe.snap(l.path)==before
  ans=l.correct('a','a2','new a','test','reason')
  assert ans['affected']==['b','c']
  assert l.history('b')['entry']['status']=='superseded'
  assert l.history('b2')['entry']['status']=='active'
  assert l.history('c')['entry']['status']=='stale'
  assert l.history('a')['entry']['status']=='superseded'
  assert l.history('a2')['entry']['status']=='active'
  assert [r['action'] for r in l.history('a')['events']]==['created','corrected']
  assert [r['id'] for r in l.impact('a')]==['b','c']
  checks.append({'arm':arm,'preinsert_rollback':True,'postmutation_rollback':True,'triggered':triggered,'exact_impact':True,'history':True,'preserved_superseded':True})
(probe.OUT/'validation-v2.json').write_text(json.dumps({'checks':checks,'producer_fixture_error':'original probe invalidation fixture had no active descendants; expected failure was invalid. Only validation fixture changed; original measurement data retained pending independent review.'},indent=2)+'\n')
print(json.dumps(checks))
