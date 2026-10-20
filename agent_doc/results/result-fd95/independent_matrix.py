"""Independent paired ownership oracle; prints raw observations, no pass labels imported."""
import contextlib
import errno
import hashlib
import json
import os
from pathlib import Path
import platform
import stat
import subprocess
import sys
import tempfile
import types
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
BASE = 'e30dfce8424f7912a3716dd6ef035f648808e2f7'
SOURCES = {
    'baseline': subprocess.check_output(['git', 'show', BASE + ':agent_runtime/result_store.py'], cwd=ROOT),
    'candidate': (ROOT / 'agent_runtime/result_store.py').read_bytes(),
}
PAYLOAD = b'fd95\x00\xff\n'
SHA = hashlib.sha256(PAYLOAD).hexdigest()
REAL_OPEN, REAL_CLOSE, REAL_FDOPEN = os.open, os.close, os.fdopen
REAL_STAT, REAL_LINK, REAL_FSYNC = os.fstat, os.link, os.fsync


def check(value, reason):
    if not value:
        raise AssertionError(reason)


def alive(fd):
    try:
        REAL_STAT(fd)
    except OSError as exc:
        check(exc.errno == errno.EBADF, 'unexpected fstat errno')
        return False
    return True


def load(source, label):
    module = types.ModuleType('agent_runtime.independent_' + label)
    module.__package__ = 'agent_runtime'
    exec(compile(source, label + '-result_store.py', 'exec'), module.__dict__)
    return module


