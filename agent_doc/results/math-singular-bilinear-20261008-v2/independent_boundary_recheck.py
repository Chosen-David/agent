"""Recheck repaired numerical boundaries without executing producer main."""
import importlib.util,json,warnings,hashlib,time
from pathlib import Path
from unittest.mock import patch
import numpy as np
BASE=Path(__file__).resolve().parent
def main():
    started=time.perf_counter();sp=importlib.util.spec_from_file_location('producer_readonly_boundary',BASE/'validate.py');p=importlib.util.module_from_spec(sp);sp.loader.exec_module(p)
    cases=[('finite_scale_overflow_C',[1e308,1.],[1e308,1.],np.eye(2),1),('finite_H_overflow_C',[2.,1.],[2.,1.],np.diag([1e308,1.]),1),('tiny_supported_scales',[1e-320,1.],[1.,1.],np.ones((2,2)),1),('mixed_tiny_and_large_H',[1e-320,1.],[1.,1.],np.array([[1e308,1e308],[1.,1.]]),1),('finite_H_reconstruction_overflow',[1.,1.],[1.,1.],np.full((2,2),1.7e308),1),('tail_only_overflow',[1.,1.],[1.,1.],np.diag([1e155,1e155]),1)]
    out=[]
    for name,a,b,H,r in cases:
        row={'id':name,'a':a,'b':b,'H':H.tolist(),'r':r,'all_inputs_finite':True,'expected':'ValueError'}
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            try:p.solve(np.eye(2),a,np.eye(2),b,H,r)
            except ValueError as e:row.update(outcome='rejected',message=str(e))
            else:raise AssertionError('unsafe accepted case '+name)
            row['warnings']=[str(x.message) for x in w]
        out.append(row)
    args=[np.eye(2),[1.,1.],np.eye(2),[1.,1.],np.eye(2),1]
    # Explicitly injected faults test error paths; they are not observed backend failures.
    for name,kw in [('injected_nonconvergence',{'side_effect':np.linalg.LinAlgError('injected independent nonconvergence')}),('injected_nonfinite_left',{'return_value':(np.full((2,2),np.inf),np.ones(2),np.eye(2))}),('injected_nonfinite_singular',{'return_value':(np.eye(2),np.array([np.inf,1.]),np.eye(2))}),('injected_nonfinite_right',{'return_value':(np.eye(2),np.ones(2),np.full((2,2),np.nan))})]:
        with patch.object(p.np.linalg,'svd',**kw):
            try:p.solve(*args)
            except ValueError as e:out.append({'id':name,'kind':'injected error-path check, not backend observation','outcome':'rejected','message':str(e)})
            else:raise AssertionError(name)
    # A representable small nonzero direction is accepted and remains mathematically nonzero.
    H=np.array([[0.,0.],[1e6,0.]]);z=p.solve(np.eye(2),[1.,1e-6],np.eye(2),[1.,1.],H,1)
    assert np.all(np.isfinite(z['M'])) and np.linalg.norm(z['M']-H)==0 and z['tail']==0
    result={'status':'scoped-boundary-repair-passes','guard_cases':out,'representable_small_direction':{'a':[1.,1e-6],'b':[1.,1.],'H':H.tolist(),'M':z['M'].tolist(),'tail':z['tail']},'limitations':['Finite intermediate/output guards are range guards, not condition-number or numerical-accuracy certificates.','Injected error cases do not establish an observed NumPy nonconvergence event.'],'producer_code_sha256':hashlib.sha256((BASE/'validate.py').read_bytes()).hexdigest(),'diagnostic_seconds':time.perf_counter()-started}
    (BASE/'independent_boundary_observations.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'guards':len(out),'representable_small_direction':'passed','diagnostic_seconds':result['diagnostic_seconds']}))
if __name__=='__main__':main()
