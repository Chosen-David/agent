"""Self-contained, lossless two-version observations; no disk 'already read' cache.

The old text is always included in this same payload. A linear single splice
may represent the new version, only when its complete JSON is smaller. This
neither selects relevant sections nor authenticates/accepts artifact contents.
"""
import hashlib
import json
from difflib import SequenceMatcher
from pathlib import Path

from .result_validation import LIMIT, _bound, _json, _need, _ref

SCHEMA = 'artifact-comparison/v2'


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
    before_text = before
    before = before.splitlines(keepends=True)
    after = after.splitlines(keepends=True)
    start = 0
    limit = min(len(before), len(after))
    while start < limit and before[start] == after[start]:
        start += 1
    end = 0
    while end < limit-start and before[-end-1] == after[-end-1]:
        end += 1
    return {'base_sha256': _digest(before_text), 'start': start,
            'delete': len(before)-start-end,
            'insert': ''.join(after[start:len(after)-end if end else len(after)])}


def _edits(before, after):
    # Bound quadratic matching; bigger files retain the existing linear mode.
    if max(len(before), len(after)) > 65536:
        return None
    old = before.splitlines(keepends=True); new = after.splitlines(keepends=True)
    if max(len(old), len(new)) > 2048:
        return None
    edits = [{'start': a, 'delete': b-a, 'insert': ''.join(new[c:d])}
             for tag,a,b,c,d in SequenceMatcher(None,old,new,autojunk=False).get_opcodes()
             if tag != 'equal']
    if not 1 <= len(edits) <= 64:
        return None
    return {'base_sha256': _digest(before), 'edits': edits}


def _unique_single_splice(before, after, patch):
    """True when byte selection cannot benefit from multi-edit matching.

    A single inserted/deleted line that occurs nowhere in the opposite text
    cannot be reused as a match. Its one-edit representation contains the same
    payload as the already-built splice plus extra schema overhead. Arbitrary
    token counters still receive every codec, so this only guards byte mode.
    """
    old = before.splitlines(keepends=True)
    new = after.splitlines(keepends=True)
    start = patch['start']
    deleted = old[start:start+patch['delete']]
    inserted = patch['insert'].splitlines(keepends=True)
    if not (deleted or inserted) or max(len(deleted), len(inserted)) > 1:
        return False
    return (all(line not in new for line in deleted) and
            all(line not in old for line in inserted))


