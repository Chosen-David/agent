#!/usr/bin/env python3
"""Replay explicitly informed relevance selection; not an automatic retriever."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--repo',type=Path,required=True)
    p.add_argument('--corpus',type=Path,required=True)
    p.add_argument('--cases',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();sys.path.insert(0,str(a.repo))
    from agent_runtime.knowledge import KnowledgeStore
    from agent_runtime.knowledge_index import build_index,indexed_search
    store=KnowledgeStore(a.corpus)
    cases={c['id']:c for c in json.loads(a.cases.read_text())['cases']}
    plans=[('files','A12',None,'ai.speculative-sampling-residual-exactness'),
           ('sqlite','A03',None,'infra.speculative-acceptance'),
           ('sqlite','A12','ai-algorithms','ai.speculative-sampling-residual-exactness')]
    rows=[]
    with tempfile.TemporaryDirectory() as tmp:
        db=Path(tmp)/'index.sqlite';build_index(store,db)
        for backend,case_id,domain,retained in plans:
            case=cases[case_id]
            raw=(store.search(case['query'],domain=domain,limit=3) if backend=='files'
                 else indexed_search(store,db,case['query'],domain=domain,limit=3))
            assert retained in [r['id'] for r in raw['results']]
            chosen=deepcopy(raw);chosen['results']=[r for r in raw['results'] if r['id']==retained]
            related=store.related(retained);context=store.context(chosen,max_entries=8,max_chars=20000)
            target=('ai.speculative-sampling-residual-exactness' if case['expected_role']=='residual'
                    else 'ai.speculative-decoding-cost-bound')
            assert target in [r['id'] for r in context['entries']]
            store.check_refs(context['knowledge_refs'])
            assert all(r['content']==store.get(r['id'])['content'] for r in context['entries'])
            rows.append({'backend':backend,'case':case_id,'query':case['query'],'domain_filter':domain,
                'actual_search':raw,'retained_id':retained,'related':related,'context':context,
                'target':target,'recovered':True,'operator_reason':'Human/agent relevance decision: speculative inference and sampling correctness/cost, not unrelated algebra or RL training. Discarded cards are not erased from original test results.'})
    result={'schema_version':1,'scope':'Three known development failures; informed operator selection plus existing related/show/context within the same20000-character budget. Not automated recovery, changed gold, unseen evaluation or ranking repair.',
        'candidate_snapshot':store.snapshot,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'cases_sha256':hashlib.sha256(a.cases.read_bytes()).hexdigest(),'all_recovered':all(x['recovered'] for x in rows),'rows':rows}
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'recovered':len(rows),'maximum_used_chars':max(r['context']['budget']['used_chars'] for r in rows)}))

if __name__=='__main__':main()
