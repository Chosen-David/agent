"""Reproducible numerical checks, not a theorem prover or model evaluation."""
import json, math, time
from pathlib import Path
from agent_runtime.knowledge import KnowledgeStore

def radius(n, width, delta, sequential=False):
    if type(n) is not int or n < 1 or not math.isfinite(width) or width < 0 or not 0 < delta < 1:
        raise ValueError('invalid deterministic parameters')
    logterm=math.log(2)-math.log(delta)
    if sequential: logterm+=math.log(n)+math.log(n+1)
    return width*math.sqrt(logterm/(2*n))

def crossing(horizon, p, delta, sequential):
    # Live probability masses indexed by success count; absorb first crossing.
    live=[1.];absorbed=0.
    for n in range(1,horizon+1):
        nxt=[0.]*(n+1)
        for k,mass in enumerate(live):
            nxt[k]+=mass*(1-p);nxt[k+1]+=mass*p
        r=radius(n,1,delta,sequential)
        for k in range(n+1):
            if abs(k/n-p)>r:
                absorbed+=nxt[k];nxt[k]=0.
        live=nxt
    assert abs(sum(live)+absorbed-1)<1e-12
    return absorbed

def main():
    started=time.perf_counter();out={'scope':'Authored exposed numerical and retrieval checks, no LLM or formal prover','checks':[]}
    def check(name,condition,data):
        assert condition,name
        out['checks'].append({'name':name,'pass':True,'data':data})
    check('paired-range',math.ceil(4*math.log(40)/.02)==738,{'required_n':738,'width':2})
    fixed=radius(1000,2,.05);seq=radius(1000,2,.05,True)
    check('paired-decision-difference',.1-fixed>0 and .1-seq<0,{'fixed_radius':fixed,'sequential_radius':seq,'observed_difference':.1})
    check('sensor-cross-domain',abs(radius(100,4,.05)-.543240606)<1e-8,{'radius':radius(100,4,.05),'range':[2,6]})
    spent=sum(.05/(t*(t+1)) for t in range(1,1001))
    check('telescoping-budget',abs(spent-.05*1000/1001)<1e-14,{'spent_through_1000':spent})
    dp=[]
    for p in (.1,.5,.9):
        for sequential in (False,True):
            prob=crossing(500,p,.05,sequential)
            dp.append({'p':p,'horizon':500,'sequential':sequential,'first_crossing_probability':prob})
            if sequential: check('finite-time-coverage-'+str(p),prob<=.05,dp[-1])
    out['fixed_vs_sequential_dp']=dp
    check('dependent-sample-counterexample',2*math.exp(-2*100*.49**2)<1,{'true_probability_abs_error_ge_049':1,'misapplied_independent_upper_bound':2*math.exp(-2*100*.49**2),'action':'reject application; independent premise false'})
    check('constant-range',radius(1,0,.05)==0,{'radius':0})
    bad=0
    for params in [(0,1,.05),(1,-1,.05),(1,1,0),(True,1,.05)]:
        try: radius(*params)
        except ValueError: bad+=1
    check('invalid-parameters',bad==4,{'rejected':bad})
    check('large-n-log-stability',math.isfinite(radius(10**100,2,1e-200,True)),{'n':'10^100','delta':'1e-200'})
    store=KnowledgeStore('knowledge');refs=store.get('math.alpha-spending-stopping')['knowledge_refs']
    check('dependency-pinned',len(refs)==2,{'refs':refs})
    out.update(seconds=time.perf_counter()-started,model_calls=0,tokens=None,formal_verification=False)
    Path(__file__).with_name('checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'checks':len(out['checks']),'seconds':out['seconds'],'dp':dp},indent=2))
if __name__=='__main__': main()
