"""Independent held-out differential/allocation verification; run from checkout."""
import ast
import copy
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

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from agent_runtime import result_validation as rv
from agent_runtime.dispatch_context import prepare_dispatch
from tests.test_dispatch_context import DispatchContextTests

BASE = 'a55a3d14d8ebf0f840c4bdd9477562fdc369fe44'
OUT = Path(__file__).resolve().parent
sha = lambda data: hashlib.sha256(data).hexdigest()
source = subprocess.check_output(['git', 'show', BASE + ':agent_runtime/result_validation.py'], cwd=ROOT)
node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == '_bytes')
ns = dict(rv.__dict__)
exec(compile(ast.Module(body=[node], type_ignores=[]), '<independent original _bytes>', 'exec'), ns)
readers = [('baseline', ns['_bytes']), ('candidate', rv._bytes)]
fstat, fdopen, real_open = os.fstat, os.fdopen, os.open


def outcome(call):
    try:
        return ('ok', call())
    except (ValueError, OSError) as exc:
        return (type(exc).__name__, str(exc))


def brief(value):
    if value[0] == 'ok' and isinstance(value[1], bytes):
        return {'status': 'ok', 'bytes': len(value[1]), 'sha256': sha(value[1])}
    return {'status': value[0], 'message': value[1]}


def measure(call):
    gc.collect()
    tracemalloc.start()
    try:
        value = outcome(call)
        peak = tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()
    return value, peak


