"""Finite CPU development checks; no general/formal proof or production claim."""
from pathlib import Path
import json, math, hashlib
from fractions import Fraction as F
from decimal import Decimal, localcontext

HERE=Path(__file__).resolve().parent

def boundary(v,rho,delta):
    if not all(math.isfinite(x) for x in (v,rho,delta)) or v<0 or rho<=0 or not 0<delta<1:
        raise ValueError('outside finite scalar domain')
    return math.sqrt((v+rho)*(2*math.log(1/delta)+math.log1p(v/rho)))

def log_m(s,v,rho):
    return s*s/(2*(v+rho))-math.log1p(v/rho)/2

def run():
    checks=[]
    def record(name,**data):checks.append(dict(name=name,passed=True,**data))
    for v,rho,delta in [(0,1,.05),(4,1,.05),(20,3,.1),(1e-8,2,.01)]:
        b=boundary(v,rho,delta)
        assert math.isclose(log_m(b,v,rho),math.log(1/delta),rel_tol=1e-12)
        with localcontext() as ctx:
            ctx.prec=70
            V,R,A=map(lambda x:Decimal(str(x)),(v,rho,delta))
            exact=((V+R)*(-2*A.ln()+(1+V/R).ln())).sqrt()
            assert abs(Decimal(str(b))-exact)<Decimal('1e-12')
        record('boundary-inversion',v=v,rho=rho,delta=delta,b=b,decimal_reference=str(exact))
    # Independent numerical Gaussian integral with a bounded quadrature tail.
    for s,v,rho in [(0,0,1),(2,3,2),(-3,5,.5)]:
        center=s/(v+rho);sd=1/math.sqrt(v+rho);steps=12000
        lo=center-12*sd;hi=center+12*sd;h=(hi-lo)/steps
        def integrand(x):return math.sqrt(rho/(2*math.pi))*math.exp(x*s-(v+rho)*x*x/2)
        integral=h/3*(integrand(lo)+integrand(hi)+sum((4 if i%2 else 2)*integrand(lo+i*h) for i in range(1,steps)))
        closed=math.exp(log_m(s,v,rho));assert abs(integral/closed-1)<2e-12
        record('gaussian-square-completion',s=s,v=v,rho=rho,quadrature=integral,closed=closed,relative_tail_bound=2*math.exp(-72))
    # Actual predictable amplitudes on every branch; exact path mass and moments.
    states={(F(0),F(0),False):F(1)};rho=F(1,4);delta=.4
    largest_conditional_ratio=0
    for t in range(1,13):
        nxt={}
        for (s,v,crossed),p in states.items():
            a=F(1) if s<=0 else F(1,2)
            vals=[]
            for z in [-1,1]:
                ns,nv=s+a*z,v+a*a
                hit=crossed or abs(float(ns))>=boundary(float(nv),float(rho),delta)
                key=ns,nv,hit;nxt[key]=nxt.get(key,F(0))+p/2
                vals.append(math.exp(log_m(float(ns),float(nv),float(rho))))
            ratio=(sum(vals)/2)/math.exp(log_m(float(s),float(v),float(rho)))
            largest_conditional_ratio=max(largest_conditional_ratio,ratio)
            assert ratio<=1+1e-12
        states=nxt
    cross=sum(p for (s,v,c),p in states.items() if c)
    expectation=sum(float(p)*math.exp(log_m(float(s),float(v),float(rho))) for (s,v,c),p in states.items())
    assert float(cross)<=delta and expectation<=1+1e-12
    record('predictable-amplitude-tree',steps=12,rho=str(rho),delta=delta,crossing_exact=str(cross),crossing=float(cross),expectation=expectation,max_conditional_ratio=largest_conditional_ratio)
    # Longer iid walk, exact integer first-crossing path counts; float boundary
    # is separately checked to lie well away from lattice values.
    alive={0:1};crossed=0;min_gap=math.inf;rho=1;delta=.05
    for n in range(1,257):
        b=boundary(n,rho,delta);min_gap=min(min_gap,abs(b-round(b)))
        nxt={};new=0
        for s,count in alive.items():
            for ns in [s-1,s+1]:
                if abs(ns)>=b:new+=count
                else:nxt[ns]=nxt.get(ns,0)+count
        crossed=crossed*2+new;alive=nxt
        assert sum(alive.values())+crossed==2**n
    prob=F(crossed,2**256);assert float(prob)<=delta and min_gap>1e-6
    record('iid-first-crossing',n=256,probability_exact=str(prob),probability=float(prob),delta=delta,min_lattice_gap=min_gap)
    for v in [0,.1,4,100]:
        assert math.isclose(boundary(9*v,9,.05),3*boundary(v,1,.05),rel_tol=1e-14)
    record('unit-rescaling',scale=3)
    b=boundary(1,1,.05);p=F(1,16);mgf=(15+math.cosh(4))/16
    assert 4>b and p>F(1,20) and mgf>math.exp(.5)
    record('reject-variance-only',variance=1,boundary=b,actual_tail=str(p),mgf_lambda1=mgf,false_mgf_upper=math.exp(.5))
    b=boundary(0,.01,.05);assert 1>b
    record('reject-empirical-zero',boundary=b,actual_tail=1)
    b=boundary(100,1,.05);assert 100>b
    record('reject-marginal-only-repeated-sign',n=100,boundary=b,actual_tail=1)
    rejected=0
    for args in [(-1,1,.05),(1,0,.05),(1,1,0),(1,1,1),(math.nan,1,.05),(1,math.inf,.05)]:
        try:boundary(*args)
        except ValueError:rejected+=1
    assert rejected==6;record('invalid-domain',rejected=rejected)
    out=dict(scope='finite synthetic CPU checks; algebraic derivation separately independently reviewed; no formal proof/model result',checks=checks,passed=True,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (HERE/'checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'checks':len(checks),'passed':True,'iid_crossing':float(prob)}))

if __name__=='__main__':run()
