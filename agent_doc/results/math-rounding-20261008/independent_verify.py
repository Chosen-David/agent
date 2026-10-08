"""Independent public arithmetic/data crosscheck; canonical evidence is read-only."""
import importlib.util, json, math, itertools, random, hashlib, tempfile, time
from fractions import Fraction as Q
from pathlib import Path
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
v=load('producer_arithmetic',BASE/'validate.py')
def exact(xs,ys):
 assert len(xs)==len(ys)
 return sum((Q(*x.as_integer_ratio())*Q(*y.as_integer_ratio()) for x,y in zip(xs,ys)),Q())
def contained(iv,z): return Q(*iv[0].as_integer_ratio())<=z<=Q(*iv[1].as_integer_ratio())
start=time.process_time(); tests=[]
def check(name,p):
 assert p,name; tests.append(name)
raw=json.loads((BASE/'raw.json').read_text())
for row in raw['dot_cases']:
 xs=list(map(float.fromhex,row['x'])); ys=list(map(float.fromhex,row['y'])); z=exact(xs,ys);iv=tuple(map(float.fromhex,row['interval']))
 check('raw:'+row['id'],z==Q(row['exact']) and contained(iv,z) and iv==v.dot_interval(xs,ys,ieee_assumed=True))
check('unique-dot-ids',len({r['id'] for r in raw['dot_cases']})==len(raw['dot_cases'])==103)
for row in raw['screening_cases']:
 q=list(map(float.fromhex,row['q']));keys=[list(map(float.fromhex,k)) for k in row['keys']]; zs=[exact(q,k) for k in keys];ivs=[tuple(map(float.fromhex,b)) for b in row['intervals']]
 cs,tau=v.safe_candidates(ivs,2);want=sorted(range(len(keys)),key=lambda i:(-zs[i],i))[:2]
 check('raw:'+row['id'],all(contained(b,z) for b,z in zip(ivs,zs)) and [str(z) for z in zs]==row['exact'] and cs==row['candidates'] and tau.hex()==row['tau'] and want==row['topk']==row['recovered'])
# Discriminatory new sign/subnormal/exponent patterns, independent of producer seed.
rng=random.Random(9137502);tiny=float.fromhex('0x0.0000000000001p-1022')
values=[0.0,-0.0,tiny,-tiny,2*tiny,-2*tiny,math.ldexp(1.0,-1022),-1.0,1.0,math.nextafter(1.0,math.inf),2.0**53,-2.0**53]
for i in range(800):
 xs=[rng.choice(values) for _ in range(rng.randrange(0,9))];ys=[rng.choice([-.5,.5,-1.,1.,2.**-53]) for _ in xs]
 check('new-dot-'+str(i),contained(v.dot_interval(xs,ys,ieee_assumed=True),exact(xs,ys)))
for a,b in itertools.product(values,repeat=2):
 check('scalar-add-'+a.hex()+b.hex(),contained(v.add((a,a),(b,b)),Q(*a.as_integer_ratio())+Q(*b.as_integer_ratio())))
# All coordinate subsets, including absent tail and zero max, then exact kth proof.
for q in [[tiny,-tiny,0.0],[1.,-1.,2.**-53],[0.,0.,0.]]:
 keys=[[1.,-1.,1.],[-1.,1.,-1.],[0.,0.,0.],[1.,-1.,1.]]
 for n in range(1,4):
  for selected in itertools.combinations(range(3),n):
   ivs=v.coarse_intervals(q,keys,selected,ieee_assumed=True);zs=[exact(q,k) for k in keys]
   check('coordinate-'+repr((q,selected)),all(contained(b,z) for b,z in zip(ivs,zs)))
   for k in range(1,5):
    cs,tau=v.safe_candidates(ivs,k);want=sorted(range(4),key=lambda i:(-zs[i],i))[:k]
    check('screen-'+repr((q,selected,k)),set(want)<=set(cs))
refusals=[]
for name,call in [('max-adjacent',lambda:v.expand(float.fromhex('0x1.fffffffffffffp+1023'))),('missing-premise',lambda:v.dot_interval([1.],[1.])),('bad-coordinate',lambda:v.coarse_intervals([1.],[[1.]],[True],ieee_assumed=True)),('empty-coordinate',lambda:v.coarse_intervals([1.],[[1.]],[],ieee_assumed=True)),('mismatch',lambda:v.dot_interval([1.],[] ,ieee_assumed=True)),('nonfloat',lambda:v.dot_interval([1],[1.],ieee_assumed=True)),('inf',lambda:v.dot_interval([math.inf],[0.],ieee_assumed=True))]:
 try:call()
 except ValueError:refusals.append(name)
 else:raise AssertionError(name)
check('gamma-subnormal-relative-model-fails',abs(Q(*tiny.as_integer_ratio())/2-Q())>Q(1,2**53)*(Q(*tiny.as_integer_ratio())/2))
check('sensor',exact([.125,.25,.5],[3.,-2.,1.])==Q(3,8))
check('strict-ties',v.safe_candidates([(1.,1.),(1.,1.),(0.,0.)],1)[0]==[0,1])
check('gpu-real-order-distinction',exact([2.**53,1.,-2.**53],[1.,1.,1.])==1 and v.naive([2.**53,1.,-2.**53],[1.,1.,1.])==0.)
# Reproduce frozen producer main only after relocating BASE; do not alter its evidence.
with tempfile.TemporaryDirectory() as scratch:
 v.BASE=Path(scratch);v.main(); regenerated=json.loads((v.BASE/'raw.json').read_text()); a=dict(raw);b=dict(regenerated);a.pop('diagnostic_elapsed_seconds');b.pop('diagnostic_elapsed_seconds');check('frozen-fixtures-reproduce',a==b)
 r=load('producer_retrieval',BASE/'retrieve.py');r.BASE=Path(scratch);(r.BASE/'retrieval_protocol.json').write_bytes((BASE/'retrieval_protocol.json').read_bytes());r.main();again=json.loads((r.BASE/'retrieval.json').read_text());old=json.loads((BASE/'retrieval.json').read_text())
 check('six-retrievals',len(again['records'])==6 and all(x['hit'] for x in again['records']))
 for x,y in zip(again['records'],old['records']):
  for field in ['backend','case','query','domain','expected_id','actual','hit','output_chars','output_bytes','result']:check('retrieval-'+x['case']+x['backend']+field,x[field]==y[field])
 check('context-reproduce',again['context']==old['context'])
report={'schema_version':'independent-dot-review-observations/v1','actor':'rounding_result_review','context':'actual separate child context /root/rounding_result_review; documentary provenance, no authenticated Engine backend','checks_passed':len(tests),'refusals':refusals,'tests':tests,'cpu_seconds':time.process_time()-start,'canonical_evidence_preserved':True,'scope':'conditional public CPU development fixtures only','limitations':['Finite sampled checks and informal induction do not constitute formal proof or platform certification','No GPU/model/token quality or speedup measurement','New disclosed cases are regression, never unseen model evaluation']}
(BASE/'independent_observations.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'independent_checks':len(tests),'refusals':refusals,'cpu_seconds':report['cpu_seconds']}))
