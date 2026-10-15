"""Read-only verification of this historical evidence's discoverability/trust."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from agent_runtime.result_store import ResultStore


def run():
    store = ResultStore(ROOT)
    run_id = 'memory-storage-20261015'
    shown = store.show(run_id)
    record = shown['record']
    if (record['origin'] != 'historical-external-reference' or record['contract'] is not None
            or record['validation_at_registration'] != {'status': 'unknown', 'proof': None}):
        raise ValueError('registration must not invent a native validation contract')
    for ref in record['historical_artifacts']:
        if hashlib.sha256((ROOT / ref['path']).read_bytes()).hexdigest() != ref['sha256']:
            raise ValueError('historical artifact changed: ' + ref['path'])
    results = {}
    for query in ('MemoryLedger SQLite retrieval', run_id):
        result = store.search(query, limit=5, max_scan=200)
        if not result['results'] or result['results'][0]['run_id'] != run_id:
            raise ValueError('specific query no longer finds target first: ' + query)
        hit = result['results'][0]
        if hit['stored_validation'] != 'unknown' or hit['applicability'] != 'unchecked':
            raise ValueError('discovery must not promote trust')
        results[query] = {'rank': 1, 'partial': result['partial'], 'errors': len(result['errors'])}
    decisions = []
    for context in ({}, record['context']):
        for flags in ({}, {'new_claim': True}, {'explicit_reproduction': True}):
            value = store.decide_run(run_id, context, **flags)
            if (value['decision'] != ('rerun' if flags else 'verify_delta')
                    or value['validation_status'] != 'unknown' or value['proof'] is not None
                    or value['automatic_skip_authorized']):
                raise ValueError('historical evidence bypassed current validation')
            decisions.append({'flags': flags, 'decision': value['decision']})
    return {'record_ref': shown['record_ref'], 'queries': results, 'decisions': decisions,
            'scope': 'registry discoverability and refusal to auto-authorize reuse only'}


if __name__ == '__main__':
    print(json.dumps(run(), ensure_ascii=False, indent=2))