def compare_artifacts(root, before_ref, after_ref, *, full=False, max_chars=20000,
                      reuse_identical=False, multi_edit=False, token_counter=None):
    """Read both SHA-bound regular UTF-8 files; return a complete comparison.

    Even a fresh/reset model receives the entire base here. No persisted hint
    can omit it. Unknown/unsafe refs, stale hashes and budget overflow refuse;
    none of the original text is truncated. The host treats both versions as
    data and applies existing current instructions and independent result gates.
    """
    root = _root(root)
    _need(type(full) is bool, 'full must be boolean')
    _need(type(reuse_identical) is bool, 'reuse_identical must be boolean')
    _need(type(multi_edit) is bool, 'multi_edit must be boolean')
    _need(token_counter is None or callable(token_counter), 'token_counter must be callable')
    _need(type(max_chars) is int and 1 <= max_chars <= LIMIT, 'invalid character budget')
    before_ref = _binding(before_ref); after_ref = _binding(after_ref)
    before = _bound(root, before_ref).decode('utf-8')
    after = _bound(root, after_ref).decode('utf-8')
    target = {'ref': after_ref, 'representation': 'full', 'text': after}
    candidates = [target]
    splice = _splice(before, after)
    candidate = {'ref': after_ref, 'representation': 'splice', 'splice': splice}
    if not full:
        candidates.append(candidate)
    if not full and len(_json_text(candidate)) < len(_json_text(target)):
        target = candidate
    # Equal texts cannot produce edits. Avoid quadratic matching on repeated
    # lines; both sources have already been read and SHA-checked above.
    skip_byte_only_edits = (not full and multi_edit and before != after and
                            token_counter is None and
                            _unique_single_splice(before, after, splice))
    if not full and multi_edit and before != after and not skip_byte_only_edits:
        patch = _edits(before, after)
        if patch:
            candidate = {'ref': after_ref, 'representation': 'edits', 'patch': patch}
            candidates.append(candidate)
            if len(_json_text(candidate)) < len(_json_text(target)):
                target = candidate
    # The complete base is present in this same packet; no history/cache hint.
    if not full and reuse_identical and before == after:
        candidate = {'ref': after_ref, 'representation': 'identical'}
        candidates.append(candidate)
        if len(_json_text(candidate)) < len(_json_text(target)):
            target = candidate
    output = {'schema_version': SCHEMA, 'project_root': str(root),
              'position_unit': 'lines with terminators',
              'before': {'ref': before_ref, 'text': before}, 'after': target}
    if token_counter is not None and not full:
        best = None
        # Stable ties: full, splice, eligible edits, eligible identical. Count
        # the entire final wire packet; a longer target may tokenize cheaper.
        for candidate in candidates:
            packet = {**output, 'after': candidate}
            wire = _json_text(packet)
            if len(wire) > max_chars:
                continue
            count = token_counter(wire)
            _need(type(count) is int and count >= 0, 'token_counter must return a nonnegative integer')
            if best is None or count < best[0]:
                best = (count, packet)
        _need(best is not None, 'comparison exceeds budget; never truncate either version')
        output = best[1]
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
          payload['position_unit'] == 'lines with terminators', 'comparison version/project/unit mismatch')
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
    elif new.get('representation') == 'identical':
        _need(set(new) == {'ref', 'representation'}, 'invalid identical representation')
        _need(before_ref['sha256'] == after_ref['sha256'], 'identical hash mismatch')
        after = before
    elif new.get('representation') == 'edits':
        _need(set(new) == {'ref', 'representation', 'patch'}, 'invalid multi-edit representation')
        patch = new['patch']
        _need(isinstance(patch,dict) and set(patch) == {'base_sha256','edits'} and
              patch['base_sha256'] == before_ref['sha256'], 'invalid multi-edit base/fields')
        edits = patch['edits']
        _need(isinstance(edits,list) and 1 <= len(edits) <= 64, 'invalid multi-edit count')
        lines = before.splitlines(keepends=True); pieces = []; end = 0; previous = -1
        chars = 0; byte_count = 0
        def append_piece(text):
            nonlocal chars,byte_count
            _need(len(text) <= LIMIT-chars, 'reconstructed character budget exceeded')
            size = len(text.encode('utf-8'))
            _need(size <= LIMIT-byte_count, 'reconstructed byte budget exceeded')
            chars += len(text);byte_count += size;pieces.append(text)
        for edit in edits:
            _need(isinstance(edit,dict) and set(edit) == {'start','delete','insert'}, 'invalid edit fields')
            start,delete,insert = edit['start'],edit['delete'],edit['insert']
            _need(type(start) is int and type(delete) is int and isinstance(insert,str) and
                  end <= start <= len(lines) and previous < start and
                  0 <= delete <= len(lines)-start, 'invalid or overlapping edit')
            _need(len(insert) <= LIMIT, 'edit insert exceeds character bound')
            append_piece(''.join(lines[end:start]));append_piece(insert)
            end=start+delete;previous=start
        append_piece(''.join(lines[end:]));after=''.join(pieces)
    else:
        _need(new.get('representation') == 'splice' and set(new) == {'ref', 'representation', 'splice'}, 'unknown representation')
        patch = new['splice']
        _need(isinstance(patch, dict) and set(patch) == {'base_sha256', 'start', 'delete', 'insert'}, 'invalid splice fields')
        start = patch['start']; delete = patch['delete']; inserted = patch['insert']
        lines = before.splitlines(keepends=True)
        _need(patch['base_sha256'] == before_ref['sha256'] and type(start) is int and type(delete) is int and
              0 <= start <= len(lines) and 0 <= delete <= len(lines)-start and isinstance(inserted, str), 'invalid splice/base/range')
        _need(len(inserted) <= LIMIT, 'splice insert exceeds character bound')
        _need(len(inserted.encode('utf-8')) <= LIMIT, 'splice insert exceeds byte bound')
        after = ''.join(lines[:start]) + inserted + ''.join(lines[start+delete:])
    _need(_digest(after) == after_ref['sha256'], 'target text changed')
    return before, after
