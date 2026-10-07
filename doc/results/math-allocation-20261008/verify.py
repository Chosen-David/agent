"""Public finite exact-arithmetic developer fixtures, not a production solver."""
import argparse,itertools,json,random,sys,platform,time
from pathlib import Path
from fractions import Fraction as F

def dp(menus,B):
    # D_i(b): best loss at cost AT MOST b; tie-breaking stable and explicit.
    prev=[(0,()) for b in range(B+1)]
    for menu in menus:
        nxt=[]
        for b in range(B+1):
            candidates=[(prev[b-c][0]+e,prev[b-c][1]+(j,)) for j,(c,e) in enumerate(menu) if c<=b and prev[b-c] is not None]
            nxt.append(min(candidates) if candidates else None)
        prev=nxt
    return prev[B]

def enumerate_opt(menus,B):
    candidates=[]
    for js in itertools.product(*(range(len(x)) for x in menus)):
        cost=sum(menus[i][j][0] for i,j in enumerate(js))
        if cost<=B: candidates.append((sum(menus[i][j][1] for i,j in enumerate(js)),js))
    return min(candidates) if candidates else None

def dual(menus,B,lam): return sum(min(F(e)+lam*c for c,e in m) for m in menus)-lam*B

def main(out):
    source=Path(__file__).parent; cfg=json.loads((source/'config.json').read_text());out.mkdir(parents=True,exist_ok=True)
    rng=random.Random(cfg['seed']); rows=[];assertions=0;t=time.perf_counter()
    menusets=[[[tuple(rng.randint(*cfg[k]) for k in ('cost_range','loss_range')) for _ in range(rng.randint(1,cfg['max_options']))] for _ in range(cfg['groups'])] for _ in range(cfg['random_instances'])]
    menusets += [[[(0,5),(2,4),(3,0)]],[[(0,2),(0,2)],[(0,3)]],[[(3,0)],[(4,0)]],[]]
    for i,menus in enumerate(menusets):
        for B in cfg['budgets']:
            a=dp(menus,B);b=enumerate_opt(menus,B);assert a==b;assertions+=1
            lbs={x:str(dual(menus,B,F(x))) for x in cfg['lambda_grid']}
            if a is not None:
                e,js=a;cost=sum(menus[l][j][0] for l,j in enumerate(js));assert cost<=B;assertions+=1
                for x in cfg['lambda_grid']: assert dual(menus,B,F(x))<=e;assertions+=1
            rows.append({'case':i,'menus':menus,'budget':B,'opt':a,'lower_bounds':lbs})
    # Unsupported nondominated point: never Lagrange-minimal, even at ties.
    # middle≤first => lambda≤1/2; middle≤last => lambda≥4.
    assert F(1,2)<4;assertions+=1
    m=[[(0,5),(2,4),(3,0)]]
    assert dp(m,2)[0]==4 and dual(m,2,F(5,3))==F(5,3);assertions+=1
    # conservative rounding: originals expressed as exact fractions, feasibility only.
    rounding=[]
    for costs in itertools.product([F(0),F(1,3),F(2,3),F(1)],repeat=3):
        h=F(1,2);B=F(5,3);rounded=[-((-c/h).numerator//(-c/h).denominator) for c in costs];cap=(B/h).numerator//(B/h).denominator
        if sum(rounded)<=cap: assert sum(costs)<=B;assertions+=1
        rounding.append({'costs':[str(x) for x in costs],'rounded':rounded,'original_sum':str(sum(costs)),'rounded_feasible':sum(rounded)<=cap})
    # Coupling counterexample: frozen local additive loss ≠ joint true outcome.
    coupling={'menus':[[[1,1],[2,0]],[[1,1],[2,0]]],'budget':3,'joint_loss':{'00':0,'01':10,'10':10,'11':2}}
    surrogate=dp(coupling['menus'],3);key=''.join(map(str,surrogate[1]));assert coupling['joint_loss'][key]==10 and coupling['joint_loss']['00']==0;assertions+=1
    raw={'rows':rows,'rounding':rounding,'unsupported':{'integer_optimum':4,'best_dual':'5/3','gap':'7/3'},'coupling':coupling}
    (out/'raw.json').write_text(json.dumps(raw,ensure_ascii=False,separators=(',',':'))+'\n')
    (out/'summary.json').write_text(json.dumps({'instances':len(menusets),'budget_cases':len(rows),'rounding_cases':len(rounding),'assertions':assertions,'elapsed_seconds':time.perf_counter()-t,'scope':cfg['scope']},indent=2)+'\n')
    (out/'environment.json').write_text(json.dumps({'python':sys.version,'platform':platform.platform(),'arithmetic':'stdlib integers and fractions.Fraction','hardware':'host CPU; no GPU/model'},indent=2)+'\n')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=Path(__file__).parent);main(p.parse_args().out)
