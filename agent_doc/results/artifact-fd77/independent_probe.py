"""Bounded independent descriptor ownership and semantic probe."""
import ast
import errno
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from agent_runtime import result_validation as rv
BASE = '91114412e26d85ae06be5421e42e11bf84fee9c6'
old = subprocess.check_output(['git', 'show', BASE + ':agent_runtime/result_validation.py'], cwd=ROOT).decode()
node = next(n for n in ast.parse(old).body if isinstance(n, ast.FunctionDef) and n.name == '_bytes')
ns = dict(vars(rv))
exec(compile(ast.Module(body=[node], type_ignores=[]), '<baseline>', 'exec'), ns)
baseline = ns['_bytes']
real_open, real_close, real_fstat, real_fdopen = os.open, os.close, os.fstat, os.fdopen
rows = []
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / 'directory').mkdir()
    for case in ['directory'] * 12 + ['constructor', 'read', 'seek', 'exit', 'fstat', 'open', 'valid', 'oversized', 'growth', 'shrink']:
        pair = []
        for label, fn in [('baseline', baseline), ('candidate', rv._bytes)]:
            payload = bytes(range(256)) + b'held-out'
            (root / 'file').write_bytes(payload)
            if case == 'oversized':
                with (root / 'file').open('wb') as stream:
                    stream.truncate(rv.LIMIT + 1)
            opened, closed = [], []
            fault = OSError('independent-' + case)
            def opening(*args, **kwargs):
                if case == 'open':
                    raise fault
                fd = real_open(*args, **kwargs)
                opened.append(fd)
                return fd
            def closing(fd):
                closed.append(fd)
                real_close(fd)
            class Wrapped:
                def __init__(self, fd, mode, **kwargs):
                    self.raw = real_fdopen(fd, mode, **kwargs)
                def __enter__(self):
                    return self
                def __exit__(self, *args):
                    self.raw.close()
                    if case == 'exit':
                        raise fault
                def fileno(self): return self.raw.fileno()
                def seekable(self): return True
                def seek(self, *args):
                    if case == 'seek': raise fault
                    return self.raw.seek(*args)
                def read(self, n):
                    if case == 'read': raise fault
                    if case == 'seek': return b'x' * n
                    return self.raw.read(n)
            def factory(*args, **kwargs):
                if case == 'constructor': raise fault
                return Wrapped(*args, **kwargs)
            def stating(fd):
                if case == 'fstat': raise fault
                info = real_fstat(fd)
                if case == 'growth': (root / 'file').write_bytes(payload * 7)
                if case == 'shrink': (root / 'file').write_bytes(payload[:3])
                return info
            same_fault = False
            with patch.object(rv.os, 'open', opening), patch.object(rv.os, 'close', closing), patch.object(rv.os, 'fdopen', factory), patch.object(rv.os, 'fstat', stating):
                try:
                    value = fn(root, 'directory' if case == 'directory' else 'file')
                    outcome = ['bytes', len(value), hashlib.sha256(value).hexdigest()]
                except Exception as exc:
                    outcome = [type(exc).__name__, str(exc)]
                    same_fault = exc is fault
            states, cleanup = [], []
            for fd in opened:
                try:
                    real_fstat(fd)
                    states.append('open')
                    real_close(fd)
                    cleanup.append(fd)
                except OSError as exc:
                    assert exc.errno == errno.EBADF
                    states.append('EBADF')
            row = dict(case=case, version=label, opened=opened, explicit_close=closed, states=states, cleanup=cleanup, outcome=outcome, same_injected_exception=same_fault)
            rows.append(row)
            pair.append(row)
            if label == 'candidate':
                assert all(s == 'EBADF' for s in states), row
                assert closed == opened, row
            if case in ('constructor', 'read', 'seek', 'exit', 'fstat', 'open'):
                assert same_fault, row
        assert pair[0]['outcome'] == pair[1]['outcome'], pair
        if case in ('directory', 'constructor'):
            assert pair[0]['states'] == ['open']
        else:
            assert all(s == 'EBADF' for s in pair[0]['states'])
paths = ['agent_runtime/result_validation.py', 'tests/test_result_read_fd.py', 'tests/test_result_read_allocation.py', 'agent_doc/task/task_details/ARTIFACT-FD-77.md', 'agent_doc/results/artifact-fd77/before.txt', 'agent_doc/results/artifact-fd77/after.txt', 'agent_doc/results/artifact-fd77/independent_probe.py']
result = dict(baseline=BASE, baseline_source_sha256=hashlib.sha256(old.encode()).hexdigest(), environment=platform.platform() + ' Python ' + platform.python_version(), rows=rows, artifact_hashes={p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths})
(ROOT / 'agent_doc/results/artifact-fd77/raw.json').write_text(json.dumps(result, indent=2) + '\n')
print('PASS: 22 paired cases; 12 real directory failures; candidate exact fd closed once for every successful open; same bytes/errors.')
