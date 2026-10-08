"""Independent overlap-TV and Decimal-KL reference; does not alter producer files."""
import sys
sys.dont_write_bytecode = True
import argparse
import collections
import decimal
import gzip
import hashlib
import importlib.util
import json
import math
import platform
import subprocess
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--v2',action='store_true');args=parser.parse_args()
suffix='_v2' if args.v2 else ''
D = decimal.Decimal
decimal.getcontext().prec = 80
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
manifest_path = BASE/('manifest.json' if args.v2 else 'manifest_v1.json')
manifest = json.loads(manifest_path.read_text())
hashes = {}
binding_mismatches = []
for refs in manifest['artifacts'].values():
    for ref in refs:
        actual = digest(ROOT/ref['path'])
        if actual != ref['sha256']:
            binding_mismatches.append({'path':ref['path'],'expected':ref['sha256'],'actual':actual})
            assert ref['path'].endswith('/validation_plan.json')
            assert digest(BASE/'validation_plan_v2.json')==ref['sha256']
        hashes[ref['path']] = actual
manifest_hash = digest(manifest_path)
raw = json.loads(gzip.decompress((BASE/f'raw_cases{suffix}.json.gz').read_bytes()))
producer_raw = json.loads((BASE/f'validation_results{suffix}_raw_cases.json').read_text())
rerun_raw = json.loads((BASE/f'independent_results{suffix}_raw_cases.json').read_text())
assert raw == producer_raw == rerun_raw
summary = json.loads((BASE/f'validation_results{suffix}.json').read_text())
rerun = json.loads((BASE/f'independent_results{suffix}.json').read_text())
counts = dict(collections.Counter(r['kind'] for r in raw))
assert len(raw) == summary['case_count'] == rerun['case_count'] == 1731
assert counts == summary['counts'] == rerun['counts']
assert summary['max_float_absolute_error'] == rerun['max_float_absolute_error']
vectors = [(Fraction(i,4), Fraction(j,4), Fraction(4-i-j,4))
           for i in range(5) for j in range(5-i)]
# Match frozen IDs but independently enumerate using two coordinates.
assert len(vectors) == 15
def overlap_tv(p, q):
    assert len(p) == len(q) and sum(p) == sum(q) == 1
    return 1-sum(min(x,y) for x,y in zip(p,q))
def restricted(p, event):
    mass = sum(p[i] for i in event)
    assert mass > 0
    return tuple(p[i]/mass for i in event)
def dec(x):
    return D(x.numerator)/D(x.denominator)
def reference_kl(p,q):
    assert len(p)==len(q)
    if any(x>0 and y==0 for x,y in zip(p,q)):
        return D('Infinity')
    return sum((dec(x)*(dec(x)/dec(y)).ln() for x,y in zip(p,q) if x),D(0))
spec=importlib.util.spec_from_file_location('conditioning_producer', BASE/'verify_conditioning_by_gpt.py')
producer=importlib.util.module_from_spec(spec)
spec.loader.exec_module(producer)
maximum=0.0
seen_tv=set(); seen_kl=set(); tv_checked=0; kl_checked=0
for record in raw:
    kind=record['kind']
    if kind in ('exact_tv','zero_event_refusal'):
        pi,qi,event=record['p'],record['q'],tuple(record['event'])
        key=(pi,qi,event)
        assert key not in seen_tv
        seen_tv.add(key)
        p,q=vectors[pi],vectors[qi]
        a,b=sum(p[i] for i in event),sum(q[i] for i in event)
        if kind=='zero_event_refusal':
            assert a==0 or b==0
        else:
            actual=overlap_tv(restricted(p,event),restricted(q,event))
            delta=overlap_tv(p,q)
            bound=min(Fraction(1),delta/max(a,b))
            assert actual<=bound
            for name,value in [('delta',delta),('a',a),('b',b),('actual',actual),('bound',bound)]:
                assert Fraction(record[name])==value
            tv_checked+=1
    elif kind in ('kl_decomposition','projection_minimum','forward_kl_infinite'):
        p=vectors[record['p']]; event=tuple(record['event'])
        a=sum(p[i] for i in event)
        pc=tuple(p[i]/a if i in event else Fraction(0) for i in range(3))
        if kind=='forward_kl_infinite':
            assert reference_kl(p,pc).is_infinite()
        else:
            q=vectors[record['q']] if kind=='kl_decomposition' else pc
            lhs=reference_kl(q,p)
            rhs=reference_kl(q,pc)-dec(a).ln()
            assert abs(lhs-rhs)<D('1e-75')
            err=abs(producer.kl(q,p)-float(lhs))
            maximum=max(maximum,err)
            assert err <= 1e-12
            if kind=='kl_decomposition':
                key=(record['p'],record['q'],event)
                assert key not in seen_kl
                seen_kl.add(key)
            kl_checked+=1
    elif kind=='stable_normalizer':
        weights=[D(str(x)).exp() for x in record['logits']]
        expected=sum(weights[i] for i in record['event'])/sum(weights)
        err=abs(record['mass']-float(expected))
        maximum=max(maximum,err)
        assert err<=1e-12
