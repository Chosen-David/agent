from pathlib import Path
import sys,types,json,tempfile,sqlite3,hashlib
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import agent_runtime.project_memory as candidate
RUN=Path(__file__).parent
baseline=types.ModuleType('agent_runtime._revision11_baseline');baseline.__package__='agent_runtime'
exec(compile((RUN/'baseline.py').read_text(),'baseline.py','exec'),baseline.__dict__)

def rows(ledger):
 with sqlite3.connect(ledger.path) as db:
  return {t:db.execute('SELECT * FROM '+t+' ORDER BY rowid').fetchall() for t in ('entries','dependencies','events','document_dependencies')}
def seed(mod,root):
 l=mod.MemoryLedger(root,create=True)
 for id,deps,evidence in [('old',[],'verified'),('child',['old'],'verified'),('grand',['child'],'verified'),('raw',[],'verified'),('candidate',['raw'],'candidate')]:
  l.add(id,'claim','text:'+id,'fixture',deps=deps,evidence=evidence)
 return l

def outcome(mod,kwargs):
 with tempfile.TemporaryDirectory() as tmp:
  l=seed(mod,tmp); before=rows(l)
  try:
   result=l.correct(**dict(old_id='old',new_id='new',content='changed',source='user',reason='because',**{} )|kwargs)
   return 'success',result,l.list('all')
  except Exception as exc:
   assert rows(l)==before, ('partial mutation',kwargs)
   return type(exc).__name__,str(exc),None

def clean(value):
 if isinstance(value,dict):return {k:clean(v) for k,v in value.items() if k!='created_at'}
 if isinstance(value,list):
  result=[clean(v) for v in value]
  return sorted(result,key=lambda v:v['id']) if result and all(isinstance(v,dict) and 'id' in v for v in result) else result
 if isinstance(value,tuple):return tuple(clean(v) for v in value)
 return value

def main():
 checks=[]
 invalid=[None,1,1.5,True,[[]],[{}],['child',{}],set(),{},'raw',b'raw',[None],[1],['bad space'],['raw','raw']]
 for deps in invalid:
  b=outcome(baseline,{'deps':deps}); c=outcome(candidate,{'deps':deps})
  assert c[0]=='MemoryError',(repr(deps),c)
  checks.append({'case':'invalid:'+repr(deps),'baseline':b[0],'candidate':c[0],'rollback':True})
 for deps in ([],(),['raw'],('raw',),['missing'],['old'],['child'],['grand'],['new'],['candidate']):
  b=outcome(baseline,{'deps':deps});c=outcome(candidate,{'deps':deps})
  assert clean(b)==clean(c),(deps,b,c)
  checks.append({'case':'control:'+repr(deps),'exact_semantics_without_generated_timestamps':True,'outcome':c[0]})
 for overrides in ({'source':''},{'reason':''},{'old_id':'absent'}):
  b=outcome(baseline,{'deps':None,**overrides});c=outcome(candidate,{'deps':None,**overrides})
  assert b==c
  checks.append({'case':'precedence:'+repr(overrides),'exact_error':c[1],'rollback':True})
 for mod in (baseline,candidate):
  with tempfile.TemporaryDirectory() as tmp:
   l=seed(mod,tmp);result=l.accept('candidate','accepted','review','confirmed')
   assert result['revision']['content']=='text:candidate' and result['revision']['deps']==['raw']
   assert l.history('candidate')['entry']['status']=='superseded'
   assert l.check(['accepted'])[0]['evidence']=='verified'
   before=rows(l)
   try:l.correct('candidate','new','new','user','reason',deps=None)
   except mod.MemoryError as e:assert 'already superseded' in str(e)
   else:raise AssertionError('superseded allowed')
   assert rows(l)==before
 checks.append({'case':'accept-and-superseded-precedence','both_versions':True})
 with tempfile.TemporaryDirectory() as tmp:
  l=seed(candidate,tmp);before=rows(l)
  def broken_insert(db,*args,**kwargs):
   db.execute("UPDATE entries SET content='injected corruption' WHERE id='raw'")
   raise TypeError('internal injected failure')
  with patch.object(candidate.MemoryLedger,'_insert',side_effect=broken_insert):
   try:l.correct('old','new','changed','user','because',deps=['raw'])
   except TypeError as exc:assert str(exc)=='internal injected failure'
   else:raise AssertionError('internal TypeError hidden')
  assert rows(l)==before
 checks.append({'case':'internal-TypeError-unmasked-and-rollback','passed':True})
 data={'checks':checks,'count':len(checks),'source_sha256':hashlib.sha256(Path(candidate.__file__).read_bytes()).hexdigest(),'scope':'manual independent public Python API + real SQLite; invalid rows exact; valid comparisons exclude generated created_at timestamps and sort entry lists by ID because fixture generation times differ; no performance/model/GPU claim'}
 (RUN/'independent-raw.json').write_text(json.dumps(data,indent=2));print(json.dumps(data))
if __name__=='__main__':main()
