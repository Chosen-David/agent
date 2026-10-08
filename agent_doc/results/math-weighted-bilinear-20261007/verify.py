"""Finite product-law verification; no model or GPU performance evaluation."""
import json,time,platform,sys,itertools
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent
cfg=json.loads((D/'config.json').read_text());rng=np.random.default_rng(cfg['seed'])
start=time.perf_counter();rows=[];checks=0

def root(S):
    vals,U=np.linalg.eigh(S)
    if vals.min()<=0: raise ValueError('SPD required; do not silently regularize')
    return (U*np.sqrt(vals))@U.T

def fit(Sq,Sk,H,r):
    m,n=H.shape
    if not isinstance(r,int) or r<0 or r>min(m,n): raise ValueError('invalid rank')
    L=root(Sq);R=root(Sk);C=L@H@R
    U,s,Vt=np.linalg.svd(C,full_matrices=False)
    Cr=(U[:,:r]*s[:r])@Vt[:r]
    M=np.linalg.solve(L,Cr);M=np.linalg.solve(R.T,M.T).T
    A=(np.sqrt(s[:r])[:,None]*U[:,:r].T)@np.linalg.solve(L,np.eye(m))
    B=(np.sqrt(s[:r])[:,None]*Vt[:r])@np.linalg.solve(R,np.eye(n))
    return M,A,B,float(np.sum(s[r:]**2))

def product_loss(Sq,Sk,E):
    m,n=E.shape
    # 2m and 2n equally weighted atoms independently realize uncentered moments.
    Q=np.concatenate([root(Sq).T,-root(Sq).T])*np.sqrt(m)
    K=np.concatenate([root(Sk).T,-root(Sk).T])*np.sqrt(n)
    return float(np.mean((Q@E@K.T)**2))

for t in range(cfg['random_trials']):
    for m,n in [(3,3),(3,2)]:
        F=rng.normal(size=(m,m));G=rng.normal(size=(n,n))
        Sq=F@F.T+np.eye(m)*.5;Sk=G@G.T+np.eye(n)*.5;H=rng.normal(size=(m,n))
        for rank in range(min(m,n)+1):
            M,A,B,tail=fit(Sq,Sk,H,rank);E=H-M
            risk=product_loss(Sq,Sk,E);trace=float(np.trace(E@Sk@E.T@Sq))
            assert abs(risk-trace)<cfg['tolerance']
            assert abs(risk-tail)<cfg['tolerance']
            assert np.linalg.norm(A.T@B-M)<cfg['tolerance']
            assert np.linalg.matrix_rank(M,tol=1e-8)<=rank
            checks+=4
            gaps=[]
            for _ in range(8):
                candidate=rng.normal(size=(m,rank))@rng.normal(size=(rank,n))
                gap=product_loss(Sq,Sk,H-candidate)-risk
                assert gap>=-cfg['tolerance'];gaps.append(gap);checks+=1
            rows.append({'trial':t,'shape':[m,n],'rank':rank,'product_risk':risk,'trace_risk':trace,'svd_tail':tail,'minimum_sampled_candidate_gap':min(gaps)})
Sq=np.diag([.01,100]);Sk=np.diag([100,1]);M,A,B,tail=fit(Sq,Sk,np.eye(2),1)
key_pca=np.diag([1,0]);pca=product_loss(Sq,Sk,np.eye(2)-key_pca)
assert abs(tail-1)<1e-10 and abs(pca-100)<1e-10;checks+=2
# Independence violation explicitly checked; scalar product formula predicts 1, actual paired risk 2.
x=np.array([-np.sqrt(2),0,np.sqrt(2)]);p=np.array([.25,.5,.25]);paired=float(p@x**4);pred=float(p@x**2)**2
assert abs(paired-2)<1e-10 and abs(pred-1)<1e-10;checks+=2
# Nonzero means and zero covariance are not interchangeable.
assert (2*3)**2==36 and (2**2)*(3**2)==36;checks+=1
for sq,sk,h,r in [(np.diag([1,0]),np.eye(2),np.eye(2),1),(np.diag([1,-1]),np.eye(2),np.eye(2),1),(np.eye(2),np.eye(2),np.eye(2),-1),(np.eye(2),np.eye(2),np.eye(2),3)]:
    try: fit(sq,sk,h,r)
    except ValueError: checks+=1
    else: raise AssertionError('must refuse outside declared interface')
M,_,_,_=fit(np.array([[4.,1.],[1.,1.]]),np.diag([9.,1.]),np.eye(2),1)
assert np.linalg.norm(M-M.T)>1e-3;checks+=1
raw={'records':rows,'counterexamples':{'key_pca_score_risk':pca,'weighted_score_risk':tail,'dependent_actual_risk':paired,'dependent_factorized_prediction':pred,'nonzero_mean_risk':36,'nonsymmetry_norm':float(np.linalg.norm(M-M.T))}}
(D/'raw.json').write_text(json.dumps(raw,indent=2)+'\n')
summary={'finite_assertions':checks,'finite_records':len(rows),'duration_seconds':time.perf_counter()-start,'model_calls':0,'token_cost':'unknown for host orchestration; no model A/B; separate local encoder estimate only','general_proof':'displayed algebra, not numerical certification','unseen_tests':'not-run; all cases public development','scope':cfg['scope']}
(D/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
(D/'environment.json').write_text(json.dumps({'python':sys.version,'numpy':np.__version__,'platform':platform.platform(),'hardware':'CPU only','dtype':'float64'},indent=2)+'\n')
print(json.dumps(summary))
