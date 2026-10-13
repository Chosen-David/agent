"""Whole public search entry, original filesystem path and gate calls retained."""
import copy
import hashlib
import inspect
import json
import platform
from pathlib import Path
import statistics
import subprocess
import sys
import textwrap
import time
from types import MethodType

ROOT = Path('/workspace/scratch/88c3234ecfbc/agent-research-0756')
sys.path.insert(0, str(ROOT))
import agent_runtime.result_store as module


def digest(value):
    return hashlib.sha256(value).hexdigest()


def main():
    frozen_input = json.loads(Path(sys.argv[1]).read_text()) if len(sys.argv) > 1 else None
    current_source = textwrap.dedent(inspect.getsource(module.ResultStore.search))
    src = frozen_input['baseline_source'] if frozen_input else current_source
    old = "exact = (context is not None and set(context) == set(CONTEXT_FIELDS) and\n                     not _unknown(context) and context == record['context'])"
    if src.count(old) != 1:
        raise RuntimeError('baseline exact expression changed')
    # Retain per-record evaluation for exotic equality / overridden show hooks.
    helper_src = '''def _plain_search_context(value):
    pending = [value]
    while pending:
        item = pending.pop()
        if type(item) is dict:
            if any(type(k) is not str for k in item):
                return False
            pending.extend(item.values())
        elif type(item) is list:
            pending.extend(item)
        elif type(item) not in (str, int, float, bool, type(None)):
            return False
    return True
'''
    candidate_src = src.replace('    hits, errors = [], []\n',
        '    exact_eligible = None\n    context_checked = False\n    hits, errors = [], []\n').replace(
        old,
        "if not context_checked:\n"
        "                if type(self) is ResultStore and 'show' not in self.__dict__ and _plain_search_context(context):\n"
        "                    exact_eligible = (context is not None and set(context) == set(CONTEXT_FIELDS) and\n"
        "                                      not _unknown(context))\n"
        "                context_checked = True\n"
        "            exact = ((context is not None and set(context) == set(CONTEXT_FIELDS) and\n"
        "                      not _unknown(context) and context == record['context'])\n"
        "                     if exact_eligible is None else exact_eligible and context == record['context'])")
    ns = dict(vars(module))
    exec(compile(helper_src, '<isolated-plain-context>', 'exec'), ns)
    exec(compile(candidate_src, '<isolated-invariant-search>', 'exec'), ns)
    if frozen_input and (candidate_src != frozen_input['candidate_source'] or helper_src != frozen_input['candidate_helper']):
        raise RuntimeError('frozen candidate changed')
    baseline_ns = dict(vars(module))
    exec(compile(src, '<frozen-baseline-search>', 'exec'), baseline_ns)
    files = sorted((ROOT / 'agent_doc/results').glob('*/record.json'))
    frozen = {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in files}
    def context(name):
        return json.loads((ROOT / 'agent_doc/results' / name / 'record.json').read_bytes())['context']
    unknown = copy.deepcopy(context('comm-batch-20261010'))
    unknown['code_revision'] = 'unknown'
    cases = [('large-corpus', context('combined-corpus-v4-20261007')),
             ('large-math', context('math-inverse-update-20261009')),
             ('medium-batch', context('comm-batch-20261010')),
             ('none', None), ('incomplete', {}), ('unknown', unknown)]
    candidate = module.ResultStore(ROOT)
    candidate.search = MethodType(ns['search'], candidate)
    base = module.ResultStore(ROOT)
    base.search = MethodType(baseline_ns['search'], base)
    if current_source == candidate_src:
        candidate.search = MethodType(module.ResultStore.search, candidate)
    elif current_source != src:
        raise RuntimeError('current search is neither baseline nor frozen candidate')
    stores = {'baseline': base, 'candidate': candidate}
    observations = []
    for name, ctx in cases:
        def invoke(variant):
            return stores[variant].search('result source context', context=ctx, limit=3, max_scan=250)
        expected = invoke('baseline')
        if invoke('candidate') != expected:
            raise RuntimeError('warmup difference ' + name)
        samples = {'baseline': [], 'candidate': []}
        pairs = []
        for i in range(11):
            order = ('baseline', 'candidate') if i % 2 == 0 else ('candidate', 'baseline')
            pair = {}
            for variant in order:
                start = time.perf_counter_ns()
                observed = invoke(variant)
                elapsed = time.perf_counter_ns() - start
                if observed != expected:
                    raise RuntimeError('return difference ' + name + variant)
                samples[variant].append(elapsed / 1e6)
                pair[variant] = elapsed / 1e6
            pairs.append({'order': list(order), 'ms': pair})
        bm = statistics.median(samples['baseline'])
        cm = statistics.median(samples['candidate'])
        observations.append({'name': name, 'context_sha256': digest(json.dumps(ctx, sort_keys=True).encode()),
                             'context_json_bytes': len(json.dumps(ctx).encode()),
                             'pairs': pairs, 'median_ms': {'baseline': bm, 'candidate': cm},
                             'reduction_fraction': 1 - cm / bm, 'result': expected})
    if {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in files} != frozen:
        raise RuntimeError('source records changed during measurement')
    print(json.dumps({'main': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
                      'environment': {'platform': platform.platform(), 'python': platform.python_version()},
                      'timer': 'perf_counter_ns, full ResultStore.search, warm OS cache, serial alternating pairs',
                      'baseline_source': src, 'candidate_source': candidate_src,
                      'candidate_helper': helper_src,
                      'baseline_source_sha256': digest(src.encode()),
                      'candidate_source_sha256': digest(candidate_src.encode()),
                      'module_sha256': digest(Path(module.__file__).read_bytes()),
                      'frozen_record_hashes': frozen, 'cases': observations}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
