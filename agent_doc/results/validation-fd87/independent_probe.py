"""Independent paired ownership probe; baseline leaks cleaned only after observation."""
import ast
from copy import deepcopy
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
from agent_runtime import validation_context as module

BASE = '80e7bf3ba8de99e0aee55505091172c6a5816c40'
source = subprocess.check_output(['git', 'show', BASE + ':agent_runtime/validation_context.py'], cwd=ROOT, text=True)
tree = ast.parse(source)
function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'write_validation_context')
namespace = dict(vars(module))
exec(compile(ast.Module(body=[function], type_ignores=[]), '<frozen-baseline>', 'exec'), namespace)
baseline = namespace['write_validation_context']
candidate = module.write_validation_context


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def state(fd):
    try:
        os.fstat(fd)
    except OSError as error:
        require(error.errno == errno.EBADF, 'unexpected fstat failure')
        return 'EBADF'
    return 'open'


def run(writer, root, directory, phase, status):
    result = {'status': status, 'scope': 'independent Unicode 回执',
              'errors': ['retained failure'] if status == 'invalid' else [],
              'next_action': 'verify independently',
              'proof': {'artifact_hashes': {'input': 'a' * 64},
                        'review_evidence': {'evidence': 'b' * 64},
                        'limitations': ['display only']}}
    original = deepcopy(result)
    payload = (json.dumps({'schema_version': 'validation-context-record/v1',
                          'project_root': str(root), 'result': result},
                         ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()
    real_open, real_close, real_fdopen, real_fsync = os.open, os.close, os.fdopen, os.fsync
    opened, closed, streams, synced = [], [], [], []
    error = KeyboardInterrupt('injected interrupt') if phase == 'interrupt' else OSError('injected ' + str(phase))
    observation = {'phase': phase, 'status': status}

    def open_fd(*args, **kwargs):
        if phase == 'open':
            raise error
        fd = real_open(*args, **kwargs)
        opened.append(fd)
        return fd

    def close_fd(fd):
        closed.append(fd)
        return real_close(fd)

    class Proxy:
        def __init__(self, stream):
            self.stream = stream

        def __enter__(self):
            if phase == 'enter':
                raise error
            return self

        def __exit__(self, *args):
            self.stream.close()
            if phase == 'exit':
                raise error

        def write(self, data):
            if phase == 'write':
                raise error
            return self.stream.write(data)

        def flush(self):
            if phase == 'flush':
                raise error
            return self.stream.flush()

        def fileno(self):
            return self.stream.fileno()

    def construct(*args, **kwargs):
        if phase in ('construct', 'interrupt'):
            raise error
        stream = real_fdopen(*args, **kwargs)
        streams.append(stream)
        return Proxy(stream)

    def sync(fd):
        if phase == 'fsync':
            raise error
        synced.append(fd)
        return real_fsync(fd)

    try:
        with patch.object(os, 'open', side_effect=open_fd), patch.object(os, 'close', side_effect=close_fd), patch.object(os, 'fdopen', side_effect=construct), patch.object(os, 'fsync', side_effect=sync):
            try:
                receipt = writer(root, result, directory)
            except BaseException as caught:
                require(phase is not None, 'unexpected success-path error')
                require(caught is error, 'injected exception identity lost')
                observation['exception_identity'] = True
                observation['exception_type'] = type(caught).__name__
            else:
                require(phase is None, 'fault not triggered')
                require(receipt['status'] == status, 'status changed')
                require('Display only' in receipt['trust'], 'trust warning changed')
                require(receipt['detail_counts'] == {'artifact_hashes': 1, 'review_evidence': 1}, 'display projection changed')
        observation.update(opened=opened, explicit_closes=closed, fd_states=[state(fd) for fd in opened], real_fsync_calls=len(synced))
        require(result == original, 'input mutated')
        require(len(opened) == (0 if phase == 'open' else 1), 'unexpected open count')
        if writer is candidate:
            require(all(value == 'EBADF' for value in observation['fd_states']), 'candidate leaked descriptor')
            require(closed == opened, 'candidate ownership did not close exactly once')
        files = list((root / directory).glob('*.json'))
        require(len(files) == (0 if phase == 'open' else 1), 'failed target removed or duplicated')
        if files:
            actual = files[0].read_bytes()
            observation.update(file_bytes=len(actual), file_sha256=hashlib.sha256(actual).hexdigest(), file_complete=actual == payload)
            # Existing complete records remain idempotent; incomplete records must refuse overwrite.
            if actual == payload:
                retried = writer(root, result, directory)
                require(module.restore_validation_context(root, retried['record_ref']) == result, 'restore mismatch')
                require(writer(root, result, directory) == retried, 'idempotency mismatch')
                observation['retry'] = 'idempotent-complete'
            else:
                try:
                    writer(root, result, directory)
                except ValueError as caught:
                    require('preserve and repair' in str(caught), 'unexpected conflict error')
                else:
                    raise AssertionError('incomplete record overwritten')
                require(files[0].read_bytes() == actual, 'retry modified failed target')
                observation['retry'] = 'refused-incomplete-unchanged'
            if phase is None:
                require(actual == payload, 'reference serialization differs')
                require(len(synced) == 1, 'success did not call real fsync')
        return observation
    finally:
        for stream in streams:
            stream.close()
        for fd in opened:
            if state(fd) == 'open':
                real_close(fd)


cases = [('construct', 'pending')] * 10 + [(phase, 'pending') for phase in ('interrupt', 'enter', 'write', 'flush', 'fsync', 'exit', 'open')] + [(None, status) for status in ('pending', 'invalid', 'usable-with-scope')]
observations = []
with tempfile.TemporaryDirectory(prefix='fd87-independent-') as temporary:
    root = Path(temporary)
    for index, (phase, status) in enumerate(cases):
        left = run(baseline, root, f'agent_doc/results/baseline-{index}', phase, status)
        right = run(candidate, root, f'agent_doc/results/candidate-{index}', phase, status)
        for field in ('exception_identity', 'exception_type', 'file_bytes', 'file_sha256', 'file_complete', 'retry', 'real_fsync_calls'):
            require(left.get(field) == right.get(field), 'paired semantic mismatch: ' + field)
        observations.append({'case': index, 'baseline': left, 'candidate': right})

summary = {}
for version in ('baseline', 'candidate'):
    summary[version] = {'calls': len(cases), 'successful_opens': sum(len(row[version]['opened']) for row in observations),
                        'leaked_descriptors': sum(row[version]['fd_states'].count('open') for row in observations),
                        'explicit_closes': sum(len(row[version]['explicit_closes']) for row in observations)}
paths = ['agent_runtime/validation_context.py', 'tests/test_validation_write_fd.py',
         'agent_doc/results/validation-fd87/plan.md', 'agent_doc/results/validation-fd87/independent_probe.py']
print(json.dumps({'baseline_revision': BASE, 'python': sys.version, 'platform': platform.platform(),
                  'baseline_source_sha256': hashlib.sha256(source.encode()).hexdigest(),
                  'hashes': {path: hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in paths},
                  'summary': summary, 'observations': observations}, ensure_ascii=False, indent=2))
