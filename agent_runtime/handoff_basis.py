"""Consumer-owned evidence gates and bounded context, not scientific acceptance.

Only declared dependencies can be tracked. Cache hints come from the trusted
host's current model context and never waive freshness checks.
"""
from __future__ import annotations

import json
from pathlib import Path

from .knowledge import KnowledgeStore, check_handoff_knowledge
from .project_memory import MemoryLedger, _ids
from scripts.validate_handoff import validate


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _policy(request, key):
    value = request.get(key, False)
    _require(type(value) is bool, key + ' must be boolean')
    return value


def claim_graph(record):
    """Check local claim DAG, reference scope, and observable premise records."""
    claims = record.get('evidence_claims', [])
    _require(isinstance(claims, list), 'evidence_claims must be a list')
    graph = {}
    allowed = {key: {r['id'] for r in record.get(field, [])} for key, field in
               (('knowledge_ids', 'knowledge_refs'), ('artifact_ids', 'artifacts'))}
    allowed['memory_ids'] = set(record.get('memory_refs', []))
    fields = {'id', 'status', 'knowledge_ids', 'memory_ids', 'artifact_ids',
              'depends_on', 'assumptions'}
    for claim in claims:
        _require(isinstance(claim, dict) and set(claim) == fields, 'invalid evidence claim fields')
        _ids([claim['id']], 'claim ID')
        _require(claim['id'] not in graph, 'duplicate claim ID')
        _require(claim['status'] in ('supported', 'rejected', 'candidate'), 'invalid claim status')
        for key in ('knowledge_ids', 'memory_ids', 'artifact_ids', 'depends_on'):
            _ids(claim[key], key)
            if key in allowed:
                _require(set(claim[key]) <= allowed[key], 'claim references undeclared ' + key)
        assumptions = claim['assumptions']
        _require(isinstance(assumptions, list), 'claim assumptions must be a list')
        for item in assumptions:
            _require(isinstance(item, dict) and set(item) == {'name', 'status', 'evidence_ids'},
                     'invalid assumption record')
            _require(isinstance(item['name'], str) and bool(item['name'].strip()), 'assumption needs name')
            _require(item['status'] in ('satisfied', 'unsatisfied', 'unknown'), 'invalid assumption status')
            _ids(item['evidence_ids'], 'assumption evidence_ids')
            _require(set(item['evidence_ids']) <= set(claim['artifact_ids']),
                     'assumption evidence must be claim artifacts')
            if claim['status'] == 'supported':
                _require(item['status'] == 'satisfied' and bool(item['evidence_ids']),
                         'supported claim needs satisfied premises with evidence')
        _require(claim['status'] != 'supported' or any(claim[k] for k in allowed) or claim['depends_on'],
                 'supported claim needs declared evidence')
        graph[claim['id']] = claim
    # Iterative topological check also bounds stack depth for untrusted records.
    pending = set(graph)
    while pending:
        ready = {cid for cid in pending if not (set(graph[cid]['depends_on']) & pending)}
        _require(bool(ready), 'cyclic claim dependencies')
        for cid in ready:
            parents = graph[cid]['depends_on']
            _require(set(parents) <= graph.keys(), 'unknown parent claim')
            if graph[cid]['status'] == 'supported':
                _require(all(graph[p]['status'] == 'supported' for p in parents),
                         'supported claim depends on unsupported claim')
        pending -= ready
    return graph


def check_handoff_basis(root, record, request):
    """Mandatory when declared; requirements belong to the consumer, not output."""
    _require(isinstance(record, dict) and isinstance(request, dict), 'basis requires objects')
    for key in ('context_max_chars', 'context_max_tokens'):
        if key in request:
            cap = request[key]
            _require(type(cap) is int and cap > 0 and (key != 'context_max_chars' or cap <= 200000),
                     'invalid consumer ' + key)
    if _policy(request, 'knowledge_required'):
        _require(bool(record.get('knowledge_refs')), 'knowledge_required: missing knowledge_refs')
    knowledge = check_handoff_knowledge(root, record, request)
    supplied, required = record.get('memory_refs', []), request.get('memory_refs', [])
    _require(isinstance(supplied, list) and isinstance(required, list), 'memory_refs must be lists')
    _ids(supplied, 'memory_refs'); _ids(required, 'consumer memory_refs')
    if _policy(request, 'memory_required'):
        _require(bool(supplied), 'memory_required: missing memory_refs')
    memory = []
    if supplied or required:
        ledger = MemoryLedger(root)
        if required:
            ledger.check(required)
        _require(set(required) <= set(supplied), 'handoff omits consumer-required memory_refs')
        if supplied:
            memory = ledger.check(supplied)
    graph = claim_graph(record)
    expected = request.get('required_claim_ids', [])
    _ids(expected, 'required_claim_ids')
    _require(set(expected) <= graph.keys(), 'handoff omits required claims')
    _require(all(graph[c]['status'] == 'supported' for c in expected), 'required claim is unsupported')
    return {'knowledge': knowledge, 'memory': memory, 'claims': graph,
            'scope': 'declared identity, dependencies and premise records; scientific applicability unchecked'}


