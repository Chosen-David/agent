"""Bounded independent baseline reproduction of unrelated final-suite failures."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
if sys.platform != 'linux':
    raise SystemExit('Run under the same WSL Python as final regressions')
receipt = json.loads((OUT / 'final-checks.json').read_text(encoding='utf-8'))
candidate = ROOT
baseline = Path(tempfile.mkdtemp(prefix='independent-memory-index96-baseline-'))
with tarfile.open(ROOT / '.agent-runs/memory-index96-final-checks/baseline.tar') as archive:
    archive.extractall(baseline, filter='data')
paths = ['agent_runtime/result_store.py', 'agent_runtime/result_validation.py', 'agent_runtime/project_docs.py',
         'tests/test_result_search_depth.py', 'scripts/result_store.py',
         'tests/test_reader.py', 'apps/paper-reader/tests/test_app.py']
hashes = {p: {'baseline': hashlib.sha256((baseline / p).read_bytes()).hexdigest(),
              'candidate': hashlib.sha256((candidate / p).read_bytes()).hexdigest()} for p in paths}
commands = []
for name, root in [('baseline', baseline), ('candidate', candidate)]:
    command = [sys.executable, '-m', 'unittest', 'tests.test_result_search_depth', '-v']
    result = subprocess.run(command, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log = f'independent-regression-{name}.log'
    with (OUT / log).open('xb') as stream:
        stream.write(result.stdout)
    commands.append({'command': command, 'cwd': str(root), 'exit_code': result.returncode, 'log': log})
probe = subprocess.run([sys.executable, '-c', "import json; print(json.loads('['*10000+'0'+']'*10000)[0] is not None); import fitz"],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
with (OUT / 'independent-regression-environment.log').open('xb') as stream:
    stream.write(probe.stdout)
payload = {'python': sys.version, 'baseline_root': str(baseline), 'candidate_root': str(candidate),
           'hashes': hashes, 'commands': commands, 'environment_probe_exit': probe.returncode,
           'environment_probe_log': 'independent-regression-environment.log',
           'scope': 'targeted baseline comparison only; full repository regression not independently repeated'}
with (OUT / 'independent-regression-diagnostic.json').open('x', encoding='utf-8') as stream:
    stream.write(json.dumps(payload, indent=2) + '\n')
print(json.dumps(payload, indent=2))
