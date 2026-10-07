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
import stat
import subprocess
import time

from .project_memory import check_task_memory
from .task_manifest import atomic_json, requirements
from .project_docs import (assert_ai_writable, check_document_refs, resolve_task_file,
                           snapshot_project_docs)


class PublicationError(ValueError):
    """Publication remains pending until this gate is resolved."""


def _hash(value):
    return hashlib.sha256(value).hexdigest()


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()


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

    def __init__(self, root, state_path, *, authorize=None, accept=None, remote_reader=None):
        self.root = Path(root).resolve()
        self.path = Path(os.path.abspath(state_path))
        self.authorize, self.accept, self.remote_reader = authorize, accept, remote_reader
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
        value = json.loads(_regular_bytes(self.path))
        if value.get('schema_version') != 'publication/v1' or value['scope']['repository'] != str(self.root):
            raise PublicationError('state repository or schema mismatch')
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
        ids = {item['id'] for item in requirements(task_file)}
        if not changed or not isinstance(file_task_refs, dict) or set(file_task_refs) != set(changed):
            raise PublicationError('every changed file needs exact TASK ownership; no omitted or extra paths')
        for refs in file_task_refs.values():
            if (not isinstance(refs, list) or not refs or any(not isinstance(r, str) or r not in ids for r in refs)
                    or len(set(refs)) != len(refs)):
                raise PublicationError('file ownership requires existing stable TASK IDs')
        candidate.update(base_commit=base, file_task_refs=copy.deepcopy(file_task_refs),
                         task_path=task_relative, task_sha256=_hash(_regular_bytes(task_file)),
                         project_documents=snapshot_project_docs(self.root))
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

    def _acceptance(self, value):
        self._evidence(value)
        evidence = value['evidence']
        if self.accept is None or self.accept(copy.deepcopy(value['candidate']), copy.deepcopy(evidence)) is not True:
            raise PublicationError('trusted independent acceptance failed or unavailable')
        self._evidence(value)

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
