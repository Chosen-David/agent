"""Immutable project results and bounded, evidence-aware prior-result retrieval.

The registry is a file source, not an authority. Persisted pass labels, query hits
and exact metadata matches never authenticate a review or establish applicability.
Only a trusted host verifier can renew scoped result acceptance. This module never
executes experiment commands or chooses/imports an adapter from stored data.
"""
from __future__ import annotations

from copy import deepcopy
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import tempfile

from .project_docs import assert_ai_writable
from .result_validation import inspect_result
from .legacy_result_paths import legacy_read_binding, check_relocated_digest, relocated_digest_matches

HOME = 'agent_doc/results'
SCHEMA = 'project-result-record/v1'
CONTEXT_FIELDS = ('scope', 'code_revision', 'artifacts', 'execution', 'metrics')
METADATA_LIMIT = 1024 * 1024
ARTIFACT_LIMIT = 256 * 1024 * 1024


class ResultStoreError(ValueError):
    pass


def _need(condition, message):
    if not condition:
        raise ResultStoreError(message)


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _identifier(value):
    _need(isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,95}', value),
          'run_id must be a bounded filename-safe identifier')
    return value


def _path(root, value):
    _need(_text(value), 'relative path required')
    raw = Path(value)
    _need(not raw.is_absolute() and '..' not in raw.parts, 'path outside project')
    path = root / raw
    for part in (path, *path.parents):
        if part == root:
            break
        _need(not part.is_symlink(), 'result path must not contain symlinks')
    _need(path.resolve().is_relative_to(root), 'path outside project')
    return path


def _read(root, value, limit=METADATA_LIMIT):
    read_path, relocated_digest = legacy_read_binding(root, value)
    path = _path(root, read_path)
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0))
    with os.fdopen(fd, 'rb') as stream:
        info = os.fstat(stream.fileno())
        _need(stat.S_ISREG(info.st_mode), 'result input must be a regular file')
        _need(info.st_size <= limit, 'result input exceeds read bound')
        data = stream.read(limit + 1)
    _need(len(data) <= limit, 'result input grew beyond read bound')
    check_relocated_digest(data, relocated_digest)
    return data


def _json(data):
    def pairs(items):
        value = {}
        for key, item in items:
            _need(key not in value, 'duplicate JSON key: ' + key)
            value[key] = item
        return value
    def reject(value):
        raise ResultStoreError('nonfinite JSON value: ' + value)
    value = json.loads(data, object_pairs_hook=pairs, parse_constant=reject)
    _need(isinstance(value, dict), 'JSON object required')
    return value


def _ref(value):
    _need(isinstance(value, dict) and _text(value.get('path')) and
          isinstance(value.get('sha256'), str) and re.fullmatch('[0-9a-f]{64}', value['sha256']),
          'artifact path/sha256 binding required')
    return value


def _check_ref(root, ref):
    _ref(ref)
    read_path, relocated_digest = legacy_read_binding(root, ref['path'])
    path = _path(root, read_path)
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0))
    digest, size = hashlib.sha256(), 0
    with os.fdopen(fd, 'rb') as stream:
        info = os.fstat(stream.fileno())
        _need(stat.S_ISREG(info.st_mode), 'artifact must be a regular file')
        _need(info.st_size <= ARTIFACT_LIMIT, 'artifact exceeds 256 MiB; use bounded shard manifests')
        while block := stream.read(1024 * 1024):
            size += len(block)
            _need(size <= ARTIFACT_LIMIT, 'artifact grew beyond hash bound')
            digest.update(block)
    _need(digest.hexdigest() == ref['sha256'], 'stale artifact: ' + ref['path'])
    _need(relocated_digest_matches(digest.hexdigest(), relocated_digest),
          'relocated historical result bytes changed')


def _timestamp(value):
    _need(_text(value), 'timezone-aware ISO8601 time required')
    try:
        instant = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as exc:
        raise ResultStoreError('invalid ISO8601 time') from exc
    _need(instant.tzinfo is not None, 'timestamp must include timezone')
    return instant.astimezone(dt.timezone.utc)


