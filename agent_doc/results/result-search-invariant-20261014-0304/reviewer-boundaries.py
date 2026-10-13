"""Independent API boundary comparison against frozen candidate source."""
import copy
import hashlib
import inspect
import json
from pathlib import Path
import sys
import tempfile
import textwrap
from types import MethodType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
import agent_runtime.result_store as m

raw = json.loads((HERE / sys.argv[1]).read_text())
namespace = dict(vars(m))
exec(raw['candidate_helper'], namespace)
exec(raw['baseline_source'], namespace)
baseline = namespace['search']
if textwrap.dedent(inspect.getsource(m.ResultStore.search)) != raw['candidate_source']:
    raise RuntimeError('Native production search differs from frozen candidate')
if textwrap.dedent(inspect.getsource(m._plain_search_context)) != raw['candidate_helper']:
    raise RuntimeError('Native production helper differs from frozen candidate')
candidate = m.ResultStore.search
known = dict(scope='scope', code_revision='revision', artifacts={'code': ['artifact']},
             execution={'command': ['execute']}, metrics=[{'name': 'metric', 'unit': 'unit'}])

class BadDict(dict):
    def __eq__(self, other):
        raise ValueError('custom equality failure')

class OddString(str):
    def __eq__(self, other):
        raise TypeError('custom scalar equality failure')
    __hash__ = str.__hash__

class CountingKey(str):
    calls = 0
    def __hash__(self):
        type(self).calls += 1
        return super().__hash__()

observations = []
def deep_unknown():
    value = 'artifact'
    for _ in range(600):
        value = [value]
    return dict(copy.deepcopy(known), scope='unknown', artifacts={'code': value})

def compare(name, store, context_factory, override=False):
    values = []
    for method in (baseline, candidate):
        ctx = context_factory()
        CountingKey.calls = 0
        original = store.show
        if override:
            count = [0]
            def mutating_show(run_id):
                count[0] += 1
                if count[0] == 2:
                    ctx['code_revision'] = 'changed-by-show'
                return original(run_id)
            store.show = mutating_show
        try:
            out = {'return': method(store, 'scope', context=ctx, limit=20, max_scan=250)}
        except Exception as exc:
            out = {'exception': type(exc).__name__, 'message': str(exc)}
        finally:
            if override:
                del store.show
        out['key_hash_calls'] = CountingKey.calls
        values.append(out)
    if values[0] != values[1]:
        raise RuntimeError(str((name, values)))
    observations.append({'case': name, 'outcome': values[0]})

with tempfile.TemporaryDirectory(prefix='reviewer-result-search-') as tmp:
    root = Path(tmp)
    store = m.ResultStore(root)
    compare('missing_registry_bad_dict', store, lambda: BadDict(known))
    (root / 'agent_doc/results').mkdir(parents=True)
    compare('empty_registry_bad_dict', store, lambda: BadDict(known))
    (root / 'payload').write_text('artifact data')
    artifact = {'path': 'payload', 'sha256': hashlib.sha256((root / 'payload').read_bytes()).hexdigest()}
    for run_id in ('a-known', 'b-known'):
        store.register_history(run_id, 'scope result', [artifact], context=known)
    for label, factory in (
        ('known', lambda: copy.deepcopy(known)), ('none', lambda: None),
        ('incomplete', lambda: {}), ('bad_dict', lambda: BadDict(known)),
        ('nested_unknown', lambda: dict(copy.deepcopy(known), artifacts={'code': ['unknown']})),
        ('tuple_accepted', lambda: dict(copy.deepcopy(known), artifacts={'code': ('artifact',)})),
        ('scalar_subclass', lambda: dict(copy.deepcopy(known), scope=OddString('scope'))),
        ('key_subclass', lambda: {CountingKey(k): copy.deepcopy(v) for k, v in known.items()}),
        ('invalid_set', lambda: dict(copy.deepcopy(known), artifacts={'code': {1}})),
        ('nan', lambda: dict(copy.deepcopy(known), artifacts={'code': float('nan')})),
        ('deep_unknown_short_circuit', deep_unknown),
    ):
        compare(label, store, factory)
    compare('instance_show_mutation', store, lambda: copy.deepcopy(known), override=True)
    class HookedStore(m.ResultStore):
        pass
    compare('subclass_fallback', HookedStore(root), lambda: copy.deepcopy(known))
    incident = root / '.agent-runs/contamination/runs' / hashlib.sha256(b'a-known').hexdigest() / 'incident.json'
    incident.parent.mkdir(parents=True)
    incident.write_text('{}')
    compare('revoked_record', store, lambda: copy.deepcopy(known))
    (root / 'agent_doc/results/b-known/record.json').write_text('{')
    compare('revoked_plus_corrupt_no_eligible_records', store, lambda: BadDict(known))
    compare('revoked_plus_corrupt_plain', store, lambda: copy.deepcopy(known))

print(json.dumps({'candidate_source_sha256': raw['candidate_source_sha256'],
                  'count': len(observations), 'cases': observations}, indent=2))
