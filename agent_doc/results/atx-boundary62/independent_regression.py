"""Persist actual independent bounded regression commands and complete outputs."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
out = Path(__file__).with_name('independent-regression-v2.json')
if out.exists():
    raise SystemExit('refusing to overwrite evidence')
source = root / 'agent_runtime/knowledge_index.py'
hash_before = hashlib.sha256(source.read_bytes()).hexdigest()
rows = []
for extra, directory, pattern in [([], 'tests', 'test_knowledge_atx.py'),
                                  (['-O'], 'tests', 'test_knowledge_atx.py'),
                                  ([], 'tests', 'test_knowledge_index*.py'),
                                  ([], 'apps/paper-reader/tests', 'test*.py')]:
    command = [sys.executable, *extra, '-m', 'unittest', 'discover', '-s', directory, '-p', pattern, '-v']
    run = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=60)
    rows.append(dict(command=command, returncode=run.returncode, stdout=run.stdout, stderr=run.stderr))
hash_after = hashlib.sha256(source.read_bytes()).hexdigest()
with out.open('x') as handle:
    json.dump(dict(source_before=hash_before, source_after=hash_after, runs=rows), handle, indent=2)
print(json.dumps(dict(source_unchanged=hash_before == hash_after, codes=[r['returncode'] for r in rows])))
if hash_before != hash_after or any(row['returncode'] for row in rows):
    raise SystemExit(1)
