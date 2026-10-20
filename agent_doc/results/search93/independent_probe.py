"""Independent SEARCH-DEPTH-93 differential checks; stdout is raw JSON evidence.

Run from project root using normal Python and python -O. Uses real temporary
files and frozen Git source, never changes recursion limits or production files.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
import agent_runtime.result_store as candidate

BASE = 'd065a055cf29b10ed37717db197995283c1665d4'
source = subprocess.check_output(['git', 'show', BASE + ':agent_runtime/result_store.py'], cwd=ROOT)
baseline = types.ModuleType('agent_runtime._independent_search93_baseline')
baseline.__package__ = 'agent_runtime'
exec(compile(source, 'frozen-' + BASE + '/result_store.py', 'exec'), baseline.__dict__)
checks = []


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def exception(call, kind=RecursionError):
    try:
        call()
    except kind as error:
        return error
    raise AssertionError('expected ' + kind.__name__)


def record(run_id, context=None):
    return {'schema_version': candidate.SCHEMA, 'run_id': run_id,
            'origin': 'historical-external-reference', 'summary': 'needle ' + run_id,
            'registered_at': '2026-10-20T00:00:00+00:00',
            'context': {} if context is None else context,
            'validation_at_registration': {'status': 'unknown'}}


with tempfile.TemporaryDirectory(prefix='independent-search93-') as temporary:
    root = Path(temporary)
    def write(run_id, data):
        path = root / candidate.HOME / run_id / 'record.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path
    exact = {'scope': 'needle', 'code_revision': 'test-version',
             'artifacts': {'inputs': [{'path': 'x', 'sha256': 'a' * 64}]},
             'execution': {'command': ['python', 'x'], 'seeds': [0], 'repeats': 1},
             'metrics': [{'name': 'count', 'unit': 'dimensionless'}]}
    shallow = {'execution': {'nested': [[{'x': 1}]]}}
    for name, context in [('good-a', {}), ('good-b', exact), ('good-c', shallow)]:
        write(name, json.dumps(record(name, context)).encode())
    old, new = baseline.ResultStore(root), candidate.ResultStore(root)
    variants = [('needle', {}), ('unmatched', {}), ('needle', {'limit': 1}),
                ('needle', {'max_scan': 2}), ('unmatched', {'context': exact}),
                ('needle', {'context': {'scope': 'unknown'}}),
                ('needle', {'context': shallow})]
    for query, kwargs in variants:
        require(old.search(query, **kwargs) == new.search(query, **kwargs), 'ordinary full output mismatch')
    checks.append({'name': 'ordinary_full_output_differential', 'cases': len(variants), 'pass': True})
    ordinary = new.search('needle')
    fixtures = []
    for name, left, right in [('bad-list', '[', ']'), ('bad-dict', '{"x":', '}')]:
        data = ('{"payload":' + left * 10000 + '0' + right * 10000 + '}').encode()
        require(len(data) < candidate.METADATA_LIMIT, 'fixture exceeds byte bound')
        raw = exception(lambda: json.loads(data))
        path = write(name, data)
        base_error = exception(lambda: old.show(name))
        new_error = exception(lambda: new.show(name))
        require(type(base_error) is RecursionError, 'baseline exception not raw')
        require(type(new_error) is candidate._ResultJSONDepthError, 'candidate subtype absent')
        require(str(raw) == str(base_error) == str(new_error), 'decoder message changed')
        require(type(new_error.__cause__) is RecursionError and str(new_error.__cause__) == str(raw),
                'decoder cause changed')
        fixtures.append({'run_id': name, 'depth': 10000, 'bytes': len(data),
                         'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'error': str(raw)})
    checks.append({'name': 'list_dict_direct_show_message_category_cause', 'cases': 2, 'pass': True})
    before = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in root.rglob('record.json')}
    exception(lambda: old.search('needle'))
    result = new.search('needle')
    require(result['results'] == ordinary['results'], 'good candidate output changed')
    require([e['run_id'] for e in result['errors']] == ['bad-dict', 'bad-list'], 'error identity mismatch')
    require(result['status'] == 'candidates' and result['scanned'] == 5 and not result['partial'],
            'mixed status/scan/partial mismatch')
    unmatched = new.search('unmatched')
    require(unmatched['status'] == 'incomplete' and not unmatched['results'], 'unmatched status mismatch')
    checks.append({'name': 'frozen_base_failure_candidate_mixed_and_unmatched', 'cases': 3, 'pass': True})
    for klass in (baseline.ResultStore, candidate.ResultStore):
        store = klass(root)
        for kind in (RecursionError, RuntimeError, SystemExit):
            error = kind('independent custom show')
            with patch.object(store, 'show', side_effect=error):
                require(exception(lambda: store.search('needle'), kind) is error, 'custom error identity changed')
        # An unrelated exception after successful show must not become a record error.
        store._directories = lambda maximum: (['good-a'], False)
        error = RecursionError('independent contamination recursion')
        with patch('agent_runtime.contamination.assert_not_revoked', side_effect=error):
            require(exception(lambda: store.search('needle')) is error, 'post-show recursion swallowed')
        nested = 0
        for _ in range(10000):
            nested = [nested]
        require(type(exception(lambda: store.search('needle', context={'execution': {'deep': nested}})))
                is RecursionError, 'caller recursion normalized or swallowed')
    checks.append({'name': 'custom_show_and_post_show_and_caller_propagation', 'cases': 10, 'pass': True})
    cli = subprocess.run([sys.executable, *(['-O'] if sys.flags.optimize else []),
                          str(ROOT / 'scripts/result_store.py'), '--root', str(root), 'search', 'needle'],
                         capture_output=True, text=True, timeout=15)
    require(cli.returncode == 0, cli.stderr)
    require(json.loads(cli.stdout) == result, 'CLI output mismatch')
    checks.append({'name': 'cli_structured_full_output', 'cases': 1, 'pass': True})
    after = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in root.rglob('record.json')}
    require(before == after, 'input mutation')
    checks.append({'name': 'all_fixture_bytes_unchanged', 'cases': 5, 'pass': True})
    only = candidate.ResultStore(root)
    only._directories = lambda maximum: (['bad-dict', 'bad-list'], False)
    result = only.search('needle')
    require(result['status'] == 'incomplete' and len(result['errors']) == 2 and not result['results'],
            'all-bad output mismatch')
    checks.append({'name': 'all_bad_incomplete', 'cases': 1, 'pass': True})

print(json.dumps({'base': BASE, 'base_source_sha256': hashlib.sha256(source).hexdigest(),
                  'candidate_source_sha256': hashlib.sha256((ROOT / 'agent_runtime/result_store.py').read_bytes()).hexdigest(),
                  'test_sha256': hashlib.sha256((ROOT / 'tests/test_result_search_depth.py').read_bytes()).hexdigest(),
                  'probe_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  'python': sys.version, 'optimized': sys.flags.optimize,
                  'recursion_limit': sys.getrecursionlimit(), 'fixtures': fixtures,
                  'checks': checks, 'verdict': 'usable-with-scope'}, indent=2))
