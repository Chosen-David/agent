"""Deterministic complete wire bytes, not a tokenizer or model benchmark."""
import hashlib
import json
from pathlib import Path
import platform
import sqlite3
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from agent_runtime.project_memory import MemoryLedger, _index_json


CONFIG = {'entries': 24, 'page_limit': 8, 'long_repeats': 180,
          'read_cases': [0, 1, 24], 'scope': 'T96'}


def pretty_bytes(value):
    return len((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))


def measure():
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        ledger = MemoryLedger(root, create=True)
        for shape in ('long', 'short'):
            # Fresh logical scope keeps both cases in the same normal ledger.
            for i in range(CONFIG['entries']):
                body = f'{i}: 原始事实 must retain source and corrections.\n'
                if shape == 'long':
                    body *= CONFIG['long_repeats']
                ledger.add(f'{shape}{i:03}', 'observation', body, 'synthetic:MEM-INDEX-96',
                           scope=[CONFIG['scope'], shape], evidence='verified')
            with ledger._connect(write=True) as db:
                db.execute("UPDATE entries SET created_at='2026-10-20'")
            full = ledger.list(scope=shape)
            page_bytes, page_sizes, ids = 0, [], []
            cursor = snapshot = None
            while True:
                page = ledger.index(scope=shape, limit=CONFIG['page_limit'], after_id=cursor,
                                    expected_snapshot=snapshot)
                wire = (_index_json(page) + '\n').encode('utf-8')
                page_bytes += len(wire); page_sizes.append(len(wire))
                ids.extend(row['id'] for row in page['entries'])
                cursor, snapshot = page['next_after_id'], page['snapshot']
                if cursor is None:
                    break
            if ids != [entry['id'] for entry in full]:
                raise AssertionError('pagination differs from full source')
            recalls = [pretty_bytes(ledger.check([entry['id']])) for entry in full]
            baseline = pretty_bytes(full)
            for read_count in CONFIG['read_cases']:
                read_bytes = sum(recalls[:read_count])
                candidate = page_bytes + read_bytes
                rows.append({'shape': shape, 'entries': len(full), 'read_entries': read_count,
                             'page_sizes_bytes': page_sizes, 'index_bytes': page_bytes,
                             'recall_bytes': read_bytes, 'baseline_list_bytes': baseline,
                             'candidate_bytes': candidate, 'saving_bytes': baseline-candidate,
                             'saving_fraction': (baseline-candidate)/baseline,
                             'root_path_chars': len(str(root))})
        storage = ledger.storage()
    return {'schema_version': 'memory-index-byte-observations/v1', 'config': CONFIG,
            'environment': {'python': sys.version, 'platform': platform.platform(),
                            'sqlite': sqlite3.sqlite_version}, 'observations': rows,
            'storage': storage, 'status': 'pending-independent-validation',
            'limitations': ['UTF-8 serialized CLI JSON bytes only; no token/server/quality or time measurement',
                            'All pages plus individually checked recalls counted; no claim when every body is needed',
                            'Temporary absolute root length changes packet size; exact literal bytes retained per run',
                            'No persistent summary cache is created; storage is observation, not disk compaction']}


if __name__ == '__main__':
    result = measure()
    out = Path(__file__).with_name('raw.json')
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(out), 'scenarios': len(result['observations'])}))
