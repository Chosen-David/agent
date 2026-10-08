"""Exact finite development checks. General proof is in card, not supplied by examples."""
from fractions import Fraction as F
from pathlib import Path
import json,time,itertools
BASE=Path(__file__).resolve().parent

def mat(m,n,v=0):return [[F(v) for _ in range(n)] for _ in range(m)]
def tr(A):return list(map(list,zip(*A)))
def mm(A,B):return [[sum((x*y for x,y in zip(row,col)),F(0)) for col in zip(*B)] for row in A]
def add(A,B,sign=1):return [[a+sign*b for a,b in zip(x,y)] for x,y in zip(A,B)]
def outer(a,b):return [[x*y for y in b] for x in a]
def mv(A,b):return [sum((x*y for x,y in zip(row,b)),F(0)) for row in A]
def dot(a,b):return sum((x*y for x,y in zip(a,b)),F(0))
def inv(A):
 n=len(A);a=[row[:]+[F(i==j) for j in range(n)] for i,row in enumerate(A)]
 for i in range(n):
  pivot=next((j for j in range(i,n) if a[j][i]),None)
  if pivot is None:raise ValueError('singular retained moment; SPD interface refuses')
  a[i],a[pivot]=a[pivot],a[i];p=a[i][i];a[i]=[v/p for v in a[i]]
  for j in range(n):
   if j!=i:
    p=a[j][i];a[j]=[v-p*w for v,w in zip(a[j],a[i])]
 return [row[n:] for row in a]
def moment(samples,fn,m,n):
 R=mat(m,n)
 for p,a,b in samples:R=add(R,[[p*x for x in row] for row in fn(a,b)])
 return R
def residual(T,a,b):return [v-w for v,w in zip(b,mv(T,a))]
def psd2(A):
 assert A==tr(A)
 if len(A)==1:return A[0][0]>=0
 assert len(A)==2
 return A[0][0]>=0 and A[1][1]>=0 and A[0][0]*A[1][1]-A[0][1]*A[1][0]>=0
def ser(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,(list,tuple)):return [ser(v) for v in x]
 if isinstance(x,dict):return {k:ser(v) for k,v in x.items()}
 return x

