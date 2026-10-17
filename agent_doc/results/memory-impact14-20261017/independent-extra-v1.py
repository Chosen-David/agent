"""Independent deterministic boundaries and actual import-path probes, untimed."""
import copy
import inspect
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check as h

def require(x, msg):
    if not x:
        raise RuntimeError(msg)

def oracle(graph, seeds):
    answer = set()
    for cid in graph:
        queue, seen = [cid], set()
        while queue:
            node = queue.pop()
            if node in seeds:
                answer.add(cid)
                break
            if node not in seen:
                seen.add(node)
                queue.extend(graph[node]['depends_on'])
    return answer | set(seeds)

results = []
def closure_case(label, graph, seeds):
    oldgraph, oldseeds = copy.deepcopy(graph), set(seeds)
    got = h.candidate._claim_descendants(graph, seeds)
    require(got == oracle(graph, oldseeds) == h.legacy(graph, oldseeds), label)
    require(graph == oldgraph and seeds == oldseeds, label + ' mutation')
    results.append(label)

for n in (0, 1, 8, 63, 64, 65, 128):
    graph = {str(i): {'depends_on': tuple([str(i-1)] if i else [])}
             for i in reversed(range(n))}
    for seeds in (set(), {'0'} if n else set(), {str(n//2)} if n else set()):
        closure_case(f'chain-{n}-{sorted(seeds)}', graph, seeds)

for edges in (511, 512, 513):
    n = 128
    graph = {str(i): {'depends_on': [str(i-1)] if i else []} for i in range(n)}
    count = n-1
    for i in range(n):
        for j in range(i-1):
            if count == edges:
                break
            graph[str(i)]['depends_on'].append(str(j))
            count += 1
        if count == edges:
            break
    fast = []
    lines, start = inspect.getsourcelines(h.candidate._claim_descendants)
    target = start + next(i for i, line in enumerate(lines) if 'children = {' in line)
    def trace(frame, event, arg):
        if frame.f_code is h.candidate._claim_descendants.__code__ and event == 'line' and frame.f_lineno == target:
            fast.append(True)
        return trace
    sys.settrace(trace)
    try:
        closure_case(f'density-{edges}', graph, {'0'})
    finally:
        sys.settrace(None)
    require(bool(fast) == (edges <= 512), 'density dispatch')

graph = {str(i): {'depends_on': [str(i-1)] if i else []} for i in range(128)}
graph.update({f'u{i}': {'depends_on': [f'u{i-1}'] if i else []} for i in range(128)})
closure_case('unrelated-multiple-seeds', graph, {'0', '20', 'u100'})
closure_case('unrelated-rootless', graph, set())

trace_calls = []
class Deps(list):
    def __iter__(self):
        trace_calls.append('iter')
        return super().__iter__()
    def __len__(self):
        trace_calls.append('len')
        return super().__len__()
class Claim(dict):
    def __getitem__(self, key):
        trace_calls.append(('get', key))
        return super().__getitem__(key)
class ID(str):
    def __hash__(self):
        trace_calls.append('hash')
        return super().__hash__()
    def __eq__(self, other):
        trace_calls.append('eq')
        return super().__eq__(other)
for kind in ('deps', 'claim', 'id', 'parent'):
    graph = {str(i): {'depends_on': [str(i-1)] if i else []} for i in range(65)}
    if kind == 'deps': graph['50']['depends_on'] = Deps(['49'])
    if kind == 'claim': graph['50'] = Claim(graph['50'])
    if kind == 'id': graph[ID('50')] = graph.pop('50')
    if kind == 'parent': graph['50']['depends_on'] = [ID('49')]
    trace_calls.clear()
    expected = h.legacy(graph, {'0'})
    calls = list(trace_calls)
    trace_calls.clear()
    actual = h.candidate._claim_descendants(graph, {'0'})
    require(actual == expected and trace_calls == calls, 'custom trace ' + kind)
    results.append('custom-trace-' + kind)

with tempfile.TemporaryDirectory(prefix='impact14-independent-') as temp:
    box, record, request = h.f.fixture(Path(temp), 65, 'mixed', 'artifact')
    before = h.f.snapshot(box)
    for actor, module in [('baseline', h.baseline), ('candidate', h.candidate)]:
        observed = []
        def profile(frame, event, arg):
            if event == 'call' and frame.f_code.co_name == 'basis_impact':
                observed.append(frame.f_code)
        sys.setprofile(profile)
        try:
            value = h.call(module, box)
        finally:
            sys.setprofile(None)
        require(observed == [module.basis_impact.__code__], 'real module ' + actor)
        require(value[0]['claim_ids'] == [f'c{i:04}' for i in range(32)], 'public mixed')
        results.append('actual-import-' + actor)
    require(sys.modules[h.KEY] is h.candidate, 'module restored')
    require(h.f.snapshot(box) == before, 'public mutation')
    # Persisted malformed basis is not a normal public write, but its diagnostics
    # must still be identical; no fixture used for performance is changed.
    for field, value in [('evidence_claims', None), ('memory_refs', [None])]:
        broken = dict(record, **{field: value})
        with box.connect() as db:
            db.execute('UPDATE communication_basis SET record=?', (h.f.canonical(broken),))
        errors = []
        for module in (h.baseline, h.candidate):
            try:
                h.call(module, box)
            except Exception as exc:
                errors.append((type(exc).__name__, str(exc)))
            else:
                errors.append(None)
        require(errors[0] == errors[1] and errors[0] is not None, 'error equivalence ' + field)
        results.append('public-error-' + field)

(HERE/'independent-extra.json').write_text(json.dumps({'passed': len(results), 'cases': results}, indent=2)+'\n')
print(json.dumps({'passed': len(results)}))
