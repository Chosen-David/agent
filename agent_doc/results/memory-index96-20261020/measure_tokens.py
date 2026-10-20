"""Count complete CLI response text with a pinned local encoding, no model calls."""
from contextlib import redirect_stdout, redirect_stderr
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import sqlite3
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT), str(ROOT / '.agent-runs/memory-index96-deps')]
os.environ['TIKTOKEN_CACHE_DIR'] = str(ROOT / '.agent-runs/memory-index96-token-cache')
import tiktoken
from agent_runtime.project_memory import MemoryLedger, main

CONFIG = {'entries': 24, 'page_limit': 8, 'long_repeats': 180,
          'read_cases': [0, 1, 24], 'encoding': 'o200k_base', 'tiktoken': '0.12.0'}


def measure():
    if tiktoken.__version__ != CONFIG['tiktoken']:
        raise ValueError('pinned tokenizer version required')
    enc = tiktoken.get_encoding(CONFIG['encoding'])
    observations = []
    def cli(root, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(['--root', str(root), *args])
        if code or err.getvalue():
            raise AssertionError((code, err.getvalue()))
        wire = out.getvalue()
        return json.loads(wire), {'sha256': hashlib.sha256(wire.encode('utf-8')).hexdigest(),
                                 'bytes': len(wire.encode('utf-8')), 'chars': len(wire),
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
            for count in CONFIG['read_cases']:
                candidate = sum(row['tokens'] for row in pages + recalls[:count])
                observations.append({'shape': shape, 'read_entries': count,
                                     'baseline_tokens': baseline['tokens'], 'candidate_tokens': candidate,
                                     'saving_tokens': baseline['tokens']-candidate,
                                     'saving_fraction': (baseline['tokens']-candidate)/baseline['tokens'],
                                     'baseline': baseline, 'pages': pages, 'recalls': recalls[:count]})
    return {'schema_version': 'memory-index-payload-tokens/v1', 'config': CONFIG,
            'environment': {'python': sys.version, 'platform': platform.platform(),
                            'sqlite': sqlite3.sqlite_version, 'tiktoken': tiktoken.__version__,
                            'encoding': enc.name, 'temporary_root': str(root)},
            'observations': observations, 'status': 'pending-independent-validation',
            'limitations': ['Exact local o200k_base CLI response text counts, not model-specific message accounting',
                            'All index pages, recalled JSON and newlines counted; request/tool envelopes, history, reasoning and answers excluded',
                            'No server input/output/cached accounting, cash, quality, TTFT or actual KV cache experiment',
                            'All-bodies and short-body controls may regress; temporary path changes tokenization slightly']}


if __name__ == '__main__':
    result = measure()
    (OUT / 'raw-tokens.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'output': 'raw-tokens.json', 'scenarios': len(result['observations'])}))
