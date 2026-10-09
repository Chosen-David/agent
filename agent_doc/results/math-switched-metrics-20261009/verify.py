"""Public exact two-dimensional fixtures; finite arithmetic is not a general proof."""
from fractions import Fraction as F
from pathlib import Path
import json,time,sys
B=Path(__file__).resolve().parent
def matrix(rows):return [[F(v) for v in row] for row in rows]
def transpose(A):return list(map(list,zip(*A)))
def mul(A,B):return [[sum(a*b for a,b in zip(row,col)) for col in zip(*B)] for row in A]
def scale(a,A):return [[a*x for x in row] for row in A]
def sub(A,B):return [[x-y for x,y in zip(a,b)] for a,b in zip(A,B)]
def psd(A):return A[0][1]==A[1][0] and A[0][0]>=0 and A[1][1]>=0 and A[0][0]*A[1][1]-A[0][1]**2>=0
def energy(x,P):return sum(x[i]*P[i][j]*x[j] for i in range(2) for j in range(2))
def update(A,x):return [sum(a*b for a,b in zip(row,x)) for row in A]
def run():
 start=time.perf_counter();I=matrix([[1,0],[0,1]]);small=matrix([['1/2','1/8'],[0,'1/2']]);A=matrix([['1/2',1],[0,'1/2']]);AT=transpose(A);P=[matrix([[1,0],[0,16]]),matrix([[16,0],[0,1]])];a=F(3,4);mu=F(16);rows=[]
 def record(n,ok,**kw):assert ok,n;rows.append({'id':n,'pass':bool(ok),**kw})
 record('common',all(psd(sub(scale(F(1,2),I),mul(mul(transpose(T),I),T))) for T in [small,transpose(small)]))
 residuals=[sub(scale(a,p),mul(mul(transpose(T),p),T)) for T,p in zip([A,AT],P)];record('mode',all(psd(x) for x in residuals),residuals=[[[str(x) for x in row] for row in Q] for Q in residuals])
 record('comparison',all(psd(sub(scale(mu,p),q)) for p in P for q in P))
 product=mul(AT,A);D=sub(I,product);det=D[0][0]*D[1][1]-D[0][1]**2;record('unstable',det<0 and energy(update(product,[F(1),F(1)]),I)>2,det_I_minus_product=str(det))
 x=[F(1),F(1)];v0=energy(x,P[0]);ns=0;trace=[]
 for t in range(100):
  mode=(t//10)%2; nxt=((t+1)//10)%2;x=update([A,AT][mode],x);ns+=int(mode!=nxt);v=energy(x,P[nxt]);bound=mu**ns*a**(t+1)*v0;assert v<=bound;trace.append({'t':t+1,'switches':ns,'v':str(v),'bound':str(bound)})
 record('dwell',mu*a**10<1,block_factor=str(mu*a**10),trace=trace)
 record('boundary',mul(I,I)==I,reason='a=1:identity gives no strict decay')
 record('zero',update(A,[F(0),F(0)])==[0,0])
 # Alternating x/2 followed by x/2+1 has limiting cycle 2/3,4/3.
 lo,hi=F(2,3),F(4,3);record('affine',hi/2==lo and lo/2+1==hi and hi!=lo,reason='distinct equilibria reject shared-zero premise',cycle=[str(lo),str(hi)])
 return {'scope':'8 public exact fixtures; proof separately reviewed; no model/GPU','records':rows,'seconds':time.perf_counter()-start,'token_cost':'unknown'}
if __name__=='__main__':
 out=run();dest=Path(sys.argv[1]) if len(sys.argv)>1 else B/'raw.json';dest.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'cases':len(out['records']),'passed':all(x['pass'] for x in out['records']),'seconds':out['seconds']}))
