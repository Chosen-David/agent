import subprocess,types,sys,copy,random,graphlib
from agent_runtime.core import validate
m=types.ModuleType('agent_runtime._review_baseline');m.__package__='agent_runtime';sys.modules[m.__name__]=m
exec(compile(subprocess.check_output(['git','show','56ccc46d1458dd7df257b68d296616eb34014c58:agent_runtime/core.py']),'baseline.py','exec'),m.__dict__)
def make(deps):
 return {'schema_version':'task-dag/v1','run_id':'r','user_goal':'g','authorization_reference':'a','supervision':{'min_seconds':1,'max_seconds':2,'rationale':'r'},'tasks':[dict(task_id=str(i),depends_on=[str(j) for j in d],action='a',owner='o',done_when='d',max_attempts=1,estimated_seconds=1,risk='low') for i,d in enumerate(deps)]}
def outcome(fn,p):
 try: fn(p); return None
 except Exception as e:return type(e).__name__,str(e)
count=0
for residual in [63,64,65]:
 for delta in [-1,0,1]:
  n=residual+2; deps=[set() if i==0 else {i-1} for i in range(n)]
  # Exact count of dependency entries in residual, including peeled vertices.
  target=4*residual+delta
  for i in range(2,n):
   for j in range(i):
    if sum(len(x) for x in deps[2:])>=target:break
    deps[i].add(j)
  if sum(len(x) for x in deps[2:])!=target:raise RuntimeError('fixture density')
  for cycle in [False,True]:
   x=copy.deepcopy(deps)
   if cycle:x[2].add(n-1)
   p=make(x);before=copy.deepcopy(p)
   a=outcome(m.validate,p);b=outcome(validate,p)
   if a!=b or before!=p:raise RuntimeError((residual,delta,cycle,a,b))
   count+=1
rng=random.Random(88016)
for n in [66,128,256]:
 for trial in range(16):
  order=list(range(n));rng.shuffle(order);pos={x:i for i,x in enumerate(order)}
  deps=[set() for _ in range(n)]
  for i in range(n):
   deps[i]={j for j in range(n) if pos[j]<pos[i] and rng.random()<3/n}
  if trial%2:
   # Guaranteed closed cycle, possibly alongside removable acyclic prefixes.
   deps[order[1]].add(order[2]);deps[order[2]].add(order[1])
  p=make(deps);a=outcome(m.validate,p);b=outcome(validate,p)
  try:list(graphlib.TopologicalSorter({str(i):[str(j) for j in d] for i,d in enumerate(deps)}).static_order());expected=None
  except graphlib.CycleError:expected=('ValueError','dependency cycle')
  if a!=b or b!=expected:raise RuntimeError((n,trial,a,b,expected))
  count+=1
print('Reviewer-designed supplemental differential cases passed:',count)
