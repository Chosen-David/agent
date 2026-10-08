"""Exact finite public fixtures; no floating/general formal proof or model test."""
import json,time
from fractions import Fraction as F
from pathlib import Path
BASE=Path(__file__).resolve().parent

def rref(rows):
 a=[list(row) for row in rows];piv=[];h=0
 for j in range(len(a[0])):
  pivot=next((i for i in range(h,len(a)) if a[i][j]),None)
  if pivot is None:continue
  a[h],a[pivot]=a[pivot],a[h];scale=a[h][j];a[h]=[x/scale for x in a[h]]
  for i in range(len(a)):
   if i!=h:
    scale=a[i][j];a[i]=[x-scale*y for x,y in zip(a[i],a[h])]
  piv.append(j);h+=1
  if h==len(a):break
 return a,piv

def output(v,w):return [sum(w[i]*v[i][j] for i in range(len(w))) for j in range(len(v[0]))]
def reduce_support(values,weights):
 if not values or not values[0] or len(values)!=len(weights) or any(len(x)!=len(values[0]) for x in values):raise ValueError('nonempty matching rectangular vectors required')
 v=[[F(x) for x in row] for row in values];w=list(map(F,weights))
 if any(x<0 for x in w) or sum(w)!=1:raise ValueError('nonnegative unit mass required')
 target=output(v,w);full=[[row[j] for row in v] for j in range(len(v[0]))]+[[F(1)]*len(v)]
 rank=len(rref(full)[1]);trace=[]
 while True:
  active=[i for i,x in enumerate(w) if x>0];rows=[[row[i] for i in active] for row in full];a,piv=rref(rows)
  if len(piv)==len(active):break
  free=next(j for j in range(len(active)) if j not in piv);direction=[F(0)]*len(active);direction[free]=1
  for h,j in enumerate(piv):direction[j]=-a[h][free]
  assert sum(direction)==0 and any(x>0 for x in direction) and any(x<0 for x in direction)
  theta=min(w[i]/direction[j] for j,i in enumerate(active) if direction[j]>0)
  before=len(active)
  for j,i in enumerate(active):w[i]-=theta*direction[j]
  assert all(x>=0 for x in w) and sum(w)==1 and output(v,w)==target
  assert sum(x>0 for x in w)<before
  trace.append({'theta':str(theta),'weights':list(map(str,w))})
 assert sum(x>0 for x in w)<=rank
 return {'weights':list(map(str,w)),'output':list(map(str,target)),'affine_dimension':rank-1,'support':sum(x>0 for x in w),'trace':trace}

def main():
 t=time.perf_counter();cases=json.loads((BASE/'cases.json').read_text());out=[]
 for c in cases:
  try:r=reduce_support(c['values'],c['weights'])
  except ValueError as e:
   assert c.get('expect')=='reject';out.append({'id':c['id'],'rejected':True,'reason':str(e)});continue
  assert c.get('expect')!='reject';out.append({'id':c['id'],**r})
 assert out[5]['support']==3 and out[5]['affine_dimension']==2
 z=F(5,6);assert F(13,18)*0+F(5,18)*3==z
 original_subset=F(1,6)/(F(1,2)+F(1,6))*3;assert original_subset==F(3,4) and z-original_subset==F(1,12)
 # Fixed W=[1,0] loses raw output: two points with same image, choose first.
 assert [0,0]!=[0,1] and 0==0
 result={'cases':out,'counterexample':{'full':str(z),'reweighted':str(z),'original_subset':str(original_subset),'error':str(z-original_subset)},'projected_output_warning':'W=[1,0], points(0,0),(0,2), equal weights: choosing first preserves Wz=0 but loses raw z=(0,1)','seconds':time.perf_counter()-t,'scope':'8 public exact cases, not general formal proof/model evaluation'}
 (BASE/'raw.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed_cases':len(out),'seconds':result['seconds']}))
if __name__=='__main__':main()