def run_case(rs, label, op, phase):
    with tempfile.TemporaryDirectory(prefix='independent-fixture-', dir=Path(__file__).parent) as name:
        root = Path(name)
        (root / 'input').write_bytes(PAYLOAD)
        (root / 'directory').mkdir()
        ref = {'path': 'input', 'sha256': SHA}
        acquired, streams, close_calls, events = [], [], [], []
        error = KeyboardInterrupt('injected') if phase == 'interrupt' else RuntimeError('injected-' + phase)
        caught, result = None, None
        target = root / rs.HOME / 'saved/record.json'
        record = {'schema_version': rs.SCHEMA, 'run_id': 'saved', 'summary': 'needle',
                  'origin': 'historical-external-reference', 'context': {},
                  'registered_at': '2026-10-20T00:00:00+00:00',
                  'validation_at_registration': {'status': 'unknown'}}
        expected = (json.dumps(record, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode()
        store = rs.ResultStore(root)
        store.show = lambda _: {'bytes': target.read_bytes()}

        def opened(*args, **kwargs):
            if phase == 'open':
                raise error
            fd = REAL_OPEN(*args, **kwargs)
            acquired.append(fd)
            events.append('open')
            return fd

        def closed(fd):
            close_calls.append(fd)
            events.append('raw-close')
            return REAL_CLOSE(fd)

        class Stream:
            def __init__(self, inner):
                self.inner = inner
            def __enter__(self):
                if phase == 'enter':
                    raise error
                return self
            def __exit__(self, *args):
                self.inner.close()
                events.append('stream-close')
                if phase == 'exit':
                    raise error
            def fileno(self):
                return self.inner.fileno()
            def read(self, *args):
                if phase == 'read':
                    raise error
                return self.inner.read(*args)
            def write(self, data):
                check(data == expected, 'serialized record bytes changed')
                if phase == 'write':
                    raise error
                return self.inner.write(data)
            def flush(self):
                if phase == 'flush':
                    raise error
                self.inner.flush()
                events.append('flush')

        def fdopen(*args, **kwargs):
            if phase in ('construct', 'interrupt'):
                raise error
            stream = REAL_FDOPEN(*args, **kwargs)
            streams.append(stream)
            return Stream(stream)

        def fstat(fd):
            if phase == 'fstat':
                raise error
            info = REAL_STAT(fd)
            if phase == 'nonregular':
                return types.SimpleNamespace(st_mode=stat.S_IFIFO, st_size=info.st_size)
            if phase == 'growth':
                return types.SimpleNamespace(st_mode=info.st_mode, st_size=0)
            return info

        def fsync(fd):
            if phase == 'fsync':
                raise error
            events.append('fsync')
            return REAL_FSYNC(fd)

        def link(src, dst, **kwargs):
            check(all(not alive(fd) for fd in acquired), 'publication before descriptor closed')
            events.append('link-after-close')
            check(Path(src).read_bytes() == expected, 'temporary publication bytes differ')
            if phase == 'link':
                raise error
            if phase == 'race':
                Path(dst).write_bytes(b'concurrent winner')
                try:
                    REAL_LINK(src, dst, **kwargs)
                except FileExistsError as exc:
                    nonlocal caught_race
                    caught_race = exc
                    raise
            return REAL_LINK(src, dst, **kwargs)

        caught_race = None
        if phase == 'directory':
            ref['path'] = 'directory'
        if phase == 'stale':
            ref['sha256'] = '0' * 64
        try:
            with contextlib.ExitStack() as stack:
                for attr, replacement in [('open', opened), ('close', closed), ('fdopen', fdopen),
                                           ('fstat', fstat), ('fsync', fsync), ('link', link)]:
                    stack.enter_context(patch.object(rs.os, attr, replacement))
                if phase == 'mkstemp':
                    stack.enter_context(patch.object(rs.tempfile, 'mkstemp', side_effect=error))
                if phase == 'hash-init':
                    stack.enter_context(patch.object(rs.hashlib, 'sha256', side_effect=error))
                if phase in ('limit', 'growth'):
                    stack.enter_context(patch.object(rs, 'ARTIFACT_LIMIT', 4))
                try:
                    if op == 'read':
                        result = rs._read(root, ref['path'], 4 if phase in ('limit', 'growth') else rs.METADATA_LIMIT)
                    elif op == 'check':
                        result = rs._check_ref(root, ref)
                    else:
                        result = store._save(record)
                except BaseException as exc:
                    caught = exc
            leaks = [fd for fd in acquired if alive(fd)]
            target_bytes = target.read_bytes() if target.exists() else None
            temporaries = list(target.parent.glob('.record-*')) if target.parent.exists() else []
            check(not temporaries, 'temporary name survived operation')
            injected = phase in {'construct', 'interrupt', 'enter', 'exit', 'fstat', 'read', 'write',
                                 'flush', 'fsync', 'link', 'open', 'mkstemp', 'hash-init'}
            if injected:
                check(caught is error, 'injected exception identity changed')
            elif phase == 'success':
                check(caught is None, 'successful operation failed')
                if op == 'read':
                    check(result == PAYLOAD, 'read bytes changed')
                if op == 'save':
                    check(result == {'bytes': expected}, 'save bytes changed')
            elif phase == 'directory':
                check(isinstance(caught, IsADirectoryError), 'directory error changed')
            elif phase == 'race':
                check(isinstance(caught, rs.ResultStoreError) and caught.__cause__ is caught_race,
                      'concurrent FileExists translation changed')
                check(target_bytes == b'concurrent winner', 'concurrent target overwritten')
            else:
                check(isinstance(caught, rs.ResultStoreError), 'rejection class changed')
            if op == 'save' and phase not in ('success', 'race'):
                check(target_bytes is None, 'failed save published target')
            if label == 'candidate':
                check(not leaks, 'candidate leaked acquired descriptor')
                check(close_calls == acquired, 'candidate did not close each owned fd exactly once')
            row = {'version': label, 'operation': op, 'phase': phase, 'acquired': len(acquired),
                   'leaked_fds': len(leaks), 'raw_close_calls': len(close_calls),
                   'exception': type(caught).__name__ if caught else None,
                   'exception_identity_preserved': caught is error if injected else None,
                   'exception_message': str(caught).replace(str(root), '<fixture>') if caught else None,
                   'events': events, 'temporary_names_remaining': len(temporaries),
                   'target_sha256': hashlib.sha256(target_bytes).hexdigest() if target_bytes else None}
        finally:
            for stream in streams:
                stream.close()
            for fd in acquired:
                if alive(fd):
                    REAL_CLOSE(fd)
        return row


cases = []
for operation in ('read', 'check'):
    phases = ['success', 'directory', 'construct', 'interrupt', 'enter', 'exit', 'fstat', 'read',
              'open', 'nonregular', 'limit', 'growth']
    if operation == 'check':
        phases += ['stale', 'hash-init']
    cases += [(operation, phase) for phase in phases]
cases += [('save', phase) for phase in ['success', 'construct', 'interrupt', 'enter', 'exit', 'write',
                                       'flush', 'fsync', 'link', 'race', 'open', 'mkstemp']]
rows = [run_case(load(source, label), label, op, phase)
        for label, source in SOURCES.items() for op, phase in cases]
count = len(cases)
for old, new in zip(rows[:count], rows[count:]):
    for field in ('exception', 'exception_message', 'target_sha256', 'temporary_names_remaining'):
        check(old[field] == new[field], 'paired observable changed: ' + str((old['operation'], old['phase'], field)))
print(json.dumps({'baseline': BASE, 'python': sys.version, 'platform': platform.platform(),
                  'optimized': sys.flags.optimize, 'input_sha256': SHA,
                  'source_sha256': {k: hashlib.sha256(v).hexdigest() for k, v in SOURCES.items()},
                  'case_count_each': count, 'rows': rows,
                  'leaks': {label: sum(r['leaked_fds'] for r in rows if r['version'] == label)
                            for label in SOURCES}}, indent=2))