assert len(seen_tv)==15*15*7
assert len(seen_kl)==99
# A finer sum-six grid, independently using overlap rather than L1 absolute sums.
finer=[(Fraction(i,6),Fraction(j,6),Fraction(6-i-j,6)) for i in range(7) for j in range(7-i)]
extra_tv=0
for p in finer:
    for q in finer:
        for event in [(0,),(1,),(2,),(0,1),(0,2),(1,2),(0,1,2)]:
            a,b=sum(p[i] for i in event),sum(q[i] for i in event)
            if a and b:
                assert overlap_tv(restricted(p,event),restricted(q,event))<=min(1,overlap_tv(p,q)/max(a,b))
                extra_tv+=1
# Sharpness, unequal masses, zeros and probabilities with far subnormal event mass.
for eps in [Fraction(1,10),Fraction(1,10**20),Fraction(1,10**400)]:
    p=(eps,0,1-eps);q=(0,eps,1-eps)
    assert overlap_tv(restricted(p,(0,1)),restricted(q,(0,1)))==1
    assert overlap_tv(p,q)==eps
p=(Fraction(1,2),Fraction(1,3),Fraction(1,6)); event=(0,1)
assert producer.condition(p,event)==(Fraction(3,5),Fraction(2,5),0)
assert math.isinf(producer.kl(p,producer.condition(p,event)))
assert reference_kl((Fraction(1),0),(0,Fraction(1))).is_infinite()
assert producer.kl((0,Fraction(1)),(0,Fraction(1)))==0
for p,event in [((Fraction(1),),()),((Fraction(1),),(0,0)),((Fraction(1),),(1,)),((Fraction(-1),Fraction(2)),(0,)),((Fraction(1,2),),(0,)),((),()),((0,Fraction(1)),(0,)),((Fraction(1),),(-1,))]:
    try: producer.condition(p,event)
    except ValueError: pass
    else: raise AssertionError((p,event))
c=(Fraction(4,5),Fraction(1,5))
for mass in [Fraction(1,10),Fraction(9,10)]:
    p=(mass*c[0],mass*c[1],1-mass)
    assert restricted(p,(0,1))==c
    assert p[0]==mass*c[0]
far=float(D(1)/(D(1)+D(20).exp()))
assert abs(producer.mass_from_logs(0,20)-far)<1e-24
assert producer.mass_from_logs(-1000,1000)==0.0
assert producer.mass_from_logs(1000,-1000)==1.0
for name in ['exact_violations','max_float_absolute_error','elapsed_seconds']:
    assert math.isfinite(summary[name])
raw_max=max(r.get('error',0.0) for r in raw)
assert raw_max==summary['max_float_absolute_error']
# Read-only corpus validation; the card's current ID is resolved rather than a guessed filename.
commands=[['python','-m','agent_runtime.knowledge','--root','knowledge','validate'],
          ['python','-m','agent_runtime.knowledge','--root','knowledge','show','math.support-conditioning','--include-unpublished']]
knowledge=[]
for command in commands:
    result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
    assert result.returncode==0, result.stdout+result.stderr
    knowledge.append({'command':command,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
card=json.loads(knowledge[-1]['stdout'])
assert card['content']==(ROOT/'knowledge/entries/math.support-conditioning.md').read_text()
command=commands[-1]+['--version','1','--sha256',card['sha256']]
result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
assert result.returncode==0
knowledge.append({'command':command,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
refs_path=BASE/f'independent_results{suffix}_knowledge_refs.json'
refs_path.write_text(json.dumps({'knowledge_refs':card['knowledge_refs']},indent=2)+'\n')
command=['python','-m','agent_runtime.knowledge','--root','knowledge','check-refs',str(refs_path)]
result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
# Current candidate cannot pass published-only refs; canonical show has pinned live ID/version/hash.
knowledge.append({'command':command,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'interpretation':'candidate status prevents published-only consumption until publication'})
assert digest(manifest_path)==manifest_hash
for path,sha in hashes.items(): assert digest(ROOT/path)==sha
result={'status':'independent-reference-passed','manifest_sha256':manifest_hash,
        'binding_mismatches':binding_mismatches,
        'artifact_hashes':hashes,'raw_count':len(raw),'counts':counts,
        'gzip_and_uncompressed_and_rerun_records_identical':True,
        'independent_exact_tv_records':tv_checked,'independent_decimal_kl_records':kl_checked,
        'additional_sum6_exact_tv_cases':extra_tv,'max_decimal_reference_float_error':maximum,
        'knowledge_checks':knowledge,'python':sys.version,'platform':platform.platform(),
        'method':'Exact overlap-TV; Decimal precision80 KL/normalizer; full raw record replay; code import boundary checks',
        'limitations':['Public development cases, no held-out model validation','No formal proof or model/GPU improvement','Direct host independent review, not authenticated Engine runtime']}
(BASE/f'independent_results{suffix}_reference.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('knowledge_checks','artifact_hashes')},indent=2))
