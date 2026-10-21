"""Independent read-only frozen-source and complete snapshot audit."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[2]
RUN = Path(__file__).resolve().parent
PRODUCER = ROOT / 'agent_doc/results/memory-pack-20261021'
sys.path.insert(0, str(ROOT))
from agent_runtime.result_validation import _snapshot
contract = json.loads((PRODUCER / 'contract.json').read_text(encoding='utf-8'))
manifest, plan, proof = _snapshot(ROOT, contract)
snapshot = json.loads((PRODUCER / 'strict-source-snapshot.json').read_text(encoding='utf-8'))
differences = []
for name, expected in snapshot.items():
    raw = (ROOT / name).read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected:
        differences.append({'path': name, 'expected': expected, 'actual': actual,
                            'lf_normalized_sha256': hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest()})
result = {'contract': contract, 'proof': proof,
          'artifact_role_counts': {k: len(v) for k,v in manifest['artifacts'].items()},
          'strict_snapshot_count': len(snapshot), 'strict_snapshot_current_differences': differences,
          'head_at_check': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT).decode().strip(),
          'status': 'all declared manifest hashes valid; strict snapshot differences listed separately'}
with (RUN / 'bindings-v1.json').open('x', encoding='utf-8') as stream:
    stream.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: result[k] for k in ('artifact_role_counts','strict_snapshot_count','strict_snapshot_current_differences','head_at_check')}))
