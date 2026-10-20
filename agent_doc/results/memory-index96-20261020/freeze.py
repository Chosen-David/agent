"""Freeze this producer's two bounded local observations, never self-accept."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from agent_runtime.result_validation import _snapshot, validate_result_plan


def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def ref(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
contracts, tasks = [], []
code = [ROOT / 'agent_runtime/project_memory.py', ROOT / 'agent_runtime/project_docs.py',
        ROOT / 'tests/test_memory_index.py', ROOT / 'tests/test_memory_cli_input.py']
for suffix, raw_name, script, plan_name, unit in [
        ('bytes', 'raw.json', 'measure.py', 'validation_plan.json', 'byte'),
        ('tokens', 'raw-tokens.json', 'measure_tokens.py', 'validation_plan-tokens-v2.json', 'token')]:
    raw = json.loads((OUT / raw_name).read_text(encoding='utf-8'))
    plan = json.loads((OUT / plan_name).read_text(encoding='utf-8'))
    write('config-' + suffix + '.json', raw['config'])
    write('environment-' + suffix + '.json', raw['environment'])
    contract = {'result_id': 'memory-index96-' + suffix + '-20261020',
                'producer_task_id': 'produce-' + suffix, 'producer_actor': '/root',
                'manifest_path': (OUT / ('manifest-' + suffix + '.json')).relative_to(ROOT).as_posix(),
                'validation_plan': ref(OUT / plan_name), 'scope': plan['scope']}
    metrics = []
    for row in raw['observations']:
        key = row['shape'] + '-read-' + str(row['read_entries'])
        metrics.append({'name': key + '-candidate', 'value': row['candidate_bytes' if suffix == 'bytes' else 'candidate_tokens'], 'unit': unit})
    manifest = {'schema_version': 'experiment-result/v1', **contract,
                'run_id': 'memory-index96-' + suffix + '-20261020',
                'code_revision': revision + '+dirty-bound-source-hashes',
                'execution': {'command': ['python agent_doc/results/memory-index96-20261020/' + script],
                              'environment_description': json.dumps(raw['environment'], ensure_ascii=False),
                              'seeds': ['deterministic-fixed-24-record-fixtures'], 'repeats': 1},
                'artifacts': {'code': [ref(p) for p in code + [OUT / script]],
                              'inputs': [ref(OUT / script)],
                              'config': [ref(OUT / ('config-' + suffix + '.json'))],
                              'raw_data': [ref(OUT / raw_name)],
                              'outputs': [ref(OUT / raw_name)],
                              'environment': [ref(OUT / ('environment-' + suffix + '.json'))]},
                'metrics': metrics}
    write('manifest-' + suffix + '.json', manifest)
    write('contract-' + suffix + '.json', contract)
    _snapshot(ROOT, contract)
    contracts.append(contract)
    tasks += [{'task_id': contract['producer_task_id'], 'owner': '/root', 'task_type': 'experiment',
               'produces_data': True, 'experiment_result': contract, 'depends_on': []},
              {'task_id': 'verify-' + suffix, 'owner': '/root/memory_index_verifier',
               'action': 'verify_experiment_result', 'result_validation': contract,
               'depends_on': [contract['producer_task_id']]}]
tasks.append({'task_id': 'report-and-publication', 'owner': '/root',
              'depends_on': ['verify-bytes', 'verify-tokens'], 'required_result_refs': contracts})
dag = {'tasks': tasks}
validate_result_plan(dag)
write('validation-dag.json', dag)
print(json.dumps({'contracts': len(contracts), 'state': 'pending-independent-validation'}))
