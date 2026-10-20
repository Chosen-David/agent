"""Paired Python allocation test; no RSS, latency, or model-quality claim.

Run from the checkout: python scripts/benchmark_artifact_read.py
The baseline commit must be available locally. Fixtures are outside tracing.
"""
import gc
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import tracemalloc
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from agent_runtime import result_validation as rv
from agent_runtime.dispatch_context import prepare_dispatch
from tests.test_dispatch_context import DispatchContextTests

BASELINE = 'a55a3d14d8ebf0f840c4bdd9477562fdc369fe44'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def measure(call):
    gc.collect()
    tracemalloc.start()
    try:
        try:
            result = call()
            outcome = ('ok', result)
        except ValueError as exc:
            outcome = (type(exc).__name__, str(exc))
        peak = tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()
    return outcome, peak


def main():
    source = subprocess.check_output(
        ['git', 'show', BASELINE + ':agent_runtime/result_validation.py'], cwd=ROOT)
    namespace = dict(rv.__dict__)
    exec(compile(source, '<frozen baseline>', 'exec'), namespace)
    readers = [('baseline', namespace['_bytes']), ('candidate', rv._bytes)]
    rows = []
    real_fstat = os.fstat
    sizes = (0, 5, 4096, 65535, 65536, 1024 * 1024, rv.LIMIT)
    cases = [('stable', size, size) for size in sizes]
    cases += [('growth', start, end) for start in (0, 1, 65535, 8 * 1024 * 1024)
              for end in (rv.LIMIT, rv.LIMIT + 1)]
    cases += [('shrink', 65535, 0), ('shrink', 8 * 1024 * 1024, 5)]
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        path = root / 'artifact'
        for label, start, end in cases:
            initial, payload = b'a' * start, b'z' * end
            row = {'kind': label, 'initial_size': start, 'final_size': end,
                   'initial_sha256': digest(initial if start != end else payload),
                   'input_sha256': digest(payload), 'baseline': [], 'candidate': []}
            def change(fd):
                info = real_fstat(fd)
                path.write_bytes(payload)
                return info
            for rep in range(-2, 5):
                for name, read in readers:
                    path.write_bytes(initial if start != end else payload)
                    with patch.object(rv.os, 'fstat', change if start != end else real_fstat):
                        outcome, peak = measure(lambda: read(root, 'artifact'))
                    if end > rv.LIMIT:
                        assert outcome == ('ResultValidationError', 'artifact grew beyond verification bound')
                    else:
                        assert outcome == ('ok', payload)
                    if rep >= 0:
                        row[name].append(peak)
            row['outcome'] = {'status': outcome[0], 'sha256': digest(outcome[1])} if outcome[0] == 'ok' else {'status': outcome[0], 'message': outcome[1]}
            row['ratio'] = statistics.median(row['candidate']) / statistics.median(row['baseline'])
            row['gate'] = row['ratio'] <= 1.01
            rows.append(row)
    case = DispatchContextTests()
    case.setUp()
    try:
        dispatch = {'baseline': [], 'candidate': [], 'packet_equal': True,
                    'request_sha256': digest(json.dumps(case.request, sort_keys=True).replace(str(case.root), '<ROOT>').encode()),
                    'input_hashes': case.request['context_refs']}
        reference = None
        for rep in range(-2, 5):
            for name, read in readers:
                with patch.object(rv, '_bytes', read):
                    outcome, peak = measure(lambda: prepare_dispatch(case.root, case.request))
                assert outcome[0] == 'ok'
                if reference is None:
                    reference = outcome[1]
                assert outcome[1] == reference
                if rep >= 0:
                    dispatch[name].append(peak)
        dispatch['packet_chars'] = len(reference['input_text'])
        dispatch['normalized_packet_sha256'] = digest(json.dumps(reference, sort_keys=True).replace(str(case.root), '<ROOT>').encode())
        dispatch['ratio'] = statistics.median(dispatch['candidate']) / statistics.median(dispatch['baseline'])
        dispatch['gate'] = dispatch['ratio'] < 0.1
    finally:
        case.doCleanups()
    result = {'baseline_sha': BASELINE, 'baseline_source_sha256': digest(source),
              'candidate_source_sha256': digest((ROOT / 'agent_runtime/result_validation.py').read_bytes()),
              'script_sha256': digest(Path(__file__).read_bytes()),
              'python': sys.version, 'platform': platform.platform(),
              'command': ['python', 'scripts/benchmark_artifact_read.py'],
              'unit': 'tracemalloc peak bytes', 'warmups': 2, 'repeats': 5,
              'fixture_excluded': True, 'file_reads': rows, 'dispatch': dispatch,
              'accepted': all(r['gate'] for r in rows) and dispatch['gate']}
    print(json.dumps(result, indent=2))
    return 0 if result['accepted'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
