#!/usr/bin/env python3
"""Check the existing scoped-search recovery, retaining default-budget closure."""
import argparse
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
    p.add_argument('--unscoped',action='store_true',help='Also reproduce default retrieval failures without domain recovery')
    a=p.parse_args()
    sys.path.insert(0,str(a.repo))
    from agent_runtime.knowledge import KnowledgeStore
    from agent_runtime.knowledge_index import build_index,indexed_search
    store=KnowledgeStore(a.corpus)
    cases=json.loads(a.cases.read_text())['cases']
    rows=[]
    with tempfile.TemporaryDirectory() as tmp:
        db=Path(tmp)/'index.sqlite';build_index(store,db)
        for backend in ['files','sqlite']:
            for case in cases:
                query=case['query']
                search=store.search(query,domain=None if a.unscoped else 'ai-algorithms',limit=3) if backend=='files' else indexed_search(store,db,query,domain=None if a.unscoped else 'ai-algorithms',limit=3)
                context=store.context(search)
                target='ai.speculative-sampling-residual-exactness' if case['expected_role']=='residual' else 'ai.speculative-decoding-cost-bound'
                ids=[x['id'] for x in context['entries']]
                if context['knowledge_refs']:store.check_refs(context['knowledge_refs'])
                fulltext=all(x['content']==store.get(x['id'])['content'] for x in context['entries'])
                rows.append({'backend':backend,'case':case['id'],'query':query,'raw_ids':[x['id'] for x in search['results']],
                    'context_ids':ids,'target':target,'hit':target in ids,'fulltext_unchanged':fulltext,
                    'budget':context['budget'],'refs':context['knowledge_refs'],'skipped':context['skipped']})
    result={'schema_version':1,'scope':('Unscoped default' if a.unscoped else 'Explicit existing domain=ai-algorithms recovery')+' development/regression replay; same frozen queries/gold and default 8 entries/20000-character context budget. Not unseen evaluation.',
        'snapshot':store.snapshot,'cases_sha256':hashlib.sha256(a.cases.read_bytes()).hexdigest(),
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'all_passed':all(r['hit'] and r['fulltext_unchanged'] for r in rows),'rows':rows}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'all_passed':result['all_passed'],'hits':sum(r['hit'] for r in rows),'checks':len(rows),'max_payload_chars':max(r['budget']['used_chars'] for r in rows)}))
    return 0 if result['all_passed'] else 1

if __name__=='__main__':raise SystemExit(main())
