"""Frozen independent checks; append run history, never overwrite failures."""
import sys, json, math, hashlib, datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from agent_runtime.knowledge import KnowledgeStore
HERE=Path(__file__).resolve().parent
cases=json.loads((HERE/'independent_cases.json').read_text())
corpus=Path(sys.argv[sys.argv.index('--root')+1]) if '--root' in sys.argv else ROOT/'knowledge'
store=KnowledgeStore(corpus)
kid=cases['target']
entry=store.get(kid,include_unpublished=True)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def b(v,r,d): return math.sqrt((v+r)*(2*math.log(1/d)+math.log1p(v/r)))
checks=[]
def check(name,ok,detail): checks.append({'name':name,'pass':bool(ok),'detail':detail})
# Independently integrate the Gaussian density times exponential martingale.
integration=[]
for s,v,r in [(1.2,.5,3),(-2.1,4,.7),(0,0,.125)]:
    center=s/(v+r); sd=1/math.sqrt(v+r); n=20000
    lo=center-12*sd; hi=center+12*sd; h=(hi-lo)/n
    def f(x): return math.sqrt(r/(2*math.pi))*math.exp(x*s-(v+r)*x*x/2)
    actual=h/3*(f(lo)+f(hi)+sum((4 if i%2 else 2)*f(lo+i*h) for i in range(1,n)))
    closed=math.sqrt(r/(r+v))*math.exp(s*s/(2*(r+v)))
    integration.append({'s':s,'v':v,'rho':r,'quadrature':actual,'closed':closed,'relative_error':abs(actual/closed-1)})
check('Gaussian mixture quadrature',all(x['relative_error']<1e-8 for x in integration),integration)
errors=[]
for v,r,d in [(0,.125,.01),(.6,3,.07),(200,.7,.2)]:
    boundary=b(v,r,d)
    logm=.5*math.log(r/(r+v))+boundary**2/(2*(v+r))
    errors.append(abs(logm-math.log(1/d)))
check('boundary inversion',max(errors)<1e-12,errors)
check('unit scale equivariance',abs(b(49*2.3,49*.7,.03)/b(2.3,.7,.03)-7)<1e-12,{'c':7})
mgf=.99+.01*math.cosh(10)
check('variance counterexample',mgf>math.exp(.5),{'mgf':mgf,'claimed_bound':math.exp(.5)})
# Enumerate exactly equiprobable histories. Absorb crossing paths.
paths=[(0.,0.,1.)]; crossed=0.
for t in range(14):
    nxt=[]
    for s,v,p in paths:
        a=.5 if s>=0 else 1.5
        for sign in [-1,1]:
            sn=s+sign*a; vn=v+a*a
            if abs(sn)>=b(vn,.7,.2): crossed+=p/2
            else: nxt.append((sn,vn,p/2))
    paths=nxt
check('adaptive finite tree',crossed<=.2 and abs(crossed+sum(x[2] for x in paths)-1)<1e-12,{'depth':14,'crossing_probability':crossed,'delta':.2,'surviving_paths':len(paths)})
retr=[]
for q in cases['retrieval']['queries']:
    result=store.search(q,limit=5,include_unpublished=True)
    ids=[x['id'] for x in result['results']]
    retr.append({'query':q,'ids':ids,'hit':kid in ids,'snapshot':result['snapshot']})
check('fresh bilingual retrieval',sum(x['hit'] for x in retr)>=4 and any(x['hit'] for x in retr[:3]) and any(x['hit'] for x in retr[3:]),retr)
refs=entry['knowledge_refs']; closure=set(); todo=[kid]
while todo:
    x=todo.pop()
    if x in closure: continue
    closure.add(x); todo.extend(y['id'] for y in store.records[x]['requires'])
check('dependency closure',closure=={x['id'] for x in refs},refs)
deps=[x for x in refs if x['id']!=kid]
check('published dependency versions',all(store.records[x['id']]['status']=='published' and store.records[x['id']]['version']==x['version'] for x in deps),deps)
# Check dependency validation even when root is legitimately candidate.
valid_refs=deps if deps else refs
if entry['status']=='published' or deps:
    store.check_refs(valid_refs)
    wrong=[dict(x) for x in valid_refs]; wrong[0]['sha256']='0'*64
    try: store.check_refs(wrong); rejected=False
    except Exception as e: rejected=True
    check('stale digest rejection',rejected,{'checked_refs':valid_refs})
    if entry['status']=='published' and deps:
        try: store.check_refs([x for x in refs if x['id']!=deps[0]['id']]); rejected=False
        except Exception: rejected=True
        check('omitted dependency rejection',rejected,{'omitted':deps[0]['id']})
run={'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'snapshot':store.snapshot,'cases_sha256':digest(HERE/'independent_cases.json'),'verifier_sha256':digest(Path(__file__)),'candidate':entry,'checks':checks,'machine_pass':all(x['pass'] for x in checks),'manual_scientific_review_required':True}
p=HERE/'independent_results.json'
history=json.loads(p.read_text()) if p.exists() else {'runs':[]}
history['runs'].append(run); p.write_text(json.dumps(history,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'run':len(history['runs']),'machine_pass':run['machine_pass'],'checks':[{k:x[k] for k in ('name','pass')} for x in checks]},ensure_ascii=False,indent=2))
