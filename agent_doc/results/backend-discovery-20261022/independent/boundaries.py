import importlib.util,json
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('independent_discover',ROOT/'scripts/discover_backends.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def entry(d):return {'id':'fixture','adoption':'test','category':'test','repo':'local','detect':d}
cases=[]
with patch.object(m.importlib.metadata,'packages_distributions') as mp:
    v=m.probe_backend(entry({}))
    assert v['status']=='manual_check' and v['python_versions']=={}
    mp.assert_not_called();cases.append('empty probes')
with patch.object(m.importlib.util,'find_spec',return_value=None),patch.object(m.importlib.metadata,'packages_distributions') as mp,patch.object(m.importlib.metadata,'version',side_effect=lambda n:{'second':'2','first':'1'}[n]):
    v=m.probe_backend(entry({'python_modules':['missing'],'python_distributions':['second','first']}))
    assert v['status']=='not_detected' and v['detected_version']=='2' and v['version_source']=='python_distribution:second'
    mp.assert_not_called();cases.append('declared priority while module absent')
with patch.object(m.importlib.util,'find_spec',return_value=object()),patch.object(m.importlib.metadata,'packages_distributions',side_effect=[{'present':['distA']},{'present':['distB']}]) as mp,patch.object(m.importlib.metadata,'version',side_effect=lambda n:{'distA':'A','distB':'B'}[n]):
    a=m.probe_backend(entry({'python_modules':['present']}));b=m.probe_backend(entry({'python_modules':['present']}))
    assert a['python_versions']=={'distA':'A'} and b['python_versions']=={'distB':'B'} and mp.call_count==2
    cases.append('fresh standalone mapping and inferred versions')
with patch.object(m.importlib.util,'find_spec',side_effect=AssertionError('parent import forbidden')),patch.object(m.importlib.metadata,'packages_distributions') as mp:
    v=m.probe_backend(entry({'python_modules':['parent.child']}))
    assert v['probe_errors'] and v['status']=='not_detected';mp.assert_not_called();cases.append('dotted module skip')
with patch.object(m.importlib.util,'find_spec',return_value=object()),patch.object(m.importlib.metadata,'packages_distributions',side_effect=RuntimeError('broken')),patch.object(m.importlib.metadata,'version',return_value='D'):
    v=m.probe_backend(entry({'python_modules':['present'],'python_distributions':['declared']}))
    assert v['status']=='available' and v['python_versions']=={'declared':'D'};cases.append('mapping failure preserves declared metadata')
print(json.dumps({'passed':len(cases),'cases':cases}))
