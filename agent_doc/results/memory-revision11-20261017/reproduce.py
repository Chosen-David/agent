from pathlib import Path
import sys,json,tempfile,sqlite3
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from agent_runtime.project_memory import MemoryLedger,MemoryError

def rows(ledger):
 with sqlite3.connect(ledger.path) as db:
  return {t:db.execute('SELECT * FROM '+t+' ORDER BY rowid').fetchall() for t in ['entries','dependencies','events','document_dependencies']}

def main():
 outcomes=[]
 with tempfile.TemporaryDirectory() as tmp:
  ledger=MemoryLedger(tmp,create=True);ledger.add('old','claim','old','fixture',evidence='verified');ledger.add('child','claim','child','fixture',deps=['old'],evidence='verified')
  for name,deps in [('none',None),('integer',1),('nested-list',[[]]),('nested-dict',[{}]),('mixed',['child',{}])]:
   before=rows(ledger)
   try:ledger.correct('old','new','new','user','reason',deps=deps);error='NO ERROR'
   except Exception as e:error=type(e).__name__
   outcomes.append({'case':name,'exception':error,'business_rows_unchanged':rows(ledger)==before})
 Path(__file__).with_name('reproduction.json').write_text(json.dumps(outcomes,indent=2));print(json.dumps(outcomes))
if __name__=='__main__':main()
