"""Reproduce allocation during rejection; no wall-time or model-quality claim."""
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import tempfile
import tracemalloc

ROOT = Path(__file__).resolve().parents[3]
BASE = '0cb8cc1d68dd12200ec32c792b1f478e6b71339d'
NAME = 'agent_runtime/prompt_context.py'
baseline = subprocess.check_output(['git', 'show', BASE + ':' + NAME], cwd=ROOT)
candidate = (ROOT / NAME).read_bytes()
rows = []
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    for size in (1000001, 8388608, 16777216):
        data = b'x' * size
        (root / 'prompt.md').write_bytes(data)
        digest = hashlib.sha256(data).hexdigest()
        for label, source in (('baseline', baseline), ('candidate', candidate)):
            namespace = {}
            exec(compile(source, NAME, 'exec'), namespace)
            tracemalloc.start()
            try:
                namespace['_read'](root, 'prompt.md')
            except ValueError as exc:
                error = str(exc)
            else:
                error = None
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            rows.append(dict(version=label, input_bytes=size, input_sha256=digest,
                             error=error, python_peak_bytes=peak))
print(json.dumps(dict(base_sha=BASE, python=platform.python_version(),
                      machine=platform.machine(), source_sha256={
                          'baseline': hashlib.sha256(baseline).hexdigest(),
                          'candidate': hashlib.sha256(candidate).hexdigest()},
                      rows=rows), indent=2))
