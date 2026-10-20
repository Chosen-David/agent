"""Independent owned test log capture; never rewrites producer evidence."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
label = sys.argv[1]
records = []
commands = [
    [sys.executable, '-m', 'unittest', 'tests.test_memory_index', 'tests.test_memory_retrieval',
     'tests.test_memory_check', 'tests.test_memory_context_closure', 'tests.test_memory_cli_input', '-v'],
    [sys.executable, '-O', '-m', 'unittest', 'tests.test_memory_index', '-v'],
]
for i, command in enumerate(commands):
    done = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    name = f'independent-tests-{label}-{i}.log'
    target = OUT / name
    with target.open('xb') as stream:
        stream.write(done.stdout)
    records.append({'command': command, 'exit_code': done.returncode, 'log': name,
                    'log_sha256': hashlib.sha256(done.stdout).hexdigest()})
payload = {'tested_code_sha256': hashlib.sha256((ROOT / 'agent_runtime/project_memory.py').read_bytes()).hexdigest(),
           'commands': records}
with (OUT / f'independent-tests-{label}.json').open('x', encoding='utf-8') as stream:
    stream.write(json.dumps(payload, indent=2) + '\n')
print(json.dumps(payload, indent=2))
sys.exit(int(any(r['exit_code'] for r in records)))
