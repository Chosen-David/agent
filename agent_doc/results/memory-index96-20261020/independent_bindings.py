"""Verify frozen artifacts/metric mapping; structured hashes are not acceptance."""
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from agent_runtime.result_validation import _snapshot
raw = json.loads((OUT / 'raw-native-v3.json').read_text(encoding='utf-8'))
require = lambda cond, reason: None if cond else (_ for _ in ()).throw(AssertionError(reason))
proofs = {}
for unit, suffix in (('byte', 'bytes'), ('token', 'tokens')):
    contract = json.loads((OUT / f'contract-native-v3-{suffix}.json').read_text(encoding='utf-8'))
    manifest, plan, proof = _snapshot(ROOT, contract)
    for ref in manifest['artifacts']['config']:
        require(json.loads((ROOT / ref['path']).read_text(encoding='utf-8')) == raw['config'], 'config mismatch')
    for ref in manifest['artifacts']['environment']:
        require(json.loads((ROOT / ref['path']).read_text(encoding='utf-8')) == raw['environment'], 'environment mismatch')
    expected = {f"{r['shape']}-read-{r['read_entries']}-candidate": r['candidate_' + suffix] for r in raw['observations']}
    require({m['name']: m['value'] for m in manifest['metrics']} == expected, 'metric mapping')
    require(all(m['unit'] == unit for m in manifest['metrics']), 'metric units')
    proofs[suffix] = proof
label = '-' + sys.argv[1] if len(sys.argv) > 1 else ''
with (OUT / ('independent-bindings-v3' + label + '.json')).open('x', encoding='utf-8') as stream:
    stream.write(json.dumps({'status': 'bound-only; semantic acceptance separate', 'proofs': proofs}, indent=2) + '\n')
print(json.dumps({'contracts_verified': list(proofs)}))
