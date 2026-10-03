"""Trusted-controller acceptance gate; this module does not judge prose or identity.

Only the caller may supply acceptance. Never load it from a worker-controlled
record field. The caller must protect the acceptance file/API argument and must
actually observe independent review and host events. Hashes bind reviewed bytes;
they do not authenticate a reviewer, prove reading, or detect a dishonest trusted
controller. Receipt JSON is similarly evidence supplied by that controller.

Schema v1: {schema_version, record_sha256, reviewer_actor, file_hashes,
versions: [{language, snapshot_sha256, checks: {artifact_fit: {verdict, evidence},
originality: {verdict, evidence}}}]}. Evidence is a nonempty list of concrete
locations/reasons from independent review. No keyword-based prose classifier.
"""
import hashlib
import json
from pathlib import Path


SEMANTIC_CHECKS = ('artifact_fit', 'originality')


def canonical_record_sha256(record):
    """Hash the complete record, not an acceptance object embedded in it."""
    encoded = json.dumps(record, sort_keys=True, separators=(',', ':'),
                         ensure_ascii=False, allow_nan=False).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


def declared_file_hashes(record):
    """Collect every artifact binding, rejecting contradictory duplicate paths."""
    result = {}
    def visit(value):
        if isinstance(value, dict):
            if 'path' in value and 'sha256' in value:
                path, digest = value['path'], value['sha256']
                if not isinstance(path, str) or not isinstance(digest, str):
                    raise ValueError('invalid artifact hash binding')
                if path in result and result[path] != digest:
                    raise ValueError('contradictory artifact hash binding')
                result[path] = digest
            for item in value.values(): visit(item)
        elif isinstance(value, list):
            for item in value: visit(item)
    visit(record)
    return result


def safe_file(root, path):
    raw = Path(path)
    resolved = (root / raw).resolve()
    if raw.is_absolute() or not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError('artifact path outside root or missing')
    return resolved


def validate_role_events(binding, root, expected_run_id=None):
    """Return errors and observed event IDs, never infer an event from dispatch."""
    errors, event_ids = [], []
    role = binding.get('role')
    for field, kind in (('start_receipt', 'start'), ('result_receipt', 'complete')):
        try:
            artifact = binding[field]
            path = safe_file(Path(root).resolve(), artifact['path'])
            content = path.read_bytes()
            if hashlib.sha256(content).hexdigest() != artifact['sha256']:
                raise ValueError('receipt hash mismatch')
            event = json.loads(content)
            if not isinstance(event, dict): raise ValueError('receipt must be an object')
            if any(marker in event and event[marker] is not False for marker in ('synthetic', 'fixture_only')) or event.get('adapter') in ('mock', 'fixture', 'synthetic'):
                raise ValueError('synthetic/mock receipt cannot certify actual execution')
            if event.get('kind') != kind: raise ValueError(f'expected {kind} event')
            if kind == 'start' and event.get('status') != 'started':
                raise ValueError('start event must have started status; cannot be queued or incomplete')
            if kind == 'complete' and event.get('status') != 'produced':
                raise ValueError('completion event must have produced status')
            if not isinstance(expected_run_id, str) or not expected_run_id.strip() or binding.get('run_id') != expected_run_id:
                raise ValueError('receipt binding must match record run_id')
            for key in ('actor', 'role', 'revision', 'run_id', 'task_id'):
                if not isinstance(binding.get(key), str) or not binding[key].strip() or event.get(key) != binding[key]:
                    raise ValueError(f'receipt {key} does not match binding')
            if type(binding.get('attempt')) is not int or binding['attempt'] < 1 or type(event.get('attempt')) is not int or event['attempt'] != binding['attempt']:
                raise ValueError('receipt attempt does not match positive binding attempt')
            event_id = event.get('event_id')
            if not isinstance(event_id, str) or not event_id.strip():
                raise ValueError('receipt event_id required')
            event_ids.append(event_id)
        except (KeyError, TypeError, ValueError, OSError, RuntimeError) as exc:
            errors.append(f'{role}: invalid observed {field}: {exc}')
    return errors, event_ids


def validate_acceptance(record, root, acceptance):
    """Fail closed unless the external trusted controller supplied bound passes."""
    errors = []
    if not isinstance(acceptance, dict):
        return ['unverified: completion requires external trusted semantic acceptance']
    def need(ok, message):
        if not ok: errors.append('semantic acceptance: '+message)
    need(type(acceptance.get('schema_version')) is int and acceptance['schema_version'] == 1,
         'schema_version')
    try:
        need(acceptance.get('record_sha256') == canonical_record_sha256(record), 'stale record hash')
        files = declared_file_hashes(record)
        need(acceptance.get('file_hashes') == files and bool(files), 'file hash coverage mismatch')
        for path, digest in files.items():
            actual = safe_file(Path(root).resolve(), path).read_bytes()
            need(hashlib.sha256(actual).hexdigest() == digest, f'stale file: {path}')
    except (TypeError, ValueError, OSError, RuntimeError) as exc:
        errors.append(f'semantic acceptance: invalid record/files: {exc}')
    bindings = record.get('bindings')
    bindings = bindings if isinstance(bindings, list) else []
    writers = [b.get('actor') for b in bindings if isinstance(b, dict) and b.get('role') == 'research-write']
    reviewers = [b.get('actor') for b in bindings if isinstance(b, dict) and b.get('role') == 'research-review'
                 and b.get('state') == 'completed' and b.get('mode') == 'independent']
    actor = acceptance.get('reviewer_actor')
    need(isinstance(actor, str) and bool(actor.strip()) and actor not in writers and actor in reviewers,
         'reviewer must match independent review binding and differ from writer')
    versions = record.get('versions')
    versions = versions if isinstance(versions, list) else []
    accepted = acceptance.get('versions')
    accepted = accepted if isinstance(accepted, list) else []
    languages = [v.get('language') for v in versions if isinstance(v, dict)]
    accepted_languages = [v.get('language') for v in accepted if isinstance(v, dict)]
    need(all(isinstance(x, str) for x in languages + accepted_languages)
         and len(accepted) == len(versions) and len(accepted_languages) == len(accepted)
         and sorted(str(x) for x in accepted_languages) == sorted(str(x) for x in languages),
         'language coverage mismatch')
    for version in versions:
        if not isinstance(version, dict): continue
        language = version.get('language')
        candidates = [v for v in accepted if isinstance(v, dict) and v.get('language') == language]
        if len(candidates) != 1:
            errors.append(f'semantic acceptance: {language}: unique language acceptance required')
            continue
        review = candidates[0]
        snapshot = version.get('snapshot')
        snapshot = snapshot if isinstance(snapshot, dict) else {}
        need(isinstance(snapshot.get('sha256'), str) and review.get('snapshot_sha256') == snapshot['sha256'],
             f'{language}: stale snapshot hash')
        checks = review.get('checks')
        checks = checks if isinstance(checks, dict) else {}
        for criterion in SEMANTIC_CHECKS:
            check = checks.get(criterion)
            check = check if isinstance(check, dict) else {}
            evidence = check.get('evidence')
            need(check.get('verdict') == 'pass', f'{language}/{criterion}: independent pass required')
            need(isinstance(evidence, list) and bool(evidence) and
                 all(isinstance(item, str) and bool(item.strip()) for item in evidence),
                 f'{language}/{criterion}: evidence locations required')
    return errors
