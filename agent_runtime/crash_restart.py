"""Durable bounded process-crash retries; no model or task budget reset."""
from pathlib import Path

from .external_json import ExternalJSONError, load_json
from .task_manifest import atomic_json

MAX_FAILURES=3
CRASH_STATE_LIMIT=1024 * 1024

def read_crash_state(path,run_id):
    path=Path(path)
    try:
        value=load_json(path,max_bytes=CRASH_STATE_LIMIT)
    except ExternalJSONError as exc:
        # A missing optional latch means no crash. Every object that does exist,
        # including symlinks and special files, must fail closed.
        if isinstance(exc.__cause__, FileNotFoundError):
            return {'run_id':run_id,'failures':0,'status':'ready'}
        raise
    if not isinstance(value, dict):
        raise ValueError('crash state must be a JSON object')
    n=value.get('failures')
    if value.get('run_id')!=run_id or type(n) is not int or not 0<=n<=MAX_FAILURES:
        raise ValueError('foreign or invalid crash state; explicit recovery required')
    expected='blocked' if n==MAX_FAILURES else 'retry' if n else 'ready'
    if value.get('status')!=expected:raise ValueError('inconsistent crash state')
    return value

def record_crash(path,run_id,returncode):
    if type(returncode) is not int or returncode==0:raise ValueError('nonzero process exit required')
    previous=read_crash_state(path,run_id)
    failures=min(MAX_FAILURES,previous['failures']+1)
    value={'run_id':run_id,'failures':failures,'returncode':returncode,
           'status':'blocked' if failures==MAX_FAILURES else 'retry',
           'retry_seconds':None if failures==MAX_FAILURES else 5*2**(failures-1),
           'reason':'worker process crash; repair adapter and explicitly clear this latch after diagnosis'}
    atomic_json(Path(path),value)
    return value
