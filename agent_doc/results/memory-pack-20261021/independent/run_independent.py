"""Independent bounded runs; binary logs and all writable scratch stay here."""
import json
import os
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[2]
RUN = Path(__file__).resolve().parent
temp = RUN / 'tmp'
temp.mkdir(exist_ok=True)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONIOENCODING='utf-8',
           TEMP=str(temp), TMP=str(temp), TMPDIR=str(temp),
           PYTHONPATH=os.pathsep.join([str(ROOT), str(ROOT/'tests'), str(ROOT/'.agent-runs/memory-index96-deps')]),
           TIKTOKEN_CACHE_DIR=str(ROOT/'.agent-runs/memory-index96-token-cache'))
commands = [
    ('rerun-v1.log', [sys.executable, '-B', '-X', 'utf8', 'agent_doc/results/memory-pack-20261021/measure.py',
                     '--output', str(RUN/'rerun-v1')]),
    ('regressions-v1.log', [sys.executable, '-B', '-X', 'utf8', '-m', 'unittest',
                         'test_memory_tables', 'test_handoff_encoding',
                         'test_handoff_basis.BasisTests.test_consumer_table_format_preserves_full_basis_and_gates', '-v']),
    ('optimized-v1.log', [sys.executable, '-B', '-O', '-X', 'utf8', '-m', 'unittest',
                        'test_memory_tables.MemoryTableTests', 'test_handoff_encoding', '-v']),
]
records = []
for log, command in commands:
    with (RUN/log).open('xb') as stream:
        done = subprocess.run(command, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT, timeout=300)
    records.append({'command': command, 'cwd': str(ROOT), 'log': log, 'exit_code': done.returncode})
    (RUN/'runs-v1.json').write_text(json.dumps({'environment': {k:env[k] for k in ('PYTHONUTF8','PYTHONIOENCODING','PYTHONDONTWRITEBYTECODE','PYTHONPATH','TEMP','TIKTOKEN_CACHE_DIR')}, 'commands': records}, indent=2), encoding='utf-8')
    print(log, done.returncode, flush=True)
sys.exit(int(any(row['exit_code'] for row in records)))
