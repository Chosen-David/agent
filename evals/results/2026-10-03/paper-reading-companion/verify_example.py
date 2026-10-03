"""Verify only the supplied teaching example; no RoPE implementation or experiment."""
import json, math
from pathlib import Path

def evaluate(b):
    a=(0.0,0.0); values=(0.0,10.0)
    z=[x+y for x,y in zip(a,b)]
    exp=[math.exp(x-max(z)) for x in z]
    weights=[x/sum(exp) for x in exp]
    return {'b':list(b),'weights':weights,'output':sum(w*v for w,v in zip(weights,values))}

baseline=evaluate((0.0,0.0))
changed=evaluate((0.0,math.log(3.0)))
common_shift=evaluate((1.0,1.0))
assert math.isclose(baseline['output'],5.0)
assert math.isclose(changed['output'],7.5)
assert math.isclose(common_shift['output'],5.0)
result={'baseline':baseline,'changed':changed,'output_difference':changed['output']-baseline['output'],'common_shift_teaching_check':common_shift,'scope':'Arithmetic of supplied example only; no RoPE model, error metric, data or experiment.'}
Path(__file__).with_name('arithmetic_check.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(result,ensure_ascii=False))
