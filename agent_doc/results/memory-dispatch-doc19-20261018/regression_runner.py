"""Serial final regression; test durations are not performance measurements."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCES = ['agent_runtime/task_manifest.py', 'tests/test_dispatch_freshness.py']
def hashes():
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in SOURCES}

before = hashes()
results = []
for name, command in [('full', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v']),
                      ('reader', [sys.executable, '-m', 'unittest', 'discover', '-s', 'apps/paper-reader/tests', '-v'])]:
    start = time.monotonic()
    with (OUT / (name + '.log')).open('w') as log:
        proc = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    results.append({'name': name, 'command': command, 'exit_code': proc.returncode,
                    'test_wall_seconds_not_benchmark': time.monotonic() - start})
    print(name, proc.returncode, flush=True)
record = {'source_hashes_before': before, 'source_hashes_after': hashes(), 'results': results}
(OUT / 'final-regression.json').write_text(json.dumps(record, indent=2) + '\n')
sys.exit(0 if before == hashes() and all(r['exit_code'] == 0 for r in results) else 1)
