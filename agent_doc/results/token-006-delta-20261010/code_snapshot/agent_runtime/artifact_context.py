"""Self-contained, lossless two-version observations; no disk 'already read' cache.

The old text is always included in this same payload. A linear single splice
may represent the new version, only when its complete JSON is smaller. This
neither selects relevant sections nor authenticates/accepts artifact contents.
"""
import hashlib
import json
from pathlib import Path

from .result_validation import LIMIT, _bound, _json, _need, _ref

SCHEMA = 'artifact-comparison/v1'


def _root(root):
    root = Path(root)
    _need(root.is_absolute() and root.is_dir(), 'existing absolute PROJECT_ROOT required')
    return root.resolve()


def _binding(ref):
    _ref(ref)
    _need(set(ref) == {'path', 'sha256'}, 'exact path/sha256 reference required')
    return dict(ref)


def _digest(text):
    _need(isinstance(text, str) and len(text) <= LIMIT, 'text exceeds character bound')
    data = text.encode('utf-8')
    _need(len(data) <= LIMIT, 'text exceeds byte bound')
    return hashlib.sha256(data).hexdigest()


def _json_text(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':'))


def _splice(before, after):
    start = 0
    limit = min(len(before), len(after))
    while start < limit and before[start] == after[start]:
        start += 1
    end = 0
    while end < limit-start and before[-end-1] == after[-end-1]:
        end += 1
    return {'base_sha256': _digest(before), 'start': start,
            'delete': len(before)-start-end,
            'insert': after[start:len(after)-end if end else len(after)]}


def compare_artifacts(root, before_ref, after_ref, *, full=False, max_chars=20000):
    """Read both SHA-bound regular UTF-8 files; return a complete comparison.

    Even a fresh/reset model receives the entire base here. No persisted hint
    can omit it. Unknown/unsafe refs, stale hashes and budget overflow refuse;
    none of the original text is truncated. The host treats both versions as
    data and applies existing current instructions and independent result gates.
    """
    root = _root(root)
    _need(type(full) is bool, 'full must be boolean')
    _need(type(max_chars) is int and 1 <= max_chars <= LIMIT, 'invalid character budget')
    before_ref = _binding(before_ref); after_ref = _binding(after_ref)
    before = _bound(root, before_ref).decode('utf-8')
    after = _bound(root, after_ref).decode('utf-8')
    target = {'ref': after_ref, 'representation': 'full', 'text': after}
    candidate = {'ref': after_ref, 'representation': 'splice', 'splice': _splice(before, after)}
    if not full and len(_json_text(candidate)) < len(_json_text(target)):
        target = candidate
    output = {'schema_version': SCHEMA, 'project_root': str(root),
              'position_unit': 'Unicode code points',
              'before': {'ref': before_ref, 'text': before}, 'after': target}
    _need(len(_json_text(output)) <= max_chars, 'comparison exceeds budget; never truncate either version')
    return output


def restore_comparison(root, payload, before_ref, after_ref):
    """Recover exact two texts against independently supplied host bindings.

    Restoration validates transport bytes; it is not current filesystem or
    scientific acceptance. A caller must re-read/revalidate before using data.
    """
    root = _root(root)
    if isinstance(payload, (str, bytes)):
        if isinstance(payload, bytes):
            _need(len(payload) <= 4*LIMIT, 'serialized comparison exceeds byte bound')
            payload = payload.decode('utf-8')
        _need(len(payload) <= LIMIT, 'serialized comparison exceeds character bound')
        payload = _json(payload)
    _need(isinstance(payload, dict) and set(payload) ==
          {'schema_version', 'project_root', 'position_unit', 'before', 'after'},
          'exact comparison fields required')
    _need(payload['schema_version'] == SCHEMA and payload['project_root'] == str(root) and
          payload['position_unit'] == 'Unicode code points', 'comparison version/project/unit mismatch')
    before_ref = _binding(before_ref); after_ref = _binding(after_ref)
    old = payload['before']; new = payload['after']
    _need(isinstance(old, dict) and set(old) == {'ref', 'text'} and old['ref'] == before_ref and
          isinstance(old['text'], str), 'base does not match host binding')
    before = old['text']
    _need(_digest(before) == before_ref['sha256'], 'base text changed')
    _need(isinstance(new, dict) and new.get('ref') == after_ref, 'target does not match host binding')
    if new.get('representation') == 'full':
        _need(set(new) == {'ref', 'representation', 'text'} and isinstance(new['text'], str), 'invalid full representation')
        after = new['text']
    else:
        _need(new.get('representation') == 'splice' and set(new) == {'ref', 'representation', 'splice'}, 'unknown representation')
        patch = new['splice']
        _need(isinstance(patch, dict) and set(patch) == {'base_sha256', 'start', 'delete', 'insert'}, 'invalid splice fields')
        start = patch['start']; delete = patch['delete']; inserted = patch['insert']
        _need(patch['base_sha256'] == before_ref['sha256'] and type(start) is int and type(delete) is int and
              0 <= start <= len(before) and 0 <= delete <= len(before)-start and isinstance(inserted, str), 'invalid splice/base/range')
        _need(len(inserted) <= LIMIT, 'splice insert exceeds character bound')
        _need(len(inserted.encode('utf-8')) <= LIMIT, 'splice insert exceeds byte bound')
        after = before[:start] + inserted + before[start+delete:]
    _need(_digest(after) == after_ref['sha256'], 'target text changed')
    return before, after