def basis_impact(root, record, request):
    """Recheck stored basis, propagating faults to local claim descendants only.

    Return affected consumers via Mailbox; never mutate historical evidence/ACK.
    Cross-handoff dependencies use immutable MemoryLedger IDs, not guessed text.
    """
    root = Path(root).resolve()
    reasons = []
    try:
        check_handoff_basis(root, record, request)
    except (ValueError, OSError) as exc:
        reasons.append(str(exc))
    if not reasons:
        # Knowledge/Memory checks do not check artifact bytes.
        errors = validate(record, root)
        if not errors:
            return {'stale': False, 'claim_ids': [], 'reasons': []}
        reasons.extend(errors)
    graph = claim_graph(record)
    if not graph:
        return {'stale': True, 'claim_ids': [], 'reasons': reasons,
                'scope': 'legacy handoff; claim dependency granularity unavailable'}
    bad = set()
    refs = {r['id']: r for r in record.get('knowledge_refs', [])}
    corpus = None
    if refs:
        try:
            target = root / request['knowledge_root']
            _require(target.resolve().is_relative_to(root), 'knowledge_root outside project')
            corpus = KnowledgeStore(target)
        except (ValueError, OSError, KeyError):
            bad.update(cid for cid, c in graph.items() if c['knowledge_ids'])
    for cid, claim in graph.items():
        try:
            if claim['knowledge_ids'] and corpus is not None:
                closure = {r['id'] for kid in claim['knowledge_ids']
                           for r in corpus.get(kid)['knowledge_refs']}
                _require(closure <= refs.keys(), 'claim prerequisites changed')
                corpus.check_refs([refs[k] for k in sorted(closure)])
            if claim['memory_ids']:
                MemoryLedger(root).check(claim['memory_ids'])
            artifacts = [a for a in record['artifacts'] if a['id'] in claim['artifact_ids']]
            _require(not validate(dict(record, status='partial', limitations=['basis recheck'],
                                       artifacts=artifacts, tasks=[], checks=[]), root),
                     'claim artifact changed')
        except (ValueError, OSError):
            bad.add(cid)
    while True:
        expanded = bad | {cid for cid, c in graph.items() if set(c['depends_on']) & bad}
        if expanded == bad:
            break
        bad = expanded
    return {'stale': True, 'claim_ids': sorted(bad), 'reasons': reasons,
            'scope': 'declared local claim DAG and project memory dependency closure'}


def basis_context(root, record, request, *, known_knowledge_refs=(), known_memory_ids=(),
                  max_chars=20000, token_counter=None, max_tokens=None):
    """Return a complete basis or fail before model dispatch; no silent truncation.

    Payload has artifact references, not file contents. Actual tokenizer is a
    trusted callable; absent it, token use is unknown (characters are not tokens).
    Cache hints mean evidence is ALREADY in this consumer's current context.
    """
    root = Path(root).resolve()
    checked = check_handoff_basis(root, record, request)
    _require(type(max_chars) is int and 1 <= max_chars <= 200000, 'invalid max_chars')
    _require(max_tokens is None or (type(max_tokens) is int and max_tokens > 0), 'invalid max_tokens')
    _require(max_tokens is None or callable(token_counter), 'token budget needs actual token_counter')
    # Consumer request may impose stricter limits than a host call. Never let
    # per-call cache/budget options relax the independent request's hard cap.
    if 'context_max_chars' in request:
        cap = request['context_max_chars']
        _require(type(cap) is int and 1 <= cap <= 200000, 'invalid consumer context_max_chars')
        max_chars = min(max_chars, cap)
    if 'context_max_tokens' in request:
        cap = request['context_max_tokens']
        _require(type(cap) is int and cap > 0, 'invalid consumer context_max_tokens')
        _require(callable(token_counter), 'token budget needs actual token_counter')
        max_tokens = cap if max_tokens is None else min(max_tokens, cap)
    _ids(known_memory_ids, 'known_memory_ids')
    _require(isinstance(known_knowledge_refs, (list, tuple)), 'invalid known_knowledge_refs')
    payload = {'input_version': record['input_version'], 'knowledge_refs': record.get('knowledge_refs', []),
               'memory_refs': record.get('memory_refs', []), 'evidence_claims': record.get('evidence_claims', []),
               'artifacts': record['artifacts'], 'knowledge_entries': [], 'memory_entries': []}
    omitted = []
    if payload['knowledge_refs'] or known_knowledge_refs:
        if known_knowledge_refs:
            check_handoff_knowledge(root, {'knowledge_refs': list(known_knowledge_refs)},
                                    dict(request, knowledge_refs=[]))
        corpus = KnowledgeStore(root / request['knowledge_root'])
        for ref in payload['knowledge_refs']:
            if ref in known_knowledge_refs:
                omitted.append(ref['id'])
            else:
                entry = corpus.get(ref['id']); entry.pop('knowledge_refs')
                payload['knowledge_entries'].append(entry)
    memory_entries = {entry['id']: entry for entry in checked['memory']}
    if payload['memory_refs'] or known_memory_ids:
        ledger = MemoryLedger(root)
        if known_memory_ids:
            ledger.check(known_memory_ids)
        pending = {dep for entry in memory_entries.values() for dep in entry['deps']}
        while pending:
            entries = ledger.check(sorted(pending))
            memory_entries.update((entry['id'], entry) for entry in entries)
            pending = {dep for entry in entries for dep in entry['deps']} - memory_entries.keys()
    payload['memory_entries'] = [memory_entries[k] for k in sorted(memory_entries) if k not in known_memory_ids]
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    _require(len(serialized) <= max_chars, 'complete basis exceeds character budget; narrow task or reuse context')
    tokens = None
    if token_counter is not None:
        _require(callable(token_counter), 'token_counter must be callable')
        tokens = token_counter(serialized)
        _require(type(tokens) is int and tokens >= 0, 'token_counter must return nonnegative integer')
        _require(max_tokens is None or tokens <= max_tokens, 'complete basis exceeds token budget')
    return {'payload': serialized, 'usage': {'chars': len(serialized), 'bytes': len(serialized.encode()),
            'tokens': tokens, 'max_chars': max_chars, 'max_tokens': max_tokens,
            'scope': 'exact serialized payload only; tool envelope and model output excluded'},
            'reused_knowledge_ids': omitted,
            'reused_memory_ids': sorted(set(memory_entries) & set(known_memory_ids))}
