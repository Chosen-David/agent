"""Explicit same-case repetition against the current parser; preserves originals."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

out = Path(__file__).resolve().parent
original = out.parent
root = out.parents[4]
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(name, value):
    (out / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

baseline_files = {str(p.relative_to(root)): digest(p) for p in original.iterdir() if p.is_file()}
old_lock = json.loads((original / 'input-lock.json').read_text())
files = [{'path': item['path'], 'sha256': digest(root / item['path']), 'bytes': (root / item['path']).stat().st_size, 'previous_sha256': item['sha256'], 'changed': digest(root / item['path']) != item['sha256']} for item in old_lock['files']]
save('input-lock.json', {'scope': 'Explicit repeated synthetic case, not an unseen test or GPU run', 'files': files, 'original_artifacts_before': baseline_files, 'capture_script_sha256': digest(Path(__file__))})
commands = [
    ('compiler-feedback', [sys.executable, '-B', str(root / 'plugins/research-assistant/skills/research-implement-optimize/scripts/compiler_feedback.py'), str(original.parent / 'forward-input.log')]),
    ('revision', ['git', 'rev-parse', 'HEAD']),
    ('task-check', ['rg', '-n', 'KERNEL-FEEDBACK', 'agent_doc/task/TASK.md']),
]
trace = []
for name, argv in commands:
    result = subprocess.run(argv, cwd=root, text=True, capture_output=True, check=False)
    entry = {'name': name, 'argv': argv, 'argv_json_sha256': hashlib.sha256(json.dumps(argv, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest(), 'cwd': str(root), 'returncode': result.returncode, 'stdout': result.stdout, 'stdout_sha256': hashlib.sha256(result.stdout.encode()).hexdigest(), 'stderr': result.stderr}
    trace.append(entry)
    if name == 'compiler-feedback':
        (out / 'compiler-feedback.stdout').write_text(result.stdout)
        save('compiler-feedback.json', json.loads(result.stdout))
save('tool-trace.json', trace)
current = json.loads(trace[0]['stdout'])
old = json.loads((original / 'compiler-feedback.json').read_text())
differences = []
def compare(left, right, path='$'):
    if type(left) is not type(right):
        differences.append({'path': path, 'old': left, 'new': right})
    elif isinstance(left, dict):
        for key in sorted(set(left) | set(right)):
            if key not in left or key not in right:
                differences.append({'path': path + '.' + key, 'old': left.get(key), 'new': right.get(key), 'missing_old': key not in left, 'missing_new': key not in right})
            else:
                compare(left[key], right[key], path + '.' + key)
    elif isinstance(left, list):
        if len(left) != len(right):
            differences.append({'path': path, 'old': left, 'new': right})
        else:
            for i, (a, b) in enumerate(zip(left, right)):
                compare(a, b, path + '[' + str(i) + ']')
    elif left != right:
        differences.append({'path': path, 'old': left, 'new': right})
compare(old, current)
after = {str(p.relative_to(root)): digest(p) for p in original.iterdir() if p.is_file()}
stable_inputs = all(digest(root / item['path']) == item['sha256'] for item in files)
comparison = {'explicit_repetition': True, 'unseen_case': False, 'parser_exit_code': trace[0]['returncode'], 'json_equal': old == current, 'old_json_sha256': digest(original / 'compiler-feedback.json'), 'new_json_sha256': digest(out / 'compiler-feedback.json'), 'differences': differences, 'original_artifacts_unchanged': baseline_files == after, 'original_artifacts_after': after, 'source_inputs_stable_during_execution': stable_inputs, 'validation_status': 'pending independent review; producer output comparison only', 'gpu_execution': False}
save('comparison.json', comparison)
print(json.dumps({k: comparison[k] for k in ('parser_exit_code', 'json_equal', 'differences', 'original_artifacts_unchanged', 'source_inputs_stable_during_execution')}))
