#!/usr/bin/env python3
"""Same synthetic cases against an arbitrary validator revision; no model calls.

Old API has no consumer_request parameter. It receives the same expected version;
that missing scope boundary is exactly the feature under comparison.
"""
import argparse
import copy
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import tempfile


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--validator', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    args = p.parse_args()
    spec = importlib.util.spec_from_file_location('subject', args.validator)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    supports_scope = 'consumer_request' in inspect.signature(module.validate).parameters
    payload = b'Identical synthetic bytes for both validator versions.\n'
    record = dict(schema_version=1, run_id='synthetic', role='worker', input_version='v2',
                  status='completed', limitations=[],
                  artifacts=[dict(id='a', path='result.txt', sha256=hashlib.sha256(payload).hexdigest())],
                  checks=[dict(criterion='synthetic', status='pass', artifact_ids=['a'])],
                  tasks=[dict(task_id='A', status='done', evidence=['a']),
                         dict(task_id='B', status='done', evidence=['a'])])
    request = dict(schema_version=1, input_version='v2', tasks=[dict(task_id='A'), dict(task_id='B')])
    cases = []
    def add(name, accepted, change=lambda r, q: None, complete=True, without_request=False):
        r, q = copy.deepcopy(record), copy.deepcopy(request)
        change(r, q)
        cases.append((name, accepted, r, None if without_request else q, complete))
    add('all_required_done', True)
    add('required_task_omitted', False, lambda r,q:r['tasks'].pop())
    add('whole_task_list_omitted', False, lambda r,q:r.pop('tasks'))
    add('unauthorized_skip', False, lambda r,q:r['tasks'][1].update(status='skipped', reason='optional according to producer'))
    add('producer_allow_skip_forgery', False, lambda r,q:r['tasks'][1].update(status='skipped', reason='producer claims authority', allow_skip=True))
    def allowed(r,q):
        r['tasks'][1].update(status='skipped', reason='consumer allows this optional task')
        q['tasks'][1]['allow_skip']=True
    add('consumer_authorized_skip', True, allowed)
    add('unexpected_task', False, lambda r,q:r['tasks'].append(dict(task_id='C', status='done', evidence=['a'])))
    add('explicit_empty_scope', True, lambda r,q:(r.update(tasks=[]),q.update(tasks=[])))
    add('no_request_completion', False, without_request=True)
    add('no_request_integrity', True, complete=False, without_request=True)
    add('stale_version', False, lambda r,q:r.update(input_version='v1'))
    add('duplicate_consumer_id', False, lambda r,q:q['tasks'].append(dict(task_id='A')))
    add('exact_identifier_mismatch', False, lambda r,q:q['tasks'][1].update(task_id='B '))
    def partial(r,q):
        r.update(status='partial', limitations=['Review pending'])
        r['tasks'][1].update(status='blocked', reason='waiting for review', evidence=[])
    add('honest_partial_integrity', True, partial, complete=False)
    add('partial_cannot_complete', False, partial)
    add('corrupt_digest', False, lambda r,q:r['artifacts'][0].update(sha256='0'*64))
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp); (root/'result.txt').write_bytes(payload)
        for name, expected, r, q, complete in cases:
            kw = dict(expected_input_version='v2')
            if supports_scope and q is not None:
                kw['consumer_request'] = q
            errors = module.validate(r, root, complete, **kw)
            results.append(dict(case=name, expected_accepted=expected, actual_accepted=not errors,
                                matched=(not errors)==expected, errors=errors))
        raw_preserved = (root/'result.txt').read_bytes() == payload
    output = dict(validator_sha256=hashlib.sha256(args.validator.read_bytes()).hexdigest(),
                  cases_sha256=hashlib.sha256(json.dumps(cases,sort_keys=True).encode()).hexdigest(),
                  consumer_request_supported=supports_scope, total=len(results),
                  matched=sum(x['matched'] for x in results), raw_preserved=raw_preserved,
                  scope='Deterministic structural acceptance comparison, not blind holdout, model accuracy or agent success rate.',
                  results=results)
    args.out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in output.items() if k!='results'}))


if __name__=='__main__':
    main()
