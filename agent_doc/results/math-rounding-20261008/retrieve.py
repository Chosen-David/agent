"""Frozen public structural retrieval checks, never a model evaluation."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from agent_runtime.knowledge import KnowledgeStore
from agent_runtime.knowledge_index import build_index,indexed_search
BASE=Path(__file__).resolve().parent


def main():
    protocol=BASE/'retrieval_protocol.json'
    assert hashlib.sha256(protocol.read_bytes()).hexdigest()=='b39d453836e41fc9485c3106e18dfb6fcd39c94aad8b567814f809e7e00aa9ae'
    config=json.loads(protocol.read_text()); t=time.perf_counter(); store=KnowledgeStore(ROOT/'knowledge')
    load_seconds=time.perf_counter()-t; records=[]
    with tempfile.TemporaryDirectory() as tmp:
        db=Path(tmp)/'search.sqlite';t=time.perf_counter();build_index(store,db);build_seconds=time.perf_counter()-t
        for backend in config['backends']:
            for case in config['queries']:
                t=time.perf_counter()
                result=(store.search(case['query'],domain=case['domain'],limit=case['top_k']) if backend=='files-lexical-v1' else indexed_search(store,db,case['query'],domain=case['domain'],limit=case['top_k']))
                seconds=time.perf_counter()-t
                encoded=json.dumps(result,ensure_ascii=False)
                actual=[r['id'] for r in result['results']]
                records.append({'backend':backend,'case':case['id'],'query':case['query'],'domain':case['domain'],'expected_id':case['expected_id'],'actual':actual,'hit':case['expected_id'] in actual,'seconds':seconds,'output_chars':len(encoded),'output_bytes':len(encoded.encode()),'result':result})
        # Point-dot needs one self-contained card; do not expand unrelated navigation.
        hit=store.search(config['queries'][0]['query'],domain='numerical-analysis',limit=1)
        context=store.context(hit,max_entries=3,max_chars=12000,include_related=False)
    assert all(r['hit'] for r in records),records
    assert context['status']=='ready' and context['retrieved_ids']==['math.floating-dot-enclosure'],context
    refs=store.get('math.floating-dot-enclosure')['knowledge_refs']+store.get('math.residual-interval-screening')['knowledge_refs']
    by_id={r['id']:r for r in refs};refs=list(by_id.values());store.check_refs(refs)
    (BASE/'knowledge_use.json').write_text(json.dumps({'task_id':'MATH-47','knowledge_root':'knowledge','knowledge_refs':refs,'premise_decisions':{'point-dot':'conditional adopt RN/gradual/stored target','coordinate-screening':'adopt only with all valid outward intervals and strict threshold','sensor-current':'conditional linear arithmetic only S*V=A','quantized-original/FTZ/ideal-RoPE/GPU-kernel':'refuse unverified target and arithmetic premises'}},ensure_ascii=False,indent=2)+'\n')
    output={'scope':'Frozen public structural file/SQLite queries and actual referenced content; no model retrieval/refusal quality','corpus_snapshot':store.snapshot,'protocol_sha256':hashlib.sha256(protocol.read_bytes()).hexdigest(),'records':records,'load_seconds':load_seconds,'index_build_seconds':build_seconds,'context':{'ids':[e['id'] for e in context['entries']],'status':context['status'],'budget':context['budget'],'refs':context['knowledge_refs']},'token_cost':'unmeasured; output chars/bytes are not token counts','holdouts_metadata_sha256':hashlib.sha256((ROOT/'knowledge/evaluation_holdouts.json').read_bytes()).hexdigest()}
    (BASE/'retrieval.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'checks':len(records),'hits':sum(r['hit'] for r in records),'context':output['context'],'token_cost':'unmeasured'},ensure_ascii=False))


if __name__=='__main__':main()
