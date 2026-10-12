"""Generate content bindings from actual files; no fabricated acceptance."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[3]
run = Path(__file__).parent
prefix = run.relative_to(root).as_posix()
def ref(path):
    return {'path':path,'sha256':hashlib.sha256((root/path).read_bytes()).hexdigest()}
data = json.loads((run/'measurement.json').read_text())
plan = json.loads((run/'validation_plan.json').read_text())
print(json.dumps({
    'schema_version':'experiment-result/v1','result_id':'artifact-bound-cpu-20261012-2221',
    'producer_task_id':'ART-BOUND-01','producer_actor':'root', 'run_id':run.name,
    'manifest_path':prefix+'/manifest.json','validation_plan':ref(prefix+'/validation_plan.json'),
    'scope':plan['scope'],'code_revision':data['baseline']+'+working-tree-bound-candidate',
    'execution':{'command':['python '+prefix+'/measure.py','python -m unittest discover -s tests'],
        'environment_description':data['python']+'; '+data['platform']+'; local CPU only',
        'seeds':[2221],'repeats':7},
    'artifacts':{
        'code':[ref('agent_runtime/artifact_context.py'),ref(prefix+'/measure.py'),ref('tests/test_artifact_bound.py'),
                ref('tests/test_artifact_identical_fastpath.py'),ref('tests/test_artifact_localized_diff.py')],
        'inputs':[ref(prefix+'/measure.py')],'config':[ref(prefix+'/validation_plan.json')],
        'raw_data':[ref(prefix+'/measurement.json')],
        'outputs':[ref(prefix+'/tests-final.log'),ref(prefix+'/full-tests-final.log')],
        'environment':[ref(prefix+'/measurement.json')]},
    'metrics':[{'name':k,'value':data[v],'unit':unit} for k,v,unit in
        [('baseline_median','baseline_median_ms','milliseconds'),('candidate_median','candidate_median_ms','milliseconds'),
         ('reduction','reduction_fraction','dimensionless'),('complete_entry_checks','checks','count')]]
},indent=2))
