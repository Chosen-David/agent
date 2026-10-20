"""Export only staged objects for a checked non-force GitHub tree publication."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


entries = []
names = [p for p in git('diff', '--cached', '--name-only', '-z').decode().split('\0') if p]
if '--chunk' in sys.argv:
    relative, offset, length = sys.argv[2:]
    raw = git('show', ':' + relative).decode('utf-8')
    print(json.dumps(raw[int(offset):int(offset)+int(length)], ensure_ascii=False))
    raise SystemExit(0)
if '--batch' in sys.argv:
    start, count = map(int, sys.argv[2:])
    names = names[start:start + count]
for relative in names:
    if not relative:
        continue
    if relative.startswith('agent_doc/guide/') or relative in ('.gitattributes', 'docs/token_optimization/progress.json'):
        raise ValueError('unauthorized staged scope: ' + relative)
    line = git('ls-files', '--stage', '--', relative).decode().split('\t')[0]
    mode, sha, stage = line.split()
    if stage != '0':
        raise ValueError('unresolved stage')
    raw = git('cat-file', 'blob', sha)
    entry = {'path': relative, 'mode': mode, 'type': 'blob', 'expected_blob_sha': sha,
             'sha256': hashlib.sha256(raw).hexdigest()}
    try:
        content = raw.decode('utf-8')
        if len(content) > 40000:
            entry['content_chars'] = len(content)
        else:
            entry['content'] = content
    except UnicodeDecodeError:
        entry['base64'] = base64.b64encode(raw).decode('ascii')
    entries.append(entry)
print(json.dumps({'parent': git('rev-parse', 'HEAD').decode().strip(),
                  'base_tree': git('rev-parse', 'HEAD^{tree}').decode().strip(),
                  'expected_tree': git('write-tree').decode().strip() if '--batch' not in sys.argv or start == 0 else None,
                  'total_files': len(git('diff', '--cached', '--name-only', '-z').decode().split('\0'))-1,
                  'entries': entries}, ensure_ascii=False))
