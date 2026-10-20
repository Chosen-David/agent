"""Freeze corrected v3 evidence; v1/v2 files remain historical and unaccepted."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from agent_runtime.result_validation import _snapshot, validate_result_plan


def ref(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


raw = json.loads((OUT / 'raw-native-v3.json').read_text(encoding='utf-8'))
plan = json.loads((OUT / 'validation_plan-native-v3.json').read_text(encoding='utf-8'))
write('config-native-v3.json', raw['config'])
write('environment-native-v3.json', raw['environment'])
revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
contracts, tasks = [], []
for unit in ('bytes', 'tokens'):
    contract = {'result_id': 'memory-index96-native-v3-' + unit + '-20261020',
                'producer_task_id': 'produce-native-' + unit, 'producer_actor': '/root',
                'manifest_path': (OUT / ('manifest-native-v3-' + unit + '.json')).relative_to(ROOT).as_posix(),
                'validation_plan': ref(OUT / 'validation_plan-native-v3.json'), 'scope': plan['scope']}
    manifest = {'schema_version': 'experiment-result/v1', **contract,
                'run_id': 'memory-index96-native-v3-20261020', 'code_revision': revision + '+dirty-bound-LF-source',
                'execution': {'command': ['python agent_doc/results/memory-index96-20261020/measure_native.py'],
                              'environment_description': 'Windows Python 3.12; UTF-8 real subprocess stdout, CRLF retained; pinned tiktoken==0.12.0/o200k_base, actual package/ranks/cache hashes in environment-native-v3.json',
                              'seeds': ['deterministic-24-record-fixtures'], 'repeats': 1},
                'artifacts': {
                    'code': [ref(ROOT / 'agent_runtime/project_memory.py'), ref(ROOT / 'agent_runtime/project_docs.py'),
                             ref(ROOT / 'tests/test_memory_index.py'), ref(ROOT / 'tests/test_memory_cli_input.py'),
                             ref(OUT / 'measure_native.py')],
                    'inputs': [ref(OUT / 'measure_native.py')], 'config': [ref(OUT / 'config-native-v3.json')],
                    'raw_data': [ref(OUT / 'raw-native-v3.json')], 'outputs': [ref(OUT / 'raw-native-v3.json')],
                    'environment': [ref(OUT / 'environment-native-v3.json')]},
                'metrics': [{'name': row['shape'] + '-read-' + str(row['read_entries']) + '-candidate',
                             'value': row['candidate_' + unit], 'unit': 'byte' if unit == 'bytes' else 'token'}
                            for row in raw['observations']]}
    write('manifest-native-v3-' + unit + '.json', manifest)
    write('contract-native-v3-' + unit + '.json', contract)
    _snapshot(ROOT, contract)
    contracts.append(contract)
    tasks.extend([{'task_id': contract['producer_task_id'], 'owner': '/root', 'task_type': 'experiment',
                   'produces_data': True, 'experiment_result': contract, 'depends_on': []},
                  {'task_id': 'verify-native-' + unit, 'owner': '/root/memory_index_verifier',
                   'action': 'verify_experiment_result', 'result_validation': contract,
                   'depends_on': [contract['producer_task_id']]}])
tasks.append({'task_id': 'report-and-publication-native-v3', 'owner': '/root',
              'depends_on': ['verify-native-bytes', 'verify-native-tokens'], 'required_result_refs': contracts})
dag = {'tasks': tasks}
validate_result_plan(dag)
write('validation-dag-native-v3.json', dag)
print('v3 contracts structurally checked, pending independent validation')
