"""Independent bounded reader regression in the prepared native UTF-8 environment."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
env = dict(os.environ, PYTHONUTF8='1', PYTHONPATH=str(ROOT / '.agent-runs/memory-index96-native-reader') + os.pathsep + str(ROOT))
commands = [
    [sys.executable, '-m', 'unittest', 'tests.test_reader', '-v'],
    [sys.executable, '-m', 'unittest', 'discover', '-s', 'apps/paper-reader/tests', '-v'],
]
records = []
for i, command in enumerate(commands):
    result = subprocess.run(command, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    name = f'independent-reader-{i}.log'
    with (OUT / name).open('xb') as stream:
        stream.write(result.stdout)
    records.append({'command': command, 'cwd': str(ROOT), 'PYTHONUTF8': '1',
                    'PYTHONPATH': env['PYTHONPATH'], 'log': name,
                    'log_sha256': hashlib.sha256(result.stdout).hexdigest(), 'exit_code': result.returncode})
with (OUT / 'independent-reader-checks.json').open('x', encoding='utf-8') as stream:
    stream.write(json.dumps(records, indent=2) + '\n')
print(json.dumps(records, indent=2))
sys.exit(int(any(r['exit_code'] for r in records)))
