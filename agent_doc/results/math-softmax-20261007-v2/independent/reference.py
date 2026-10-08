"""Independent Decimal reference: direct probabilities, no shared softmax helper."""
import json
from decimal import Decimal, localcontext
from pathlib import Path
import hashlib
root=Path(__file__).resolve().parents[4]
out=Path(__file__).resolve().parent
checks=[]
with localcontext() as c:
    c.prec=90
    for w in ['0','0.00000001','0.1','2','10','40','800']:
        z=(Decimal(w)/2).exp()
        a=Decimal(1)/(1+z)
        b=z/(1+z)
        tv=abs(b-a)
        # Direct normalized probabilities with e=(w,0), not copied NumPy path.
        beta0=a*Decimal(w).exp()/(a*Decimal(w).exp()+b)
        beta1=b/(a*Decimal(w).exp()+b)
        tv_direct=(abs(a-beta0)+abs(b-beta1))/2
        assert abs(tv-tv_direct) < Decimal('1e-80')
        checks.append({'id':'decimal-sharp-'+w,'tv':str(tv),'direct_tv':str(tv_direct),'pass':True})
    alpha=[Decimal('.45'),Decimal('.30'),Decimal('.20'),Decimal('.05')]
    vals=[Decimal(0),Decimal(1),Decimal(0),Decimal(-6)]
    y=sum(a*v for a,v in zip(alpha,vals))
    for ids in [(0,), (0,1), (0,2), (0,1,2,3)]:
        p=sum(alpha[j] for j in ids)
        ys=sum(alpha[j]*vals[j] for j in ids)/p
        tv=sum(abs(alpha[j]-(alpha[j]/p if j in ids else 0)) for j in range(4))/2
        assert tv==1-p
        if p<1:
            yc=sum(alpha[j]*vals[j] for j in range(4) if j not in ids)/(1-p)
            assert y-ys == (1-p)*(yc-ys)
        checks.append({'id':'decimal-prune-'+str(ids),'mass':str(p),'tv':str(tv),'output':str(ys),'pass':True})
original=json.loads((out.parent/'raw.json').read_text())
rerun=json.loads((out/'raw.json').read_text())
assert original==rerun
assert len(original['records'])==len({r['id'] for r in original['records']})==416
assert all(r['pass'] for r in original['records'])
checks.append({'id':'all-416-records-exactly-identical','pass':True})
(out/'reference.json').write_text(json.dumps({'checks':checks,'count':len(checks),'scope':'Independent Decimal scalar closed forms plus all-record rerun comparison; not formal or model validation'},indent=2)+'\n')
print(json.dumps({'reference_checks':len(checks),'passed':len(checks),'all_records_match':True}))
