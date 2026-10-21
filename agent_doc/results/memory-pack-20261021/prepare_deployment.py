"""Versioned rebind after unrelated concurrent main changes; retain v1 bytes."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[3]
RUN=Path(__file__).resolve().parent
DEST=RUN/'deployment-v2';REL=DEST.relative_to(ROOT).as_posix()
sys.path.insert(0,str(ROOT))
from agent_runtime.result_validation import validate_result_plan


def read(path):return json.loads(path.read_text(encoding='utf-8'))
def write(path,value):path.write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode())
def ref(path):return {'path':path,'sha256':hashlib.sha256((ROOT/path).read_bytes()).hexdigest()}


if '--prepare' in sys.argv:
    plan=read(RUN/'validation_plan.json')
    plan['scope']+='; deployment v2 on d9fdf9b3 with isolated dispatch-scope delta and explicit v1 regression bridge'
    plan['criteria']['implementation']['procedure']+=' Review only the concurrent dispatch_context/default-write-scope delta and its tests; require unchanged measured entry point/encoder/strict/counter/corpus identities to bridge v1 regressions.'
    plan['criteria']['reproducibility']['procedure']+=' Reuse the independently accepted v1 52-test and property observations only with exact key-source/config/tokenizer/corpus equivalence; freshly run dispatch and Linux strict regressions.'
    write(DEST/'validation_plan.json',plan)
    source=(RUN/'run_strict_ext4.py').read_text(encoding='utf-8')
    source=source.replace('parents[3]','parents[4]').replace(
        '.agent-runs/memory-pack-20261021/strict-source.zip',
        '.agent-runs/memory-pack-20261021/deployment-v2/strict-source.zip')
    (DEST/'run_strict_ext4.py').write_bytes(source.encode())

if '--freeze' in sys.argv:
    plan=read(DEST/'validation_plan.json')
    contract={'result_id':'memory-pack-deployment-20261021-v2','producer_task_id':'produce-memory-pack-v2',
              'producer_actor':'/root','manifest_path':REL+'/manifest.json',
              'validation_plan':ref(REL+'/validation_plan.json'),'scope':plan['scope']}
    manifest=read(RUN/'manifest.json')
    manifest.update(contract)
    manifest['run_id']='memory-pack-deployment-20261021-v2'
    manifest['code_revision']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()+'+bound-dirty'
    manifest['execution']['command']=['python -X utf8 '+RUN.relative_to(ROOT).as_posix()+'/measure.py --output '+REL,
        'python -X utf8 '+REL+'/run_strict_ext4.py','python -X utf8 -m unittest tests.test_dispatch_context -v']
    manifest['execution']['environment_description']+='; prior 52-test regression/property data bridged only across unchanged relevant source; fresh dispatch and strict24 tests'
    artifacts=manifest['artifacts']
    code={entry['path'] for entry in artifacts['code']}|{
        'tests/test_dispatch_context.py',RUN.relative_to(ROOT).as_posix()+'/prepare_deployment.py',
        REL+'/run_strict_ext4.py',REL+'/old-dispatch_context.py',REL+'/old-test_dispatch_context.py'}
    artifacts['code']=[ref(p) for p in sorted(code)]
    artifacts['inputs']=[ref(REL+'/inputs.json'),ref(REL+'/strict-source-snapshot.json'),
        ref(RUN.relative_to(ROOT).as_posix()+'/independent/review-v1.json')]+[
        ref(entry['path']) for entry in artifacts['inputs'] if entry['path'].startswith('knowledge/')]
    artifacts['raw_data']=[ref(REL+'/raw.json'),ref(REL+'/dispatch-tests.txt'),ref(REL+'/strict-boundaries-ext4.txt'),
                          ref(RUN.relative_to(ROOT).as_posix()+'/targeted-tests.txt')]
    artifacts['outputs']=[ref(REL+'/dependencies.json')]
    artifacts['environment']=[ref(REL+'/environment.json')]
    manifest['metrics']=[]
    for case in read(DEST/'raw.json')['cases']:
        for fmt,value in case['formats'].items():
            for unit in ('tokens','bytes'):
                manifest['metrics'].append({'name':case['case']+':'+fmt+':'+unit,'value':value[unit],
                    'unit':'o200k_base text tokens' if unit=='tokens' else 'UTF-8 bytes'})
    dag={'tasks':[
        {'task_id':contract['producer_task_id'],'owner':'/root','task_type':'experiment','produces_data':True,'experiment_result':contract,'depends_on':[]},
        {'task_id':'verify-memory-pack-v2','owner':'/root/memory_index_verifier','action':'verify_experiment_result','result_validation':contract,'depends_on':[contract['producer_task_id']]},
        {'task_id':'publish-memory-pack-v2','owner':'/root','required_result_refs':[contract],'depends_on':['verify-memory-pack-v2']}]}
    validate_result_plan(dag)
    for name,value in [('contract.json',contract),('manifest.json',manifest),('validation-dag.json',dag)]:write(DEST/name,value)
    print(json.dumps({'status':'pending-independent-deployment-v2','manifest':REL+'/manifest.json'}))
