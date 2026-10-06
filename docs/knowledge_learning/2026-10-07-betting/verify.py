"""Finite rational verification and authored transfer; not formal or model evaluation."""
from fractions import Fraction as F
from pathlib import Path
import json, math, time
from agent_runtime.knowledge import KnowledgeStore

def bet(history, mode):
    if mode=='fixed': return F(1)
    if mode=='negative': return F(-1)
    if mode=='zero': return F(0)
    return 2*(sum(history)/len(history)-F(1,2)) if history else F(0)

def enumerate_paths(n, mode, dependent=False):
    rows=[((),F(1),F(1),False)]; expectations=[]
    for t in range(1,n+1):
        nxt=[]
        for history,weight,wealth,crossed in rows:
            outcomes=(F(1,4),F(3,4)) if dependent and history and history[-1]>F(1,2) else (F(0),F(1))
            assert sum(outcomes)/2==F(1,2)
            lam=bet(history,mode)
            assert -2<=lam<=2
            for x in outcomes:
                w=wealth*(1+lam*(x-F(1,2)))
                assert w>=0
                nxt.append((history+(x,),weight/2,w,crossed or w>=20))
        rows=nxt
        expectations.append(sum(p*w for _,p,w,_ in rows))
    return expectations,sum(p for _,p,_,c in rows if c),sum(p for _,p,_,_ in rows)

def crossing(nmax,p,rule):
    live=[1.];rejected=0.
    for n in range(1,nmax+1):
        nxt=[0.]*(n+1)
        for k,mass in enumerate(live):
            nxt[k]+=mass*(1-p);nxt[k+1]+=mass*p
        for k,mass in enumerate(nxt):
            if rule=='betting':
                hit=k*math.log(1.5)+(n-k)*math.log(.5)>=math.log(20)
            else:
                radius=math.sqrt((math.log(40)+math.log(n)+math.log(n+1))/(2*n))
                hit=k/n-radius>.5
            if hit: rejected+=mass;nxt[k]=0.
        live=nxt
    assert abs(rejected+sum(live)-1)<1e-12
    return rejected

def logwealth(xs,lam=1):
    total=0.
    for x in xs:
        if not 0<=x<=1 or not -2<=lam<=2: raise ValueError('unsupported input or bet')
        increment=lam*(x-.5)
        if increment==-1: return -math.inf
        total+=math.log1p(increment)
    return total

def main():
    started=time.perf_counter();checks=[]
    def check(name,ok,data):
        assert ok,name
        checks.append({'name':name,'pass':True,'data':data})
    for mode,dep in [('fixed',False),('adaptive',False),('adaptive',True),('zero',False)]:
        means,prob,mass=enumerate_paths(10,mode,dep)
        check('exact-paths-'+mode+('-dependent' if dep else ''),all(v==1 for v in means) and prob<=F(1,20) and mass==1,{'paths':1024,'expected_wealth':'1 at every t','crossing_probability':str(prob),'dependent':dep})
    cheat_n=8;cheat_w=F(3,2)**cheat_n
    check('current-result-leak-counterexample',cheat_w>20,{'n':8,'wealth':str(cheat_w),'false_rejection_probability':1,'premise_failure':'bet uses current observation'})
    check('marginal-not-conditional-counterexample',F(1,2)>F(1,20),{'repeated_Z_n':8,'false_rejection_probability':'.5','premise_failure':'conditional mean changes after observing Z'})
    check('one-step-mixture-not-posthoc-max',F(3,2)>1,{'predeclared_equal_mixture_expected':1,'posthoc_max_expected':'3/2','conclusion':'max is not generally a test supermartingale'})
    check('wealth-zero-absorbing',logwealth([0,1],2)==-math.inf,{'log_wealth':'-Infinity','do_not_add_epsilon':True})
    xs=[1,0,1,1,.25];ys=[10+20*x for x in xs]
    w1=logwealth(xs);w2=logwealth([(y-10)/20 for y in ys])
    check('sensor-affine-units',w1==w2,{'known_range':[10,30],'null_mean':20,'log_wealth':w1,'same_dimensionless_result':True})
    check('log-stability',math.isfinite(logwealth([1]*2000)),{'log_wealth':logwealth([1]*2000),'direct_product_overflows':True})
    rejected=0
    for xs,lam in [([1.1],1),([.5],3)]:
        try:logwealth(xs,lam)
        except ValueError:rejected+=1
    check('invalid-inputs',rejected==2,{'rejected':rejected})
    comparison=[]
    for p in (.5,.65):
        for rule in ('betting','alpha-spending'):
            q=crossing(200,p,rule)
            comparison.append({'p':p,'N':200,'rule':rule,'rejection_probability':q})
            if p==.5:check('null-risk-'+rule,q<=.05,comparison[-1])
    store=KnowledgeStore('knowledge');refs=store.get('math.betting-test-martingale')['knowledge_refs']
    check('real-knowledge-refs',len(refs)==1,{'refs':refs})
    out={'scope':'Authored finite numerical/structure checks; no independent LLM applicability test','checks':checks,'comparison':comparison,'seconds':time.perf_counter()-started,'model_calls':0,'tokens':None,'formal_verification':False,'runtime_production_changes':False}
    Path(__file__).with_name('checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'checks':len(checks),'seconds':out['seconds'],'comparison':comparison},indent=2))
if __name__=='__main__':main()
