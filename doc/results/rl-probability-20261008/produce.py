"""Bounded public retrieval and decision checks; not paper reproduction."""
import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from agent_runtime.knowledge import KnowledgeStore
from agent_runtime.knowledge_index import build_index, indexed_search
from agent_runtime.knowledge_reuse import decision_support

IDS = ['algo.rl-sft-trajectory-concentration', 'prob.horizon-aware-betting']
QUERIES = ['推理路径多样性 单次成功率 采样预算', '有限预算序贯检验 截止期 检验力']


def observe(root, cases):
    store = KnowledgeStore(root/'knowledge')
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        db=Path(tmp)/'queries.sqlite'; build_index(store, db)
        for backend in ('files','sqlite'):
            for case in cases:
                hits = store.search(case['query'], limit=3) if backend=='files' else indexed_search(store,db,case['query'],limit=3)
                actual = [x['id'] for x in hits['results']]
                expected = case['expected']
                rows.append(dict(backend=backend, case=case['id'], query=case['query'], expected=expected, actual=actual,
                                 recall=sum(x in actual for x in expected)/len(expected) if expected else None,
                                 no_hit_correct=not actual if not expected else None))
    return rows


def decisions(root):
    store=KnowledgeStore(root/'knowledge'); rows=[]
    for kid,query in zip(IDS,QUERIES):
        conditions=store.get(kid)['reuse']['conditions']
        first=next(iter(conditions))
        for name,context,force,expected in [('matching',conditions,False,'reuse_for_planning'),
                                           ('missing',{},False,'insufficient_context'),
                                           ('different',{**conditions,first:'different target setting'},False,'minimal_transfer_check'),
                                           ('explicit-reproduction',conditions,True,'run_requested_experiment')]:
            result=decision_support(store,query,context,explicit_reproduction=force,limit=20)
            hit=next(x for x in result['results'] if x['id']==kid)
            rows.append({'id':kid,'case':name,'context':context,'expected':expected,'actual':hit['disposition'],
                         'automatic_skip_authorized':hit['automatic_skip_authorized'],'knowledge_refs':hit['knowledge_refs']})
    return rows


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();root=args.root.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    cases=[]
    for path in sorted((root/'evals/knowledge').glob('*.json')):
        for case in json.loads(path.read_text())['cases']:
            cases.append({**case,'id':path.name+':'+case['id']})
    old=observe(args.baseline.resolve(),cases); current=observe(root,cases)
    new=observe(root,[{'id':kid,'query':q,'expected':[kid]} for kid,q in zip(IDS,QUERIES)])
    results={'baseline':old,'current':current,'new':new,'decisions':decisions(root)}
    (out/'retrieval.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (out/'environment.json').write_text(json.dumps({'python':sys.version,'platform':platform.platform(),'machine':platform.machine(),'hardware_scope':'CPU retrieval and unit fixtures only','seeds':['not-applicable'],'repeats':1},indent=2)+'\n')
    assert all(a['recall'] is None or b['recall'] >= a['recall'] for a,b in zip(old,current))
    assert all(a['no_hit_correct'] is not True or b['no_hit_correct'] is True for a,b in zip(old,current))
    assert all(x['recall']==1 for x in new)
    assert all(x['actual']==x['expected'] and x['automatic_skip_authorized'] is False for x in results['decisions'])
    print(json.dumps({'old_query_rows':len(old),'new_query_rows':len(new),'decision_rows':len(results['decisions']),'scope':'Public authored regressions, no unseen model evaluation or timing claim'}))


if __name__=='__main__': main()
