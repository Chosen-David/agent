"""SYSTEM-99 scoped historical registration; default mode is read-only."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from agent_runtime.result_store import ResultStore

BASE = '50c1ca1e74df1026ba05b4cfd53903605315b234'
RUN = 'result-fd95'
NAMES = ('after-opt.log', 'after.log', 'before.log', 'independent-plan-v1.md',
         'independent-plan-v2.md', 'independent-raw-normal.json', 'independent-raw-opt.json',
         'independent-regression.log', 'independent-result.md', 'independent_matrix.py',
         'plan.md', 'reader.log', 'report.md', 'research.md')
SUMMARY = ('RESULT-FD-95 result-fd95 historical descriptor-ownership repair; '
           'original failure/regression logs, independent raw matrix and scoped review; '
           'discovery only; current validation unknown; private full log unavailable')


def references():
    refs = []
    for name in NAMES:
        rel = 'agent_doc/results/' + RUN + '/' + name
        path = ROOT / rel
        data = path.read_bytes()
        old = subprocess.check_output(['git', 'show', BASE + ':' + rel], cwd=ROOT)
        if not path.is_file() or path.is_symlink() or data != old:
            raise RuntimeError('historical bytes changed: ' + rel)
        refs.append({'path': rel, 'sha256': hashlib.sha256(data).hexdigest()})
    return refs


def observe(store):
    queries = {}
    for query in ('RESULT-FD-95', RUN):
        found = store.search(query, limit=20, max_scan=5000)
        queries[query] = {'scanned': found['scanned'], 'partial': found['partial'],
                          'errors': len(found['errors']),
                          'target_errors': [e for e in found['errors'] if e['run_id'] == RUN],
                          'target_hits': [h for h in found['results'] if h['run_id'] == RUN]}
    return queries


if __name__ == '__main__':
    if sys.argv[1:] not in ([], ['--register'], ['--after']):
        raise SystemExit('use no arguments, --register, or --after')
    refs = references()
    store = ResultStore(ROOT)
    result = {'refs': refs, 'queries_before': observe(store)}
    if sys.argv[1:] == ['--register']:
        store.register_history(RUN, SUMMARY, refs, context={}, measured_at=None)
    if sys.argv[1:] in (['--register'], ['--after']):
        shown = store.show(RUN)
        record = shown['record']
        expected = {'origin': 'historical-external-reference', 'contract': None,
                    'context': {}, 'measured_at': None,
                    'validation_at_registration': {'status': 'unknown', 'proof': None}}
        if (any(record.get(k) != v for k, v in expected.items())
                or record['historical_artifacts'] != refs):
            raise RuntimeError('historical record scope changed')
        verifier_calls = []
        def verifier_spy(*args):
            verifier_calls.append(args)
            return True
        decision = store.decide_run(RUN, {}, verifier=verifier_spy)
        if (decision['decision'] != 'verify_delta' or decision['validation_status'] != 'unknown'
                or decision['proof'] is not None or decision['automatic_skip_authorized']
                or verifier_calls):
            raise RuntimeError('registration promoted historical trust')
        queries = observe(store)
        for query, found in queries.items():
            if (len(found['target_hits']) != 1 or found['target_errors']
                    or found['target_hits'][0]['record_sha256'] != shown['record_ref']['sha256']):
                raise RuntimeError('registered result not discoverable: ' + query)
        result.update(record_ref=shown['record_ref'], decision=decision, queries_after=queries)
    print(json.dumps(result, ensure_ascii=False, indent=2))