def main():
 t=time.perf_counter();laws=[]
 laws.append(('noisy',[(F(1,4),[F(a)],[F(2*a+e)]) for a,e in itertools.product([-1,1],repeat=2)]))
 laws.append(('exact',[(F(1,2),[F(a)],[F(2*a)]) for a in [-1,1]]))
 laws.append(('nonmean',[(F(1),[F(1)],[F(3)])]))
 laws.append(('nonlinear',[(F(1,4),[F(a)],[F(a*a)]) for a in [-2,-1,1,2]]))
 B0=[[F(1),F(2)],[F(-1),F(3)]];samples=[]
 for a in [[F(1),F(0)],[F(0),F(1)]]:
  for eps in [[F(1),F(0)],[F(-1),F(0)],[F(0),F(1)],[F(0),F(-1)]]:
   b=[x+y for x,y in zip(mv(B0,a),eps)];samples.append((F(1,8),a,b))
 laws.append(('matrix',samples));records=[]
 for name,samples in laws:
  s=len(samples[0][1]);h=len(samples[0][2]);assert sum(p for p,a,b in samples)==1 and all(p>0 for p,a,b in samples)
  Caa=moment(samples,lambda a,b:outer(a,a),s,s);Cba=moment(samples,lambda a,b:outer(b,a),h,s);Cbb=moment(samples,lambda a,b:outer(b,b),h,h)
  assert psd2(Caa);B=mm(Cba,inv(Caa));S=add(Cbb,mm(mm(B,Caa),tr(B)),-1)
  assert moment(samples,lambda a,b:outer(residual(B,a,b),a),h,s)==mat(h,s)
  assert moment(samples,lambda a,b:outer(residual(B,a,b),residual(B,a,b)),h,h)==S and psd2(S)
  D=mat(h,s);D[0][0]=1
  menu=[mat(h,s),B,[[-x for x in row] for row in B],add(B,mat(h,s,1)),add(B,D)]
  for j,T in enumerate(menu):
   direct=moment(samples,lambda a,b:outer(residual(T,a,b),residual(T,a,b)),h,h)
   gram=mm(mm(add(T,B,-1),Caa),tr(add(T,B,-1)));assert direct==add(S,gram) and psd2(gram)
   mse=sum(direct[i][i] for i in range(h));minimum=sum(S[i][i] for i in range(h));assert mse>=minimum
   # independent finite query distribution; u/v arbitrary, all dimensions exercised
   queries=[([F(i+1) for i in range(s)],[F(i+1) for i in range(h)]),([F(-2) for _ in range(s)],[F(-1) for _ in range(h)])]
   vv=mat(h,h);risk=F(0)
   for u,v in queries:
    vv=add(vv,[[x/2 for x in row] for row in outer(v,v)])
    for p,a,b in samples:
     e=residual(T,a,b);fold=[x+y for x,y in zip(u,mv(tr(T),v))]
     assert dot(u,a)+dot(v,b)==dot(fold,a)+dot(v,e)
     risk += p*dot(v,e)**2/2
   proxy=sum(mm(vv,direct)[i][i] for i in range(h));assert risk==proxy
   records.append({'id':name+'-'+str(j),'samples':[{'p':p,'a':a,'b':b} for p,a,b in samples],'Caa':Caa,'Cba':Cba,'Cbb':Cbb,'B':B,'S':S,'T':T,'residual_moment':direct,'PSD_difference':gram,'reconstruction_MSE':mse,'minimum_MSE':minimum,'independent_score_MSE':risk,'trace_score_MSE':proxy,'queries':queries})
 # Nonlinear/nonmean discriminators are exact, not conditional-distribution general tests.
 nonlinear=next(x for x in records if x['id']=='nonlinear-1');assert nonlinear['B']==[[F(0)]] and nonlinear['minimum_MSE']==F(17,2)
 assert all(b[0]==a[0]**2 for p,a,b in laws[3][1]);nonlinear_prediction_mse=F(0)
 assert next(x for x in records if x['id']=='nonmean-1')['B']==[[F(3)]]
 assert next(x for x in records if x['id']=='exact-1')['minimum_MSE']==0
 # Actual paired q/k risk reverses the reconstruction preference.
 paired=[{'p':F(1,2),'a':F(1),'b':F(b),'v':F(b==1)} for b in [-1,1]]
 paired_losses=[]
 for T in [F(0),F(1)]:
  key=sum(x['p']*(x['b']-T*x['a'])**2 for x in paired);score=sum(x['p']*(x['v']*(x['b']-T*x['a']))**2 for x in paired)
  paired_losses.append({'T':T,'key_MSE':key,'paired_score_MSE':score})
 assert [(x['key_MSE'],x['paired_score_MSE']) for x in paired_losses]==[(F(1),F(1,2)),(F(2),F(0))]
 singular=[[F(1),F(1)],[F(1),F(1)]]
 try:inv(singular);raise AssertionError('singular must refuse')
 except ValueError:singular_refused=True
 # Exact rational rotation, nonzero predictor commutes only for matching blocks here.
 R=[[F(3,5),F(-4,5)],[F(4,5),F(3,5)]];I=[[F(1),F(0)],[F(0),F(1)]];same=mm(R,I)==mm(I,R);different=mm(tr(R),I)!=mm(I,R);nope=mm(R,I)!=mm(I,I)
 assert same and different and nope
 sensor={'B':F(2),'conductance_S':F(3),'drop_MSE_A2':F(45),'predict_MSE_A2':F(9),'shift_MSE_V2':F(16)}
 assert sensor['drop_MSE_A2']==9*next(x for x in records if x['id']=='noisy-0')['reconstruction_MSE']
 assert sensor['predict_MSE_A2']==9*next(x for x in records if x['id']=='noisy-1')['reconstruction_MSE']
 out={'scope':'Exact finite public development, not general proof/model/GPU','records':records,'paired_samples':paired,'paired_losses':paired_losses,'nonlinear_mse':nonlinear_prediction_mse,'singular_refused':singular_refused,'rotation':{'R':R,'B':I,'same_frequency':same,'opposite_with_I_refused':different,'NoPE_RoPE_I_refused':nope},'sensor':sensor,'elapsed_seconds':time.perf_counter()-t,'token_cost':'unmeasured'}
 (BASE/'raw.json').write_text(json.dumps(ser(out),ensure_ascii=False,indent=2)+'\n');print(json.dumps({'cases':len(records),'finite_laws':len(laws),'elapsed_seconds':out['elapsed_seconds'],'scope':out['scope']}))
if __name__=='__main__':main()
