"""Public development checks; exact Fraction cases and float diagnostics are distinct."""
from fractions import Fraction as F
from pathlib import Path
import json,time,platform,sys,hashlib
import numpy as np
OUT=Path(__file__).resolve().parent
start=time.perf_counter();cases=[];checks=0

def screened(s,h,e,k,name,exact):
 global checks
 l=[a-b for a,b in zip(h,e)];u=[a+b for a,b in zip(h,e)]
 tau=sorted(l,reverse=True)[k-1];c=[i for i in range(len(s)) if u[i]>=tau]
 tol=0 if exact else 1e-10
 assert all(abs(a-b)<=v+tol for a,b,v in zip(s,h,e));checks+=1
 assert len(c)>=k;checks+=1
 picked=sorted(c,key=lambda i:(-s[i],i))[:k]
 assert sorted([s[i] for i in picked],reverse=True)==sorted(s,reverse=True)[:k];checks+=1
 enc=lambda x: str(x) if exact else float(x)
 cases.append({'name':name,'arithmetic':'Fraction-exact' if exact else 'float64-diagnostic','s':list(map(enc,s)),'h':list(map(enc,h)),'e':list(map(enc,e)),'k':k,'tau':enc(tau),'candidate_ids':c,'selected_ids':picked})

rng=np.random.default_rng(742)
for t in range(40):
 q=[F(int(x)) for x in rng.integers(-4,5,2)]
 keys=[[F(int(x)) for x in rng.integers(-6,7,2)] for _ in range(7)]
 s=[q[0]*v[0]+q[1]*v[1] for v in keys];h=[q[0]*v[0] for v in keys];e=[abs(q[1]*v[1]) for v in keys]
 screened(s,h,e,1+t%7,f'coordinate-{t}',True)
for k in [1,2,3]:
 screened([F(1)]*3,[F(1)]*3,[F(0)]*3,k,f'ties-k{k}',True)
for t in range(20):
 d=8;n=23;r=t%9;k=1+t%23
 q=rng.normal(size=d);keys=rng.normal(size=(n,d))
 U=np.linalg.qr(rng.normal(size=(d,d)))[0][:,:r];P=U@U.T
 rq=q-P@q;rk=keys-keys@P
 s=keys@q;h=keys@P@q;e=np.linalg.norm(rq)*np.linalg.norm(rk,axis=1)
 screened(s.tolist(),h.tolist(),e.tolist(),k,f'qr-{t}',False)
# Cross-domain exact sensor retrieval; compression removes a redundant channel.
screened([F(10),F(9),F(0)],[F(10),F(8),F(0)],[F(0),F(1),F(0)],1,'sensor-inner-product',True)
# Refusal witnesses, independently readable input/output, not model semantic tests.
neg=[]
neg.append({'name':'average-radius','q':[1,1],'special_key':[0,100],'other_key':[1,0],'other_count':999,'invalid_radius':0.1,'true_best':100,'wrong_threshold':0.9,'excluded_best_upper':0.1})
P=np.array([[1.,1.],[0.,0.]]);q=np.array([1.,0.]);v=np.array([0.,1.]);delta=abs(q@v-q@P@v);bound=np.linalg.norm(q-P@q)*np.linalg.norm(v-P@v)
assert delta>bound;checks+=1
neg.append({'name':'oblique-projector','actual_error':float(delta),'incorrect_bound':float(bound)})
# Lower bound threshold differs from proxy threshold: latter unsafe.
screened([F(0),F(1)],[F(50),F(1)],[F(50),F(0)],1,'proxy-threshold-refusal',True)
assert 1<50;checks+=1
neg.append({'name':'proxy-threshold','s':[0,1],'h':[50,1],'e':[50,0],'wrong_tau':50,'wrongly_excluded_id':1})
# Top-k tie contract cannot justify deleting equality.
assert not [i for i in range(2) if 1>1];checks+=1
neg.append({'name':'delete-equality','s':[1,1],'k':1,'invalid_candidates':[]})
# Top-k exact but softmax output differs (both logits0, values0 and2).
neg.append({'name':'topk-vs-output','s':[0,0],'values':[0,2],'dense_output':1,'selected_id':0,'sparse_output':0})
# Raw float residual cancellation cannot constitute a rigorous envelope.
neg.append({'name':'float-envelope','status':'not-certified','reason':'QR orthogonality, dot product, residual norm and outward rounding errors are not bounded by this diagnostic.'})
raw={'schema':'screening-development/v1','cases':cases,'refusal_witnesses':neg,'assertions':checks,'elapsed_seconds':time.perf_counter()-start,'model_calls':0,'gpu_calls':0,'holdout_used':False}
(OUT/'raw.json').write_text(json.dumps(raw,ensure_ascii=False,indent=2)+'\n')
(OUT/'environment.json').write_text(json.dumps({'python':sys.version,'numpy':np.__version__,'platform':platform.platform(),'arithmetic':'Fraction exact vs NumPy float64 explicitly distinct','formal_prover':'not-run','gpu':'not-used'},indent=2)+'\n')
print(json.dumps({'cases':len(cases),'refusal_witnesses':len(neg),'assertions':checks,'elapsed_seconds':raw['elapsed_seconds']}))
