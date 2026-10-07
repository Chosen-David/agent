"""Recheck this zero-publication maintenance round; no third-party code execution."""
import json, math, pathlib, statistics, sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from agent_runtime.knowledge import KnowledgeStore,KnowledgeError
from agent_runtime.knowledge_index import indexed_search
from agent_runtime.knowledge_reuse import decision_support

def main():
    out=pathlib.Path(__file__).resolve().parent; checks=out/'checks'; store=KnowledgeStore(ROOT/'knowledge')
    catalogs=['queries','round2-queries','morphology-queries','engineering-queries','rl-probability-queries','neuroscience-queries','bee-learning-queries']
    comparisons=[]
    for c in catalogs:
        a=json.loads((checks/('baseline-'+c+'.json')).read_text());b=json.loads((checks/('final-'+c+'.json')).read_text())
        for backend in a['backends']:
            ar=a['backends'][backend];br=b['backends'][backend]
            # Require exact query-level rankings and evidence packages, not only averages.
            rowsa=ar.get('queries',ar.get('results',[]));rowsb=br.get('queries',br.get('results',[]))
            assert rowsa and rowsb, list(ar)
            strip=lambda rows:[{k:v for k,v in r.items() if k!='seconds'} for r in rows]
            assert strip(rowsa)==strip(rowsb),(c,backend)
            comparisons.append({'catalog':c,'backend':backend,'exact_query_results_unchanged':True,'raw_recall_at_3':br['mean_recall_at_3'],'context_recall':br['mean_context_recall'],'MRR':br['mean_reciprocal_rank']})
    candidate='neuro.cephalopod-arm-segmentation'
    assert store.records[candidate]['status']=='candidate'
    try:store.get(candidate)
    except KnowledgeError:pass
    else:raise AssertionError('candidate accessible as published')
    natural='一条柔软的腕怎样把局部运动协调起来，吸盘之间的空间关系如何保留？'
    searches={}
    for backend in ['files','sqlite']:
        result=store.search(natural,domain='neuroscience',limit=3) if backend=='files' else indexed_search(store,ROOT/'.knowledge-cache/engineering-115246.sqlite',natural,domain='neuroscience',limit=3)
        ids=[r['id'] for r in result['results']];assert candidate not in ids
        searches[backend]={'query':natural,'returned_ids':ids,'applicability':'no verified arm-control coverage; candidate intentionally excluded'}
    decision=decision_support(store,natural,{},limit=20);assert candidate not in [r['id'] for r in decision['results']]
    rec=store.get('neuro.bumblebee-social-diffusion');matched=rec['reuse']['conditions'];mismatch={**matched,'species':'Octopus bimaculoides'}
    negatives=[]
    for name,context,explicit,expected in [('missing',{},False,'insufficient_context'),('matched',matched,False,'reuse_for_planning'),('wrong-species',mismatch,False,'minimal_transfer_check'),('explicit-reproduction',matched,True,'run_requested_experiment')]:
        res=decision_support(store,'熊蜂 单步 双选 开箱',context,explicit_reproduction=explicit,limit=20)
        row=next(r for r in res['results'] if r['id']==rec['id']);assert row['disposition']==expected and row['automatic_skip_authorized'] is False
        negatives.append({'case':name,'disposition':row['disposition'],'automatic_skip_authorized':False,'scientific_applicability':'human review still required'})
    assert math.isclose(244.8/360,.68) and math.isclose(115.2/360,.32)
    sd=statistics.stdev([0,2]);correct=sd/math.sqrt(2);mask_length=sd/math.sqrt(4)
    assert math.isclose(correct,1) and math.isclose(mask_length,1/math.sqrt(2))
    result={'scope':'Authored review/regression, not unseen model evaluation or animal/code reproduction','regression':comparisons,'natural_question':searches,'candidate_isolation':True,'conditions':negatives,'knowledge_refs':rec['knowledge_refs'],'synthetic_arithmetic':{'angle_fractions':[.68,.32],'group_size_SEM':correct,'full_mask_length_SEM':mask_length,'paper_impact':'unknown; authors MATLAB not run'},'checks_passed':True}
    (out/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
