"""Independent finite verifier. Never imports or executes the producer verify.py."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from collections import defaultdict
import argparse
import datetime
import hashlib
import json
import math
import platform
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from agent_runtime.knowledge import KnowledgeStore, KnowledgeError
from agent_runtime.knowledge_index import build_index, indexed_search


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tail(x, v, r):
    if x < 0 or v <= 0 or r <= 0:
        raise ValueError('outside stated formula domain')
    return math.exp(-float(x*x / (2*(v+r*x/3))))


def root(v, r, delta):
    if v <= 0 or r <= 0 or not 0 < delta < 1:
        raise ValueError('outside inversion domain')
    ell = -math.log(delta)
    b = float(r)*ell/3
    return b+math.sqrt(2*float(v)*ell+b*b)


def enumerate_leaves(n, x, cap, law):
    """Enumerate all leaves and every prefix, retaining paths after first crossing."""
    total = F(0)
    hit = F(0)
    terminal_hit = F(0)
    variance_values = set()
    conditional_nodes = set()
    for signs in product((1, -1), repeat=n):
        s, v, mass = F(0), F(0), F(1)
        crossed = (s >= x and v <= cap)
        previous = 1
        for t, sign in enumerate(signs, 1):
            if law == 'new':
                a = F(2) if previous > 0 else F(1, 3)
                outcomes = [(a, F(2,5)), (-2*a/3, F(3,5))]
                upper = F(2)
            else:
                a = F(1,2) if s > 0 else F(1)
                outcomes = [(a, F(1,3)), (-a/2, F(2,3))]
                upper = F(1)
            mean = sum(d*p for d,p in outcomes)
            variance = sum(d*d*p for d,p in outcomes)
            assert mean == 0 and max(d for d,p in outcomes) <= upper
            conditional_nodes.add((a, mean, variance))
            d,p = outcomes[0 if sign > 0 else 1]
            mass *= p
            s += d
            v += variance
            variance_values.add(v)
            crossed |= (s >= x and v <= cap)
            previous = sign
        total += mass
        if crossed:
            hit += mass
        if s >= x and v <= cap:
            terminal_hit += mass
    assert total == 1
    return hit, terminal_hit, sorted(conditional_nodes), len(variance_values)


def varying_survival(n):
    """Independent complementary recursion with live noncrossing paths only."""
    live = {0:1}
    for t in range(1,n+1):
        arrivals = defaultdict(int)
        for s,count in live.items():
            arrivals[s+1] += count
            arrivals[s-1] += count
        live = {s: count for s,count in arrivals.items()
                if s < 2 or (s-2)*(s-2) < 6*t}
    return 1-F(sum(live.values()),2**n)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--corpus-root',default='/tmp/knowledge-freedman-0915/published-eval')
    args=parser.parse_args()
    cases = json.loads((HERE/'independent_cases.json').read_text())
    result = {'actor':'/root/knowledge_result','execution_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'python':platform.python_version(),'command':'PYTHONDONTWRITEBYTECODE=1 python agent_doc/results/knowledge-freedman-20261008T0915Z/independent_verify.py',
              'case_sha256':sha(HERE/'independent_cases.json'),'code_sha256':sha(Path(__file__)),
              'archived_verifier_source':Path(__file__).read_text(),
              'corpus_root':str(Path(args.corpus_root).resolve()),
              'argv':sys.argv,
              'rerun_note':'Frozen cases unchanged; after repair these are exposed regression cases. Final published-root rerun checks the actual published state instead of asserting the old candidate state.',
              'scope':cases['scope'],'checks':[]}
    def add(name, ok, **data):
        result['checks'].append({'id':name,'passed':bool(ok),**data})
    hit, terminal, nodes, vcount = enumerate_leaves(7,F(3),F(6),'new')
    b = tail(F(3),F(6),F(2))
    add('adaptive-new-law', 0 < hit <= b, hit_exact=str(hit), terminal_exact=str(terminal),bound=b,
        conditional_nodes=[[str(z) for z in node] for node in nodes],distinct_prefix_variances=vcount)
    b = tail(F(10),F(10),F(1))
    add('marginal-not-conditional', F(1,2)>b, actual_probability='1/2',false_bound=b,
        conditional_mean_after_first_observation='Z, not zero',second_moment_sum=10)
    joint=F(0); eligible=F(0); slightly_lower=F(0)
    for zs in product((-1,1),repeat=3):
        tau=2 if zs[:2]==(1,1) else 3
        s=sum(zs[:tau]);v=tau
        eligible += F(int(v<=2),8)
        joint += F(int(s>=2 and v<=2),8)
        slightly_lower += F(int(s>=2 and F(v)<=F(199,100)),8)
    conditional=joint/eligible
    b=tail(F(2),F(2),F(1))
    add('stop-joint-not-conditional', joint==F(1,4) and joint<=b<conditional==1 and slightly_lower==0,
        joint_exact=str(joint),conditional_exact=str(conditional),eligible_exact=str(eligible),bound=b,
        probability_with_v_1_99=str(slightly_lower))
    dist=[(F(2),F(9,10)),(F(-18),F(1,10))]
    mean=sum(d*p for d,p in dist);variance=sum(d*d*p for d,p in dist)
    wrong=tail(F(18),variance,F(2));correct=tail(F(18),variance,F(18))
    add('one-sided-new-law',mean==0 and variance==36 and wrong<F(1,10)<=correct,
        mean=str(mean),variance=str(variance),actual_negative_tail='1/10',wrong_bound=wrong,correct_bound=correct)
    roots=[]
    for delta in (.2,.007):
        r,v=F(2),F(13,7);x=root(v,r,delta)
        negative_root=2*float(r)*(-math.log(delta))/3-x
        assert negative_root < 0 < x
        observed=tail(x,v,r)
        assert math.isclose(observed,delta,rel_tol=1e-12)
        for scale in (F(1,7),F(13)):
            xs=root(v*scale**2,r*scale,delta)
            assert math.isclose(xs,float(scale)*x,rel_tol=1e-12)
            assert math.isclose(tail(xs,v*scale**2,r*scale),delta,rel_tol=1e-12)
        roots.append({'delta':delta,'root':x,'bound':observed})
    add('root-and-units',True,results=roots,scales=['1/7','13'],units='S and R scale c; v scales c^2')
    rejected=0
    for f,domain_args in [(tail,(-1,1,1)),(tail,(1,0,1)),(tail,(1,1,0)),(root,(1,1,0)),(root,(1,1,1)),(root,(0,1,.5)),(root,(1,0,.5))]:
        try:f(*domain_args)
        except ValueError:rejected+=1
    h,*_=enumerate_leaves(1,F(0),F(1),'new')
    add('stop-domain',rejected==7 and h==1 and tail(0,1,1)==1,
        rejected_formula_inputs=rejected,time_zero_probability=str(h),tau_infinity_joint_probability=0,
        zero_R_argument='D<=0 and conditional mean zero imply D=0 almost surely; countably many t permits common probability-one set')
    producer=json.loads((HERE/'checks.json').read_text())
    replay=[]
    for check in producer['checks']:
        if check['kind']=='adaptive_positive':
            hp,tp,ns,_=enumerate_leaves(check['n'],F(check['x']),F(check['v']),'development')
            ok=(hp==F(check['probability_exact']) and math.isclose(tail(F(check['x']),F(check['v']),F(1)),check['bound_float'],rel_tol=1e-14))
            replay.append({'n':check['n'],'x':check['x'],'v':check['v'],'probability_exact':str(hp),'matches':ok})
    dp=varying_survival(1024)
    reported=next(c for c in producer['checks'] if c['kind']=='reject_varying_budget')
    for c in producer['checks']:
        if c['kind']=='reject_empirical_variance':
            assert c['actual_probability']==.25 and math.isclose(c['false_bound'],tail(F(2),F(1,100),F(1)),rel_tol=1e-14)
        if c['kind']=='reject_one_sided_flip':
            assert c['actual_probability']==.01 and math.isclose(c['false_bound'],tail(F(99),F(99),F(1)),rel_tol=1e-14)
        if c['kind']=='threshold_and_units':
            assert math.isclose(c['x'],root(F(4),F(1),.05),rel_tol=1e-14)
    add('recompute-development',len(replay)==9 and all(c['matches'] for c in replay) and dp==F(reported['probability_exact']) and dp>math.exp(-3),
        adaptive_replay=replay,varying_budget_exact=str(dp),varying_budget_float=float(dp),false_bound=math.exp(-3),
        method='full leaves for adaptive cases; complementary survivor counts for varying budget; old development cases are NOT new unseen cases')
    corpus=Path(args.corpus_root)
    store=KnowledgeStore(corpus)
    index=Path('/tmp/knowledge-freedman-0915')/('independent-index-'+hashlib.sha256(str(corpus.resolve()).encode()).hexdigest()[:12]+'.sqlite')
    build_index(store,index,rebuild=True)
    retrieval=next(c for c in cases['cases'] if c['id']=='new-retrieval')
    rec=[]
    for backend in retrieval['backends']:
        for q in retrieval['queries']+[retrieval['no_hit_query']]:
            search=store.search(q,limit=3) if backend=='files' else indexed_search(store,index,q,limit=3)
            ids=[r['id'] for r in search['results']]
            context=store.context(search,max_entries=8,max_chars=20000)
            ctx=[r['id'] for r in context['entries']]
            ok=(not ids if q==retrieval['no_hit_query'] else retrieval['expected_id'] in ids and retrieval['expected_id'] in ctx)
            ok &= search['applicability']=='unchecked'
            rec.append({'backend':backend,'query':q,'ids':ids,'context_ids':ctx,'passed':ok})
    add('new-retrieval',all(r['passed'] for r in rec),results=rec,corpus_snapshot=store.snapshot)
    kid='math.freedman-variance-budget';entry=store.get(kid);refs=entry['knowledge_refs']
    good=store.check_refs(refs)['valid'];rejections=[]
    for key,value in [('sha256','0'*64),('version',entry['version']+1)]:
        wrong=[{**refs[0],key:value}]
        try:store.check_refs(wrong)
        except KnowledgeError:rejections.append(key)
    mainstore=KnowledgeStore(ROOT/'knowledge')
    try:mainstore.check_refs(mainstore.get(kid,include_unpublished=True)['knowledge_refs']);candidate_rejected=False
    except KnowledgeError:candidate_rejected=True
    main_status=mainstore.records[kid]['status']
    main_state_correct=candidate_rejected if main_status=='candidate' else (main_status=='published' and not candidate_rejected)
    related=store.related(kid)['results'];related_ids=[r['id'] for r in related]
    required=[]
    add('refs-navigation',good and len(refs)==1 and refs[0]['id']==kid and entry['requires']==[] and len(rejections)==2 and main_state_correct and len(related_ids)>=3,
        refs=refs,requires=required,related_ids=related_ids,rejected_changed_fields=rejections,main_candidate_ref_rejected=candidate_rejected,main_status=main_status)
    comparison_prefix='final' if corpus.resolve()==(ROOT/'knowledge').resolve() else 'candidate'
    baseline_prefixes=['baseline']
    if (HERE/'integrated-baseline-original.json').exists():
        baseline_prefixes.append('integrated-baseline')
    for baseline_prefix in baseline_prefixes:
        comparisons=[]
        for suite in ('original','round2','morphology'):
            before=json.loads((HERE/f'{baseline_prefix}-{suite}.json').read_text())
            after=json.loads((HERE/f'{comparison_prefix}-{suite}.json').read_text())
            for backend,bdata in before['backends'].items():
                rows={q['case']:q for q in after['backends'][backend]['queries']}
                assert len(rows)==len(bdata['queries'])
                for old in bdata['queries']:
                    new=rows[old['case']]
                    ok=old['query']==new['query'] and old['expected']==new['expected']
                    metrics={}
                    for metric in ('recall_at_3','context_recall','no_hit_correct','reciprocal_rank'):
                        a,b=old.get(metric),new.get(metric)
                        metrics[metric]={'before':a,'after':b}
                        if metric!='reciprocal_rank':
                            ok &= (a is None and b is None) or (a is not None and b is not None and b>=a)
                    actual_search=store.search(old['query'],limit=3) if backend=='files' else indexed_search(store,index,old['query'],limit=3)
                    actual_ids=[x['id'] for x in actual_search['results']]
                    context_limit=after['context_candidate_limit']
                    actual_ctx_search=store.search(old['query'],limit=context_limit) if backend=='files' else indexed_search(store,index,old['query'],limit=context_limit)
                    actual_ctx=store.context(actual_ctx_search)
                    actual_ctx_ids=[x['id'] for x in actual_ctx['entries']]
                    expected=old['expected']
                    actual_recall=sum(k in actual_ids for k in expected)/len(expected) if expected else None
                    actual_ctx_recall=sum(k in actual_ctx_ids for k in expected)/len(expected) if expected else None
                    actual_nohit=(not actual_ids) if not expected else None
                    independent_match=(actual_ids==new['actual'] and actual_recall==new['recall_at_3'] and actual_ctx_recall==new['context_recall'] and actual_nohit==new['no_hit_correct'])
                    ok &= independent_match
                    comparisons.append({'independent_retrieval_matches':independent_match,'suite':suite,'backend':backend,'case':old['case'],'passed':ok,'metrics':metrics})
        exits=json.loads((HERE/'evaluation-commands.json').read_text())
        add('legacy-retrieval-nonregression' if baseline_prefix=='baseline' else 'integrated-baseline-nonregression',all(c['passed'] for c in comparisons),queries=comparisons,
            candidate_suite_exit_codes=[c['exit_code'] for c in exits],inherited_failures_preserved=True,
            limit='Nonregression does not make inherited failed suites pass. Timing and model utility not accepted.')
    paths=[HERE/x for x in ('independent_cases.json','verify.py','checks.json','plan.md','sources.json','baseline.json','evaluation-commands.json')]
    paths += [HERE/f'{prefix}-{suite}.json' for prefix in ('baseline','candidate') for suite in ('original','round2','morphology')]
    paths += [ROOT/'knowledge/entries'/f'{kid}.{ext}' for ext in ('json','md')]
    paths += [ROOT/'agent_runtime'/x for x in ('knowledge.py','knowledge_index.py')]
    paths += [ROOT/'scripts/eval_knowledge.py']
    paths += [HERE/f'{prefix}-{suite}.json' for prefix in (*baseline_prefixes,comparison_prefix) for suite in ('original','round2','morphology')]
    result['input_hashes']={str(p.relative_to(ROOT)):sha(p) for p in paths}
    result['all_checks_passed']=all(c['passed'] for c in result['checks'])
    result['acceptance']='usable-with-scope' if result['all_checks_passed'] else 'requires-review'
    if 'integrated-baseline' in baseline_prefixes:
        result['scope_reconciliation']={'reason':'Parent instructed rebase onto concurrent HEAD 59ad8d962ce934085f76171f651370ef5dcd9944 and compare both original and integrated baselines; frozen original criteria remain visible.','original_scope_passed':result['all_checks_passed'],'incremental_scope':'Only Freedman-card increment over exact integrated HEAD, not a claim of globally nondegraded retrieval since initial HEAD.'}
        result['incremental_checks_passed']=all(c['passed'] for c in result['checks'] if c['id']!='legacy-retrieval-nonregression')
        result['scientific_acceptance']='usable-with-scope' if all(c['passed'] for c in result['checks'] if c['id'] not in ('legacy-retrieval-nonregression','integrated-baseline-nonregression')) else 'requires-review'
        result['publication_acceptance']='allowed-with-scope' if result['all_checks_passed'] else 'blocked-by-original-baseline-gate'
        result['acceptance']='usable-with-scope' if result['all_checks_passed'] else 'publication-blocked'
        result['scope_reconciliation']['publication_rule']='Do not replace the frozen original-baseline gate with incremental-only acceptance; parent explicitly retained original gate.'
    prior_path=HERE/'independent_results.json'
    if prior_path.exists():
        prior=json.loads(prior_path.read_text())
        history=prior.pop('prior_runs',[])
        result['prior_runs']=[*history,prior]
    (HERE/'independent_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'acceptance':result['acceptance'],'checks':[{k:c[k] for k in ('id','passed')} for c in result['checks']]},ensure_ascii=False))

if __name__=='__main__':
    main()
