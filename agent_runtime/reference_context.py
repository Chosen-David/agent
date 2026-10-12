"""Lossless directory-prefix transport; no reference existence or validity proof."""
import hashlib
import json
import os
import re
from .advice_poll import _root
from .maintenance_observer import read_bound
from .record_context import _pairs, _constant, _float

SCOPE = 'complete parsed values/order; path-prefix transport only; restore before existing freshness/result gates; no reference existence, validity or permission proof'


def _wire(value):
    try:
        text = json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':'))
        text.encode('utf-8')
        return text
    except (TypeError, UnicodeError, RecursionError) as exc:
        raise ValueError('bounded valid Unicode JSON required') from exc


def _json(text):
    try:
        value = json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant, parse_float=_float)
        _wire(value)
        return value
    except RecursionError as exc:
        raise ValueError('JSON nesting exceeds bounds') from exc


def _path(path):
    if (type(path) is not str or not path or '\\' in path or ':' in path or '\x00' in path or
            any(p in ('', '.', '..') for p in path.split('/'))):
        raise ValueError('normalized project-relative reference path required')
    return path


def _source(root, path, sha):
    if type(sha) is not str or re.fullmatch('[0-9a-f]{64}', sha) is None:
        raise ValueError('source SHA256 required')
    raw = read_bound(root, path, max_bytes=2 * 1024 * 1024)
    if hashlib.sha256(raw).hexdigest() != sha:
        raise ValueError('source changed; refresh transport')
    data = _json(raw.decode('utf-8'))
    if type(data) is not dict or type(data.get('references')) is not list or len(data['references']) > 50000:
        raise ValueError('bounded complete reference collection required')
    for ref in data['references']:
        if type(ref) is not dict or 'path' not in ref or 'sha256' not in ref:
            raise ValueError('complete path/SHA references required')
        _path(ref['path'])
        if type(ref['sha256']) is not str or re.fullmatch('[0-9a-f]{64}', ref['sha256']) is None:
            raise ValueError('reference SHA256 required')
    return data


def _budget(max_chars):
    if type(max_chars) is not int or not 1 <= max_chars <= 1000000:
        raise ValueError('invalid display budget')


def reference_view(root, path, expected_sha256, *, full=False, max_chars=20000):
    root = _root(root)
    _budget(max_chars)
    if type(full) is not bool:
        raise ValueError('explicit full flag required')
    data = _source(root, path, expected_sha256)
    value = {'schema_version': 'reference-view/v1', 'project_root': str(root),
             'source': {'path': path, 'sha256': expected_sha256}, 'scope': SCOPE,
             'encoding': 'full', 'data': data}
    refs = data['references']
    if not full and refs and all(set(ref) == {'path', 'sha256'} for ref in refs):
        common = os.path.commonprefix([ref['path'] for ref in refs])
        prefix = common[:common.rfind('/') + 1]
        if prefix:
            candidate = dict(value)
            candidate['data'] = dict(data)
            candidate['data']['references'] = [dict(ref) for ref in refs]
            candidate.update(encoding='directory-prefix', path_prefix=prefix)
            for ref in candidate['data']['references']:
                ref['path'] = ref['path'][len(prefix):]
            if len(_wire(candidate)) < len(_wire(value)):
                value = candidate
    if len(_wire(value)) > max_chars:
        raise ValueError('complete reference context exceeds budget; no truncation')
    return value


def restore_reference_view(root, text, path, expected_sha256, *, max_chars=1000000):
    """Reconstruct against a fresh exact source; does not authenticate artifacts."""
    root = _root(root)
    _budget(max_chars)
    if type(text) is not str or len(text) > max_chars:
        raise ValueError('bounded serialized reference view required')
    packet = _json(text)
    if type(packet) is not dict:
        raise ValueError('reference frame required')
    encoding = packet.get('encoding')
    keys = {'schema_version', 'project_root', 'source', 'scope', 'encoding', 'data'}
    if encoding == 'directory-prefix':
        keys.add('path_prefix')
    if encoding not in ('full', 'directory-prefix') or set(packet) != keys:
        raise ValueError('unknown or ambiguous reference encoding')
    if (packet['schema_version'] != 'reference-view/v1' or packet['project_root'] != str(root) or
            packet['source'] != {'path': path, 'sha256': expected_sha256} or packet['scope'] != SCOPE):
        raise ValueError('source/project/transport binding mismatch')
    original = _source(root, path, expected_sha256)
    restored = packet['data']
    if type(restored) is not dict or type(restored.get('references')) is not list:
        raise ValueError('complete reference data required')
    if encoding == 'directory-prefix':
        prefix = packet['path_prefix']
        if type(prefix) is not str or not prefix.endswith('/'):
            raise ValueError('directory boundary prefix required')
        _path(prefix[:-1])
        for ref in restored['references']:
            if type(ref) is not dict or set(ref) != {'path', 'sha256'}:
                raise ValueError('encoded reference shape required')
            _path(ref['path'])
            ref['path'] = _path(prefix + ref['path'])
    if _wire(restored) != _wire(original):
        raise ValueError('reconstructed ordered values disagree with exact source')
    return restored
