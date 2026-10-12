"""Exact nonzero integer-grid transport; no scientific validity or authority."""
import hashlib
import re
from .advice_poll import _root
from .maintenance_observer import read_bound
from .reference_context import _json, _wire, _budget

MAX_VALUE = 2 ** 63 - 1
MAX_COUNT = 50000
SCOPE = 'complete parsed coordinate values/types/order and metadata; restore exact current source before existing scientific/result gates; no validity or permission proof'


def _integer(value):
    return type(value) is int and abs(value) <= MAX_VALUE


def _source(root, path, sha):
    if type(sha) is not str or re.fullmatch('[0-9a-f]{64}', sha) is None:
        raise ValueError('source SHA256 required')
    raw = read_bound(root, path, max_bytes=2 * 1024 * 1024)
    if hashlib.sha256(raw).hexdigest() != sha:
        raise ValueError('source changed; refresh transport')
    data = _json(raw.decode('utf-8'))
    if type(data) is not dict or type(data.get('coordinates')) is not list or len(data['coordinates']) > MAX_COUNT:
        raise ValueError('bounded complete coordinate collection required')
    return data


def grid_view(root, path, expected_sha256, *, full=False, max_chars=20000):
    root = _root(root)
    _budget(max_chars)
    if type(full) is not bool:
        raise ValueError('explicit full flag required')
    data = _source(root, path, expected_sha256)
    value = {'schema_version': 'grid-view/v1', 'project_root': str(root),
             'source': {'path': path, 'sha256': expected_sha256}, 'scope': SCOPE,
             'encoding': 'full', 'data': data}
    coords = data['coordinates']
    if not full and len(coords) >= 3 and all(_integer(x) for x in coords):
        start = coords[0]; step = coords[1] - start
        if step and _integer(step) and all(x == start + i * step for i, x in enumerate(coords)):
            candidate = dict(value)
            candidate['data'] = dict(data)
            candidate['data']['coordinates'] = {'start': start, 'step': step, 'count': len(coords)}
            candidate['encoding'] = 'arithmetic'
            if len(_wire(candidate)) < len(_wire(value)):
                value = candidate
    if len(_wire(value)) > max_chars:
        raise ValueError('complete grid context exceeds budget; no truncation')
    return value


def restore_grid_view(root, text, path, expected_sha256, *, max_chars=1000000):
    """Recover complete ordered values against the fresh host-bound source."""
    root = _root(root)
    _budget(max_chars)
    if type(text) is not str or len(text) > max_chars:
        raise ValueError('bounded serialized grid view required')
    packet = _json(text)
    keys = {'schema_version', 'project_root', 'source', 'scope', 'encoding', 'data'}
    if type(packet) is not dict or set(packet) != keys or packet['encoding'] not in ('full', 'arithmetic'):
        raise ValueError('unknown or ambiguous grid encoding')
    if (packet['schema_version'] != 'grid-view/v1' or packet['project_root'] != str(root) or
            packet['source'] != {'path': path, 'sha256': expected_sha256} or packet['scope'] != SCOPE):
        raise ValueError('source/project/transport binding mismatch')
    original = _source(root, path, expected_sha256)
    original_wire = _wire(original)
    if len(original_wire) > max_chars:
        raise ValueError('restored complete grid exceeds budget; no truncation')
    restored = packet['data']
    if type(restored) is not dict or 'coordinates' not in restored:
        raise ValueError('complete grid data required')
    if packet['encoding'] == 'arithmetic':
        grid = restored['coordinates']
        if type(grid) is not dict or set(grid) != {'start', 'step', 'count'}:
            raise ValueError('exact arithmetic fields required')
        start, step, count = grid['start'], grid['step'], grid['count']
        if (not _integer(start) or not _integer(step) or not step or
                type(count) is not int or not 3 <= count <= MAX_COUNT):
            raise ValueError('bounded nonzero integer progression required')
        # Bound expansion BEFORE allocating, including the final endpoint.
        if count != len(original['coordinates']) or not _integer(start + (count - 1) * step):
            raise ValueError('progression size or endpoint exceeds source bounds')
        restored['coordinates'] = [start + i * step for i in range(count)]
    elif type(restored['coordinates']) is not list:
        raise ValueError('complete full coordinate list required')
    if _wire(restored) != original_wire:
        raise ValueError('reconstructed ordered values disagree with exact source')
    return restored
