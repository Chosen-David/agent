"""Preserve raw diagnostic subprocess output and exit codes."""
import json
from pathlib import Path
import subprocess
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
records = []
for mode in ('current', 'baseline'):
    command = ['wsl', '--cd', '/mnt/c/Users/WI/Desktop/home_work/AI_LLM/agent', '--exec',
               'python3', 'agent_doc/results/memory-index96-20261020/independent-diagnostic.py', mode]
    result = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log = 'independent-diagnostic-' + mode + '.log'
    (OUT / log).write_bytes(result.stdout)
    records.append({'mode': mode, 'command': command, 'exit_code': result.returncode, 'log': log})
(OUT / 'independent-diagnostic-checks.json').write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')
print(json.dumps(records, indent=2))
