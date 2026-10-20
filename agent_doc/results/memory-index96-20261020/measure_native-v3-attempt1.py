"""v3: real UTF-8 subprocess stdout, preserving native line terminators."""
import hashlib
import json
import os
from pathlib import Path
import platform
import sqlite3
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT), str(ROOT / '.agent-runs/memory-index96-deps')]
os.environ['TIKTOKEN_CACHE_DIR'] = str(ROOT / '.agent-runs/memory-index96-token-cache')
import tiktoken
from agent_runtime.project_memory import MemoryLedger

CONFIG = {'entries': 24, 'page_limit': 8, 'long_repeats': 180, 'read_cases': [0, 1, 24],
          'encoding': 'o200k_base', 'tiktoken': '0.12.0', 'PYTHONIOENCODING': 'utf-8',
          'stdout_capture': 'subprocess binary; preserve CRLF/LF exactly'}


def measure():
    if tiktoken.__version__ != CONFIG['tiktoken']:
        raise ValueError('pinned tokenizer required')
    enc = tiktoken.get_encoding(CONFIG['encoding'])
    observations, captures = [], {}
    def cli(root, *args):
        command = [sys.executable, '-m', 'agent_runtime.project_memory', '--root', str(root), *args]
        result = subprocess.run(command, cwd=ROOT, capture_output=True,
                                env=dict(os.environ, PYTHONIOENCODING=CONFIG['PYTHONIOENCODING']))
        if result.returncode or result.stderr:
            raise AssertionError((command, result.returncode, result.stderr))
        wire = result.stdout.decode('utf-8')
        if not wire.endswith(os.linesep):
            raise AssertionError('unexpected native line terminator')
        return json.loads(wire), {'command_tail': list(args),
                                 'sha256': hashlib.sha256(result.stdout).hexdigest(),
                                 'bytes': len(result.stdout), 'chars': len(wire),
                                 'tokens': len(enc.encode(wire, disallowed_special=()))}
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        ledger = MemoryLedger(root, create=True)
        for shape in ('long', 'short'):
            for i in range(CONFIG['entries']):
                body = f'{i}: 原始事实 must retain source and corrections.\n'
                if shape == 'long':
                    body *= CONFIG['long_repeats']
                ledger.add(f'{shape}{i:03}', 'observation', body, 'synthetic:MEM-INDEX-96',
                           scope=['T96', shape], evidence='verified')
            with ledger._connect(write=True) as db:
                db.execute("UPDATE entries SET created_at='2026-10-20'")
            full, baseline = cli(root, 'list', '--scope', shape)
            pages, ids = [], []
            cursor = snapshot = None
            while True:
                args = ['index', '--scope', shape, '--limit', str(CONFIG['page_limit'])]
                if cursor is not None:
                    args += ['--after-id', cursor, '--snapshot', snapshot]
                page, accounting = cli(root, *args)
                pages.append(accounting)
                ids.extend(row['id'] for row in page['entries'])
                cursor, snapshot = page['next_after_id'], page['snapshot']
                if cursor is None:
                    break
            if ids != [entry['id'] for entry in full]:
                raise AssertionError('incomplete directory')
            recalls = []
            for entry in full:
                value, accounting = cli(root, 'check', entry['id'])
                if value != [entry]:
                    raise AssertionError('body changed')
                recalls.append(accounting)
            captures[shape] = {'baseline': baseline, 'pages': pages, 'recalls': recalls}
            for count in CONFIG['read_cases']:
                row = {'shape': shape, 'read_entries': count}
                for unit in ('bytes', 'tokens'):
                    candidate = sum(item[unit] for item in pages + recalls[:count])
                    base = baseline[unit]
                    row.update({f'baseline_{unit}': base, f'candidate_{unit}': candidate,
                                f'saving_{unit}': base-candidate,
                                f'saving_fraction_{unit}': (base-candidate)/base})
                observations.append(row)
        before = hashlib.sha256(ledger.path.read_bytes()).hexdigest()
        storage, storage_capture = cli(root, 'storage')
        after = hashlib.sha256(ledger.path.read_bytes()).hexdigest()
    return {'schema_version': 'memory-index-native-observations/v3', 'config': CONFIG,
            'environment': {'python': sys.version, 'platform': platform.platform(), 'sqlite': sqlite3.sqlite_version,
                            'tiktoken': tiktoken.__version__, 'encoding': enc.name,
                            'temporary_root': str(root), 'os_linesep_repr': repr(os.linesep)},
            'observations': observations, 'captures': captures, 'storage': storage,
            'storage_capture': storage_capture, 'storage_main_sha256_before': before,
            'storage_main_sha256_after': after, 'status': 'pending-independent-validation',
            'limitations': ['Exact UTF-8 subprocess stdout bytes and local o200k_base text tokens only; native newlines retained',
                            'All directory pages and needed recall outputs counted; CLI request/tool wrappers, history, reasoning and answers excluded',
                            'No server usage, cash, model quality, latency or KV cache claim; temporary path affects counts',
                            'Short entries and full reading can regress; no database CPU or disk-compaction claim']}


if __name__ == '__main__':
    (OUT / 'raw-native-v3.json').write_text(json.dumps(measure(), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('raw-native-v3.json written; pending independent validation')
