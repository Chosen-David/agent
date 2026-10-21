"""Explicit exact-version NDJSON records; selection never proves completeness."""
import hashlib
import json
import math
import re
from .advice_poll import _root
from .maintenance_observer import read_bound

MAX_JSON_DEPTH = 256


def _bounded_depth(value):
    """Reject adversarial nesting without recursing over the decoded value."""
    pending = [(value, 0)]
    while pending:
        item, depth = pending.pop()
        if depth > MAX_JSON_DEPTH:
            raise ValueError('JSON nesting exceeds bounds')
        if type(item) is dict:
            pending.extend((child, depth + 1) for child in item.values()
                           if type(child) in (dict, list))
        elif type(item) is list:
            pending.extend((child, depth + 1) for child in item
                           if type(child) in (dict, list))
    return value


def _indices(value):
    if (not isinstance(value, (list, tuple)) or not 1 <= len(value) <= 128 or
            any(type(n) is not int or n < 1 for n in value) or len(set(value)) != len(value)):
        raise ValueError('distinct positive physical record lines required')
    return list(value)


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key')
        result[key] = value
    return result


def _constant(value):
    raise ValueError('non-finite JSON number')


def _float(value):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError('non-finite JSON number')
    return number


def record_view(root, path, expected_sha256, *, lines, global_lines, max_chars=20000):
    """Host enumerates all required records, including mandatory global rules."""
    root = _root(root)
    lines = _indices(lines)
    globals_ = _indices(global_lines)
    if type(expected_sha256) is not str or re.fullmatch('[0-9a-f]{64}', expected_sha256) is None:
        raise ValueError('source SHA256 required')
    if type(max_chars) is not int or not 1 <= max_chars <= 1000000:
        raise ValueError('invalid display budget')
    data = read_bound(root, path, max_bytes=2 * 1024 * 1024)
    if hashlib.sha256(data).hexdigest() != expected_sha256:
        raise ValueError('source changed; refresh selection')
    text = data.decode('utf-8')
    parts = text.split('\n')
    if parts[-1] == '':
        parts.pop()
    if not 1 <= len(parts) <= 50000:
        raise ValueError('record count exceeds bounds')
    records = []
    for i, part in enumerate(parts):
        # LF is the physical delimiter. Valid Unicode separators inside JSON
        # strings must not invent records; preserve original CRLF and EOF.
        raw = part + ('\n' if i < len(parts) - 1 or text.endswith('\n') else '')
        try:
            parsed = json.loads(raw, object_pairs_hook=_pairs, parse_constant=_constant,
                                parse_float=_float)
            _bounded_depth(parsed)
        except (ValueError, RecursionError) as exc:
            raise ValueError(f'invalid JSON record at physical line {i + 1}') from exc
        records.append(raw)
    keep = sorted(set(lines) | set(globals_))
    if keep[-1] > len(records):
        raise ValueError('selected line outside source')
    result = {
        'schema_version': 'record-view/v1', 'project_root': str(root),
        'source': {'path': path, 'sha256': expected_sha256},
        'selection': {'lines': lines, 'global_lines': globals_},
        'total_records': len(records), 'omitted_records': len(records) - len(keep),
        'records': [{'line': n, 'text': records[n - 1]} for n in keep],
        'scope': 'partial display; host must enumerate every required global/current/dependency record or read full exact source; no closure, validity or absence inference',
    }
    if len(json.dumps(result, ensure_ascii=False, allow_nan=False)) > max_chars:
        raise ValueError('selected records exceed budget; no silent truncation')
    return result
