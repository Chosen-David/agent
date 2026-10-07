#!/usr/bin/env python3
"""Read-only main corpus inspection; evaluate frozen queries in a copied corpus.
Only candidate status is changed in the copy. Does not alter ranking/expectations.
"""
import argparse,sys,json,hashlib,shutil,datetime
from pathlib import Path
sys.dont_write_bytecode=True

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def files(root):return {str(p.relative_to(root)):sha(p) for p in sorted((root/'entries').rglob('*')) if p.is_file()}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--work',type=Path,required=True)
    ap.add_argument('--base-corpus',type=Path,help='Fixed baseline corpus; defaults to repo/knowledge')
    ap.add_argument('--cases',type=Path,default=Path(__file__).with_name('frozen_tasks.json'))
    ap.add_argument('--residual-json',type=Path);ap.add_argument('--prefix-json',type=Path)
    a=ap.parse_args();a.work.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(a.repo))
    from agent_runtime.knowledge import KnowledgeStore
    from agent_runtime.knowledge_index import build_index,indexed_search,navigate
    main_root=a.repo/'knowledge';before=files(main_root);base_root=a.base_corpus or main_root
    dest=a.work/'knowledge';shutil.copytree(base_root,dest,ignore=shutil.ignore_patterns('*holdout*','*reserved*'))
    source_ids={};sources={}
    for role,path in [('residual',a.residual_json),('prefix',a.prefix_json)]:
        if not path:continue
        md=path.with_suffix('.md');meta=json.loads(path.read_text());kid=meta['id']
        source_ids[role]=kid;sources[role]={'json_sha256':sha(path),'md_sha256':sha(md),'id':kid,'original_status':meta['status']}
        if any(json.loads(p.read_text()).get('id')==kid for p in (dest/'entries').rglob('*.json')):raise ValueError('candidate id already exists')
        target=dest/'entries'/'validation_candidates';target.mkdir(exist_ok=True)
        shutil.copy2(path,target/path.name);shutil.copy2(md,target/md.name)
    original_store=KnowledgeStore(dest)
    candidates_hidden={}
    for role,kid in source_ids.items():
        candidates_hidden[role]=not any(row['id']==kid for row in original_store.search(kid,limit=20)['results'])
        # Publish status only in the copy, preserving every other field and full body.
        path=dest/'entries'/'validation_candidates'/({'residual':a.residual_json,'prefix':a.prefix_json}[role].name)
        meta=json.loads(path.read_text());old=dict(meta);meta['status']='published'
        assert {k:v for k,v in old.items() if k!='status'}=={k:v for k,v in meta.items() if k!='status'}
        path.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    store=KnowledgeStore(dest);db=a.work/'index.sqlite';build_index(store,db)
    cases=json.loads(a.cases.read_text())['cases'];backends={}
    for backend in ('files','sqlite'):
        rows=[]
        for case in cases:
            search=store.search(case['query'],limit=3) if backend=='files' else indexed_search(store,db,case['query'],limit=3)
            context=store.context(search)
            ids=[r['id'] for r in search['results']];contexts=[r['id'] for r in context['entries']]
            kid=source_ids.get(case['expected_role'])
            rows.append({'case':case['id'],'kind':case['kind'],'query':case['query'],'expected_role':case['expected_role'],'expected_id':kid,'raw_top3':ids,'context_ids':contexts,'raw_hit':kid in ids if kid else None,'context_hit':kid in contexts if kid else None,'applicability':search['applicability'],'context_status':context['status'],'budget':context['budget'],'skipped':context['skipped'],'search':search})
            # Retain actual context full text for audit, separately from short summary.
            (a.work/f'{backend}_{case["id"]}_context.json').write_text(json.dumps(context,ensure_ascii=False,indent=2)+'\n')
        backends[backend]={'query_count':len(rows),'raw_hits':sum(r['raw_hit'] is True for r in rows),'context_hits':sum(r['context_hit'] is True for r in rows),'rows':rows}
    full={}
    for role,kid in source_ids.items():
        content=store.get(kid);store.check_refs(content['knowledge_refs'])
        tree=navigate(store,kid)
        (a.work/f'{role}_show.json').write_text(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
        (a.work/f'{role}_tree.json').write_text(json.dumps(tree,ensure_ascii=False,indent=2)+'\n')
        full[role]={'id':kid,'knowledge_refs':content['knowledge_refs'],'source_json_sha256':sources[role]['json_sha256'],'source_md_sha256':sources[role]['md_sha256'],'body_unchanged':content['content']==({'residual':a.residual_json,'prefix':a.prefix_json}[role].with_suffix('.md').read_text())}
    after=files(main_root);assert before==after
    result={'schema_version':1,'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_tasks_sha256':sha(a.cases),'scope':'Frozen independent synthetic retrieval/context test; relevant negative-case retrieval is not permission to apply a theorem. No independent model use or performance measurement. Candidate copy status-only promotion, main corpus unchanged.','snapshot':store.snapshot,'candidate_sources':sources,'candidate_hidden_before_status_change':candidates_hidden,'fulltext_reference_checks':full,'main_entry_corpus_unchanged':True,'backends':backends}
    (a.work/'retrieval_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'work':str(a.work),'snapshot':store.snapshot,'backends':{k:{f:v[f] for f in ('query_count','raw_hits','context_hits')} for k,v in backends.items()}},ensure_ascii=False))
if __name__=='__main__':main()
