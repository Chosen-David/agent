"""Public exact quadratic FW trajectories; not a production optimizer/float certificate."""
import json,time
from fractions import Fraction as F
from pathlib import Path
B=Path(__file__).resolve().parent

def dot(x,y):return sum((a*b for a,b in zip(x,y)),F(0))
def sub(x,y):return [a-b for a,b in zip(x,y)]
def norm2(x):return dot(x,x)
def mix(v,b):return [sum((b[i]*v[i][j] for i in range(len(v))),F(0)) for j in range(len(v[0]))]
def rational(obj):
 if isinstance(obj,F):return str(obj)
 if isinstance(obj,dict):return {k:rational(x) for k,x in obj.items()}
 if isinstance(obj,list):return [rational(x) for x in obj]
 return obj

def main():
 t=time.perf_counter();cfg=json.loads((B/'cases.json').read_text());records=[];transitions=0
 for c in cfg['cases']:
  v=[[F(x) for x in row] for row in c['v']];z=[F(x) for x in c['z']]
  if not v:records.append({'id':c['id'],'rejected':'empty'});continue
  b=[F(x) for x in c.get('beta',[1]+[0]*(len(v)-1))]
  if len(b)!=len(v) or min(b)<0 or sum(b)!=1:records.append({'id':c['id'],'rejected':'signed'});continue
  assert all(len(row)==len(z) for row in v)
  opt=F(c['opt']);D2=max(norm2(sub(a,d)) for a in v for d in v)
  item={'id':c['id'],'D2':D2,'opt':opt,'policies':{}}
  for policy in cfg['policies']:
   beta=b[:];history=[]
   for step in range(cfg['steps']+1):
    y=mix(v,beta);r=sub(z,y);f=norm2(r)/2; scores=[dot(r,w) for w in v];best=max(scores);j=scores.index(best);d=sub(v[j],y);g=dot(r,d);h=f-opt
    assert min(beta)>=0 and sum(beta)==1 and F(0)<=h<=g
    assert sum(x>0 for x in beta)<=step+1
    if step>=1:assert h<=2*D2/F(step+2)
    state={'step':step,'y':y,'beta':beta[:],'f':f,'h':h,'gap':g,'oracle':j}
    history.append(state)
    if step==cfg['steps']:break
    L=norm2(d);gamma=(F(2,step+2) if policy=='schedule' else (min(F(1),max(F(0),g/L)) if L else F(0)))
    newb=[(1-gamma)*x for x in beta];newb[j]+=gamma;newy=mix(v,newb);newf=norm2(sub(z,newy))/2
    assert newf==f-gamma*g+gamma*gamma*L/2
    scheduled=F(2,step+2)
    assert newf-opt <= (1-scheduled)*h+scheduled*scheduled*D2/2
    if policy=='line-search':assert newf<=f
    state['gamma']=gamma;beta=newb;transitions+=1
   item['policies'][policy]=history
  if c['id']=='F1':assert item['policies']['schedule'][1]['f']>item['policies']['schedule'][0]['f']
  if 'sampled_indices' in c:
   y=v[c['sampled_oracle_at']];r=sub(z,y);full=max(dot(r,w) for w in v);part=max(dot(r,v[i]) for i in c['sampled_indices']);gpart=part-dot(r,y);eta=full-part;gap=full-dot(r,y);h=norm2(r)/2-opt
   assert gpart==0 and h>0 and gap>0 and h<=gpart+eta
   item['sampled_false_stop']={'y':y,'gap_partial':gpart,'gap_full':gap,'eta':eta,'h':h}
  records.append(item)
 output={'records':rational(records),'case_count':len(records),'transition_count':transitions,'scope':'Public exact recurrence only','seconds_diagnostic':time.perf_counter()-t}
 (B/'raw.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'cases':len(records),'transitions':transitions,'seconds_diagnostic':output['seconds_diagnostic']}))
if __name__=='__main__':main()
