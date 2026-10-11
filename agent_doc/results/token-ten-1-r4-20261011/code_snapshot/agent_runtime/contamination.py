"""Confirmed experiment defects: revoke, stop exact jobs, quarantine, repair gate.

Trusted host API, not a scheduler or a defect detector. Host callbacks authenticate
findings, own/fence jobs and enumerate the complete reference closure. No JSON
command is executed. Files are renamed recoverably; old identities stay revoked.
"""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re

from .project_docs import assert_ai_writable, atomic_write

HOME = '.agent-runs/contamination'


def _key(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('nonempty identity required')
    return hashlib.sha256(value.encode()).hexdigest()


def _path(root, name):
    from .result_validation import _path as checked_path
    return checked_path(Path(root).resolve(), name)


def _read(root, name):
    from .result_validation import _bytes, _json
    return _json(_bytes(Path(root).resolve(), name))


def _save(root, name, value):
    atomic_write(root, name, (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode())


def _run(run_id):
    return f'{HOME}/runs/{_key(run_id)}'


def assert_not_revoked(root, *, result_id=None, run_id=None):
    """Read-only gate, also used before/after independent result verification."""
    if result_id is not None:
        index = f'{HOME}/results/{_key(result_id)}.json'
        if _path(root, index).exists():
            registered = _read(root, index)['run_id']
            assert_not_revoked(root, run_id=registered)
    if run_id is not None:
        incident = f'{_run(run_id)}/incident.json'
        if _path(root, incident).exists():
            # Any incident, including unreadable/partial state, is fail closed.
            raise ValueError('contaminated experiment revoked: ' + run_id + '; see ' + incident)


class Contamination:
    """Main-AI host entry; authorize(action, binding) must use live host authority.

    bind is called before launch; job is the host's immutable reserved job identity.
    stop(binding) must return {job: exact identity, stopped: True, fenced: True,
    source: actual readback reference}. Fencing covers all ranks/writers and retry
    dispatch. The host must bound callback deadlines; this API cannot preempt a
    hung external controller. Shared indexes require per-run entries or an external
    transactional invalidator; inventory_complete is checked by authorize, not
    inferred from a directory name or a worker's assertion.
    """
    def __init__(self, root, *, authorize):
        self.root = Path(root).resolve()
        self.authorize = authorize

    @contextmanager
    def _lock(self, run_id=None):
        # Stable lock inode, shared by participating controllers on this host.
        import fcntl
        name = f'{_run(run_id)}/lock' if run_id is not None else f'{HOME}/lock'
        path = assert_ai_writable(self.root, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('a+b') as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            yield

    def _allow(self, action, binding):
        if self.authorize(action, deepcopy(binding)) is not True:
            raise ValueError('host authorization/ownership unavailable: ' + action)

    def _binding(self, binding):
        from .result_validation import _bound
        value = deepcopy(binding)
        run_id = value.get('run_id')
        if not isinstance(run_id, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}', run_id):
            raise ValueError('safe unique run_id required')
        for field in ('result_ids', 'task_refs'):
            items = value.get(field)
            if not isinstance(items, list) or not items or len(set(items)) != len(items):
                raise ValueError('unique nonempty ' + field + ' required')
            for item in items:
                _key(item)
        if not isinstance(value.get('job'), dict) or not value['job']:
            raise ValueError('immutable host job identity required; bare PID is insufficient')
        for role in ('code', 'config', 'data'):
            refs = value.get(role)
            if not isinstance(refs, list) or not refs:
                raise ValueError('frozen ' + role + ' bindings required')
            for ref in refs:
                _bound(self.root, ref)
        if value.get('inventory_complete') is not True:
            raise ValueError('host must enumerate complete output/reference/cache closure')
        paths = value.get('owned_paths')
        if not isinstance(paths, list) or not paths:
            raise ValueError('run-exclusive output/reference/cache paths required')
        normalized = []
        for name in paths:
            p = _path(self.root, name)
            assert_ai_writable(self.root, p)
            # Only per-run output namespaces, never source, guide or shared index.
            parts = Path(name).parts
            allowed = (parts[:2] == ('agent_doc', 'results') or parts[:1] == ('.agent-runs',))
            if not allowed or run_id not in parts or parts[:2] == ('.agent-runs', 'contamination'):
                raise ValueError('owned path must be in an explicit per-run output namespace')
            if any(p == q or p.is_relative_to(q) or q.is_relative_to(p) for q in normalized):
                raise ValueError('overlapping owned paths')
            normalized.append(p)
        value['identity_sha256'] = hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()
        return value

    def bind(self, binding):
        """Freeze before launch; cannot reuse a run/result ID or previous paths."""
        with self._lock():
            value = self._binding(binding)
            self._allow('bind', value)
            location = f'{_run(value["run_id"])}/binding.json'
            if _path(self.root, location).exists():
                raise ValueError('run identity already frozen; use a new run')
            for rid in value['result_ids']:
                if _path(self.root, f'{HOME}/results/{_key(rid)}.json').exists():
                    raise ValueError('result identity already frozen')
            # All outputs must start absent; no old checkpoint or cache admission.
            if any(_path(self.root, p).exists() for p in value['owned_paths']):
                raise ValueError('fresh output/cache namespaces required')
            parent = _path(self.root, f'{HOME}/runs')
            if parent.exists():
                for old in parent.glob('*/binding.json'):
                    previous = _read(self.root, str(old.relative_to(self.root)))
                    for a in value['owned_paths']:
                        for b in previous['owned_paths']:
                            x, y = Path(a), Path(b)
                            if x == y or x.is_relative_to(y) or y.is_relative_to(x):
                                raise ValueError('output ownership overlaps a frozen run')
            # Binding first: interrupted registration remains unlaunchable and
            # burns the run ID rather than silently admitting a partial identity.
            _save(self.root, location, value)
            for rid in value['result_ids']:
                _save(self.root, f'{HOME}/results/{_key(rid)}.json', {'run_id': value['run_id']})
            return value

    def load(self, run_id):
        return _read(self.root, f'{_run(run_id)}/binding.json')

    def _stop(self, binding, stop):
        self._allow('stop', binding)
        receipt = stop(deepcopy(binding))
        if not (isinstance(receipt, dict) and receipt.get('job') == binding['job'] and
                receipt.get('stopped') is True and receipt.get('fenced') is True and receipt.get('source')):
            raise ValueError('exact job exit and writer/retry fencing readback required')
        return receipt

    def contain(self, run_id, finding, *, confirm, stop):
        """Immediate host-confirmed incident; retries keep the original finding.

        Suspicion or a confirmed but inapplicable defect has no stop/cleanup effect.
        confirm(binding, finding) returns the exact identity_sha256 only after
        independently checking evidence and applicability to this execution.
        """
        with self._lock(run_id):
            binding = self.load(run_id)
            evidence = None
            location = f'{_run(run_id)}/incident.json'
            if _path(self.root, location).exists():
                incident = _read(self.root, location)
            else:
                if finding.get('status') != 'confirmed' or finding.get('affects_run') is not True:
                    return {'status': 'verify-risk', 'run_id': run_id, 'stopped': False}
                from .result_validation import _bound
                if not finding.get('reason') or not finding.get('evidence'):
                    raise ValueError('defect reason and reproducible evidence required')
                evidence = [_bound(self.root, ref) for ref in finding['evidence']]
                if confirm(deepcopy(binding), deepcopy(finding)) != binding['identity_sha256']:
                    raise ValueError('confirmed finding is not authenticated for this frozen execution')
                self._allow('contain', binding)
                incident = {'run_id': run_id, 'identity_sha256': binding['identity_sha256'],
                            'finding': deepcopy(finding), 'status': 'stop-required', 'moves': []}
                # This is the irrevocable validity revocation, before any stop.
                try:
                    _save(self.root, location, incident)
                except OSError as exc:
                    # Disk failure must not leave a confirmed bad job running.
                    # No cleanup/rerun: host must restore durable gate storage.
                    incident.update(status='blocked', error='revocation persistence failed: ' + str(exc))
                    try:
                        incident['stop_receipt'] = self._stop(binding, stop)
                    except Exception as stop_error:
                        incident['stop_error'] = str(stop_error)
                    incident['durable'] = False
                    return incident
            if incident['status'] == 'quarantined':
                return incident
            try:
                receipt = self._stop(binding, stop)
                incident.update(status='stopped', stop_receipt=receipt)
                _save(self.root, location, incident)
                from .result_validation import _bound
                for n, ref in enumerate(incident['finding']['evidence']):
                    target = f'{_run(run_id)}/evidence/{n}'
                    if not _path(self.root, target).exists():
                        data = evidence[n] if evidence is not None else _bound(self.root, ref)
                        atomic_write(self.root, target, data)
                self._allow('quarantine', binding)
                for n, name in enumerate(binding['owned_paths']):
                    src = _path(self.root, name)
                    dst_name = f'{_run(run_id)}/quarantine/{n}'
                    dst = _path(self.root, dst_name)
                    assert_ai_writable(self.root, src)
                    assert_ai_writable(self.root, dst)
                    if src.exists() and dst.exists():
                        raise ValueError('both active and quarantine paths exist; reconcile writers')
                    if src.exists():
                        # Reject redirected/special descendants rather than moving
                        # unknown resources. This is not an adversarial OS sandbox.
                        files = [src, *src.rglob('*')] if src.is_dir() else [src]
                        for path in files:
                            _path(self.root, str(path.relative_to(self.root)))
                            assert_ai_writable(self.root, path)
                            if not (path.is_file() or path.is_dir()):
                                raise ValueError('nonregular quarantine artifact')
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        src.rename(dst)
                    move = {'source': name, 'quarantine': dst_name, 'present': dst.exists()}
                    incident['moves'] = [m for m in incident['moves'] if m['source'] != name] + [move]
                    _save(self.root, location, incident)
                incident['status'] = 'quarantined'
                incident.pop('error', None)
            except Exception as exc:
                incident.update(status='blocked', error=f'{type(exc).__name__}: {exc}')
            _save(self.root, location, incident)
            return incident

    def prepare_replacement(self, run_id, binding, *, verify_fix):
        """No launch: validate repair, current resource authority, freeze new IDs.

        verify_fix(old, new) is a trusted independent code/test verifier and returns
        the new identity digest. It must check frozen tests against the actual fix.
        New results still require existing verify_experiment_result acceptance.
        """
        with self._lock(run_id):
            old = self.load(run_id)
            incident = _read(self.root, f'{_run(run_id)}/incident.json')
            if incident['status'] != 'quarantined':
                raise ValueError('stop/cleanup incomplete; replacement blocked')
            if incident.get('replacement'):
                raise ValueError('replacement already reserved; reconcile that run, do not duplicate')
            new = self._binding(binding)
            if new['run_id'] == run_id or set(new['result_ids']) & set(old['result_ids']):
                raise ValueError('replacement requires new run and result identities')
            if new['code'] == old['code'] and new['config'] == old['config']:
                raise ValueError('repair must change frozen code or configuration')
            if new['job'] == old['job']:
                raise ValueError('new job identity required')
            if any(_path(self.root, p).exists() for p in new['owned_paths']):
                raise ValueError('fresh output/cache namespaces required')
            if any(_path(self.root, p).exists() for p in old['owned_paths']):
                raise ValueError('old writer recreated active outputs; reconcile before rerun')
            self._allow('rerun', new)
            if verify_fix(deepcopy(old), deepcopy(new)) != new['identity_sha256']:
                raise ValueError('independent repair validation unavailable or failed')
            # Re-read bound bytes at bind time to catch mutation during verification.
            self._binding(binding)
            incident['replacement'] = {'run_id': new['run_id'], 'identity_sha256': new['identity_sha256']}
            _save(self.root, f'{_run(run_id)}/incident.json', incident)
            value = self.bind(binding)
            _save(self.root, f'{_run(value["run_id"])}/repair.json',
                  {'supersedes': run_id, 'identity_sha256': value['identity_sha256']})
            return value
