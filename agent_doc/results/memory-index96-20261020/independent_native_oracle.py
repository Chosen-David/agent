"""Reconstruct every producer wire from fixed fixture fields, without ledger reads.

Compare UTF-8 hashes, native terminators and counts, and independently implement
rank-driven byte-pair merging against the declared o200k encoding table.
"""
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / '.agent-runs/memory-index96-deps')]
os.environ['TIKTOKEN_CACHE_DIR'] = str(ROOT / '.agent-runs/memory-index96-token-cache')
import regex
import tiktoken

def require(condition, reason):
    if not condition:
        raise AssertionError(reason)
def sha(raw):
    return hashlib.sha256(raw).hexdigest()
def canon(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
enc = tiktoken.get_encoding('o200k_base')
token_cache = {}
def reference_tokens(text):
    total = []
    for piece in regex.findall(enc._pat_str, text):
        raw = piece.encode('utf-8')
        if raw not in token_cache:
            parts = [bytes([b]) for b in raw]
            while len(parts) > 1:
                best = min(range(len(parts) - 1), key=lambda i: enc._mergeable_ranks.get(parts[i] + parts[i+1], float('inf')))
                if parts[best] + parts[best+1] not in enc._mergeable_ranks:
                    break
                parts[best:best+2] = [parts[best] + parts[best+1]]
            token_cache[raw] = [enc._mergeable_ranks[p] for p in parts]
        total.extend(token_cache[raw])
    return total

def run(raw_path):
    raw = json.loads(raw_path.read_text(encoding='utf-8'))
    root = raw['environment']['temporary_root']
    terminator = '\r\n'
    identity = raw['environment']['tokenizer_identity']
    ranks = hashlib.sha256()
    for token, rank in sorted(enc._mergeable_ranks.items()):
        ranks.update(len(token).to_bytes(8, 'big') + token + rank.to_bytes(8, 'big'))
    require(ranks.hexdigest() == identity['mergeable_ranks_sha256'], 'rank table changed')
    require(enc._pat_str == identity['pattern'] and enc._special_tokens == identity['special_tokens'], 'tokenizer pattern/specials changed')
    require(tiktoken.__version__ == '0.12.0', 'tokenizer version')
    for path, expected in identity['package_file_sha256'].items():
        require(sha((ROOT / '.agent-runs/memory-index96-deps' / path).read_bytes()) == expected, 'package hash ' + path)
    for path, expected in identity['cache_file_sha256'].items():
        require(sha((ROOT / '.agent-runs/memory-index96-token-cache' / path).read_bytes()) == expected, 'cache hash ' + path)
    verified = []
    def verify_wire(value, compact, capture, name):
        # Windows TextIOWrapper translates every emitted LF, including pretty
        # JSON layout; JSON escapes embedded body newlines before this step.
        logical = (canon(value) if compact else json.dumps(value, ensure_ascii=False, indent=2)) + '\n'
        wire = logical.replace('\n', terminator)
        binary = wire.encode('utf-8')
        tokens = enc.encode(wire, disallowed_special=())
        require(tokens == reference_tokens(wire), 'independent BPE token sequence differs: ' + name)
        actual = {'sha256': sha(binary), 'bytes': len(binary), 'chars': len(wire), 'tokens': len(tokens)}
        for field, expected in actual.items():
            require(capture[field] == expected, f'{name}: {field} {capture[field]} != {expected}')
        verified.append({'capture': name, **actual})
    for shape in ('long', 'short'):
        entries = []
        for i in range(24):
            body = f'{i}: 原始事实 must retain source and corrections.\n' * (180 if shape == 'long' else 1)
            entries.append({'id': f'{shape}{i:03}', 'kind': 'observation', 'content': body,
                            'source': 'synthetic:MEM-INDEX-96', 'scope': ['T96', shape], 'evidence': 'verified',
                            'status': 'active', 'created_at': '2026-10-20', 'document_refs': None, 'deps': []})
        capture = raw['captures'][shape]
        require(len(capture['pages']) == 3 and len(capture['recalls']) == 24, 'capture coverage')
        verify_wire(entries, False, capture['baseline'], shape + ':baseline')
        binding = {'project_root': root, 'filter': {'status': 'active', 'scope': shape}}
        digest = hashlib.sha256(canon(binding).encode('utf-8'))
        projections = []
        for entry in entries:
            entry_hash = sha(canon(entry).encode('utf-8'))
            digest.update(b'\n' + entry_hash.encode('ascii'))
            projection = {k: v for k, v in entry.items() if k != 'content'}
            projection.update(content_sha256=sha(entry['content'].encode('utf-8')), content_chars=len(entry['content']), entry_sha256=entry_hash)
            projections.append(projection)
        snapshot = digest.hexdigest()
        for index, start in enumerate((0, 8, 16)):
            more = start + 8 < 24
            page = {'schema_version': 'memory-index/v1', **binding, 'snapshot': snapshot, 'total_entries': 24,
                    'start': start, 'entries': projections[start:start+8],
                    'next_after_id': entries[start+7]['id'] if more else None, 'partial': more,
                    'scope': 'navigation only; content omitted; read required bodies and dependencies through current memory checks before use; no validity or completeness proof'}
            verify_wire(page, True, capture['pages'][index], shape + ':page:' + str(index))
        for i, entry in enumerate(entries):
            verify_wire([entry], False, capture['recalls'][i], shape + ':recall:' + str(i))
    verify_wire(raw['storage'], False, raw['storage_capture'], 'storage')
    require(raw['storage_main_sha256_before'] == raw['storage_main_sha256_after'], 'storage changed main DB fixture')
    rows = raw['observations']
    require([(r['shape'], r['read_entries']) for r in rows] == [(s, n) for s in ('long', 'short') for n in (0, 1, 24)], 'scenario coverage')
    for row in rows:
        capture = raw['captures'][row['shape']]
        for unit in ('bytes', 'tokens'):
            baseline = capture['baseline'][unit]
            candidate = sum(c[unit] for c in capture['pages'] + capture['recalls'][:row['read_entries']])
            require(row['baseline_' + unit] == baseline and row['candidate_' + unit] == candidate, 'sum arithmetic')
            require(row['saving_' + unit] == baseline - candidate, 'signed savings')
            require(row['saving_fraction_' + unit] == (baseline-candidate)/baseline, 'fraction arithmetic')
            require((candidate < baseline) == (row['shape'] == 'long' and row['read_entries'] < 24), 'control direction')
    return {'raw_file': raw_path.name, 'raw_sha256': sha(raw_path.read_bytes()), 'verified_wire_captures': len(verified),
            'independent_bpe': 'full token sequence matched all captures', 'rank_sha256': ranks.hexdigest(),
            'captures': verified, 'observations': rows}

if __name__ == '__main__':
    name = sys.argv[1] if len(sys.argv) > 1 else 'raw-native-v3.json'
    result = run(OUT / name)
    label = '-' + sys.argv[2] if len(sys.argv) > 2 else ''
    target = OUT / ('independent-oracle-' + Path(name).stem + label + '.json')
    with target.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'verified_wire_captures': result['verified_wire_captures'], 'output': str(target)}))
