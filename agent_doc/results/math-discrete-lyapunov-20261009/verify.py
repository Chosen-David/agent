"""Eight public exact fixtures; no finite trajectory proves a general theorem."""
from fractions import Fraction as F
from pathlib import Path
import json,time,sys
B=Path(__file__).resolve().parent
M=lambda a:[[F(x) for x in r] for r in a]
def mul(a,b):return [[sum((a[i][k]*b[k][j] for k in range(len(b))),F(0)) for j in range(len(b[0]))] for i in range(len(a))]
def tr(a):return list(map(list,zip(*a)))
def sub(a,b):return [[x-y for x,y in zip(r,s)] for r,s in zip(a,b)]
def pd(a):return a[0][0]>0 and a[0][0]*a[1][1]-a[0][1]*a[1][0]>0 and a==tr(a)
def energy(p,x):return mul(mul(tr(x),p),x)[0][0]
def gauss(a,b):
 n=len(b);z=[r[:]+[v] for r,v in zip(a,b)]
 for j in range(n):
  k=next(k for k in range(j,n) if z[k][j]);z[j],z[k]=z[k],z[j];v=z[j][j];z[j]=[x/v for x in z[j]]
  for k in range(n):
   if k!=j:
    v=z[k][j];z[k]=[x-v*y for x,y in zip(z[k],z[j])]
 return [r[-1] for r in z]
def run():
 start=time.perf_counter();cfg=json.loads((B/'cases.json').read_text());A=M(cfg['A']);I=M(cfg['Q']);records=[]
 def put(i,passed,values):assert passed,(i,values);records.append({'id':i,'passed':True,'values':values})
 # Solve ALL four coordinates of P, not just hardcoded symmetric entries.
 bases=[[[F(i==u and j==v) for j in range(2)] for i in range(2)] for u in range(2) for v in range(2)]
 coeff=[sub(e,mul(mul(tr(A),e),A)) for e in bases];mat=[[c[i][j] for c in coeff] for i in range(2) for j in range(2)]
 z=gauss(mat,[I[i][j] for i in range(2) for j in range(2)]);P=[z[:2],z[2:]];D=sub(P,mul(mul(tr(A),P),A))
 put('C1',P==M([['4/3','16/9'],['16/9','356/27']]) and D==I and pd(P),{'P':P,'det':P[0][0]*P[1][1]-P[0][1]*P[1][0],'residual':sub(D,I)})
 e=M([['0'],['1']]);e1=mul(A,e);put('C2',energy(I,e1)==F(17,4) and energy(P,e)-energy(P,e1)==1,{'norm2_before':energy(I,e),'norm2_after':energy(I,e1),'V_before':energy(P,e),'V_after':energy(P,e1)})
 T=I;seq=[]
 for t in range(31):
  exact=M([[F(1,2)**t,0 if t==0 else 2*t*F(1,2)**(t-1)],[0,F(1,2)**t]])
  assert T==exact;seq.append({'t':t,'power':T});T=mul(T,A)
 put('C3',True,seq)
 put('C4',1-F(1)**2==0 and 1-F(-1)**2==0 and 1/(1-F(11,10)**2)==F(-100,21),{'boundary_coefficient':0,'unstable_P':F(-100,21)})
 As=M([['1/2','0'],['0','1']]);Ps=M([['4/3','0'],['0','1']]);Qs=M([['1','0'],['0','0']]);put('C5',sub(Ps,mul(mul(tr(As),Ps),As))==Qs and mul(As,e)==e,{'A':As,'P':Ps,'Q':Qs,'hidden_state':e})
 As=M([['1/2','0'],['0','2']]);Ps=M([['1','0'],['0','0']]);Qs=M([['3/4','0'],['0','0']]);put('C6',sub(Ps,mul(mul(tr(As),Ps),As))==Qs and energy(Ps,e)==0 and mul(As,e)==M([['0'],['2']]),{'A':As,'P':Ps,'Q':Qs})
 BA=mul(tr(A),A);x=M([['1'],['1']]);seq=[]
 for t in range(9):
  assert all(row[0]>=F(5,4)**t for row in x);seq.append({'t':t,'state':x});x=mul(BA,x)
 put('C7',BA==M([['1/4','1'],['1','17/4']]),{'BA':BA,'cycles':seq,'minimum_row_sum':min(map(sum,BA))})
 gamma=F(31,32);margin=sub([[gamma**2*v for v in r] for r in P],mul(mul(tr(A),P),A));assert pd(margin)
 x=e;bound=F(4);eta=F(1,50);seq=[]
 for t in range(cfg['steps']+1):
  assert energy(P,x)<=bound**2;seq.append({'t':t,'energy':energy(P,x),'bound_squared':bound**2})
  w=M([[F((-1)**t,100)],[0]]);assert energy(P,w)<=eta**2
  x=[[a+b for a,b in zip(r,s)] for r,s in zip(mul(A,x),w)];bound=gamma*bound+eta
 put('C8',True,{'gamma':gamma,'eta':eta,'matrix_margin':margin,'trajectory':seq})
 assert [x['id'] for x in records]==[x['id'] for x in cfg['cases']]
 return {'scope':'public exact CPU fixtures only','records':records,'elapsed_seconds':time.perf_counter()-start,'token_cost':'unmeasured','arithmetic':'stdlib Fraction exact'}
if __name__=='__main__':
 out=Path(sys.argv[1]) if len(sys.argv)>1 else B/'raw.json';r=run();out.write_text(json.dumps(r,ensure_ascii=False,indent=2,default=str)+'\n');print(json.dumps({'cases':len(r['records']),'elapsed_seconds':r['elapsed_seconds']}))
