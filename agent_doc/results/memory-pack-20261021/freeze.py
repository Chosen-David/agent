"""Bind actual measured files after execution; independent review owns acceptance."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[3]
RUN=Path(__file__).resolve().parent
REL=RUN.relative_to(ROOT).as_posix()
sys.path.insert(0,str(ROOT))
from agent_runtime.result_validation import validate_result_plan


def ref(relative):
    return {'path':relative,'sha256':hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()}


plan=json.loads((RUN/'validation_plan.json').read_text(encoding='utf-8'))
contract={'result_id':'memory-pack-20261021-v1','producer_task_id':'produce-memory-pack',
          'producer_actor':'/root','manifest_path':REL+'/manifest.json',
          'validation_plan':ref(REL+'/validation_plan.json'),'scope':plan['scope']}
deps=json.loads((RUN/'dependencies.json').read_text(encoding='utf-8'))
code=set(deps['code'])|{'agent_runtime/handoff_encoding.py','agent_runtime/handoff_basis.py',
    'tests/test_memory_tables.py','tests/test_handoff_encoding.py','tests/test_selective_context.py',
    REL+'/measure.py',REL+'/freeze.py',REL+'/run_checks.py','tests/test_external_json_boundaries.py',
    'tests/test_memory_context_closure.py',REL+'/run_strict_ext4.py'}
# Include the executable regression dependency surface, excluding unrelated
# untracked user work. The measurement also records actually imported modules.
tracked=subprocess.check_output(['git','ls-files','-z','agent_runtime','scripts'],cwd=ROOT).decode().split('\0')
code.update(p for p in tracked if p.endswith('.py'))
raw=json.loads((RUN/'raw.json').read_text(encoding='utf-8'))
metrics=[]
for case in raw['cases']:
    for fmt,value in case['formats'].items():
        for unit in ('tokens','bytes'):
            metrics.append({'name':case['case']+':'+fmt+':'+unit,'value':value[unit],
                            'unit':'o200k_base text tokens' if unit=='tokens' else 'UTF-8 bytes'})
manifest={'schema_version':'experiment-result/v1',**contract,'run_id':'memory-pack-20261021',
          'code_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()+'+bound-dirty',
          'execution':{'command':['python -X utf8 '+REL+'/measure.py --output '+REL],
            'environment_description':'Windows Python 3.12, pinned tiktoken 0.12.0/o200k_base; complete final payload strings, no stdout framing or model invocation',
            'seeds':['deterministic-v1'],'repeats':1},
          'artifacts':{'code':[ref(p) for p in sorted(code)],
             'inputs':[ref(REL+'/inputs.json'),ref(REL+'/strict-source-snapshot.json')]+[ref(p) for p in deps['corpus']],
             'config':[ref(REL+'/config.json')],
             'raw_data':[ref(REL+'/raw.json'),ref(REL+'/targeted-tests.txt'),ref(REL+'/strict-boundaries-ext4.txt')],
             'outputs':[ref(REL+'/dependencies.json')],
             'environment':[ref(REL+'/environment.json')]},'metrics':metrics}
dag={'tasks':[
    {'task_id':'produce-memory-pack','owner':'/root','task_type':'experiment','produces_data':True,
     'experiment_result':contract,'depends_on':[]},
    {'task_id':'verify-memory-pack','owner':'/root/memory_index_verifier','action':'verify_experiment_result',
     'result_validation':contract,'depends_on':['produce-memory-pack']},
    {'task_id':'publish-memory-pack','owner':'/root','required_result_refs':[contract],
     'depends_on':['verify-memory-pack']}]}
validate_result_plan(dag)
for name,value in [('contract.json',contract),('manifest.json',manifest),('validation-dag.json',dag)]:
    (RUN/name).write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'status':'pending','code_files':len(code),'corpus_files':len(deps['corpus'])}))
