"""Frozen public file/SQLite structure checks; no model/refusal evaluation."""
import json,hashlib,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from agent_runtime.knowledge import KnowledgeStore
from agent_runtime.knowledge_index import build_index,indexed_search
BASE=Path(__file__).resolve().parent

def main():
 protocol=BASE/'retrieval_protocol.json';assert protocol.is_file()
 cfg=json.loads(protocol.read_text());t=time.perf_counter();s=KnowledgeStore(ROOT/'knowledge');load=time.perf_counter()-t;records=[]
 with tempfile.TemporaryDirectory() as tmp:
  db=Path(tmp)/'search.sqlite';t=time.perf_counter();build_index(s,db);build=time.perf_counter()-t
  for backend in cfg['required_backends']:
   for i,q in enumerate(cfg['queries']):
    t=time.perf_counter();result=(s.search(q,domain=cfg['domain'],limit=cfg['cutoff']) if backend=='files-lexical-v1' else indexed_search(s,db,q,domain=cfg['domain'],limit=cfg['cutoff']));seconds=time.perf_counter()-t
    ids=[x['id'] for x in result['results']];payload=json.dumps(result,ensure_ascii=False)
    records.append({'backend':backend,'case':'R'+str(i+1),'query':q,'actual':ids,'hit':cfg['expected_id'] in ids,'seconds':seconds,'chars':len(payload),'bytes':len(payload.encode()),'result':result})
  context=s.context(s.search(cfg['queries'][0],domain=cfg['domain'],limit=1),**cfg['context'])
 output={'scope':'Public structural checks only','snapshot':s.snapshot,'protocol_sha256':hashlib.sha256(protocol.read_bytes()).hexdigest(),'load_seconds':load,'index_build_seconds':build,'records':records,'context':context,'token_cost':'unmeasured; chars/bytes not tokens','holdouts_metadata_sha256':hashlib.sha256((ROOT/'knowledge/evaluation_holdouts.json').read_bytes()).hexdigest()}
 ((Path(sys.argv[1])/'retrieval.json') if len(sys.argv)>1 else (BASE/'retrieval.json')).write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
 assert all(x['hit'] for x in records),[(x['backend'],x['case'],x['actual']) for x in records]
 assert context['status'] in ('ready','partial') and context['retrieved_ids']==[cfg['expected_id']] and set(cfg['expected_closure']) == {e['id'] for e in context['entries']} and len(context['entries'])<=cfg['context']['max_entries'],context['retrieved_ids']
 refs=s.get(cfg['expected_id'])['knowledge_refs'];s.check_refs(refs)
 ((Path(sys.argv[1])/'retrieval_knowledge_use.json') if len(sys.argv)>1 else (BASE/'retrieval_knowledge_use.json')).write_text(json.dumps({'task_id':'MATH-65','knowledge_root':'knowledge','knowledge_refs':refs,'premise_decisions':{'R1':'apply repaired full-support exact coupling before cost','R2':'same-unit linear force mixture with nonnegative normalized mass only','R3':'reject forbidden-support completion and nonconserved raw plan'},'scope':'Premise decisions are manual math inspection, not model refusal test'},ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'checks':len(records),'hits':sum(x['hit'] for x in records),'context_ids':context['retrieved_ids'],'budget':context['budget'],'token_cost':'unmeasured'},ensure_ascii=False))
if __name__=='__main__':main()
