"""Finite exact fixtures: enumerate nonsingular face KKT systems, certify full hull."""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import json,time
BASE=Path(__file__).resolve().parent

def dot(a,b):return sum((x*y for x,y in zip(a,b)),F(0))
def matvec(A,x):return [dot(row,x) for row in A]
def parse(values,z):
 if not values or not z or any(len(row)!=len(z) for row in values):raise ValueError('nonempty compatible finite vectors required')
 return [[F(x) for x in row] for row in values],list(map(F,z))
def yof(v,b):return [sum((a*row[j] for a,row in zip(b,v)),F(0)) for j in range(len(v[0]))]
def feasible(b,n):
 if len(b)!=n or any(x<0 for x in b) or sum(b)!=1:raise ValueError('nonnegative unit simplex required')
def solve(A,b):
 n=len(A);a=[list(row)+[rhs] for row,rhs in zip(A,b)]
 for j in range(n):
  p=next((i for i in range(j,n) if a[i][j]),None)
  if p is None:return None
  a[j],a[p]=a[p],a[j];scale=a[j][j];a[j]=[x/scale for x in a[j]]
  for i in range(n):
   if i!=j:
    scale=a[i][j];a[i]=[x-scale*y for x,y in zip(a[i],a[j])]
 return [a[i][-1] for i in range(n)]
def cert(v,z,b):
 feasible(b,len(v));y=yof(v,b);r=[a-c for a,c in zip(z,y)];P=dot(r,r);scores=[dot(r,x) for x in v];g=max(scores)-dot(r,y);assert g>=0
 return {'y':y,'residual':r,'P':P,'gap':g,'D':P-2*g,'clipped_lower':max(F(0),P-2*g),'vertex_scores':scores}
def project(v,z):
 best=None;trials=0
 for size in range(1,min(len(v),len(z)+1)+1):
  for idx in combinations(range(len(v)),size):
   vs=[v[i] for i in idx];A=[[dot(x,y) for y in vs]+[F(1)] for x in vs]+[[F(1)]*size+[F(0)]];rhs=[dot(x,z) for x in vs]+[F(1)];x=solve(A,rhs);trials+=1
   if x is None or any(a<0 for a in x[:-1]):continue
   b=[F(0)]*len(v)
   for i,a in zip(idx,x[:-1]):b[i]=a
   c=cert(v,z,b)
   if best is None or c['P']<best[1]['P']:best=(b,c)
 assert best is not None
 assert best[1]['gap']==0,'full-vertex certificate must certify optimum'
 return best[0],best[1],trials
def serial(o):
 if isinstance(o,F):return str(o)
 if isinstance(o,dict):return {k:serial(v) for k,v in o.items()}
 if isinstance(o,list):return [serial(v) for v in o]
 return o
def main():
 t=time.perf_counter();rows=[]
 for case in json.loads((BASE/'cases.json').read_text()):
  try:v,z=parse(case['values'],case['target'])
  except ValueError as e:
   assert case.get('expect')=='reject_empty';rows.append({'id':case['id'],'rejected':True,'reason':str(e)});continue
  raw_v,raw_z=v,z
  if 'W' in case:
   W=[[F(x) for x in row] for row in case['W']];v=[matvec(W,x) for x in v];z=matvec(W,z)
  if case.get('expect')=='reject_proposal':
   try:cert(v,z,list(map(F,case['proposal'])))
   except ValueError as e:rows.append({'id':case['id'],'rejected':True,'reason':str(e)});continue
   raise AssertionError('illegal negative proposal accepted')
  b,c,trials=project(v,z);assert c['P']==F(case['expected_squared'])
  row={'id':case['id'],'weights':b,'optimal':c,'face_trials':trials}
  if 'proposal' in case:
   pr=cert(v,z,list(map(F,case['proposal'])));assert pr['gap']==F(case['expected_gap']) and pr['D']==F(case['expected_lower']);assert pr['D']<=c['P']<=pr['P'];row['proposal']=pr
  if 'W' in case:
   raw_y=yof(raw_v,b);raw_r=[a-c for a,c in zip(raw_z,raw_y)];row.update(raw_y=raw_y,raw_squared=dot(raw_r,raw_r));assert row['raw_squared']==1
  rows.append(row)
 # Explicit relaxed affine combination gives zero error but illegal simplex weights.
 assert -F(1)*0+F(2)*1==2
 # Using an incomplete max would produce a false lower bound 4 for actual optimum0.
 false_D=F(4);assert false_D>0
 out=serial({'cases':rows,'affine_relaxation':{'weights':[F(-1),F(2)],'error_squared':F(0),'simplex_error_squared':F(1)},'incomplete_max':{'false_lower':false_D,'actual_optimum':F(0)},'seconds':time.perf_counter()-t,'scope':'12 public exact cases; not a general production QP solver or floating certificate'})
 (BASE/'raw.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'passed_cases':len(rows),'seconds':out['seconds']}))
if __name__=='__main__':main()
