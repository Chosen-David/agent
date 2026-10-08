"""Reproducible bounded Linux checks; output directory must already exist."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    root, out = Path(args.root).resolve(), Path(args.output).resolve()
    def dump(name, value):
        (out / name).write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    names = subprocess.check_output(['git', 'ls-files'], cwd=root, text=True).splitlines()
    files = []
    for name in names:
        if name.startswith(('agent_runtime/', 'tests/', 'workflows/', 'templates/', 'scripts/')) and name.endswith(('.py', '.md')) or name in ('setup.py', 'README.md', 'doc/README.md', 'docs/codex_adoption/README.md'):
            data = (root / name).read_bytes().decode('utf-8').replace('\r\n', '\n').encode('utf-8')
            files.append({'path': name, 'sha256': hashlib.sha256(data).hexdigest(), 'normalization': 'utf8-lf'})
    dump('source-inventory.json', {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(), 'files': files})
    dump('environment.json', {'platform': platform.platform(), 'python': sys.version,
                             'tmux': os.environ.get('TMUX'), 'pid': os.getpid(),
                             'root': str(root), 'real_tmux_tests': True})
    env = dict(os.environ, AGENT_TEST_REAL_TMUX='1', PYTHONUTF8='1')
    commands = [('repository', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v']),
                ('reader', [sys.executable, '-m', 'unittest', 'discover', '-s', 'apps/paper-reader/tests', '-v']),
                ('plugin', [sys.executable, 'scripts/sync_plugin_references.py', '--check']),
                ('knowledge', [sys.executable, '-m', 'agent_runtime.knowledge', '--root', 'knowledge', 'validate'])]
    receipts = []
    for name, command in commands:
        dump('live.json', {'phase': name, 'pid': os.getpid()})
        start = time.monotonic()
        with (out / (name + '.log')).open('wb') as log:
            result = subprocess.run(command, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=300)
        receipts.append({'name': name, 'command': command, 'exit_code': result.returncode,
                         'seconds': time.monotonic() - start})
        dump('checks.json', receipts)
    dump('live.json', {'phase': 'completed', 'failed': [x['name'] for x in receipts if x['exit_code']]})
    return int(any(x['exit_code'] for x in receipts))


if __name__ == '__main__':
    raise SystemExit(main())
