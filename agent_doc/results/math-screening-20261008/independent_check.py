"""Read-only producer replay and independent raw-data reference checking."""
from pathlib import Path
from fractions import Fraction as F
import json, hashlib, math, platform, sys
import numpy as np

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

manifest=json.loads((BASE/'manifest.json').read_text())
raw=json.loads((BASE/'raw.json').read_text())
before={a['path']:sha(ROOT/a['path']) for a in manifest['artifacts']}
assert all(before[a['path']]==a['sha256'] for a in manifest['artifacts'])
assert len(raw['cases'])==65 and len(raw['refusal_witnesses'])==6
assert len(set(c['name'] for c in raw['cases']))==65
assert raw['assertions']==65*3+3
assert raw['model_calls']==raw['gpu_calls']==0 and raw['holdout_used'] is False
rng=np.random.default_rng(742)
references={}
for t in range(40):
    q=[F(int(x)) for x in rng.integers(-4,5,2)]
    keys=[[F(int(x)) for x in rng.integers(-6,7,2)] for _ in range(7)]
    references[f'coordinate-{t}']=(
        [sum(a*b for a,b in zip(q,v)) for v in keys],
        [q[0]*v[0] for v in keys], [abs(q[1]*v[1]) for v in keys])
for k in [1,2,3]:
    references[f'ties-k{k}']=([F(1)]*3,[F(1)]*3,[F(0)]*3)
float_reference_max_error=0.0
for t in range(20):
    q=rng.normal(size=8); keys=rng.normal(size=(23,8))
    U=np.linalg.qr(rng.normal(size=(8,8)))[0][:,:t%9]
    # The input RNG/QR match is necessary provenance; scalar summation paths
    # below differ from producer matrix dot paths and are only diagnostics.
    pq=U@(U.T@q)
    pk=(keys@U)@U.T
    s=[math.fsum(float(a*b) for a,b in zip(q,v)) for v in keys]
    h=[math.fsum(float(a*b) for a,b in zip(pq,v)) for v in keys]
    e=[math.sqrt(math.fsum(float(a*a) for a in q-pq))*
       math.sqrt(math.fsum(float(a*a) for a in v-p)) for v,p in zip(keys,pk)]
    references[f'qr-{t}']=(s,h,e)
references['sensor-inner-product']=([F(10),F(9),F(0)], [F(10),F(8),F(0)], [F(0),F(1),F(0)])
references['proxy-threshold-refusal']=([F(0),F(1)],[F(50),F(1)],[F(50),F(0)])
exact_cases=float_cases=0
float_envelope_violations=[]
for case in raw['cases']:
    exact=case['arithmetic']=='Fraction-exact'
    conv=F if exact else float
    s,h,e=([conv(x) for x in case[name]] for name in ['s','h','e'])
    assert len(s)==len(h)==len(e) and 1<=case['k']<=len(s)
    assert all(x>=0 for x in e)
    if exact: exact_cases+=1
    else:
        float_cases+=1
        assert all(math.isfinite(x) for x in s+h+e)
    for values,ref in zip((s,h,e),references[case['name']]):
        if exact: assert values==ref
        else:
            error=max(abs(a-b) for a,b in zip(values,ref))
            float_reference_max_error=max(float_reference_max_error,error)
            assert error<1e-12 # comparison diagnostic, not an outward interval
    tau=sorted([a-b for a,b in zip(h,e)],reverse=True)[case['k']-1]
    assert tau==conv(case['tau'])
    keep=[i for i in range(len(s)) if h[i]+e[i]>=tau]
    assert keep==case['candidate_ids'] and len(keep)>=case['k']
    picked=sorted(keep,key=lambda i:(-s[i],i))[:case['k']]
    assert picked==case['selected_ids']
    assert picked==sorted(range(len(s)),key=lambda i:(-s[i],i))[:case['k']]
    gap=max(abs(a-b)-v for a,b,v in zip(s,h,e))
    if exact: assert gap<=0
    else:
        assert gap<=1e-10
        if gap>0: float_envelope_violations.append({'name':case['name'],'gap':gap})
# Verify producer's refusal facts, not merely their existence.
negative={c['name']:c for c in raw['refusal_witnesses']}
a=negative['average-radius']
assert F(100,1000)==F(str(a['invalid_radius']))
assert F(str(a['excluded_best_upper']))<F(str(a['wrong_threshold']))<F(a['true_best'])
assert negative['oblique-projector']['actual_error']==1 and negative['oblique-projector']['incorrect_bound']==0
p=negative['proxy-threshold']; assert p['h'][1]+p['e'][1]<p['wrong_tau'] and p['s'][1]>p['s'][0]
assert negative['delete-equality']['invalid_candidates']==[]
v=negative['topk-vs-output']; assert F(sum(v['values']),2)==v['dense_output'] and v['values'][v['selected_id']]==v['sparse_output']
assert negative['float-envelope']['status']=='not-certified'
after={p:sha(ROOT/p) for p in before}; assert after==before
out={'verdict':'pass-with-scope','producer_cases':65,'exact_cases':exact_cases,
     'float_diagnostic_cases':float_cases,'refusal_witnesses':6,'producer_assertions':198,
     'float_reference_max_error':float_reference_max_error,
     'raw_float_envelope_violations':float_envelope_violations,
     'manifest_sha256':sha(BASE/'manifest.json'),'artifact_hashes':before,
     'validation_plan_sha256':sha(BASE/'validation-plan.json'),
     'independent_script_sha256':sha(Path(__file__)),
     'environment':{'python':sys.version,'numpy':np.__version__,'platform':platform.platform()},
     'limitations':['Floating-point envelopes actually violate exact bounds in listed cases and are accepted only as explicitly non-certified diagnostics.',
                    'Sensor fixture is an algebraic inner-product example, not measured sensor retrieval data.',
                    'No timing comparison, holdout, model, GPU, formal prover, or managed ReviewSession/provider authentication.']}
(BASE/'independent_check_outputs.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['artifact_hashes','environment']},indent=2))