def result_context(manifest):
    """Exact comparable conditions, derived from the bound executed manifest.

    Paths as well as hashes are retained conservatively; a relocated but equal
    source needs explicit delta review. Metric values are outcomes, not criteria.
    """
    return {'scope': manifest['scope'], 'code_revision': manifest['code_revision'],
            'artifacts': {role: sorted(deepcopy(manifest['artifacts'][role]), key=lambda x: x['path'])
                          for role in ('code', 'inputs', 'config', 'environment')},
            'execution': {key: deepcopy(manifest['execution'][key]) for key in
                          ('command', 'environment_description', 'seeds', 'repeats')},
            'metrics': sorted([{'name': m['name'], 'unit': m['unit']} for m in manifest['metrics']],
                              key=lambda x: x['name'])}


def _context(value, *, complete=False):
    _need(isinstance(value, dict) and not (set(value) - set(CONTEXT_FIELDS)),
          'context must contain only scope/code_revision/artifacts/execution/metrics')
    if complete:
        _need(set(value) == set(CONTEXT_FIELDS), 'complete experiment context required')
    # Ensure JSON-safe exact values. Unknown fields are omitted, never guessed.
    json.dumps(value, allow_nan=False)
    for field in ('scope', 'code_revision'):
        if field in value:
            _need(_text(value[field]), 'nonempty context ' + field + ' required')
    if 'metrics' in value:
        metrics = value['metrics']
        _need(isinstance(metrics, list) and metrics and all(isinstance(m, dict) and
              set(m) == {'name', 'unit'} and _text(m['name']) and _text(m['unit']) for m in metrics),
              'exact named metric units required')
        _need(len({m['name'] for m in metrics}) == len(metrics), 'duplicate metric name')
    for field in ('artifacts', 'execution'):
        if field in value:
            _need(isinstance(value[field], dict) and value[field], 'nonempty context ' + field + ' required')
    return value


def _unknown(value):
    """Two equally absent/unknown values are not evidence of compatibility."""
    if value is None or value == '' or value == [] or value == {}:
        return True
    if isinstance(value, str):
        return value.strip().casefold() in ('unknown', 'unspecified', 'not recorded', 'not-recorded',
                                           'unavailable', 'tbd', '?', '未知', '未记录')
    if isinstance(value, dict):
        return any(_unknown(v) for v in value.values())
    if isinstance(value, list):
        return any(_unknown(v) for v in value)
    return False


def _tokens(query):
    """Deterministic lexical search with CJK bigrams, not semantic retrieval."""
    tokens = []
    for word in re.findall(r'[a-z0-9_][a-z0-9_.:-]*|[\u3400-\u9fff]+', query.casefold()):
        if re.fullmatch(r'[\u3400-\u9fff]+', word):
            tokens.extend(word[i:i + 2] for i in range(max(1, len(word) - 1)))
        else:
            tokens.append(word)
    # Other scripts still retain their exact whitespace-delimited words.
    tokens.extend(query.casefold().split())
    return list(dict.fromkeys(tokens))[:96]


