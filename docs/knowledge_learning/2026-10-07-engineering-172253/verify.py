"""Verify recorded baseline nonregression and candidate/decision boundaries.

Authored structural checks only; no biological or author-code reproduction.
Run from the repository root after rebuilding the documented SQLite index.
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
    candidate='neuro.spider-rem-like-state';assert store.records[candidate]['status']=='candidate'
    try:store.get(candidate)
    except KnowledgeError:pass
    else:raise AssertionError('candidate returned as published')
    natural='夜间静止的小动物出现周期性眼部运动和抽动，怎样区分睡眠与运动节律？';searches={}
    for backend in ['files','sqlite']:
        r=store.search(natural,domain='neuroscience',limit=3) if backend=='files' else indexed_search(store,ROOT/'.knowledge-cache/engineering-172253.sqlite',natural,domain='neuroscience',limit=3)
        ids=[x['id'] for x in r['results']];assert candidate not in ids;searches[backend]={'query':natural,'returned_ids':ids,'interpretation':'related octopus/anesthesia evidence cannot establish spider-specific state; candidate deliberately excluded'}
    assert candidate not in [x['id'] for x in decision_support(store,natural,{},limit=20)['results']]
    rec=store.get('neuro.octopus-sleep-state-boundary');matched=rec['reuse']['conditions'];cases=[]
    for name,ctx,explicit,want in [('missing',{},False,'insufficient_context'),('matched',matched,False,'reuse_for_planning'),('wrong-species',{**matched,'species':'Evarcha arcuata'},False,'minimal_transfer_check'),('explicit-reproduction',matched,True,'run_requested_experiment')]:
        r=decision_support(store,'章鱼 睡眠 阶段 皮肤 神经活动',ctx,explicit_reproduction=explicit,limit=20);x=next(x for x in r['results'] if x['id']==rec['id']);assert x['disposition']==want and x['automatic_skip_authorized'] is False;cases.append({'case':name,'disposition':want,'automatic_skip_authorized':False})
    forward=135/135;reverse=135/342;assert forward==1 and math.isclose(reverse,0.39473684210526316)
    # A 10-frame missing interval at30fps is1/3s; a50-frame smoothing span5/3s.
    # Arithmetic on documented parameters, not execution of MATLAB filters.
    result={'scope':'Authored structural regression, not blind scientific review or biological/R/MATLAB/model reproduction','regression':rows,'natural_question':searches,'candidate_isolation':True,'conditions':cases,'knowledge_refs':rec['knowledge_refs'],'synthetic_arithmetic':{'retinal_given_curl':forward,'curl_given_retinal':reverse,'retinal_without_curl_fraction':1-reverse,'duration_analysis_events':330,'association_analysis_events':342,'short_gap_seconds_at30fps':10/30,'smoothing_span_seconds_at30fps':50/30,'interpretation':'conditional directions and denominators differ; raw subsets and real filter output unverified'},'checks_passed':True}
    (out/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('14 backend/catalog comparisons unchanged; candidate isolated; 4 decision boundaries passed')

if __name__=='__main__':main()
