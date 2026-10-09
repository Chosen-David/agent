"""Exact public packetizer fixtures; not a production scheduler or general proof."""
from fractions import Fraction as F
from bisect import bisect_right
from pathlib import Path
import json,time,hashlib,sys
B=Path(__file__).resolve().parent;cfg=json.loads((B/'cases.json').read_text());Q=[F(0)]
for l in cfg['lengths']:Q.append(Q[-1]+F(l))
L=max(map(F,cfg['lengths']));grid=[F(i,cfg['grid_denominator']) for i in range(25)];rows=[];start=time.perf_counter()
def P(x):
 assert 0<=x<=Q[-1]
 return Q[bisect_right(Q,x)-1]
def emit(id,values):rows.append({'id':id,'values':values})
gaps=[x-P(x) for x in grid];assert all(0<=g<L for g in gaps)
assert P(F(3))==3 and P(F(11,4))==0
emit('residue-boundary',{'Q':Q,'grid':grid,'P':[P(x) for x in grid],'gaps':gaps})
shift=[]
for a in Q:
 for y in grid:
  if a+y<=Q[-1]:
   p=P(a+y);lo=a+max(F(0),y-L);assert p>=lo;shift.append([a,y,p,lo])
emit('shifted-boundary-lower',{'observations':shift})
th=[]
for a in Q:
 fluid=[x for x in grid if x>=a];complete=[x for x in grid if P(x)>=a];assert fluid==complete;th.append({'boundary':a,'fluid_set':fluid,'complete_set':complete})
emit('threshold-sets',{'sets':th})
arrival=F(1);rate=F(2);finish=[arrival+F(3)/rate,arrival+F(5)/rate];df=min(F(5),rate*(F(2)-arrival));dc=P(df)
assert finish==[F(5,2),F(7,2)] and (df,dc)==(2,0)
emit('fifo-record-stream',{'arrive':arrival,'finish':finish,'Df_at2':df,'Dc_at2':dc,'Bf':5-df,'Bc':5-dc,'last_boundary_delay_fluid':finish[-1]-arrival,'last_boundary_delay_complete':finish[-1]-arrival})
partial=F(1);whole=F(2);assert partial!=whole
emit('nonboundary-target',{'length':F(2),'rate':F(1),'partial_hit':partial,'complete_hit':whole,'decision':'reject nonboundary equality'})
qq=[F(0),F(100),F(101)];actual=F(1);prefix=qq[bisect_right(qq,actual)-1];assert actual!=prefix
emit('outoforder-workers',{'lengths':[F(100),F(1)],'second_finished_work':actual,'original_prefix_packetizer':prefix,'decision':'reject FIFO mapping'})
compute=F(2);visible=compute+F(1);assert visible!=compute
emit('visibility-stage',{'compute_finish':compute,'visible_finish':visible,'decision':'reject immediate visibility;separate stage'})
flow=arrival+F(3)/rate;sf=arrival+2*F(3)/rate;assert (flow,sf)==(F(5,2),F(4))
emit('tandem-storeforward',{'length':F(3),'rate':rate,'arrival':arrival,'fluid_tandem_end':flow,'intermediate_packetized_end':sf,'extra_delay':sf-flow,'decision':'reject terminal invariance for changed intermediate system'})
assert P(F(0))<Q[1]
emit('never-completes',{'target':Q[1],'constant_processed':F(0),'fluid_hit_set':'empty','complete_hit_set':'empty','both_delays':'infinity'})
R=F(2);T=F(1);tau=T+L/R;vals=[]
for h in grid:
 b=R*max(F(0),h-T);bc=max(F(0),b-L);rhs=R*max(F(0),h-tau);assert bc==rhs;vals.append([h,b,bc])
emit('weakened-rate-latency',{'R':R,'T':T,'L':L,'weakened_parameter':tau,'values':vals,'interpretation':'service lower bound parameter;not actual added terminal delay'})
assert [r['id'] for r in rows]==cfg['cases']
def ser(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,list):return [ser(a) for a in x]
 if isinstance(x,dict):return {k:ser(v) for k,v in x.items()}
 return x
out={'schema':'public-packetizer-checks/v1','cases_sha256':hashlib.sha256((B/'cases.json').read_bytes()).hexdigest(),'records':ser(rows),'elapsed_seconds':time.perf_counter()-start,'scope':cfg['scope']};(B/'raw.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'cases':len(rows),'scope':cfg['scope']}))