def payload(size):
    return (bytes(range(256)) * ((size + 255) // 256))[:size]


def main():
    result = {'reviewer': '/root/artifact76_verify', 'baseline_commit': BASE,
              'baseline_source_sha256': sha(source), 'candidate_source_sha256': sha((ROOT / 'agent_runtime/result_validation.py').read_bytes()),
              'probe_sha256': sha(Path(__file__).read_bytes()), 'python': sys.version,
              'platform': platform.platform(), 'cpu_count': os.cpu_count(),
              'command': ['python', 'agent_doc/results/artifact-read76/independent_probe.py'],
              'warmups': 2, 'repeats': 5, 'unit': 'tracemalloc peak bytes',
              'semantic': [], 'allocation': []}
    with tempfile.TemporaryDirectory(prefix='independent-read76-') as tmp:
        root = Path(tmp)
        p = root / 'blob'
        def compare(label, call):
            values = []
            for name, reader in readers:
                opened = []
                def tracked_open(*args, **kwargs):
                    fd = real_open(*args, **kwargs)
                    opened.append(fd)
                    return fd
                # fdopen(directory) raises with the fd in its message and leaves
                # that test-owned fd open in both versions. Reclaim it so the
                # exact baseline/candidate message uses the same descriptor.
                with patch.object(rv, '_bytes', reader), patch.object(rv.os, 'open', tracked_open):
                    try:
                        values.append(outcome(lambda: call(reader)))
                    finally:
                        for fd in opened:
                            try: os.close(fd)
                            except OSError: pass
            assert values[0] == values[1], (label, values)
            result['semantic'].append({'case': label, 'equal': True, 'outcome': brief(values[0])})
            return values[0]
        p.write_bytes(b'\x00\xff\r\n\x80')
        (root / 'link').symlink_to(p)
        (root / 'parent-link').symlink_to(root, target_is_directory=True)
        os.mkfifo(root / 'fifo')
        (root / 'directory').mkdir()
        for name in ('', '../blob', str(p), 'link', 'parent-link/blob', 'fifo', 'directory', 'missing'):
            compare('path:' + name, lambda read, name=name: read(root, name))
        for digest in (sha(p.read_bytes()), '0' * 64):
            compare('bound:' + digest, lambda _: rv._bound(root, {'path': 'blob', 'sha256': digest}))
        old = 'doc/results/run/data'
        moved = root / 'agent_doc/results/run/data'
        moved.parent.mkdir(parents=True)
        moved.write_bytes(b'legacy\x00\xff')
        marker = root / 'agent_doc/legacy-result-paths.json'
        marker.write_text(json.dumps({'schema_version': 'agent-doc-relocation/v1', 'files': {old: sha(moved.read_bytes())}}))
        compare('legacy:valid', lambda read: read(root, old))
        moved.write_bytes(b'corrupt')
        compare('legacy:stale', lambda read: read(root, old))
        moved.unlink()
        moved.symlink_to(p)
        compare('legacy:symlink', lambda read: read(root, old))
        moved.unlink()
        moved.write_bytes(b'legacy\x00\xff')
        original = root / old
        original.parent.mkdir(parents=True)
        original.write_bytes(b'collision')
        compare('legacy:collision', lambda read: read(root, old))

        calls = []
        class Stream:
            can_seek = False
            fail_seek = False
            def __init__(self, fd, mode): self.raw = fdopen(fd, mode)
            def __enter__(self): return self
            def __exit__(self, *args): self.raw.close()
            def fileno(self): return self.raw.fileno()
            def seekable(self): return self.can_seek
            def seek(self, offset):
                calls.append(['seek', offset])
                if self.fail_seek: raise OSError('held-out seek failure')
                return self.raw.seek(offset)
            def read(self, count):
                calls.append(['read', count])
                return self.raw.read(count)
        with patch.object(rv.os, 'fdopen', Stream):
            compare('nonseekable:binary', lambda read: read(root, 'blob'))
        assert calls == [['read', rv.LIMIT + 1]] * 2, calls
        result['nonseekable_calls'] = copy.deepcopy(calls)
        calls.clear()
        Stream.can_seek = True
        Stream.fail_seek = True
        p.write_bytes(b'a')
        def mutate(fd):
            info = fstat(fd)
            p.write_bytes(b'held-out growth')
            return info
        with patch.object(rv.os, 'fstat', mutate), patch.object(rv.os, 'fdopen', Stream):
            failed = outcome(lambda: readers[1][1](root, 'blob'))
        assert failed == ('OSError', 'held-out seek failure')
        result['seek_failure'] = {'outcome': brief(failed), 'calls': copy.deepcopy(calls), 'scope': 'new explicit failure path, not baseline equivalence claim'}

        sizes = (0, 2, 17, 65534, 65535, 65536, 1024 * 1024, rv.LIMIT, rv.LIMIT + 1)
        cases = [('stable', s, s) for s in sizes]
        cases += [('growth', a, b) for a in (0, 1, 37, 65535, 65536, 8 * 1024 * 1024) for b in (rv.LIMIT, rv.LIMIT + 1)]
        cases += [('shrink', 65534, 17), ('shrink', rv.LIMIT, 0)]
        for kind, a, b in cases:
            before, after = payload(a), payload(b)
            row = {'case': kind, 'initial_size': a, 'final_size': b, 'initial_sha256': sha(before), 'input_sha256': sha(after), 'baseline': [], 'candidate': []}
            def mutate(fd):
                info = fstat(fd)
                p.write_bytes(after)
                return info
            for rep in range(-2, 5):
                seen = []
                for name, reader in readers:
                    p.write_bytes(before)
                    with patch.object(rv.os, 'fstat', fstat if a == b else mutate):
                        value, peak = measure(lambda: reader(root, 'blob'))
                    seen.append(value)
                    if b <= rv.LIMIT:
                        assert value == ('ok', after), (kind, a, b, value[0])
                    else:
                        expected = 'artifact exceeds 16 MiB bound; use bounded shard manifests' if a == b else 'artifact grew beyond verification bound'
                        assert value == ('ResultValidationError', expected), value
                    if rep >= 0: row[name].append(peak)
                assert seen[0] == seen[1]
            row['outcome'] = brief(value)
            row['ratio'] = statistics.median(row['candidate']) / statistics.median(row['baseline'])
            assert row['ratio'] <= 1.01, row
            result['allocation'].append(row)

        # Record requests independently; large stable input must have only original read.
        calls.clear()
        Stream.fail_seek = False
        p.write_bytes(payload(65536))
        with patch.object(rv.os, 'fdopen', Stream):
            assert readers[1][1](root, 'blob') == payload(65536)
        assert calls == [['read', rv.LIMIT + 1]], calls
        result['large_read_calls'] = copy.deepcopy(calls)

    case = DispatchContextTests()
    case.setUp()
    try:
        normalized = lambda obj: json.dumps(obj, sort_keys=True).replace(str(case.root), '<ROOT>').encode()
        # Reproduce original producer input binding before held-out request change.
        result['producer_request_sha256_recomputed'] = sha(normalized(case.request))
        original_packet = prepare_dispatch(case.root, case.request)
        result['producer_packet_sha256_recomputed'] = sha(normalized(original_packet))
        case.request['instruction'] = 'Held-out binary-safe reader check; retain cancellation and unknown constraints.'
        dispatch = {'baseline': [], 'candidate': [], 'request_sha256': sha(normalized(case.request)), 'input_hashes': case.request['context_refs']}
        expected = prepare_dispatch(case.root, case.request)
        for rep in range(-2, 5):
            for name, reader in readers:
                with patch.object(rv, '_bytes', reader):
                    value, peak = measure(lambda: prepare_dispatch(case.root, case.request))
                assert value == ('ok', expected)
                if rep >= 0: dispatch[name].append(peak)
        dispatch['ratio'] = statistics.median(dispatch['candidate']) / statistics.median(dispatch['baseline'])
        dispatch['reduction_percent'] = 100 * (1 - dispatch['ratio'])
        dispatch['normalized_packet_sha256'] = sha(normalized(expected))
        dispatch['packet_equal'] = True
        assert dispatch['ratio'] < .1
        result['dispatch'] = dispatch
    finally:
        case.doCleanups()

    raw = json.loads((OUT / 'raw.json').read_text())
    assert raw['baseline_source_sha256'] == result['baseline_source_sha256']
    assert raw['candidate_source_sha256'] == result['candidate_source_sha256']
    assert raw['script_sha256'] == sha((ROOT / 'scripts/benchmark_artifact_read.py').read_bytes())
    assert len(raw['file_reads']) == 17
    assert raw['dispatch']['request_sha256'] == result['producer_request_sha256_recomputed']
    assert raw['dispatch']['normalized_packet_sha256'] == result['producer_packet_sha256_recomputed']
    for row in raw['file_reads'] + [raw['dispatch']]:
        for name in ('baseline', 'candidate'):
            assert len(row[name]) == 5 and all(type(x) is int and x >= 0 for x in row[name])
        ratio = statistics.median(row['candidate']) / statistics.median(row['baseline'])
        assert row['ratio'] == ratio
        assert row['gate'] == (ratio < .1 if row is raw['dispatch'] else ratio <= 1.01)
        if row is not raw['dispatch']:
            start, end = row['initial_size'], row['final_size']
            assert row['initial_sha256'] == sha((b'z' if start == end else b'a') * start)
            assert row['input_sha256'] == sha(b'z' * end)
            if end <= rv.LIMIT: assert row['outcome']['sha256'] == sha(b'z' * end)
    result['producer_integrity'] = 'all 17 rows, 5 pairs, medians, payload/code/input/output/request hashes verified'
    bindings = ['agent_runtime/result_validation.py', 'agent_runtime/dispatch_context.py', 'agent_runtime/legacy_result_paths.py', 'tests/test_result_read_allocation.py', 'tests/test_dispatch_context.py', 'scripts/benchmark_artifact_read.py']
    bindings += ['agent_doc/results/artifact-read76/' + f for f in ('plan.md', 'plan-v2.md', 'review-plan.md', 'raw.json', 'before.log', 'after.log', 'full-tests.log', 'reader-tests.log', 'independent_probe.py')]
    result['artifact_hashes'] = {p: sha((ROOT / p).read_bytes()) for p in bindings}
    result['all_checks_passed'] = True
    (OUT / 'independent-raw.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'semantic_cases': len(result['semantic']), 'allocation_cases': len(result['allocation']), 'dispatch': result['dispatch'], 'max_file_ratio': max(r['ratio'] for r in result['allocation']), 'all_checks_passed': True}, indent=2))


if __name__ == '__main__':
    main()
