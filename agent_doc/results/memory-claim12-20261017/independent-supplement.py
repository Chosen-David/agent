from pathlib import Path
import importlib.util,sys,json,hashlib,random
from unittest.mock import patch
R=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('claim12_check',R/'check.py'); c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
import agent_runtime.handoff_basis as h
out=[]
def compare(r,label,valid=None):
 a=c.outcome(c.baseline.claim_graph,r);b=c.outcome(h.claim_graph,r)
 assert a==b,(label,a,b)
 if valid is not None: assert (a[0]=='ok')==valid,(label,a)
 out.append({'case':label,'outcome':a[0]})
for residual in (63,64,65):
 r=c.chain(residual+2);calls=[];orig=h._valid_claim_residual
 def wrap(g,p):calls.append(len(p));return orig(g,p)
 with patch.object(h,'_valid_claim_residual',wrap):compare(r,f'residual{residual}',True)
 assert calls==([] if residual==63 else [residual]),calls
for target in (391,392,393):
 r=c.chain(100);claims=r['evidence_claims'];total=sum(len(x['depends_on']) for x in claims[2:])
 for i in range(2,100):
  for j in range(i-1):
   if total>=target:break
   claims[i]['depends_on'].append(f'c{j}');total+=1
  if total>=target:break
 assert total==target
 g={x['id']:x for x in claims};pending={f'c{i}' for i in range(2,100)}
 assert h._valid_claim_residual(g,pending)==(target<=392)
 compare(r,f'density{target}/392',True)
for n in (66,67,100,180):
 for where in (0,1,2,n//2,n-2):
  for mode in ('candidate','unknown','self','two-cycle','mixed'):
   r=c.chain(n);cs=r['evidence_claims']
   if mode=='candidate':cs[where]['status']='candidate'
   elif mode=='unknown':cs[where]['depends_on'].append('missing')
   elif mode=='self':cs[where]['depends_on'].append(f'c{where}')
   elif mode=='two-cycle':cs[where]['depends_on'].append(f'c{where+1}')
   else:
    cs[-2]['depends_on']=['c'+str(n-1)];cs[where]['depends_on'].append('missing');cs[n//2]['status']='candidate'
   compare(r,f'{n}:{where}:{mode}',False)
for n in (66,150):
 r=c.chain(n)
 for claim in r['evidence_claims']:claim['depends_on']=tuple(claim['depends_on'])
 compare(r,f'tuple{n}',True)
# New trace classes include already-peeled parent and late exotic objects.
for mode in ('id','parent','status','dict','list','tuple'):
 for where in (0,1,60,99):
  events=[]
  class S(str):
   def __hash__(self):events.append(('hash',str(self)));return super().__hash__()
   def __eq__(self,o):events.append(('eq',str(self),str(o)));return super().__eq__(o)
  class D(dict):
   def __getitem__(self,k):events.append(('get',k));return super().__getitem__(k)
  class L(list):
   def __iter__(self):events.append('iter-list');return super().__iter__()
  class T(tuple):
   def __iter__(self):events.append('iter-tuple');return super().__iter__()
  r=c.chain(100);cs=r['evidence_claims'];cl=cs[where]
  if mode=='id':cl['id']=S(cl['id'])
  elif mode=='status':cl['status']=S(cl['status'])
  elif mode=='parent':cs[max(where,1)]['depends_on']=[S('c'+str(max(where,1)-1))]
  elif mode=='dict':cs[where]=D(cl)
  elif mode=='list':cl['depends_on']=L(cl['depends_on'])
  else:cl['depends_on']=T(cl['depends_on'])
  events.clear();a=c.outcome(c.baseline.claim_graph,r);ea=events[:]
  events.clear();b=c.outcome(h.claim_graph,r);eb=events[:]
  assert a==b and ea==eb,(mode,where,a,b,len(ea),len(eb))
  out.append({'case':f'custom:{mode}:{where}','outcome':'trace-match'})
# Independent reachability oracle on valid random DAGs then back-edge failures.
rng=random.Random(91712)
for trial in range(60):
 n=rng.randrange(68,160)
 p={f'c{i}':[f'c{j}' for j in range(i) if rng.random()<.04] for i in range(n)}
 # impose deep spine to activate optimized path on some fixtures
 if trial%2==0:
  for i in range(1,n):p[f'c{i}']=list(set(p[f'c{i}']+['c'+str(i-1)]))
 compare(c.record_for(p),f'random-dag{trial}',True)
 r=c.record_for(p);r['evidence_claims'][0]['depends_on']=['c0'];compare(r,f'random-self{trial}',False)
(R/'independent-supplement.json').write_text(json.dumps({'cases':len(out),'checks':out,'source_sha256':hashlib.sha256(Path(h.__file__).read_bytes()).hexdigest()},indent=2)+'\n')
print('supplement cases',len(out))
