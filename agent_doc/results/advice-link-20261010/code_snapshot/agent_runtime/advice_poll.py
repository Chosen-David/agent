"""Bounded advice change navigation; never an assessment or permission cache."""
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat

SCHEMA = 'advice-inventory/v1'
PREFIX = 'agent_doc/advice/'
MAX_FILES = 2000
MAX_BYTES = 32 * 1024 * 1024
MAX_DIRS = 2000


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')


def _root(value):
    root = Path(value)
    if not root.is_absolute() or not root.is_dir():
        raise ValueError('absolute existing PROJECT_ROOT required')
    return root.resolve(strict=True)


def _path(value):
    if not isinstance(value, str) or not value.startswith(PREFIX):
        raise ValueError('inventory path must be under agent_doc/advice/')
    parts = PurePosixPath(value).parts
    if ('\\' in value or ':' in value or '\x00' in value or
            any(p in ('.', '..') for p in value.split('/')) or
            any(not p for p in value.split('/')) or len(parts) < 3):
        raise ValueError('invalid advice path')
    return value


def _safe(root, path):
    absolute = Path(os.path.abspath(path))
    if not absolute.is_relative_to(root):
        raise ValueError('path outside project')
    for item in (absolute, *absolute.parents):
        if item == root:
            break
        if item.is_symlink() or (hasattr(item, 'is_junction') and item.is_junction()):
            raise ValueError('links and junctions are not supported')
    if absolute.resolve() != absolute:
        raise ValueError('resolved path differs')
    return absolute


def validate_snapshot(root, value):
    root = _root(root)
    if (not isinstance(value, dict) or set(value) != {'schema_version', 'project_root', 'files'} or
            value['schema_version'] != SCHEMA or value['project_root'] != root.as_posix() or
            not isinstance(value['files'], dict) or len(value['files']) > MAX_FILES):
        raise ValueError('invalid or foreign advice inventory')
    seen = set()
    for path, sha in value['files'].items():
        _path(path)
        if (path.casefold() in seen or not isinstance(sha, str) or
                re.fullmatch('[0-9a-f]{64}', sha) is None):
            raise ValueError('ambiguous path or invalid source SHA256')
        seen.add(path.casefold())
    return value


def _scan(root, max_files, max_bytes, max_dirs):
    directory = _safe(root, root / 'agent_doc/advice')
    files = {}
    used = 0
    if directory.exists():
        if not directory.is_dir():
            raise ValueError('advice must be a directory')
        pending = [directory]
        directory_count = 1
        while pending:
            with os.scandir(pending.pop()) as entries:
                for entry in entries:
                    path = _safe(root, Path(entry.path))
                    if entry.is_dir(follow_symlinks=False):
                        directory_count += 1
                        if directory_count > max_dirs:
                            raise ValueError('advice directory bound exceeded; no partial snapshot')
                        pending.append(path)
                        continue
                    rel = _path(path.relative_to(root).as_posix())
                    if len(files) >= max_files:
                        raise ValueError('advice file bound exceeded; no partial snapshot')
                    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) |
                                 getattr(os, 'O_NONBLOCK', 0))
                    digest = hashlib.sha256()
                    with os.fdopen(fd, 'rb') as stream:
                        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                            raise ValueError('advice must contain only regular files')
                        while chunk := stream.read(min(65536, max_bytes - used + 1)):
                            used += len(chunk)
                            if used > max_bytes:
                                raise ValueError('advice byte bound exceeded; no partial snapshot')
                            digest.update(chunk)
                    files[rel] = digest.hexdigest()
    value = {'schema_version': SCHEMA, 'project_root': root.as_posix(), 'files': dict(sorted(files.items()))}
    return validate_snapshot(root, value)


def observe_advice(root, baseline=None, *, max_files=MAX_FILES, max_bytes=MAX_BYTES, max_dirs=MAX_DIRS):
    """Return (navigation, current inventory). No source writes or auto ACK."""
    root = _root(root)
    if (type(max_files) is not int or not 1 <= max_files <= MAX_FILES or
            type(max_bytes) is not int or not 1 <= max_bytes <= MAX_BYTES or
            type(max_dirs) is not int or not 1 <= max_dirs <= MAX_DIRS):
        raise ValueError('invalid bounded scan budget')
    if baseline is not None:
        validate_snapshot(root, baseline)
    current = _scan(root, max_files, max_bytes, max_dirs)
    if current != _scan(root, max_files, max_bytes, max_dirs):
        raise ValueError('advice changed during observation; retry with a new observation')
    before = baseline['files'] if baseline is not None else {}
    after = current['files']
    removed = {p: before[p] for p in before.keys() - after.keys()}
    added = {p: after[p] for p in after.keys() - before.keys()}
    old_hashes, new_hashes = defaultdict(list), defaultdict(list)
    for path, sha in removed.items(): old_hashes[sha].append(path)
    for path, sha in added.items(): new_hashes[sha].append(path)
    events = []
    # This is content equivalence, not proof of a Git rename or author/run identity.
    for sha in sorted(old_hashes.keys() & new_hashes.keys()):
        if len(old_hashes[sha]) == len(new_hashes[sha]) == 1:
            old, new = old_hashes[sha][0], new_hashes[sha][0]
            events.append({'kind': 'content_relocated', 'before': {'path': old, 'sha256': sha},
                           'after': {'path': new, 'sha256': sha}})
            del removed[old]; del added[new]
    for path in sorted(before.keys() & after.keys()):
        if before[path] != after[path]:
            events.append({'kind': 'modified', 'before': {'path': path, 'sha256': before[path]},
                           'after': {'path': path, 'sha256': after[path]}})
    events.extend({'kind': 'removed', 'before': {'path': p, 'sha256': s}} for p, s in sorted(removed.items()))
    events.extend({'kind': 'added', 'after': {'path': p, 'sha256': s}} for p, s in sorted(added.items()))
    navigation = {'schema_version': 'advice-changes/v1', 'project_root': root.as_posix(),
                  'initial_observation': baseline is None, 'changed': bool(events),
                  'baseline_sha256': hashlib.sha256(encode(baseline)).hexdigest() if baseline is not None else None,
                  'inventory_sha256': hashlib.sha256(encode(current)).hexdigest(),
                  'file_count': len(after), 'events': events,
                  'scope': 'advice byte/path changes only; no assessment, closure, authorization, source-context retention or scheduler decision'}
    return navigation, current
