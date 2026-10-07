"""Conditional reuse of reported experiments and pinned implementation pointers.

This module never launches experiments, installs code, or approves skipping work.
Exact string matching is deliberately conservative and is not scientific review.
"""
from __future__ import annotations
import re


def _need(ok, message):
    if not ok:
        raise ValueError('reuse: ' + message)


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _texts(value):
    return isinstance(value, list) and bool(value) and all(_text(x) for x in value)


def validate_reuse(value):
    _need(isinstance(value, dict), 'must be an object')
    common = {'type', 'claim', 'conditions', 'observations', 'limitations', 'minimal_checks'}
    kind = value.get('type')
    _need(kind in ('paper-result', 'implementation'), 'unsupported type')
    extra = 'paper' if kind == 'paper-result' else 'code'
    _need(set(value) == common | {extra}, 'fields mismatch')
    _need(_text(value['claim']), 'claim required')
    conditions = value['conditions']
    _need(isinstance(conditions, dict) and bool(conditions) and
          all(_text(k) and _text(v) for k, v in conditions.items()), 'explicit conditions required')
    for field in ('observations', 'limitations', 'minimal_checks'):
        _need(_texts(value[field]), field + ' required')
    detail = value[extra]
    _need(isinstance(detail, dict), extra + ' must be an object')
    if kind == 'paper-result':
        _need(set(detail) == {'venue', 'year', 'review_status', 'local_reproduction'}, 'paper fields mismatch')
        _need(_text(detail['venue']) and type(detail['year']) is int and 1900 <= detail['year'] <= 2100,
              'invalid venue/year')
        _need(detail['review_status'] in ('peer-reviewed', 'preprint'), 'review status required')
        _need(detail['local_reproduction'] == 'not-run', 'reported results cannot be labeled local measurements')
    else:
        _need(set(detail) == {'repository', 'commit', 'paths', 'symbols', 'license', 'language',
                             'entrypoint', 'local_execution'}, 'code fields mismatch')
        _need(_text(detail['repository']) and re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', detail['repository']),
              'invalid repository')
        _need(isinstance(detail['commit'], str) and re.fullmatch(r'[0-9a-f]{40}', detail['commit']), 'pin full commit')
        _need(_texts(detail['paths']) and all(not p.startswith('/') and '..' not in p.split('/')
                                            for p in detail['paths']), 'invalid source paths')
        _need(_texts(detail['symbols']), 'symbols required')
        _need(all(_text(detail[k]) for k in ('license', 'language', 'entrypoint')), 'license/API required')
        _need(detail['local_execution'] == 'not-run', 'pointer is not local execution evidence')


def decision_support(store, query, context, *, purpose='experiment', explicit_reproduction=False, limit=5):
    _need(isinstance(context, dict) and all(_text(k) and _text(v) for k, v in context.items()),
          'task context must be a string-valued object; omit unknowns')
    _need(purpose in ('experiment', 'implementation'), 'invalid purpose')
    _need(type(explicit_reproduction) is bool, 'explicit_reproduction must be boolean')
    _need(type(limit) is int and 1 <= limit <= 20, 'limit must be 1..20')
    # Filter before truncation so other knowledge kinds cannot crowd out cards.
    eligible = {kid: rec for kid, rec in store.records.items() if rec['status'] == 'published'
                and rec.get('reuse', {}).get('type') ==
                ('paper-result' if purpose == 'experiment' else 'implementation')}
    # The normal search limit is 20; reuse corpora can exceed that. Rank an isolated
    # view using the same established search rather than silently truncating first.
    from copy import copy
    view = copy(store)
    view.records = eligible
    hits = view.search(query, limit=limit)['results'] if eligible else []
    results, refs = [], {}
    for hit in hits:
        record = store.get(hit['id'])
        card = record['reuse']
        missing = [k for k in card['conditions'] if k not in context]
        mismatched = [{'field': k, 'reported': v, 'task': context[k]}
                      for k, v in card['conditions'].items() if k in context
                      and context[k].strip().casefold() != v.strip().casefold()]
        if explicit_reproduction:
            disposition = 'run_requested_experiment'
        elif missing:
            disposition = 'insufficient_context'
        elif mismatched:
            disposition = 'minimal_transfer_check'
        elif purpose == 'implementation':
            disposition = 'evaluate_pinned_implementation'
        else:
            disposition = 'reuse_for_planning'
        results.append({**hit, 'reuse': card, 'sources': record['sources'],
                        'missing_conditions': missing, 'mismatched_conditions': mismatched,
                        'disposition': disposition, 'automatic_skip_authorized': False,
                        'applicability': 'requires-human-review', 'knowledge_refs': record['knowledge_refs']})
        refs.update({r['id']: r for r in record['knowledge_refs']})
    return {'schema_version': 1, 'snapshot': store.snapshot, 'purpose': purpose,
            'status': 'candidates' if results else 'no_hits', 'results': results,
            'knowledge_refs': [refs[k] for k in sorted(refs)],
            'scope': 'Reported evidence supports planning; new claims need local verification. '
                     'Explicit reproduction and required acceptance experiments remain required.'}
