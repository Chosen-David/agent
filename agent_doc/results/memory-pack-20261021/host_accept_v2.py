"""Explicit host binding of the observed independent deployment-v2 review.

This archived replay is not automatic trust for another host or future source.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
RUN=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from agent_runtime.result_validation import inspect_result
from agent_runtime.result_store import ResultStore

REVIEW_SHA='5e2031b6521a7386b1d0e435f12aeaf4ef29da94cfb923c0a7b6a26d3c508f39'
ARCHIVE_SHA='967581a38ddb875958283fe43ed90e1f1b26867457d053ae9f2e305bed359375'


def digest(raw):return hashlib.sha256(raw).hexdigest()


if '--archive' in sys.argv:
    source=ROOT/'.agent-runs/memory-pack-20261021/deployment-v2'
    listing=(source/'archive-files-v2.json').read_bytes()
    if digest(listing)!=ARCHIVE_SHA:raise ValueError('archive listing changed')
    destination=RUN/'independent/deployment-v2'
    for entry in json.loads(listing)['files']:
        relative=Path(entry['relative_path'])
        if relative.is_absolute() or '..' in relative.parts:raise ValueError('archive path')
        raw=(source/relative).read_bytes()
        if digest(raw)!=entry['sha256']:raise ValueError('archive bytes changed')
        target=destination/relative;target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and target.read_bytes()!=raw:raise ValueError('immutable archive collision')
        target.write_bytes(raw)
    (destination/'archive-files-v2.json').write_bytes(listing)


def verify(root,manifest,plan):
    raw=(RUN/'independent/deployment-v2/review-v2.json').read_bytes()
    if digest(raw)!=REVIEW_SHA:raise ValueError('observed review changed')
    review=json.loads(raw)
    if review['verifier']['actor']!='/root/memory_index_verifier':raise ValueError('wrong actual owner')
    return review


contract=json.loads((RUN/'deployment-v2/contract.json').read_text(encoding='utf-8'))
result=inspect_result(ROOT,contract,verifier=verify)
if result['status']!='usable-with-scope':raise ValueError(result)
if '--archive' in sys.argv:
    (RUN/'deployment-v2/accepted.json').write_bytes((json.dumps({
        'host_observation':'Native collaboration deployment-v2 completion from /root/memory_index_verifier',
        'observed_review_sha256':REVIEW_SHA,'result':result},ensure_ascii=False,indent=2)+'\n').encode())
if '--register-reference' in sys.argv:
    # Keep frozen versioned evidence in the original run; catalog it as refs,
    # rather than falsely marking bytes as copied to the new registry run ID.
    record=ResultStore(ROOT).register(contract,historical=True,verifier=verify)
    print(json.dumps({'registered_reference':record.get('record_ref')}))
print(json.dumps({'status':result['status'],'review_sha256':REVIEW_SHA}))
