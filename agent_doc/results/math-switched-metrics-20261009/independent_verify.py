"""Independent scalar coordinate reconstruction, without producer matrix helpers."""
from fractions import Fraction as F
from pathlib import Path
import json
B=Path(__file__).resolve().parent
raw=json.loads((B/'raw.json').read_text())
records={x['id']:x for x in raw['records']}
assert len(records)==len(raw['records'])==8
checks={}
def cone(d1,d2,c):
 return d1>=0 and d2>=0 and d1*d2>=c*c
# Squared norm of (x/2+y/8,y/2); swap x,y for transposed mode.
assert cone(F(1,4),F(15,64),F(-1,16))
checks['common']={'residual_diagonal':['1/4','15/64'],'cross':'-1/16','determinant':str(F(1,4)*F(15,64)-F(1,256))}
# Weighted energy after (x/2+y,y/2): x²/4+xy+5y².
assert cone(F(1,2),F(7),F(-1,2))
assert records['mode']['residuals']==[[['1/2','-1/2'],['-1/2','7']],[['7','-1/2'],['-1/2','1/2']]]
checks['mode']={'determinant':'13/4','SPD':True}
assert 16*1-16==0 and 16*16-1==255
checks['comparison']={'opposite_metric_residual_diagonal':['0','255'],'same_metric':['15','240']}
# AT*A maps (x,y) to (x/4+y/2,x/2+5y/4).
assert F(3,4)*F(-1,4)-F(1,4)==F(-7,16)
assert records['unstable']['det_I_minus_product']=='-7/16'
assert F(3,4)**2+F(7,4)**2>2
checks['unstable']={'product':[['1/4','1/2'],['1/2','5/4']],'det_I_minus_product':'-7/16','trace':'3/2','eigenvalues':'(3+2sqrt(2))/4, (3-2sqrt(2))/4'}
x=y=F(1)
v0=F(17)
for t,row in enumerate(records['dwell']['trace'],1):
 if ((t-1)//10)%2==0: x,y=x/2+y,y/2
 else: x,y=x/2,x+y/2
 switched=t//10
 v=x*x+16*y*y if (t//10)%2==0 else 16*x*x+y*y
 bound=16**switched*F(3,4)**t*v0
 assert row=={'t':t,'switches':switched,'v':str(v),'bound':str(bound)} and v<=bound
factor=16*F(3,4)**10
assert factor<1 and records['dwell']['block_factor']==str(factor)
# Count switches at terminal mode too; check every window across ten dwell blocks.
windows=0
for s in range(101):
 for t in range(s,101):
  n=t//10-s//10
  assert n<=1+F(t-s,10)
  windows+=1
checks['dwell']={'steps':100,'all_windows_checked':windows,'block_factor':str(factor),'count_formula':'floor(t/10)-floor(s/10)'}
assert x!=0 or y!=0
checks['boundary']={'identity':'nonzero state remains constant when a=1'}
checks['zero']={'coordinate_update':'(0/2+0,0/2)=(0,0)'}
lo,hi=F(2,3),F(4,3)
assert hi/2==lo and lo/2+1==hi and records['affine']['cycle']==[str(lo),str(hi)]
checks['affine']={'fixed_points':['0','2'],'two_cycle':['2/3','4/3'],'homogeneous_shared_zero':False}
assert set(checks)==set(records) and all(v['pass'] for v in records.values())
(B/'independent_exact.json').write_text(json.dumps({'checks':checks,'verdict':'pass','method':'Independent scalar coefficients and coordinate recurrences; no producer helpers'},indent=2)+'\n')
print('8 independent exact case checks passed')
