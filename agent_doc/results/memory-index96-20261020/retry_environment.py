"""One bounded isolated Python 3.12 regression retry; never change system Python."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

OUT = Path(__file__).resolve().parent
receipt = json.loads((OUT / 'final-checks.json').read_text(encoding='utf-8'))
checkout = Path(receipt['snapshot_root'])
scratch = Path(tempfile.mkdtemp(prefix='agent-memory-index96-env-'))
records = []


def run(name, command, timeout=90, cwd=None):
    try:
        with (OUT / name).open('wb') as stream:
            result = subprocess.run(command, cwd=cwd, stdout=stream, stderr=subprocess.STDOUT, timeout=timeout)
        code = result.returncode
    except subprocess.TimeoutExpired:
        code = 'timeout'
    records.append({'command': command, 'cwd': str(cwd) if cwd else None, 'log': name, 'exit_code': code})
    (OUT / 'environment-retry.json').write_text(json.dumps({'scratch': str(scratch), 'commands': records}, indent=2) + '\n', encoding='utf-8')
    print(name, code, flush=True)
    if code != 0:
        raise SystemExit(2)


run('env-bootstrap.log', [sys.executable, '-m', 'venv', str(scratch / 'bootstrap')])
python = str(scratch / 'bootstrap/bin/python')
uv = str(scratch / 'bootstrap/bin/uv')
run('env-uv.log', [python, '-m', 'pip', 'install', 'uv==0.13.3', '--disable-pip-version-check'])
run('env-python312.log', [uv, 'venv', '--python', '3.12', str(scratch / 'python312')])
python = str(scratch / 'python312/bin/python')
run('env-pymupdf.log', [uv, 'pip', 'install', '--python', python, 'PyMuPDF==1.26.7'])
run('env-versions.log', [python, '-c', 'import sys,sqlite3,fitz; print(sys.version); print(sqlite3.sqlite_version); print(fitz.version)'])
run('final312-all.log', [python, '-m', 'unittest', 'discover', '-s', 'tests', '-v'], timeout=240, cwd=checkout)
run('final312-reader.log', [python, '-m', 'unittest', 'discover', '-s', 'apps/paper-reader/tests', '-v'], timeout=90, cwd=checkout)
