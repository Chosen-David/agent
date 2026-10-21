"""Recoverable publication evidence; never stages, commits or pushes.

The main controller serializes calls and supplies trusted authorization, independent
acceptance and remote observation functions. JSON reports cannot supply those
functions. Hashes prove consistency, not test quality or scientific validity.
State is private local audit data, not tamper-proof against its filesystem owner.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import time

from .external_json import load_json
from .project_memory import check_task_memory
from .task_manifest import atomic_json, task_source_snapshot
from .project_docs import (assert_ai_writable, check_document_refs, resolve_task_file,
                           snapshot_project_docs)


class PublicationError(ValueError):
    """Publication remains pending until this gate is resolved."""


STATE_LIMIT = 16 * 1024 * 1024
HEX40_OR_64 = re.compile(r'(?:[0-9a-f]{40}|[0-9a-f]{64})\Z')
HEX64 = re.compile(r'[0-9a-f]{64}\Z')


def _hash(value):
    return hashlib.sha256(value).hexdigest()


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()


def _relative_path(value):
    return (isinstance(value, str) and bool(value) and '\x00' not in value and
            not Path(value).is_absolute() and '..' not in Path(value).parts)


def _path_hash(value):
    return (isinstance(value, dict) and set(value) == {'path', 'sha256'} and
            _relative_path(value.get('path')) and
            isinstance(value.get('sha256'), str) and HEX64.fullmatch(value['sha256']))


def _document_snapshot(value):
    keys = {'schema_version', 'layout', 'task_index', 'task_details', 'guides',
            'advice', 'adopted_advice'}
    if (not isinstance(value, dict) or set(value) != keys or
            value.get('schema_version') != 'project-documents/v1' or
            value.get('layout') not in ('canonical', 'legacy') or
            not _path_hash(value.get('task_index'))):
        return False
    details = value.get('task_details')
    if (not isinstance(details, dict) or any(
            not isinstance(task_id, str) or not task_id or not _path_hash(ref)
            for task_id, ref in details.items())):
        return False
    for field in ('guides', 'advice', 'adopted_advice'):
        mapping = value.get(field)
        if (not isinstance(mapping, dict) or any(
                not _relative_path(path) or not isinstance(digest, str) or
                HEX64.fullmatch(digest) is None for path, digest in mapping.items())):
            return False
    return True


def _candidate_shape(candidate):
    keys = {'files', 'sha256', 'base_commit', 'file_task_refs', 'task_path',
            'task_sha256', 'project_documents', 'reviewed_plan'}
    if not isinstance(candidate, dict) or set(candidate) != keys:
        return False
    files = candidate.get('files')
    if not isinstance(files, dict) or not files:
        return False
    for path, entry in files.items():
        if (not _relative_path(path) or not isinstance(entry, dict) or
                set(entry) != {'mode', 'oid', 'sha256'} or
                entry.get('mode') not in ('100644', '100755') or
                not isinstance(entry.get('oid'), str) or
                HEX40_OR_64.fullmatch(entry['oid']) is None or
                not isinstance(entry.get('sha256'), str) or
                HEX64.fullmatch(entry['sha256']) is None):
            return False
    if (not isinstance(candidate.get('sha256'), str) or
            HEX64.fullmatch(candidate['sha256']) is None or
            candidate['sha256'] != _hash(_canonical(files)) or
            not isinstance(candidate.get('base_commit'), str) or
            HEX40_OR_64.fullmatch(candidate['base_commit']) is None or
            not _relative_path(candidate.get('task_path')) or
            candidate['task_path'] not in files or
            not isinstance(candidate.get('task_sha256'), str) or
            HEX64.fullmatch(candidate['task_sha256']) is None or
            candidate['task_sha256'] != files[candidate['task_path']]['sha256'] or
            not _document_snapshot(candidate.get('project_documents'))):
        return False
    ownership = candidate.get('file_task_refs')
    if not isinstance(ownership, dict) or not ownership:
        return False
    for path, refs in ownership.items():
        if (not _relative_path(path) or not isinstance(refs, list) or not refs or
                any(not isinstance(ref, str) or not ref for ref in refs) or
                len(refs) != len(set(refs))):
            return False
    reviewed = candidate.get('reviewed_plan')
    if reviewed is not None:
        try:
            from .core import validate
            validate(reviewed)
        except (TypeError, ValueError, KeyError):
            return False
    return True


def _readback_shape(value):
    return (isinstance(value, dict) and
            set(value) == {'remote_url', 'branch', 'commit', 'observed_at'} and
            all(isinstance(value.get(key), str) and value[key]
                for key in ('remote_url', 'branch')) and
            isinstance(value.get('commit'), str) and
            HEX40_OR_64.fullmatch(value['commit']) is not None and
            type(value.get('observed_at')) in (int, float))


def _evidence_shape(value):
    if not isinstance(value, list):
        return False
    for item in value:
        refs = item.get('task_refs') if isinstance(item, dict) else None
        if (not isinstance(item, dict) or not isinstance(item.get('path'), str) or
                not Path(item['path']).is_absolute() or
                not isinstance(item.get('sha256'), str) or
                HEX64.fullmatch(item['sha256']) is None or
                not isinstance(item.get('candidate_sha256'), str) or
                HEX64.fullmatch(item['candidate_sha256']) is None or
                not isinstance(refs, list) or not refs or
                any(not isinstance(ref, str) or not ref for ref in refs) or
                len(refs) != len(set(refs))):
            return False
        memory = item.get('memory_refs')
        if (memory is not None and
                (not isinstance(memory, list) or
                 any(not isinstance(ref, str) or not ref for ref in memory) or
                 len(memory) != len(set(memory)) or not memory)):
            return False
    return True


def _regular_bytes(path):
    path = Path(path)
    for parent in (path, *path.parents):
        if parent.is_symlink():
            raise PublicationError('symlink in evidence or candidate path')
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0))
    with os.fdopen(fd, 'rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise PublicationError('evidence and candidate must be regular files')
        return stream.read()


def _git(root, *args):
    # No shell, pager, optional index writes, inherited alternate repository or
    # user-supplied executable. Commands below only inspect local Git metadata.
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env.update(GIT_OPTIONAL_LOCKS='0', GIT_TERMINAL_PROMPT='0', GIT_PAGER='cat',
               GIT_NO_REPLACE_OBJECTS='1', GIT_GRAFT_FILE=os.devnull)
    try:
        result = subprocess.run(['git', '-C', str(root), *args], env=env,
                                capture_output=True, timeout=30, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise PublicationError('Git observation unavailable') from exc
    if result.returncode:
        # Avoid propagating credential-bearing URLs or arbitrary stderr.
        raise PublicationError('Git observation failed: ' + args[0])
    return result.stdout


def local_remote_reader(scope):
    """Read a local bare repository only; never contacts a network or credentials.

    Real hosts must supply their own trusted read-only remote API callback, whose
    tool access and authorization belong to the host, not a serialized plan.
    """
    path = Path(scope['remote_url'])
    if not path.is_absolute() or not path.is_dir():
        raise PublicationError('local reader requires an absolute local repository')
    # rev-parse of a local branch avoids transport, URL rewriting and helpers.
    oid = _git(path, 'rev-parse', '--verify', 'refs/heads/' + scope['branch']).decode().strip()
    return {'remote_url': scope['remote_url'], 'branch': scope['branch'], 'commit': oid}


class PublicationLedger:
    """Single-controller ledger; absent trusted callbacks always fail closed.

    authorize(scope, action) -> bool checks current approval/revocation.
    accept(candidate, evidence) -> bool independently verifies actual acceptance.
    remote_reader(scope) -> {remote_url, branch, commit} performs a fresh read.
    The controller, not this helper, establishes those callbacks' trustworthiness.
    """

    def __init__(self, root, state_path, *, authorize=None, accept=None, remote_reader=None,
                 plan=None, plan_review_verifier=None, allow_legacy=False, publication_task_refs=None):
        self.root = Path(root).resolve()
        self.path = Path(os.path.abspath(state_path))
        self.authorize, self.accept, self.remote_reader = authorize, accept, remote_reader
        self.plan, self.plan_review_verifier = copy.deepcopy(plan), plan_review_verifier
        self.allow_legacy = allow_legacy is True
        from .plan_review import _scope
        self.publication_task_refs = _scope(publication_task_refs)
        if Path(_git(self.root, 'rev-parse', '--show-toplevel').decode().strip()).resolve() != self.root:
            raise PublicationError('root must be the repository top level')
        if self.path.is_relative_to(self.root):
            rel = str(self.path.relative_to(self.root))
            # State cannot alter its own candidate or hide arbitrary source files.
            if not rel.startswith('.agent-runs/'):
                raise PublicationError('in-repository state must be under ignored .agent-runs/')
            _git(self.root, 'check-ignore', '--no-index', '--', rel)
            if _git(self.root, 'ls-files', '--', rel):
                raise PublicationError('publication state must not be tracked')

    def _save(self, value):
        for path in (self.path, *self.path.parents):
            if path.is_symlink():
                raise PublicationError('state path must not contain symlinks')
        atomic_json(self.path, value)
        return copy.deepcopy(value)

    def status(self):
        """Historical observations, not a new assertion of current acceptance."""
        for path in (self.path, *self.path.parents):
            if path.is_symlink():
                raise PublicationError('state path must not contain symlinks')
        try:
            value = load_json(self.path, max_bytes=STATE_LIMIT)
        except ValueError as exc:
            raise PublicationError('invalid publication state: ' + str(exc)) from exc
        if not isinstance(value, dict):
            raise PublicationError('publication state must be a JSON object')
        allowed = {'schema_version', 'scope', 'candidate', 'phase', 'tested', 'committed',
                   'pushed', 'remote_verified', 'evidence', 'commit', 'events', 'last_error',
                   'push_readback', 'remote_readback'}
        required = allowed - {'push_readback', 'remote_readback'}
        if not required <= set(value) or not set(value) <= allowed:
            raise PublicationError('publication state has invalid fields')
        scope = value.get('scope')
        candidate = value.get('candidate')
        if (value.get('schema_version') != 'publication/v1' or not isinstance(scope, dict)
                or scope.get('repository') != str(self.root)):
            raise PublicationError('state repository or schema mismatch')
        if (set(scope) != {'repository', 'remote', 'remote_url', 'branch', 'authorization_reference'}
                or any(not isinstance(scope.get(key), str) or not scope[key].strip()
                       for key in scope)):
            raise PublicationError('publication state has invalid scope')
        if not _candidate_shape(candidate):
            raise PublicationError('publication state has invalid candidate')
        if (not isinstance(value.get('phase'), str) or
                value['phase'] not in {'pending', 'tested', 'committed', 'pushed', 'remote_verified'}
                or any(type(value.get(key)) is not bool
                       for key in ('tested', 'committed', 'pushed', 'remote_verified'))
                or not _evidence_shape(value.get('evidence'))
                or not isinstance(value.get('events'), list)
                or not (value.get('commit') is None or isinstance(value.get('commit'), str) and
                        HEX40_OR_64.fullmatch(value['commit']) is not None)
                or not (value.get('last_error') is None or isinstance(value.get('last_error'), str))):
            raise PublicationError('publication state has invalid lifecycle fields')
        events = value['events']
        actions = {'tested', 'committed', 'pushed', 'remote_verified', 'push_failed_pending'}
        if any(not isinstance(event, dict) or set(event) != {'action', 'observed_at'} or
               not isinstance(event.get('action'), str) or event['action'] not in actions or
               type(event.get('observed_at')) not in (int, float) for event in events):
            raise PublicationError('publication state has invalid events')
        phase = value['phase']
        expected = {
            'pending': (False, False, False, False),
            'tested': (True, False, False, False),
            'committed': (True, True, False, False),
            'pushed': (True, True, True, False),
            'remote_verified': (True, True, True, True),
        }[phase]
        flags = tuple(value[key] for key in ('tested', 'committed', 'pushed', 'remote_verified'))
        if (flags != expected or (phase == 'pending' and value['evidence']) or
                (phase != 'pending' and not value['evidence']) or
                ((phase in ('pending', 'tested')) != (value['commit'] is None)) or
                ('push_readback' in value) != (phase in ('pushed', 'remote_verified')) or
                ('remote_readback' in value) != (phase == 'remote_verified') or
                ('push_readback' in value and not _readback_shape(value['push_readback'])) or
                ('remote_readback' in value and not _readback_shape(value['remote_readback']))):
            raise PublicationError('publication state has inconsistent lifecycle')
        return value

    def _scope(self, scope, action):
        branch = _git(self.root, 'symbolic-ref', '--short', 'HEAD').decode().strip()
        urls = _git(self.root, 'remote', 'get-url', '--push', '--all', scope['remote']).decode().splitlines()
        if branch != scope['branch'] or urls != [scope['remote_url']]:
            raise PublicationError('authorized remote or branch changed')
        if self.authorize is None or self.authorize(copy.deepcopy(scope), action) is not True:
            raise PublicationError('explicit current repository/branch authorization required')

    def _tree(self, ref=None):
        entries = {}
        raw = (_git(self.root, 'ls-tree', '-r', '-z', ref) if ref else
               _git(self.root, 'ls-files', '--stage', '-z'))
        for row in raw.split(b'\0'):
            if not row:
                continue
            meta, name = row.split(b'\t', 1)
            mode, middle, last = meta.decode().split()
            oid = last if ref else middle
            if mode not in ('100644', '100755') or (not ref and last != '0'):
                raise PublicationError('unmerged, symlink or submodule candidate unsupported')
            name = os.fsdecode(name)
            if name.startswith('/') or '..' in Path(name).parts:
                raise PublicationError('unsafe Git tree path')
            entries[name] = {'mode': mode, 'oid': oid}
        return entries

    def _candidate(self):
        files = self._tree()
        if _git(self.root, 'ls-files', '--others', '--exclude-standard', '-z'):
            raise PublicationError('untracked files must be reconciled before freezing')
        algorithm = _git(self.root, 'rev-parse', '--show-object-format').decode().strip()
        for name, entry in files.items():
            path = self.root / name
            data = _regular_bytes(path)
            oid = hashlib.new(algorithm, b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
            executable = bool(path.stat().st_mode & 0o111)
            if oid != entry['oid'] or executable != (entry['mode'] == '100755'):
                raise PublicationError('unstaged content or mode differs from candidate: ' + name)
            entry['sha256'] = _hash(data)
        # Include mode and names, so byte-identical renames still change identity.
        return {'files': files, 'sha256': _hash(_canonical(files))}

    def freeze(self, file_task_refs, *, remote, branch, authorization_reference):
        if self.path.exists():
            raise PublicationError('state already exists; use a new candidate state path')
        if not all(isinstance(v, str) and v.strip() and not v.startswith('-')
                   for v in (remote, branch, authorization_reference)):
            raise PublicationError('explicit remote, branch and authorization reference required')
        urls = _git(self.root, 'remote', 'get-url', '--push', '--all', remote).decode().splitlines()
        if len(urls) != 1:
            raise PublicationError('exactly one explicit push remote URL required')
        scope = dict(repository=str(self.root), remote=remote, remote_url=urls[0], branch=branch,
                     authorization_reference=authorization_reference)
        self._scope(scope, 'freeze')
        candidate = self._candidate()
        task_file = resolve_task_file(self.root)
        task_relative = task_file.relative_to(self.root).as_posix()
        if task_relative not in candidate['files']:
            raise PublicationError('resolved TASK.md must be part of the frozen tree')
        base = _git(self.root, 'rev-parse', 'HEAD').decode().strip()
        before = self._tree(base)
        after = {p: {'mode': v['mode'], 'oid': v['oid']} for p, v in candidate['files'].items()}
        changed = sorted(p for p in before.keys() | after.keys() if before.get(p) != after.get(p))
        for name in changed:
            try:
                assert_ai_writable(self.root, name)
            except ValueError as exc:
                raise PublicationError('human guide changes cannot be included in an AI publication: ' + name) from exc
        try:
            task_snapshot = task_source_snapshot(task_file, self.root)
        except (OSError, ValueError) as exc:
            raise PublicationError('cannot bind publication TASK snapshot: ' + str(exc)) from exc
        if task_snapshot['sha256'] != candidate['files'][task_relative]['sha256']:
            raise PublicationError('TASK changed while freezing candidate ownership')
        ids = {item['id'] for item in task_snapshot['items']}
        if not changed or not isinstance(file_task_refs, dict) or set(file_task_refs) != set(changed):
            raise PublicationError('every changed file needs exact TASK ownership; no omitted or extra paths')
        for refs in file_task_refs.values():
            if (not isinstance(refs, list) or not refs or any(not isinstance(r, str) or r not in ids for r in refs)
                    or len(set(refs)) != len(refs)):
                raise PublicationError('file ownership requires existing stable TASK IDs')
        documents = snapshot_project_docs(self.root)
        expected_task_ref = {'path': task_relative, 'sha256': task_snapshot['sha256']}
        if documents.get('task_index') != expected_task_ref:
            raise PublicationError('TASK changed while freezing project documents')
        candidate.update(base_commit=base, file_task_refs=copy.deepcopy(file_task_refs),
                         task_path=task_relative, task_sha256=task_snapshot['sha256'],
                         project_documents=documents)
        self._plan_review(candidate)
        candidate['reviewed_plan'] = copy.deepcopy(self.plan)
        return self._save({'schema_version': 'publication/v1', 'scope': scope, 'candidate': candidate,
                           'phase': 'pending', 'tested': False, 'committed': False,
                           'pushed': False, 'remote_verified': False, 'evidence': [],
                           'commit': None, 'events': [], 'last_error': None})

    def _current(self, value):
        now = self._candidate()
        if (now['sha256'] != value['candidate']['sha256'] or
                _hash(_regular_bytes(resolve_task_file(self.root))) != value['candidate']['task_sha256']):
            raise PublicationError('candidate changed; freeze and independently test a new version')
        try:
            check_document_refs(self.root, value['candidate']['project_documents'])
        except (ValueError, KeyError) as exc:
            raise PublicationError('project documents changed; freeze and independently test a new version') from exc

    def _evidence(self, value):
        evidence = value['evidence']
        required = {r for refs in value['candidate']['file_task_refs'].values() for r in refs}
        covered = set()
        if not isinstance(evidence, list) or not evidence:
            raise PublicationError('independent acceptance evidence required')
        for item in evidence:
            if not isinstance(item, dict) or not isinstance(item.get('path'), str) or not Path(item['path']).is_absolute():
                raise PublicationError('evidence requires an absolute regular-file path')
            refs = item.get('task_refs')
            if (not isinstance(refs, list) or not refs or
                    any(not isinstance(r, str) or r not in required for r in refs)):
                raise PublicationError('evidence must reference changed TASK IDs')
            if (item.get('candidate_sha256') != value['candidate']['sha256'] or
                    _hash(_regular_bytes(item['path'])) != item.get('sha256')):
                raise PublicationError('stale or changed acceptance evidence')
            check_task_memory(self.root, item)
            covered.update(refs)
        if covered != required:
            raise PublicationError('acceptance omits changed TASK IDs')

    def _plan_review(self, candidate):
        from .plan_review import check_plan_review, protected_lineage
        refs = {r for values in candidate['file_task_refs'].values() for r in values}
        probe = {'tasks': [{'task_refs': sorted(refs)}]}
        plan = candidate.get('reviewed_plan', self.plan)
        try:
            if self.publication_task_refs is not None and refs != set(self.publication_task_refs):
                raise ValueError('actual changed-task coverage differs from trusted publication scope')
            protected = protected_lineage(probe, self.root)
            if protected is None and plan is None and not self.allow_legacy:
                raise ValueError('publication needs reviewed plan or explicit trusted legacy opt-in')
            if protected is not None or plan is not None:
                if plan is None or not refs <= {r for t in plan['tasks'] for r in t.get('task_refs', [])}:
                    raise ValueError('publication needs the exact reviewed plan covering changed requirements')
                check_plan_review(plan, self.root, self.plan_review_verifier, allow_legacy=self.allow_legacy,
                                  purpose='publication' if self.publication_task_refs is not None else 'execution',
                                  publication_task_refs=self.publication_task_refs)
        except (ValueError, OSError, KeyError) as exc:
            raise PublicationError('main plan review unavailable/stale: ' + str(exc)) from exc

    def _acceptance(self, value):
        self._plan_review(value['candidate'])
        self._evidence(value)
        evidence = value['evidence']
        if self.accept is None or self.accept(copy.deepcopy(value['candidate']), copy.deepcopy(evidence)) is not True:
            raise PublicationError('trusted independent acceptance failed or unavailable')
        self._evidence(value)
        self._plan_review(value['candidate'])

    def _event(self, value, action):
        value['events'].append({'action': action, 'observed_at': time.time()})
        return self._save(value)

    def mark_tested(self, evidence):
        value = self.status()
        self._scope(value['scope'], 'test')
        if value['phase'] != 'pending':
            raise PublicationError('testing requires a pending candidate')
        self._current(value)
        if _git(self.root, 'rev-parse', 'HEAD').decode().strip() != value['candidate']['base_commit']:
            raise PublicationError('candidate base changed before testing')
        value['evidence'] = copy.deepcopy(evidence)
        self._acceptance(value)
        self._current(value)  # callback is not allowed to alter the tested bytes
        value.update(phase='tested', tested=True)
        return self._event(value, 'tested')

    def _commit(self, value):
        head = _git(self.root, 'rev-parse', 'HEAD').decode().strip()
        parents = _git(self.root, 'show', '-s', '--format=%P', head).decode().strip().split()
        tree = self._tree(head)
        expected = {p: {'mode': v['mode'], 'oid': v['oid']} for p, v in value['candidate']['files'].items()}
        if parents != [value['candidate']['base_commit']] or tree != expected:
            raise PublicationError('commit must have the exact tested tree and original single parent')
        if value['commit'] is not None and value['commit'] != head:
            raise PublicationError('observed commit changed')
        return head

    def _gate(self, value, action):
        self._scope(value['scope'], action)
        if not value['tested']:
            raise PublicationError('candidate has not passed independent testing')
        self._current(value)
        self._acceptance(value)
        self._current(value)
        return self._commit(value)

    def observe_commit(self):
        value = self.status()
        head = self._gate(value, 'observe_commit')
        if value['phase'] not in ('tested', 'committed'):
            raise PublicationError('commit observation out of order')
        value.update(commit=head, committed=True, phase='committed')
        return self._event(value, 'committed')

    def _remote(self, value):
        if self.remote_reader is None:
            raise PublicationError('trusted remote readback unavailable; publication pending')
        result = self.remote_reader(copy.deepcopy(value['scope']))
        expected = dict(remote_url=value['scope']['remote_url'], branch=value['scope']['branch'],
                        commit=value['commit'])
        if not isinstance(result, dict) or any(result.get(k) != v for k, v in expected.items()):
            raise PublicationError('remote readback does not match authorized branch and tested commit')
        return {**expected, 'observed_at': time.time()}

    def observe_pushed(self):
        """Observe publication, never accept a push command's claimed success."""
        value = self.status()
        if value['phase'] != 'committed':
            raise PublicationError('push observation requires a verified local commit')
        self._gate(value, 'observe_pushed')
        value['push_readback'] = self._remote(value)
        self._gate(value, 'observe_pushed')
        value.update(pushed=True, phase='pushed', last_error=None)
        return self._event(value, 'pushed')

    def verify_remote(self):
        value = self.status()
        if value['phase'] not in ('pushed', 'remote_verified'):
            raise PublicationError('remote verification requires observed publication')
        self._gate(value, 'verify_remote')
        value['remote_readback'] = self._remote(value)
        self._gate(value, 'verify_remote')
        value.update(remote_verified=True, phase='remote_verified', last_error=None)
        return self._event(value, 'remote_verified')

    def record_push_failure(self, reason):
        value = self.status()
        self._scope(value['scope'], 'record_push_failure')
        if value['phase'] != 'committed' or not isinstance(reason, str) or not reason.strip():
            raise PublicationError('push failure requires committed state and a reason')
        value['last_error'] = reason
        return self._event(value, 'push_failed_pending')