class ResultStore:
    """No directory is created by construction, show, search or decision support."""
    def __init__(self, root):
        self.supplied_root = Path(os.path.abspath(root))
        self.root = self.supplied_root.resolve()

    def _record_path(self, run_id):
        return f'{HOME}/{_identifier(run_id)}/record.json'

    def _directories(self, max_scan):
        _need(type(max_scan) is int and 1 <= max_scan <= 5000, 'max_scan must be 1..5000')
        home = _path(self.root, HOME)
        if not home.exists():
            return [], False
        _need(home.is_dir(), 'result home must be a directory')
        names, partial = [], False
        # Bound directory enumeration too, including non-record entries.
        with os.scandir(home) as entries:
            for count, entry in enumerate(entries):
                if count >= max_scan:
                    partial = True
                    break
                if entry.is_symlink():
                    raise ResultStoreError('result directory contains symlink: ' + entry.name)
                if entry.is_dir(follow_symlinks=False):
                    _identifier(entry.name)
                    names.append(entry.name)
        return sorted(names), partial

    def show(self, run_id):
        rel = self._record_path(run_id)
        raw = _read(self.root, rel)
        record = _json(raw)
        _need(record.get('schema_version') == SCHEMA and record.get('run_id') == run_id,
              'result record schema/identity mismatch')
        _need(record.get('origin') in ('native', 'historical-external-reference', 'legacy-contract-reference'),
              'result origin required')
        _need(_text(record.get('summary')), 'result summary required')
        _timestamp(record['registered_at'])
        if record.get('measured_at') is not None:
            _timestamp(record['measured_at'])
        _context(record.get('context', {}))
        return {'record': record, 'record_ref': {'path': rel, 'sha256': hashlib.sha256(raw).hexdigest()}}

    def _save(self, record):
        run_id = _identifier(record['run_id'])
        # Check lexical root before resolving it; never alias writes into guide.
        target = assert_ai_writable(self.supplied_root, self._record_path(run_id))
        names, partial = self._directories(5000)
        _need(not partial, 'registry collision check exceeds 5000 entries; partition before registration')
        _need(not any(name.casefold() == run_id.casefold() and name != run_id for name in names),
              'case-folding run_id collision')
        _need(not target.exists(), 'run_id is immutable and already registered')
        raw = (json.dumps(record, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode()
        _need(len(raw) <= METADATA_LIMIT, 'record exceeds metadata bound')
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix='.record-', dir=target.parent)
        try:
            with os.fdopen(fd, 'wb') as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            assert_ai_writable(self.supplied_root, self._record_path(run_id))
            # Atomic publication without replacing another writer's history.
            os.link(temporary, target, follow_symlinks=False)
        except FileExistsError as exc:
            raise ResultStoreError('run_id is immutable and already registered') from exc
        finally:
            os.unlink(temporary)
        return self.show(run_id)

    def register(self, contract, *, historical=False, measured_at=None, verifier=None,
                 origin=None):
        """Index a frozen result. Native raw/derived bytes must be centralized.

        historical=True preserves old file locations, explicitly marked as refs;
        no old bytes are moved or copied. Registration itself grants no acceptance.
        """
        _need(type(historical) is bool, 'historical must be boolean')
        inspected = inspect_result(self.root, contract, verifier)
        _need(inspected.get('proof') is not None, 'cannot register unbound result: ' + '; '.join(inspected['errors']))
        proof = inspected['proof']
        raw = _read(self.root, contract['manifest_path'], 16 * METADATA_LIMIT)
        _need(hashlib.sha256(raw).hexdigest() == proof['manifest_sha256'], 'manifest changed during registration')
        manifest = _json(raw)
        run_id = _identifier(manifest['run_id'])
        base = Path(HOME) / run_id
        if not historical:
            for path in [contract['manifest_path'], *[r['path'] for role in ('raw_data', 'outputs')
                                                     for r in manifest['artifacts'][role]]]:
                _need(Path(path).is_relative_to(base), 'new manifest/raw_data/outputs belong in ' + base.as_posix())
        if measured_at is not None:
            _timestamp(measured_at)
        origin = origin or ('historical-external-reference' if historical else 'native')
        _need(origin in (('historical-external-reference', 'legacy-contract-reference') if historical else ('native',)),
              'origin/storage mismatch')
        return self._save({'schema_version': SCHEMA, 'run_id': run_id,
                          'summary': manifest['scope'], 'result_id': contract['result_id'],
                          'producer_task_id': contract['producer_task_id'], 'origin': origin,
                          'registered_at': dt.datetime.now(dt.timezone.utc).isoformat(),
                          'measured_at': measured_at, 'context': result_context(manifest),
                          'contract': deepcopy(contract),
                          'manifest_ref': {'path': contract['manifest_path'], 'sha256': proof['manifest_sha256']},
                          'artifacts': deepcopy(manifest['artifacts']), 'metrics': deepcopy(manifest['metrics']),
                          'validation_at_registration': inspected,
                          'trust_note': 'Stored validation is history, not a current trusted acceptance.'})

    def register_history(self, run_id, summary, artifacts, *, context=None, measured_at=None):
        """Index pre-contract history without inventing an independent validation."""
        _need(_text(summary), 'historical summary required')
        _need(isinstance(artifacts, list) and 1 <= len(artifacts) <= 64, '1..64 historical references required')
        _need(len({r['path'] for r in artifacts if isinstance(r, dict) and 'path' in r}) == len(artifacts),
              'duplicate or malformed historical reference')
        for ref in artifacts:
            _check_ref(self.root, ref)
        _context(context or {})
        if measured_at is not None:
            _timestamp(measured_at)
        return self._save({'schema_version': SCHEMA, 'run_id': _identifier(run_id), 'summary': summary,
                          'origin': 'historical-external-reference',
                          'registered_at': dt.datetime.now(dt.timezone.utc).isoformat(),
                          'measured_at': measured_at, 'context': deepcopy(context or {}),
                          'historical_artifacts': deepcopy(artifacts), 'contract': None,
                          'validation_at_registration': {'status': 'unknown', 'proof': None},
                          'trust_note': 'Historical refs only; old bytes are not migrated or certified.'})

    def search(self, query, *, limit=5, max_scan=200, context=None):
        _need(_text(query) and len(query) <= 2000, 'bounded nonempty query required')
        _need(type(limit) is int and 1 <= limit <= 20, 'limit must be 1..20')
        if context is not None:
            _context(context)
        names, partial = self._directories(max_scan)
        tokens = _tokens(query)
        hits, errors = [], []
        for name in names:
            try:
                shown = self.show(name)
                record = shown['record']
                haystack = json.dumps({k: record.get(k) for k in
                                      ('summary', 'run_id', 'result_id', 'producer_task_id', 'context')},
                                     ensure_ascii=False).casefold()
                score = sum(token in haystack for token in tokens)
                exact = (context is not None and set(context) == set(CONTEXT_FIELDS) and
                         not _unknown(context) and context == record['context'])
                if exact:
                    score += 1000  # Matching frozen conditions outrank vocabulary overlap.
                if score:
                    hits.append({'run_id': name, 'record_sha256': shown['record_ref']['sha256'],
                                 'record_path': shown['record_ref']['path'], 'summary': record['summary'],
                                 'origin': record['origin'], 'score': score,
                                 'match': 'exact-context' if exact else 'lexical',
                                 'stored_validation': record['validation_at_registration']['status'],
                                 'applicability': 'unchecked'})
            except (OSError, ValueError, KeyError, TypeError) as exc:
                errors.append({'run_id': name, 'error': str(exc)})
        hits.sort(key=lambda h: (-h['score'], h['run_id']))
        return {'schema_version': 'project-result-search/v1', 'query': query,
                'status': 'candidates' if hits else 'incomplete' if partial or errors else 'no_hits',
                'results': hits[:limit], 'strategy': 'lexical+exact-context' if context is not None else 'lexical',
                'scanned': len(names), 'partial': partial or len(hits) > limit,
                'errors': errors, 'authority': 'retrieval only; no applicability or acceptance proof'}

    def decide_run(self, run_id, context, *, verifier=None, explicit_reproduction=False,
                   new_claim=False, max_age_seconds=None, now=None):
        _context(context)
        _need(type(explicit_reproduction) is bool and type(new_claim) is bool, 'explicit intent flags must be boolean')
        if max_age_seconds is not None:
            _need(type(max_age_seconds) in (int, float) and math.isfinite(max_age_seconds) and max_age_seconds >= 0,
                  'max_age_seconds must be finite and nonnegative')
        shown = self.show(run_id)
        record, reasons = shown['record'], []
        old = record['context']
        missing = [key for key in CONTEXT_FIELDS if key not in context or key not in old or
                   _unknown(context[key]) or _unknown(old[key])]
        differences = [{'field': key, 'previous': old[key], 'requested': context[key]} for key in CONTEXT_FIELDS
                       if key in context and key in old and old[key] != context[key]]
        decision, status, proof, bound_measured_at = 'verify_delta', 'unknown', None, None
        if missing:
            reasons.append('missing conditions: ' + ', '.join(missing))
        if differences:
            reasons.append('changed conditions: ' + ', '.join(d['field'] for d in differences))
        try:
            contract = record.get('contract')
            if contract is None:
                for ref in record['historical_artifacts']:
                    _check_ref(self.root, ref)
                reasons.append('historical result has no independent validation contract')
            else:
                _check_ref(self.root, record['manifest_ref'])
                manifest = _json(_read(self.root, contract['manifest_path'], 16 * METADATA_LIMIT))
                bound_measured_at = manifest.get('execution', {}).get('completed_at')
                _need(result_context(manifest) == old and manifest['run_id'] == run_id,
                      'registry context/identity differs from frozen manifest')
                for key in ('result_id', 'producer_task_id', 'artifacts', 'metrics'):
                    _need(record.get(key) == manifest[key], 'registry differs from frozen manifest: ' + key)
                inspected = inspect_result(self.root, contract, verifier)
                status, proof = inspected['status'], inspected['proof']
                previous = record.get('validation_at_registration', {})
                if previous.get('status') == 'usable-with-scope' and status == 'usable-with-scope':
                    _need(previous.get('proof') == proof, 'accepted validation proof changed; version and reconcile')
                if status == 'invalid':
                    decision = 'rerun'
                if status != 'usable-with-scope':
                    reasons.extend(inspected['errors'])
                elif not missing and not differences:
                    decision = 'reuse'
                    reasons.append('exact frozen conditions and current independent scoped acceptance')
        except (OSError, ValueError, KeyError, TypeError) as exc:
            status, decision = 'stale', 'rerun'
            reasons.append(str(exc))
        if max_age_seconds is not None:
            if record.get('measured_at') is None or bound_measured_at != record.get('measured_at'):
                decision = 'verify_delta' if decision != 'rerun' else decision
                reasons.append('measurement time missing or not bound to manifest execution.completed_at; freshness cannot be established')
            else:
                instant = dt.datetime.now(dt.timezone.utc) if now is None else _timestamp(now)
                age = (instant - _timestamp(record['measured_at'])).total_seconds()
                if age < 0 or age > max_age_seconds:
                    decision = 'verify_delta' if decision != 'rerun' else decision
                    reasons.append('measurement outside requested freshness window')
        if explicit_reproduction or new_claim:
            decision = 'rerun'
            reasons.append('explicit reproduction/new-claim validation must execute; prior results are baseline only')
        return {'run_id': run_id, 'record_sha256': shown['record_ref']['sha256'], 'decision': decision,
                'reasons': reasons, 'missing_conditions': missing, 'differences': differences,
                'validation_status': status, 'proof': proof, 'automatic_skip_authorized': False,
                'next_action': {'reuse': 'host may explicitly select reuse_validated_result for this exact scope',
                                'verify_delta': 'resolve unknowns and independently verify only changed/needed conditions; create a new version',
                                'rerun': 'preserve historical data; run the required or repaired experiment and independently validate'}[decision]}

    def decide(self, query, context, *, limit=5, max_scan=200, **options):
        _context(context)
        search = self.search(query, limit=limit, max_scan=max_scan, context=context)
        results = [self.decide_run(hit['run_id'], context, **options) for hit in search['results']]
        return {'schema_version': 'project-result-decision/v1', 'query': query,
                'search': search, 'results': results,
                'status': search['status'], 'automatic_skip_authorized': False}


def check_task_reuse(root, task, verifier=None):
    """Current consumer guard. A planner, not a query hit, chooses reuse."""
    selection = task.get('result_reuse')
    if selection is None:
        _need(task.get('action') != 'reuse_validated_result', 'reuse action requires a pinned result selection')
        return []
    _need(isinstance(selection, dict), 'result_reuse object required')
    for key in ('run_id', 'record_sha256', 'query', 'context', 'explicit_reproduction', 'new_claim'):
        _need(key in selection, 'result_reuse requires ' + key)
    _need(_text(selection['query']), 'reuse query required')
    for flag in ('explicit_reproduction', 'new_claim'):
        _need(type(task.get(flag, False)) is bool and type(selection[flag]) is bool,
              'explicit intent flags must be boolean')
    result = ResultStore(root).decide_run(selection['run_id'], selection['context'], verifier=verifier,
               explicit_reproduction=selection['explicit_reproduction'] or task.get('explicit_reproduction', False),
               new_claim=selection['new_claim'] or task.get('new_claim', False),
               max_age_seconds=selection.get('max_age_seconds'))
    _need(result['record_sha256'] == selection['record_sha256'], 'prior result registry record changed; replan')
    _need(result['decision'] == 'reuse', 'prior result cannot be reused: ' + '; '.join(result['reasons']))
    return [{'run_id': result['run_id'], 'record_sha256': result['record_sha256'],
             'context': deepcopy(selection['context']), 'decision': 'reuse', 'result_proof': result['proof']}]


def register_task_result(root, task):
    """Producer hook: record pending raw results, with exact replay deduplication.

    Older plan locations retain immutable refs; result_storage='central' forbids
    that compatibility route for newly planned producers. No files are relocated.
    """
    contract = task.get('experiment_result')
    if contract is None:
        return None
    store = ResultStore(root)
    manifest = _json(_read(store.root, contract['manifest_path'], 16 * METADATA_LIMIT))
    run_id = _identifier(manifest['run_id'])
    canonical = Path(contract['manifest_path']).is_relative_to(Path(HOME) / run_id)
    if task.get('result_storage') == 'central' or (store.root / 'agent_doc/task/TASK.md').exists():
        _need(canonical, 'central result producer requires agent_doc/results/<run_id>/ manifest')
        _need(all(Path(ref['path']).is_relative_to(Path(HOME) / run_id)
                  for role in ('raw_data', 'outputs') for ref in manifest['artifacts'][role]),
              'central result producer requires centralized raw_data/outputs, including replay')
    target = _path(store.root, store._record_path(run_id))
    if target.exists():
        existing = store.show(run_id)
        record = existing['record']
        _need(record.get('contract') == contract, 'result run_id collision: different contract')
        _check_ref(store.root, record['manifest_ref'])
        _need(record['context'] == result_context(manifest), 'result run_id collision: changed context')
        inspected = inspect_result(store.root, contract)
        _need(inspected.get('proof') is not None, 'stale replay artifacts')
        return existing
    return store.register(contract, historical=not canonical,
                          origin=None if canonical else 'legacy-contract-reference')


class ReuseResultHandler:
    """Explicit trusted-host action; never silently skips a producer handler."""
    idempotent = True
    required_capabilities = frozenset({'read_artifacts', 'independent_result_validation'})

    def __init__(self, root, verifier=None):
        self.root, self.verifier = root, verifier

    def run(self, task, context):
        from .core import Outcome
        try:
            proofs = check_task_reuse(self.root, task, self.verifier)
            _need(bool(proofs), 'reuse action requires selection')
            return Outcome('complete', 'reused independently validated prior data within exact scope', proofs)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            return Outcome('pending', str(exc))

    def verify(self, task, evidence):
        try:
            proofs = check_task_reuse(self.root, task, self.verifier)
            return bool(proofs) and proofs == evidence
        except (OSError, ValueError, KeyError, TypeError):
            return False
