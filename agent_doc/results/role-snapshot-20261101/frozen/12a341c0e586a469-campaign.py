"""One bounded verification campaign with owned-group finalization, no retries."""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
D = Path(__file__).resolve().parent
PHASE = sys.argv[1]
if PHASE not in ('baseline', 'fixed', 'regression', 'independent'):
    raise SystemExit('unknown phase')
OUT = D / PHASE
OUT.mkdir(exist_ok=False)
newtests = [sys.executable, '-B', str(D / 'run_suite.py'), 'newtests', str(OUT / 'newtests.result.json')]
regression = [sys.executable, '-B', str(D / 'run_suite.py'), 'regression', str(OUT / 'regression.result.json')]
commands = [regression] if PHASE == 'regression' else [newtests, regression] if PHASE == 'independent' else [newtests]
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONPATH=str(ROOT / 'tests') + os.pathsep + str(ROOT), ROLE_SNAPSHOT_EVIDENCE=str(OUT))
started = time.monotonic()
rows = []
cancelled = []

def cancel(signum, frame):
    cancelled.append(signum)  # Defer exceptions across Popen assignment/finalization.

signal.signal(signal.SIGTERM, cancel)
signal.signal(signal.SIGINT, cancel)

def group_exists(pid):
    try:
        os.killpg(pid, 0)
        return True
    except ProcessLookupError:
        return False

for index, argv in enumerate(commands):
    row = {'argv': argv, 'cwd': str(ROOT), 'timeout': 180, 'cleanup_grace': 5,
           'timed_out': False, 'failure': None, 'returncode': None}
    child = None
    try:
        with (OUT / (str(index) + '.stdout')).open('xb') as stdout, (OUT / (str(index) + '.stderr')).open('xb') as stderr:
            if cancelled:
                raise RuntimeError('cancelled before launch')
            if time.monotonic() - started >= 180:
                row['timed_out'] = True
                raise TimeoutError('campaign deadline before launch')
            child = subprocess.Popen(argv, cwd=ROOT, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
            row['owned_process_group'] = child.pid
            while child.poll() is None:
                remaining = 180 - (time.monotonic() - started)
                if cancelled:
                    raise RuntimeError('launcher cancelled')
                if remaining <= 0:
                    row['timed_out'] = True
                    raise TimeoutError('campaign deadline')
                try:
                    child.wait(timeout=min(0.2, remaining))
                except subprocess.TimeoutExpired:
                    pass
            row['returncode'] = child.returncode
    except BaseException as exc:
        row['failure'] = type(exc).__name__ + ': ' + str(exc)
    finally:
        if child is not None:
            grace_end = time.monotonic() + 5
            try:
                present = group_exists(child.pid)
                row['observed_group_after_wait'] = present
                if present:
                    if row['failure'] is None:
                        row['failure'] = 'owned group survived direct-child exit'
                    os.killpg(child.pid, signal.SIGKILL)
                    row['cleanup_signal'] = 'SIGKILL to exact new owned group'
                child.wait(timeout=max(0.01, grace_end - time.monotonic()))
                row['returncode'] = child.returncode
                while group_exists(child.pid) and time.monotonic() < grace_end:
                    time.sleep(0.02)
                row['group_absent'] = not group_exists(child.pid)
            except BaseException as exc:
                row['cleanup_error'] = type(exc).__name__ + ': ' + str(exc)
                row['group_absent'] = False
            row['direct_child_reaped'] = child.returncode is not None
        else:
            row.update(group_absent=None, direct_child_reaped=None)
        if cancelled and row['failure'] is None:
            row['failure'] = 'launcher cancelled during finalization'
        row['cancelled_signals'] = list(cancelled)
        rows.append(row)
        record = {'phase': PHASE, 'rows': rows, 'elapsed_seconds': time.monotonic() - started,
                  'environment': {k: env[k] for k in ('PYTHONDONTWRITEBYTECODE', 'PYTHONPATH', 'ROLE_SNAPSHOT_EVIDENCE')},
                  'raw_refs': [{'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                               for p in sorted(OUT.iterdir()) if p.is_file() and p.name != 'execution.json'],
                  'limits': 'SIGKILL/host loss or disk failure may prevent parent cleanup/evidence; no such guarantee.'}
        (OUT / 'execution.json').write_text(json.dumps(record, indent=2) + '\n')
    if row['failure'] or cancelled or not row['group_absent'] or row['returncode'] != 0:
        break
print(json.dumps({'phase': PHASE, 'rows': rows, 'files': len(record['raw_refs'])}))
