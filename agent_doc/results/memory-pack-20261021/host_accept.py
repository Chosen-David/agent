"""Replay this host's observed native independent review, not general JSON trust.

The root host received completion from /root/memory_index_verifier on this task.
Reusing this script elsewhere requires that host to authenticate its own reviewer.
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

REVIEW_SHA='9bf84cced46344ce1e6d95c5291a1b70dba7e32bd28b7a69047eef2e2f838747'
ARCHIVE_SHA='6d87452354abcf023ffe5424bcea6c6e76c9c1f4ad556e17649af889fd543d62'


def digest(data):
    return hashlib.sha256(data).hexdigest()


if '--archive' in sys.argv:
    source=ROOT/'.agent-runs/memory-pack-20261021'
    listing=(source/'archive-files-v1.json').read_bytes()
    if digest(listing)!=ARCHIVE_SHA:raise ValueError('archive listing changed')
    data=json.loads(listing)
    destination=RUN/'independent'
    for entry in data['files']:
        relative=Path(entry['relative_path'])
        if relative.is_absolute() or '..' in relative.parts:raise ValueError('archive path')
        raw=(source/relative).read_bytes()
        if digest(raw)!=entry['sha256']:raise ValueError('archive bytes changed')
        target=destination/relative;target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and target.read_bytes()!=raw:raise ValueError('immutable archive collision')
        target.write_bytes(raw)
    (destination/'archive-files-v1.json').write_bytes(listing)


def verify(root,manifest,plan):
    raw=(RUN/'independent/review-v1.json').read_bytes()
    if digest(raw)!=REVIEW_SHA:raise ValueError('observed review changed')
    review=json.loads(raw)
    if review['verifier']['actor']!='/root/memory_index_verifier':raise ValueError('wrong actual owner')
    return review


contract=json.loads((RUN/'contract.json').read_text(encoding='utf-8'))
result=inspect_result(ROOT,contract,verifier=verify)
if result['status']!='usable-with-scope':raise ValueError(result)
if '--archive' in sys.argv:
    (RUN/'accepted.json').write_bytes((json.dumps({
        'host_observation':'Native collaboration completion from /root/memory_index_verifier; explicit root-host binding',
        'observed_review_sha256':REVIEW_SHA,'result':result},ensure_ascii=False,indent=2)+'\n').encode())
if '--register' in sys.argv:
    record=ResultStore(ROOT).register(contract,verifier=verify)
    print(json.dumps({'registered':record.get('record_ref',record.get('run_id'))}))
print(json.dumps({'status':result['status'],'review_sha256':REVIEW_SHA}))
