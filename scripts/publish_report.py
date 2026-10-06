#!/usr/bin/env python3
"""Publish immutable run reports and an atomically replaced, verified latest pointer.

This records existing results; it never executes experiments or certifies claims.
Linux/Unix flock serializes cooperating publishers of the same task. A successful
read is a point-in-time check; consumers must read again after memory corrections.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_runtime.project_memory import MemoryLedger


class ReportError(ValueError):
    pass


def _text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ReportError(f'{name} must be nonempty text')
    return value


def _id(value, name):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}', value):
        raise ReportError(f'{name} must be a safe ID (letters, digits, dot, dash, underscore)')
    return value


def _relative(value):
    _text(value, 'path')
    if '\\' in value or '\x00' in value or value.startswith('/') or any(
            part in ('', '.', '..') for part in value.split('/')):
        raise ReportError(f'path must be project-relative without traversal: {value!r}')
    return value


def _path(root, relative, mkdir=False):
    """Reject symlinks in every internal component, including dangling links."""
    path = root
    parts = _relative(relative).split('/')
    for index, part in enumerate(parts):
        path = path / part
        if mkdir:
            try:
                path.mkdir()
            except FileExistsError:
                pass
        try:
            mode = path.lstat().st_mode
        except FileNotFoundError:
            if index != len(parts) - 1:
                raise ReportError(f'missing parent directory: {path}')
            return path
        if stat.S_ISLNK(mode):
            raise ReportError(f'symlink is not an artifact or output path: {path}')
        if (mkdir or index < len(parts) - 1) and not stat.S_ISDIR(mode):
            raise ReportError(f'expected directory: {path}')
    return path


def _bytes(root, relative):
    path = _path(root, relative)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as handle:
        if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
            raise ReportError(f'expected regular file: {relative}')
        return handle.read()


def _sha(payload):
    return hashlib.sha256(payload).hexdigest()


def _json(payload):
    def constant(value):
        raise ReportError(f'non-finite JSON number: {value}')
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ReportError(f'duplicate JSON key: {key}')
            result[key] = value
        return result
    return json.loads(payload, parse_constant=constant, object_pairs_hook=pairs)


def _encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')


def _validate(root, manifest):
    if not isinstance(manifest, dict):
        raise ReportError('report manifest must be an object')
    _encoded(manifest)  # Reject non-finite numbers in extra metadata, too.
    for key in ('task_id', 'run_id'):
        _id(manifest.get(key), key)
    for key in ('purpose', 'summary'):
        _text(manifest.get(key), key)
    data = manifest.get('data')
    if not isinstance(data, list) or not data:
        raise ReportError('data must be a nonempty list')
    for row in data:
        if not isinstance(row, dict) or row.get('kind') not in (
                'measured', 'derived', 'synthetic', 'not_applicable'):
            raise ReportError('each data row needs an explicit valid kind')
        for key in ('description', 'meaning'):
            _text(row.get(key), f'data.{key}')
        useful = row.get('useful')
        if type(useful) is not bool and useful != 'unknown':
            raise ReportError('data.useful must be boolean or "unknown"')
    limitations = manifest.get('limitations')
    if not isinstance(limitations, list):
        raise ReportError('limitations must be a list (empty only when no known limitations)')
    for limitation in limitations:
        _text(limitation, 'limitation')
    artifacts = manifest.get('artifacts')
    if not isinstance(artifacts, list):
        raise ReportError('artifacts must be a list')
    seen = set()
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            raise ReportError('artifact must be an object')
        path = _relative(artifact.get('path'))
        _text(artifact.get('role'), 'artifact.role')
        digest = artifact.get('sha256')
        if not isinstance(digest, str) or not re.fullmatch('[0-9a-f]{64}', digest):
            raise ReportError('artifact.sha256 must be a lowercase SHA-256 digest')
        if path in seen:
            raise ReportError(f'duplicate artifact path: {path}')
        seen.add(path)
        if _sha(_bytes(root, path)) != digest:
            raise ReportError(f'artifact hash changed: {path}')
    refs = manifest.get('memory_refs', [])
    if not isinstance(refs, list):
        raise ReportError('memory_refs must be a list')
    if refs:
        MemoryLedger(root, create=False).check(refs)


def _markdown(manifest):
    lines = [f'# {manifest["task_id"]} / {manifest["run_id"]}', '',
             '## 工作目的', '', manifest['purpose'], '', '## 本轮结果', '', manifest['summary'], '',
             '## 数据、意义与用途', '']
    for row in manifest['data']:
        useful = {True: '是', False: '否', 'unknown': '未知'}[row['useful']]
        lines.extend([f'- 类型：{row["kind"]}；有用：{useful}',
                      f'  - 数据：{row["description"]}', f'  - 意义：{row["meaning"]}'])
    lines.extend(['', '## 产物索引', ''])
    for artifact in manifest['artifacts']:
        lines.append(f'- `{artifact["path"]}` — {artifact["role"]}；SHA-256 `{artifact["sha256"]}`')
    if not manifest['artifacts']:
        lines.append('无外部文件；以本报告记录为准。')
    lines.extend(['', '## 限制', ''])
    lines.extend('- ' + value for value in manifest['limitations'])
    if not manifest['limitations']:
        lines.append('未登记已知限制；这不构成科学结论的独立验证。')
    lines.extend(['', '## 记忆依赖', '', ', '.join(manifest.get('memory_refs', [])) or '未声明', '',
                  '本文件为不可变运行快照；当前有效性请通过 publish_report.py read 重新核验。', ''])
    return '\n'.join(lines).encode('utf-8')


def _write(path, payload):
    with path.open('xb') as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


@contextmanager
def _lock(root, task_id):
    _path(root, 'reports/.locks', mkdir=True)
    path = _path(root, f'reports/.locks/{task_id}.lock')
    fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
    with os.fdopen(fd, 'r+b') as handle:
        if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
            raise ReportError('report lock must be a regular file')
        fcntl.flock(handle, fcntl.LOCK_EX)
        yield


def publish(root, manifest):
    root = Path(root).resolve(strict=True)
    # Roundtrip isolates caller mutation and validates all JSON before touching outputs.
    manifest = _json(_encoded(manifest))
    _validate(root, manifest)
    task, run = manifest['task_id'], manifest['run_id']
    with _lock(root, task):
        runs = _path(root, f'reports/{task}/runs', mkdir=True)
        destination = _path(root, f'reports/{task}/runs/{run}')
        if destination.exists():
            raise ReportError(f'run already exists; choose a new run_id: {run}')
        latest = _path(root, f'reports/{task}/latest.json')
        if latest.exists() and not latest.is_file():
            raise ReportError('latest.json must be a regular file')
        staging = Path(tempfile.mkdtemp(prefix='.staging-', dir=runs))
        pointer_temp = None
        try:
            payloads = {'report.json': _encoded(manifest), 'report.md': _markdown(manifest)}
            for name, payload in payloads.items():
                _write(staging / name, payload)
            pointer = {'task_id': task, 'run_id': run, 'reports': {
                name: {'path': f'reports/{task}/runs/{run}/{name}', 'sha256': _sha(payload)}
                for name, payload in payloads.items()}}
            # Recheck evidence immediately before committing the snapshot.
            _validate(root, manifest)
            os.rename(staging, destination)
            pointer_fd, pointer_name = tempfile.mkstemp(prefix='.latest-', dir=latest.parent)
            pointer_temp = Path(pointer_name)
            with os.fdopen(pointer_fd, 'wb') as handle:
                handle.write(_encoded(pointer))
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(pointer_temp, latest)
            return pointer
        finally:
            if staging.exists():
                shutil.rmtree(staging)
            if pointer_temp is not None and pointer_temp.exists():
                pointer_temp.unlink()


def read_report(root, task_id):
    root = Path(root).resolve(strict=True)
    task_id = _id(task_id, 'task_id')
    pointer = _json(_bytes(root, f'reports/{task_id}/latest.json'))
    if not isinstance(pointer, dict) or pointer.get('task_id') != task_id:
        raise ReportError('latest task mismatch')
    run = _id(pointer.get('run_id'), 'run_id')
    reports = pointer.get('reports')
    if not isinstance(reports, dict) or set(reports) != {'report.json', 'report.md'}:
        raise ReportError('latest must bind both report snapshots')
    payloads = {}
    for name, record in reports.items():
        expected = f'reports/{task_id}/runs/{run}/{name}'
        if not isinstance(record, dict) or record.get('path') != expected:
            raise ReportError('latest report path mismatch')
        payloads[name] = _bytes(root, expected)
        if _sha(payloads[name]) != record.get('sha256'):
            raise ReportError(f'report snapshot hash changed: {name}')
    manifest = _json(payloads['report.json'])
    _validate(root, manifest)
    if manifest['task_id'] != task_id or manifest['run_id'] != run:
        raise ReportError('report identity mismatch')
    if payloads['report.md'] != _markdown(manifest):
        raise ReportError('readable report does not match JSON')
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    put = sub.add_parser('publish')
    put.add_argument('--root', required=True)
    put.add_argument('--manifest', required=True, help='project-relative JSON file')
    get = sub.add_parser('read')
    get.add_argument('--root', required=True)
    get.add_argument('--task', required=True)
    args = parser.parse_args(argv)
    try:
        root = Path(args.root).resolve(strict=True)
        result = (publish(root, _json(_bytes(root, args.manifest))) if args.command == 'publish'
                  else read_report(root, args.task))
        print(_encoded(result).decode(), end='')
        return 0
    except (ValueError, OSError, TypeError) as exc:
        print(f'report refused: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
