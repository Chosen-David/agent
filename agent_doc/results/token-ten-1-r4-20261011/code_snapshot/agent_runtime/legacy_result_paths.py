"""Read-only, exact registered historical result relocation; never a write router."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat

MARKER = 'agent_doc/legacy-result-paths.json'
LIMIT = 1024 * 1024


def _safe(root, relative):
    path = root / relative
    for candidate in (path, *path.parents):
        if candidate == root:
            break
        if candidate.is_symlink():
            raise ValueError('legacy result relocation must not contain symlinks')
    if not path.resolve().is_relative_to(root):
        raise ValueError('legacy result relocation outside project')
    return path


def _legacy_key(value):
    if not isinstance(value, str) or '\\' in value or ':' in value:
        return False
    path = PurePosixPath(value)
    return (not path.is_absolute() and len(path.parts) >= 3
            and path.parts[:2] == ('doc', 'results')
            and all(part not in ('.', '..', '') for part in path.parts)
            and path.as_posix() == value)


def legacy_read_binding(root, value):
    """Return (relative read path, original digest), or the unmodified input.

    Only an explicit marker in this project can relocate an exact old result
    filename. No task/guide fallback, ancestor search, command or destination
    supplied by metadata is accepted. A marker establishes no trusted acceptance.
    """
    if not isinstance(value, str) or not value.startswith('doc/results/'):
        return value, None
    if not _legacy_key(value):
        raise ValueError('invalid legacy result path')
    root = Path(root).resolve()
    marker = _safe(root, MARKER)
    if not marker.exists():
        return value, None
    fd = os.open(marker, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0))
    with os.fdopen(fd, 'rb') as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > LIMIT:
            raise ValueError('legacy relocation marker must be a bounded regular file')
        raw = stream.read(LIMIT + 1)
    if len(raw) > LIMIT:
        raise ValueError('legacy relocation marker exceeds bound')
    def unique_pairs(pairs):
        result = {}
        for key, item in pairs:
            if key in result:
                raise ValueError('duplicate legacy relocation key')
            result[key] = item
        return result
    record = json.loads(raw, object_pairs_hook=unique_pairs)
    if (not isinstance(record, dict) or set(record) != {'schema_version', 'files'}
            or record['schema_version'] != 'agent-doc-relocation/v1'
            or not isinstance(record['files'], dict) or len(record['files']) > 10000):
        raise ValueError('invalid legacy relocation schema')
    seen = set()
    for key, digest in record['files'].items():
        digests = [digest] if isinstance(digest, str) else digest
        if (not _legacy_key(key) or key.casefold() in seen or not isinstance(digests, list)
                or not 1 <= len(digests) <= 2 or any(not isinstance(item, str) or
                not re.fullmatch('[0-9a-f]{64}', item) for item in digests)
                or len(set(digests)) != len(digests)):
            raise ValueError('invalid or case-colliding legacy relocation entry')
        seen.add(key.casefold())
    if value not in record['files']:
        return value, None
    previous = _safe(root, value)
    destination = 'agent_doc/' + value[len('doc/'):]
    target = _safe(root, destination)
    if previous.exists():
        raise ValueError('legacy result relocation collision; reconcile original and moved paths')
    if target.exists() and not target.is_file():
        raise ValueError('relocated result must be a regular file')
    expected = record['files'][value]
    return destination, tuple(expected) if isinstance(expected, list) else expected


def relocated_digest_matches(digest, expected):
    return expected is None or digest in ((expected,) if isinstance(expected, str) else expected)


def check_relocated_digest(data, expected):
    if not relocated_digest_matches(hashlib.sha256(data).hexdigest(), expected):
        raise ValueError('relocated historical result bytes changed')
