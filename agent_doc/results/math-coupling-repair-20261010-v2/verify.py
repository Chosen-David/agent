"""Exact public repair fixtures; no float or model certification."""
from fractions import Fraction as Q
from pathlib import Path
import json,sys,time
BASE=Path(__file__).resolve().parent

def weights(a):
 a=list(map(Q,a));assert len(a)>0
 if any(x<0 for x in a) or sum(a)!=1:raise ValueError('negative or nonunit target mass')
 return a

def repair(F,a,b):
 a,b=weights(a),weights(b);F=[list(map(Q,row)) for row in F];m,n=len(a),len(b)
 if len(F)!=m or any(len(row)!=n for row in F) or any(x<0 for row in F for x in row):raise ValueError('invalid shape or negative F')
 rows=[sum(row) for row in F];cols=[sum(F[i][j] for i in range(m)) for j in range(n)]
 X=[[x*(min(Q(1),a[i]/rows[i]) if rows[i]>0 else Q(1)) for x in row] for i,row in enumerate(F)]
 xc=[sum(X[i][j] for i in range(m)) for j in range(n)]
 Y=[[X[i][j]*(min(Q(1),b[j]/xc[j]) if xc[j]>0 else Q(1)) for j in range(n)] for i in range(m)]
 rr=[a[i]-sum(Y[i]) for i in range(m)];ss=[b[j]-sum(Y[i][j] for i in range(m)) for j in range(n)];tau=sum(rr);assert tau==sum(ss) and tau>=0 and min(rr+ss)>=0
 G=[[Y[i][j]+(rr[i]*ss[j]/tau if tau else Q(0)) for j in range(n)] for i in range(m)]
 assert [sum(row) for row in G]==a and [sum(G[i][j] for i in range(m)) for j in range(n)]==b
 M=sum(rows);delta=M-sum(map(sum,Y));diff=sum(abs(G[i][j]-F[i][j]) for i in range(m) for j in range(n));assert diff<=delta+tau
 residual=sum(abs(x-y) for x,y in zip(rows,a))+sum(abs(x-y) for x,y in zip(cols,b))
 if M==1:assert diff<=residual
 return G,tau,delta,diff,residual

def main():
 start=time.perf_counter();cases=json.loads((BASE/'fixtures.json').read_text())['cases'];out=[]
 for c in cases:
  if c['id']=='T7':
   rejected=[]
   for z in [c]+c['invalid_mass_variants']:
    try:repair(z['F'],z['a'],z['b'])
    except ValueError as e:rejected.append(str(e))
    else:raise AssertionError('invalid input accepted')
   out.append({'id':'T7','pass':True,'rejections':rejected});continue
  a,b=weights(c['a']),weights(c['b']);v=list(map(Q,c['v']));C=[[abs(x-y) for y in v] for x in v]
  if c['id']=='T8':
   f,g=list(map(Q,c['f'])),list(map(Q,c['g']));h=max([Q(0)]+[f[i]+g[j]-C[i][j] for i in range(2) for j in range(2)]);L=sum(x*y for x,y in zip(a,f))+sum(x*y for x,y in zip(b,g))-h
   assert h==Q(c['expected_h']) and L==Q(c['expected_L']);assert all(f[i]-h+g[j]<=C[i][j] for i in range(2) for j in range(2));assert L<=Q(c['expected_opt'])<sum(x*y for x,y in zip(a,f))
   out.append({'id':'T8','pass':True,'h':str(h),'L':str(L),'actual_optimum':c['expected_opt']});continue
  G,tau,delta,diff,res=repair(c['F'],a,b);F=[list(map(Q,row)) for row in c['F']];U=sum(G[i][j]*C[i][j] for i in range(2) for j in range(2));raw=sum(F[i][j]*C[i][j] for i in range(2) for j in range(2));D=max(map(max,C));error=abs(sum(x*y for x,y in zip(a,v))-sum(x*y for x,y in zip(b,v)))
  assert tau==Q(c['expected_tau']) and U==Q(c['expected_U']);assert error<=U<=raw+D*tau
  forbidden=[(i,j) for i in range(2) for j in range(2) if 'mask' in c and not c['mask'][i][j] and G[i][j]>0]
  if c['id']=='T5':assert forbidden==[(0,1)]
  if c['id']=='T2':assert raw<error
  out.append({'id':c['id'],'pass':True,'G':[[str(x) for x in row] for row in G],'tau':str(tau),'delta':str(delta),'L1difference':str(diff),'marginal_residual':str(res),'raw_cost':str(raw),'U':str(U),'output_error':str(error),'forbidden_edges':forbidden})
 target=Path(sys.argv[1]) if len(sys.argv)>1 else BASE;target.mkdir(parents=True,exist_ok=True);(target/'raw.json').write_text(json.dumps({'cases':out,'seconds':time.perf_counter()-start,'visibility':'public exact CPU; no unused/model claims'},indent=2)+'\n');print(json.dumps({'public_cases':len(out),'passed':sum(x['pass'] for x in out)}))
if __name__=='__main__':main()
