"""Verify recorded retrieval nonregression and candidate/decision boundaries.

Uses repository APIs and real recorded CLI outputs; no author code execution.
"""
import json,pathlib,sys,math
ROOT=pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from agent_runtime.knowledge import KnowledgeStore,KnowledgeError
from agent_runtime.knowledge_index import indexed_search
from agent_runtime.knowledge_reuse import decision_support

def main():
    out=pathlib.Path(__file__).resolve().parent;checks=out/'checks';store=KnowledgeStore(ROOT/'knowledge');rows=[]
    for c in ['queries','round2-queries','morphology-queries','engineering-queries','rl-probability-queries','neuroscience-queries','bee-learning-queries']:
        a=json.loads((checks/('baseline-'+c+'.json')).read_text());b=json.loads((checks/('final-'+c+'.json')).read_text())
        for backend in a['backends']:
            ar=a['backends'][backend];br=b['backends'][backend]
            strip=lambda rs:[{k:v for k,v in x.items() if k!='seconds'} for x in rs]
            assert strip(ar['queries'])==strip(br['queries']),(c,backend)
            rows.append({'catalog':c,'backend':backend,'exact_query_results_unchanged':True,'raw_recall_at_3':br['mean_recall_at_3'],'context_recall':br['mean_context_recall'],'MRR':br['mean_reciprocal_rank']})
    candidate='neuro.salamander-cell-type-homology';assert store.records[candidate]['status']=='candidate'
    try:store.get(candidate)
    except KnowledgeError:pass
    else:raise AssertionError('candidate returned as published')
    natural='两种动物的脑细胞表达相似，怎样区分共同祖先和独立演化？';searches={}
    for backend in ['files','sqlite']:
        r=store.search(natural,domain='neuroscience',limit=3) if backend=='files' else indexed_search(store,ROOT/'.knowledge-cache/engineering-122522.sqlite',natural,domain='neuroscience',limit=3)
        ids=[x['id'] for x in r['results']];assert candidate not in ids;searches[backend]={'query':natural,'returned_ids':ids,'interpretation':'avian card offers related boundaries; salamander candidate deliberately excluded, no verified amphibian-specific answer'}
    assert candidate not in [x['id'] for x in decision_support(store,natural,{},limit=20)['results']]
    rec=store.get('neuro.bumblebee-social-diffusion');matched=rec['reuse']['conditions'];cases=[]
    for name,ctx,explicit,want in [('missing',{},False,'insufficient_context'),('matched',matched,False,'reuse_for_planning'),('wrong-species',{**matched,'species':'Pleurodeles waltl'},False,'minimal_transfer_check'),('explicit-reproduction',matched,True,'run_requested_experiment')]:
        r=decision_support(store,'熊蜂 单步 双选 开箱',ctx,explicit_reproduction=explicit,limit=20);x=next(x for x in r['results'] if x['id']==rec['id']);assert x['disposition']==want and x['automatic_skip_authorized'] is False;cases.append({'case':name,'disposition':want,'automatic_skip_authorized':False})
    assert 47+67==114 and math.isclose(29294/36116,0.8111086499058589,rel_tol=1e-7)
    result={'scope':'Authored structural regression; not blind scientific review, biology/R reproduction or model A/B','regression':rows,'natural_question':searches,'candidate_isolation':True,'conditions':cases,'knowledge_refs':rec['knowledge_refs'],'synthetic_arithmetic':{'clusters_sum':114,'differentiated_neurons_fraction_of_QC_cells':29294/36116,'denominator':'cells in this QC dataset, not donors or entire brain'},'checks_passed':True}
    (out/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('14 backend/catalog comparisons unchanged; candidate isolated; 4 decision boundaries passed')

if __name__=='__main__':main()
