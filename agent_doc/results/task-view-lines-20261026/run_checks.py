"""Scoped correctness regression; elapsed time is not a performance metric."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
phase = sys.argv[1]
if phase not in ('baseline', 'fixed'):
    raise SystemExit('baseline or fixed required')
patterns = ['test_task_context.py', 'test_advice_context.py']
if phase == 'fixed':
    patterns += ['test_project_docs_init.py', 'test_project_docs_acceptance.py',
                 'test_project_docs_workflow.py', 'test_markdown_protocol_regressions.py',
                 'test_advice_context_scope.py', 'test_context_cli_output.py']
script = """import sys,unittest
sys.path.insert(0,'tests')
suite=unittest.TestSuite()
for pattern in sys.argv[1:]:
    suite.addTests(unittest.defaultTestLoader.discover('tests',pattern=pattern))
result=unittest.TextTestRunner(stream=sys.stdout,verbosity=2).run(suite)
raise SystemExit(not result.wasSuccessful())
"""
paths = ['agent_runtime/task_context.py', 'agent_runtime/advice_context.py',
         'agent_runtime/project_docs.py', *('tests/' + name for name in patterns),
         'scripts/task_context.py', 'scripts/advice_context.py']
def hashes():
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in paths}
before = hashes()
completed = subprocess.run([sys.executable, '-B', '-c', script, *patterns], cwd=root,
                           capture_output=True, timeout=120)
out = Path(__file__).resolve().parent
(out / (phase + '.log')).write_bytes(completed.stdout + completed.stderr)
metadata = {'phase': phase, 'python': sys.version, 'executable': sys.executable,
            'patterns': patterns, 'outer_timeout_seconds': 120, 'returncode': completed.returncode,
            'before': before, 'after': hashes(), 'stdout_bytes': len(completed.stdout),
            'stderr_bytes': len(completed.stderr), 'scope': 'local correctness only; no fullsuite/model/token/performance acceptance'}
(out / (phase + '.json')).write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'phase': phase, 'returncode': completed.returncode,
                  'source_stable': before == metadata['after'],
                  'tail': (completed.stdout + completed.stderr).decode('utf-8')[-500:]}))
raise SystemExit(completed.returncode)
