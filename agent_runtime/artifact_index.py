"""Unified artifact index: one bounded scan of a tree classified by role/status.

Absorbs npu_kernel_agent's "single view of what is missing vs changed" pattern.
Classification is deterministic and explicit: `required` is caller-supplied and
never inferred, and unknown files are reported as `other` rather than guessed
into a role. Every entry carries a SHA-256 so two indexes diff at the hash level
instead of re-reading changed files.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path, PurePosixPath
import re

from .project_docs import DocumentError, regular_digest, _relative

INDEX_SCHEMA = 'artifact-index/v1'

# Deterministic file-name -> (category, mutable) for the supervised run layout.
# mutable=True means the writer updates it in place across the run lifetime;
# mutable=False means it is produced once and then only read. Names not listed
# here fall through to suffix rules, then to `other` with no mutable claim.
_NAME_ROLES = {
    'launch.json': ('state', True),
    'live.json': ('state', True),
    'monitor.json': ('state', True),
    'progress.json': ('state', True),
    'source-snapshot.json': ('state', True),
    'guard-failure.json': ('state', True),
    'plan.json': ('source', False),
    'receipt.json': ('delivery', False),
    'final-report.json': ('delivery', False),
    'state.sqlite': ('state', True),
    'supervisor.log': ('log', True),
    'TASK.md': ('source', False),
}


def classify(relpath):
    """Deterministic (category, mutable) for a known run/document layout."""
    name = relpath.rsplit('/', 1)[-1]
    if name in _NAME_ROLES:
        return _NAME_ROLES[name]
    if name.endswith('.log'):
        return ('log', True)
    if name.endswith('.py'):
        return ('source', False)
    if name.endswith('.md'):
        return ('document', False)
    if '/results/' in '/' + relpath + '/':
        return ('result', False)
    return ('other', None)


def _walk(root, directory, max_entries, max_total_bytes=None):
    lexical = Path(os.path.abspath(root / directory)) if directory is not None else root
    if lexical != root and root not in lexical.parents:
        raise DocumentError('index directory must live under the project root')
    path = _relative(root, directory if directory is not None else '.')
    path = path.resolve()
    if not path.exists():
        raise DocumentError(f'index directory does not exist: {directory or "."}')
    if not path.is_dir():
        raise DocumentError(f'index directory must be a directory: {directory or "."}')
    if path != root and root not in path.parents:
        raise DocumentError('index directory must live under the project root')
    files, total = {}, 0
    for parent, directories, names in os.walk(path, followlinks=False):
        # Reject symlinked directories that would let the walk escape the root.
        for name in directories:
            entry = Path(parent) / name
            if entry.is_symlink():
                raise DocumentError(f'index must not traverse symlinked directory: {entry}')
        for name in names:
            item = Path(parent) / name
            if item.is_symlink():
                raise DocumentError(f'index must not traverse symlinked file: {item}')
            if len(files) >= max_entries:
                raise DocumentError(f'index exceeds {max_entries} file entries; narrow the directory')
            rel = item.relative_to(root).as_posix()
            category, mutable = classify(rel)
            digest, size = regular_digest(root, rel, max_bytes=None if max_total_bytes is None else max_total_bytes-total)
            total += size
            files[rel] = {'sha256': digest,
                          'size': size,
                          'category': category, 'mutable': mutable}
    return dict(sorted(files.items()))


def _canonical_path(value):
    if (type(value) is not str or not value or '\\' in value or ':' in value or
            '\x00' in value or PurePosixPath(value).is_absolute() or PurePosixPath(value).as_posix() != value or
            any(part in ('', '.', '..') for part in value.split('/'))):
        raise DocumentError('required path must be canonical and project-relative')
    return value


def build_artifact_index(root, *, directory=None, required=None, max_entries=10000, max_total_bytes=None):
    """Bounded digest of every regular file under `directory` (default: root).

    `required` is an explicit list of paths, or a mapping of path -> expected
    SHA-256, each relative to `directory` (or to `root` when `directory` is
    None). Every required path reports `present`/`missing` and, when an expected
    digest is given, `match`/`mismatch`; `path` carries the root-relative name.
    The index never invents required paths; it only checks those declared.
    """
    root = Path(root).resolve()
    if type(max_entries) is not int or not 1 <= max_entries <= 100000:
        raise DocumentError('invalid index entry bound')
    if max_total_bytes is not None and (type(max_total_bytes) is not int or not 0 <= max_total_bytes <= 1024**3):
        raise DocumentError('invalid total artifact byte budget')
    files = _walk(root, directory, max_entries, max_total_bytes)
    required_status = {}
    if required is not None:
        if isinstance(required, dict):
            if any(val is not None and (type(val) is not str or re.fullmatch('[0-9a-f]{64}', val) is None) for val in required.values()):
                raise DocumentError('required digest must be lowercase SHA256')
            expected = {_canonical_path(key): val for key, val in required.items()}
        elif isinstance(required, (list, tuple, set)):
            expected = {_canonical_path(item): None for item in required}
        else:
            raise DocumentError('required must be a list of paths or a path->sha256 mapping')
        prefix = (Path(directory).relative_to(root).as_posix() if Path(directory).is_absolute() else Path(directory).as_posix()) if directory is not None else ''
        if prefix == '.':
            prefix = ''
        for rel in sorted(expected):
            full_rel = f'{prefix}/{rel.lstrip("/")}' if prefix else rel.lstrip('/')
            if full_rel in files:
                entry = files[full_rel]
                status = {'path': full_rel, 'present': True}
                if expected[rel] is not None:
                    status['match'] = entry['sha256'] == expected[rel]
            else:
                status = {'path': full_rel, 'present': False}
            required_status[rel] = status
    return {'schema_version': INDEX_SCHEMA, 'root': str(root),
            'directory': (Path(directory).as_posix() if directory is not None else None),
            'files': files, 'required': required_status, 'count': len(files),
            'scope': 'symmetric hash-level artifact inventory; category/mutable are '
                     'deterministic layout labels, not a security or acceptance verdict'}


def diff_artifact_index(current, previous):
    """Symmetric added/removed/changed over two artifact indexes."""
    if not (isinstance(current, dict) and isinstance(previous, dict)
            and current.get('schema_version') == INDEX_SCHEMA
            and previous.get('schema_version') == INDEX_SCHEMA):
        raise DocumentError('artifact diff requires two artifact-index/v1 snapshots')
    if any(current.get(key) != previous.get(key) for key in ('root', 'directory')):
        raise DocumentError('artifact diff requires the same root and directory')
    current_files, previous_files = current.get('files', {}), previous.get('files', {})
    added = sorted(set(current_files) - set(previous_files))
    removed = sorted(set(previous_files) - set(current_files))
    changed = sorted(rel for rel in set(current_files) & set(previous_files)
                     if current_files[rel]['sha256'] != previous_files[rel]['sha256'])
    return {'schema_version': INDEX_SCHEMA, 'added': added, 'removed': removed,
            'changed': changed, 'any_changed': bool(added or removed or changed)}
