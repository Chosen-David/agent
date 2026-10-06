#!/usr/bin/env python3
"""Compare file and indexed retrieval with per-query evidence, not model scores."""
import argparse
import json
from pathlib import Path
import statistics
import sys
import tempfile
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from agent_runtime.knowledge import KnowledgeStore
from agent_runtime.knowledge_index import build_index,indexed_search

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',default='knowledge')
    p.add_argument('--cases',default='evals/knowledge/queries.json')
    p.add_argument('--output',required=True)
    args=p.parse_args()
    started=time.perf_counter();store=KnowledgeStore(args.root);load=time.perf_counter()-started
    cases=json.loads(Path(args.cases).read_text())['cases']
    out={'schema_version':1,'snapshot':store.snapshot,'entries':len(store.records),'load_seconds':load,
         'scope':'Authored synthetic retrieval regression; not blind modeling, semantic retrieval or production speedup. Timings exclude corpus loading.','backends':{}}
    with tempfile.TemporaryDirectory() as tmp:
        db=Path(tmp)/'search.sqlite';t=time.perf_counter();build_index(store,db);out['index_build_seconds']=time.perf_counter()-t
        for backend in ('files','sqlite'):
            rows=[]
            for case in cases:
                start=time.perf_counter()
                result=store.search(case['query'],limit=3) if backend=='files' else indexed_search(store,db,case['query'],limit=3)
                elapsed=time.perf_counter()-start
                actual=[r['id'] for r in result['results']];expected=case['expected']
                hit=[k for k in expected if k in actual]
                rows.append({'case':case['id'],'query':case['query'],'expected':expected,'actual':actual,
                             'recall_at_3':len(hit)/len(expected) if expected else None,
                             'reciprocal_rank':1/min(actual.index(k)+1 for k in hit) if hit else 0,
                             'no_hit_correct':not actual if not expected else None,'seconds':elapsed})
            relevant=[r for r in rows if r['expected']]
            out['backends'][backend]={'mean_recall_at_3':statistics.mean(r['recall_at_3'] for r in relevant),
                'mean_reciprocal_rank':statistics.mean(r['reciprocal_rank'] for r in relevant),
                'median_query_seconds':statistics.median(r['seconds'] for r in rows),'queries':rows}
    target=Path(args.output);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({key:{k:v for k,v in val.items() if k!='queries'} for key,val in out['backends'].items()},indent=2))
    return 0 if all(b['mean_recall_at_3']==1 and all(r['no_hit_correct'] is not False for r in b['queries']) for b in out['backends'].values()) else 1
if __name__=='__main__': raise SystemExit(main())
