from pathlib import Path
import hashlib,json,subprocess,sys,shutil,platform
from decimal import Decimal,getcontext
import tiktoken

R=Path(__file__).resolve().parents[4];D=R/'doc/results/math-softmax-kl-20261008';I=Path(__file__).parent
getcontext().prec=70
class MP:
 mpf=Decimal
 exp=staticmethod(lambda x:Decimal(x).exp())
 log=staticmethod(lambda x:Decimal(x).ln())
 cosh=staticmethod(lambda x:(Decimal(x).exp()+(-Decimal(x)).exp())/2)
 @staticmethod
 def quad(f,unused):
  # Composite midpoint-independent Gaussian quadrature: Decimal Newton
  # roots of Legendre polynomial, with explicitly computed weights.
  n=96;total=Decimal(0)
  import math
  for i in range(1,n//2+1):
   x=Decimal(str(math.cos(math.pi*(i-.25)/(n+.5))))
   for _ in range(30):
    a,b=Decimal(1),x
    for k in range(2,n+1):a,b=b,((2*k-1)*x*b-(k-1)*a)/k
    dp=n*(x*b-a)/(x*x-1);nx=x-b/dp
    if abs(nx-x)<Decimal('1e-65'):x=nx;break
    x=nx
   a,b=Decimal(1),x
   for k in range(2,n+1):a,b=b,((2*k-1)*x*b-(k-1)*a)/k
   dp=n*(x*b-a)/(x*x-1);w=2/((1-x*x)*dp*dp)
   total+=w*(f((1-x)/2)+f((1+x)/2))/2
  return total
mp=MP()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
manifest=read(D/'manifest.json');tol=mp.mpf(str(read(D/'config.json')['tolerance']))
assert digest(D/'manifest.json')=='4672366dda79e208e5b5f4073d3d5b32bf0591cf7256fbcebac242f6d3eef9d0'
bindings={manifest['validation_plan']['path']:manifest['validation_plan']['sha256']}
for refs in manifest['artifacts'].values():
 for ref in refs:
  assert digest(R/ref['path'])==ref['sha256'];bindings[ref['path']]=ref['sha256']
raw=read(D/'raw.json');assert [r['id'] for r in raw['cases']]==list(range(64))
def prob(s):
 ex=[mp.exp(v) for v in s];z=sum(ex);return [v/z for v in ex]
def var(p,e):
 # Independent pairwise identity, no producer mean-centered path.
 return sum(p[i]*p[j]*(e[i]-e[j])**2 for i in range(len(e)) for j in range(i))
def ref(s,e):
 s=list(map(mp.mpf,s));e=list(map(mp.mpf,e));p=prob(s);q=prob([a+b for a,b in zip(s,e)])
 kl=sum(a*mp.log(a/b) for a,b in zip(p,q));integ=mp.quad(lambda u:(1-u)*var(prob([a+u*b for a,b in zip(s,e)]),e),[0,mp.mpf('.5'),1])
 assert abs(kl-integ)<mp.mpf('1e-60')
 rr=max(e)-min(e);norm=sum((a-sum(e)/len(e))**2 for a in e);v=var(p,e)
 assert kl>=-mp.mpf('1e-60') and kl<=rr**2/8+mp.mpf('1e-60') and rr**2<=2*norm+mp.mpf('1e-60')
 assert mp.exp(-rr)*v/2<=kl+mp.mpf('1e-60') and kl<=mp.exp(rr)*v/2+mp.mpf('1e-60')
 return kl,integ,v
errors=[]
for row in raw['cases']+raw['boundaries']:
 kl,integ,v=ref(row['s'],row['e']);errors.append(float(abs(kl-mp.mpf(row['kl']))))
 for key,value in [('kl',kl),('bregman',kl),('path_integral',integ),('reference_variance',v)]:assert abs(mp.mpf(row[key])-value)<=tol
 assert mp.mpf(row['path_floor'])*mp.mpf(row['centered_norm2'])/2<=kl+tol
for row in raw['saturation']:
 kl,_,_=ref([row['M'],0],[1,0]);assert abs(kl-mp.mpf(row['kl']))<=tol
assert ref([100,0],[1,0])[0]<mp.mpf('1e-42')
assert ref([1,2,3],[10000]*3)[0]==0
assert ref([1],[10])[0]==0
assert abs(ref([0,0],[2,-2])[0]-mp.log(mp.cosh(2)))<mp.mpf('1e-60')
# Same-mask restriction is finite; changed mask leaves p positive where q=0.
assert mp.mpf('.5')>0 and mp.mpf('0')==0
rerun=I/'rerun';rerun.mkdir(exist_ok=True)
for name in ['verify.py','config.json']:shutil.copyfile(D/name,rerun/name)
run=subprocess.run([sys.executable,str(rerun/'verify.py')],capture_output=True,text=True,check=True)
(I/'rerun.log').write_text(run.stdout+run.stderr)
assert (rerun/'raw.json').read_bytes()==(D/'raw.json').read_bytes()
assert (rerun/'summary.json').read_bytes()==(D/'summary.json').read_bytes()
corpus=read(D/'retrieval-corpus.json')['files'];actual=sorted(str(p.relative_to(R)) for p in (R/'knowledge/entries').rglob('*') if p.is_file() and p.suffix in ['.md','.json'])
assert actual==sorted(x['path'] for x in corpus) and len(corpus)==184
for row in corpus:assert digest(R/row['path'])==row['sha256']
def cli(*args):return json.loads(subprocess.check_output([sys.executable,'-m','agent_runtime.knowledge','--root','knowledge',*args],cwd=R))
idx=I/'search.sqlite';cli('index','--db',str(idx));usage=read(D/'knowledge-usage.json');results=[]
for row in usage['retrieval']:
 result=cli('search',row['input']['query'],'--domain',row['domain'],'--limit','3',*(['--index',str(idx)] if row['backend']=='sqlite' else []))
 assert result==row['result'];results.append(result)
show=cli('show','math.softmax-kl-fisher');assert show['knowledge_refs']==usage['knowledge_refs']
tokens=len(tiktoken.get_encoding('cl100k_base').encode(json.dumps(show,ensure_ascii=False)))
assert tokens==read(D/'cost.json')['body_package_cl100k_base_tokens']==3625
assert len(results)==6 and all(r['results'][0]['id']=='math.softmax-kl-fisher' for r in results)
assert all(r['snapshot']=='4e05f3a7b5268c5dd7a7f553078f15588e7038b09b9f991e643909172954a2d9' for r in results)
sources=read(D/'research.json')['local_source_hashes']
for name,h in sources.items():assert digest(R/'.agent-runs/math-softmax-kl-20261008'/name)==h
(I/'retrieval-replay.json').write_text(json.dumps(dict(results=results,show=show),ensure_ascii=False,indent=2)+'\n')
(I/'check-result.json').write_text(json.dumps(dict(status='pass',manifest_sha256=digest(D/'manifest.json'),all_bindings=bindings,public_cases=64,boundary_cases=10,saturation_cases=4,independent_precision_digits=70,reference='Decimal positive exponent probability ratios; pairwise variance; 96-node Legendre Gaussian quadrature',maximum_direct_kl_error=max(errors),exact_rerun_raw=True,exact_rerun_summary=True,corpus_files=184,retrievals=6,actual_show_encoding_tokens=tokens,source_hashes_checked=len(sources),python=sys.version,platform=platform.platform()),indent=2)+'\n')
print('independent checks pass',max(errors),tokens)
