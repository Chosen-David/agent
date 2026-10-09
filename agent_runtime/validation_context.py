"""Recoverable display receipts; never grant or cache result acceptance."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re

from .result_validation import LIMIT, _bytes, _json, _need, _path, _ref
from .project_docs import assert_ai_writable, guard_write_path

DETAIL_FIELDS = ('artifact_hashes', 'review_evidence')
RESULT_FIELDS = {'status', 'scope', 'errors', 'next_action', 'proof'}


def _shape(result):
    _need(isinstance(result, dict) and set(result) == RESULT_FIELDS,
          'exact inspection result required; unknown fields cannot be hidden')
    _need(result['status'] in ('pending', 'invalid', 'usable-with-scope'), 'unknown inspection status')
    _need(result['scope'] is None or isinstance(result['scope'], str), 'invalid inspection scope')
    _need(isinstance(result['errors'], list) and all(isinstance(e, str) for e in result['errors']),
          'inspection errors must remain complete')
    _need(isinstance(result['next_action'], str), 'inspection action required')
    _need(result['proof'] is None or isinstance(result['proof'], dict), 'invalid inspection proof')
    if result['proof'] is not None:
        for key in DETAIL_FIELDS:
            if key in result['proof']:
                _need(isinstance(result['proof'][key], dict), 'invalid proof detail map: ' + key)


def _directory(root, relative):
    root = Path(root)
    _need(root.is_absolute() and root.is_dir(), 'existing absolute PROJECT_ROOT required')
    root = root.resolve()
    _need(isinstance(relative, str) and bool(relative), 'host-selected context directory required')
    raw = Path(relative)
    _need(not raw.is_absolute() and len(raw.parts) >= 3 and
          raw.parts[:2] == ('agent_doc', 'results') and
          all(re.fullmatch(r'[A-Za-z0-9_-][A-Za-z0-9_.-]*', part) and part not in ('.', '..')
              for part in raw.parts), 'context directory must stay under project agent_doc/results/<run_id>')
    return root, _path(root, relative)


def write_validation_context(root, result, relative_directory):
    """Persist complete observed JSON and return only a display projection.

    Host must invoke the normal live result gate first. This function does not
    authenticate its argument, authorize reuse, truncate failures, or infer that
    omitted details are irrelevant to a later task. Restore them when needed.
    """
    _shape(result)
    supplied_root = Path(root)
    root, directory = _directory(root, relative_directory)
    record = {'schema_version': 'validation-context-record/v1', 'project_root': str(root), 'result': result}
    data = (json.dumps(record, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')
    _need(len(data) <= LIMIT, 'complete inspection exceeds storage bound; never truncate')
    digest = hashlib.sha256(data).hexdigest()
    relative = (Path(relative_directory) / ('validation-' + digest + '.json')).as_posix()
    assert_ai_writable(supplied_root, relative_directory)
    guard_write_path(supplied_root / relative_directory)
    directory.mkdir(parents=True, exist_ok=True)
    target = _path(root, relative)
    assert_ai_writable(supplied_root, relative)
    guard_write_path(supplied_root / relative)
    try:
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    except FileExistsError:
        _need(_bytes(root, relative) == data, 'existing context record changed; preserve and repair')
    else:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    display = deepcopy(result)
    hidden = {}
    if display['proof'] is not None:
        for field in DETAIL_FIELDS:
            if field in display['proof']:
                hidden[field] = len(display['proof'].pop(field))
    return {'schema_version': 'validation-context/v1', 'project_root': str(root),
            **display, 'detail_counts': hidden, 'record_ref': {'path': relative, 'sha256': digest},
            'trust': 'Display only. Restore hidden details when needed; obtain current trusted independent validation before consumption.'}


def restore_validation_context(root, record_ref):
    """Recover full observed values with hash/project/path checks, not authority."""
    _ref(record_ref)
    raw = Path(record_ref['path'])
    root, _ = _directory(root, raw.parent.as_posix())
    _need(raw.name == 'validation-' + record_ref['sha256'] + '.json', 'context filename/hash mismatch')
    data = _bytes(root, record_ref['path'])
    _need(hashlib.sha256(data).hexdigest() == record_ref['sha256'], 'stale context record')
    record = _json(data)
    _need(isinstance(record, dict) and set(record) == {'schema_version', 'project_root', 'result'} and
          record['schema_version'] == 'validation-context-record/v1' and record['project_root'] == str(root),
          'context record belongs to another project or unsupported schema')
    result = record['result']
    _shape(result)
    return result
