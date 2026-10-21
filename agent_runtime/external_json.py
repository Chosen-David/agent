"""Bounded, nonblocking snapshots for explicitly supplied JSON files."""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import stat


DEFAULT_JSON_LIMIT = 16 * 1024 * 1024
MAX_JSON_DEPTH = 256


class ExternalJSONError(ValueError):
    """The supplied file is not one complete, finite JSON snapshot."""


def regular_bytes(path, *, max_bytes=DEFAULT_JSON_LIMIT):
    """Read one regular file descriptor once; never follow its final symlink."""
    if type(max_bytes) is not int or max_bytes < 1:
        raise ExternalJSONError('positive external JSON byte bound required')
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
    try:
        fd = os.open(Path(path), flags)
    except OSError as exc:
        raise ExternalJSONError('external JSON input is unavailable or not a regular file') from exc
    try:
        try:
            with os.fdopen(fd, 'rb', closefd=False) as stream:
                info = os.fstat(stream.fileno())
                if not stat.S_ISREG(info.st_mode):
                    raise ExternalJSONError('external JSON input must be a regular file')
                if info.st_size > max_bytes:
                    raise ExternalJSONError(f'external JSON input exceeds {max_bytes} byte bound')
                # Avoid allocating the whole configured ceiling for a tiny stable
                # file. One extra byte detects growth from the fstat snapshot.
                initial = min(info.st_size + 1, max_bytes + 1)
                data = stream.read(initial)
                if len(data) == initial and initial <= max_bytes:
                    del data
                    stream.seek(0)
                    data = stream.read(max_bytes + 1)
        except OSError as exc:
            raise ExternalJSONError(
                'external JSON input is unavailable or not a regular file') from exc
    finally:
        os.close(fd)
    if len(data) > max_bytes:
        raise ExternalJSONError(f'external JSON input exceeds {max_bytes} byte bound')
    return data


def strict_json(data):
    """Decode UTF-8 JSON while rejecting duplicate keys and every nonfinite number."""
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError as exc:
        raise ExternalJSONError('external JSON input must contain valid UTF-8') from exc

    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise ExternalJSONError('duplicate JSON key: ' + key)
            value[key] = item
        return value

    def constant(value):
        raise ExternalJSONError('non-finite JSON number: ' + value)

    def finite_float(value):
        parsed = float(value)
        if not math.isfinite(parsed):
            raise ExternalJSONError('non-finite JSON number: ' + value)
        return parsed

    try:
        value = json.loads(text, object_pairs_hook=pairs, parse_constant=constant,
                           parse_float=finite_float)
    except ExternalJSONError:
        raise
    except (json.JSONDecodeError, ValueError) as exc:
        raise ExternalJSONError('external JSON input is malformed') from exc
    except RecursionError as exc:
        raise ExternalJSONError('external JSON nesting exceeds parser bounds') from exc
    stack = [(value, 0)]
    while stack:
        item, depth = stack.pop()
        if depth > MAX_JSON_DEPTH:
            raise ExternalJSONError(f'external JSON nesting exceeds {MAX_JSON_DEPTH} levels')
        if isinstance(item, dict):
            stack.extend((child, depth + 1) for child in item.values()
                         if isinstance(child, (dict, list)))
        elif isinstance(item, list):
            stack.extend((child, depth + 1) for child in item
                         if isinstance(child, (dict, list)))
    return value


def load_json(path, *, max_bytes=DEFAULT_JSON_LIMIT, expected_sha256=None):
    """Return the value parsed from the exact bytes whose optional digest was checked."""
    data = regular_bytes(path, max_bytes=max_bytes)
    if expected_sha256 is not None and hashlib.sha256(data).hexdigest() != expected_sha256:
        raise ExternalJSONError('sha256 mismatch: JSON snapshot')
    return strict_json(data)
