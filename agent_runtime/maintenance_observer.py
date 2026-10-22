"""Opt-in file/event observer for MaintenanceGate; a version is not validity."""
import hashlib
import json
import os
import stat
from pathlib import PurePosixPath

from .advice_poll import _root, _safe, observe_advice
from .maintenance_gate import _json_value


def read_bound(root, path, *, max_bytes=2 * 1024 * 1024):
    """Read one explicit project file. Never follow links or return partial data."""
    root = _root(root)
    if (not isinstance(path, str) or '\\' in path or ':' in path or
            any(p in ('', '.', '..') for p in path.split('/')) or
            PurePosixPath(path).is_absolute()):
        raise ValueError('explicit project-relative file required')
    if type(max_bytes) is not int or not 1 <= max_bytes <= 32 * 1024 * 1024:
        raise ValueError('invalid read budget')
    source = _safe(root, root / path)
    if not source.is_file():
        raise ValueError('required regular source is missing')
    # _safe also checks every parent for Windows junctions.
    fd = os.open(source, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0))
    try:
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            info = os.fstat(stream.fileno())
            if info.st_size > max_bytes:
                raise ValueError('source exceeds budget; no partial context')
            if not stat.S_ISREG(info.st_mode):
                raise ValueError('required source is not regular')
            if stream.seekable():
                # Probe the observed size plus a growth sentinel, not the ceiling.
                initial = min(info.st_size + 1, max_bytes + 1)
                data = stream.read(initial)
                if len(data) == initial and initial <= max_bytes:
                    del data
                    stream.seek(0)
                    data = stream.read(max_bytes + 1)
            else:
                data = stream.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise ValueError('source exceeds budget; no partial context')
        return data
    finally:
        os.close(fd)


def maintenance_observer(root, run_id, tracked_paths, external):
    """Bind human GUIDE, canonical TASK, all advice, and explicit host events.

    The host must additionally declare every relevant code/input/result/lease
    version and deadline in tracked_paths/external. Missing inputs fail closed.
    This does not discover complete dependencies or acknowledge handled work.
    """
    root = _root(root)
    if not isinstance(run_id, str) or not run_id.strip() or not callable(external):
        raise ValueError('run identity and trusted external observer required')
    if not isinstance(tracked_paths, (list, tuple)):
        raise ValueError('explicit tracked paths required')
    paths = ['agent_doc/guide/GUIDE.md', 'agent_doc/task/TASK.md', *tracked_paths]
    if len(paths) > 128 or any(not isinstance(p, str) for p in paths):
        raise ValueError('invalid file inventory')
    if len({p.casefold() for p in paths}) != len(paths):
        raise ValueError('duplicate or ambiguous tracked path')

    def snapshot():
        files = {p: hashlib.sha256(read_bound(root, p)).hexdigest() for p in paths}
        _, advice = observe_advice(root)
        events = external()
        if not isinstance(events, dict):
            raise ValueError('explicit external event map required')
        _json_value(events)
        encoded = json.dumps(events, sort_keys=True, allow_nan=False, separators=(',', ':'))
        if len(encoded) > 32768:
            raise ValueError('external event budget exceeded')
        return {'files': files,
                'advice_sha256': hashlib.sha256(json.dumps(advice, sort_keys=True).encode()).hexdigest(),
                'external': json.loads(encoded)}

    def observe():
        before = snapshot()
        if snapshot() != before:
            raise ValueError('observation changed while reading; retry')
        return {'project_root': str(root), 'run_id': run_id, 'events': before}

    return observe
