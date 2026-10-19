"""Compact transport indexes; complete frozen raw data remain local, not replaced."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
for name in ('independent-raw-v1.json', 'independent-raw-v1-O.json',
             'independent-raw-v2.json', 'independent-raw-v2-O.json'):
    path = root / name
    raw = path.read_bytes()
    data = json.loads(raw)
    output = path.with_suffix('.summary.json')
    if output.exists():
        raise SystemExit('refusing to overwrite ' + str(output))
    corpus = data['corpus']
    summary = {k: data[k] for k in ('reviewer', 'python', 'platform', 'sqlite', 'optimized',
                                  'hashes', 'baseline_source_sha256', 'corpus_snapshot',
                                  'scanner_alphabet', 'scanner_max_tail', 'boundary_count',
                                  'boundary_failures', 'failures', 'migration')}
    summary.update(full_raw=dict(path=name, sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw),
                                 persistence='local only; deliberately excluded from Git publication'),
                   corpus_count=len(corpus), unique_ids=len({r['id'] for r in corpus}),
                   corpus_equal=sum(r['same'] for r in corpus),
                   baseline_reassembled=sum(r['baseline_reassembly'] for r in corpus),
                   candidate_reassembled=sum(r['candidate_reassembly'] for r in corpus),
                   corpus_records=[dict(id=r['id'], input_sha256=r['input_sha256'], same=r['same'],
                                        baseline_reassembly=r['baseline_reassembly'],
                                        candidate_reassembly=r['candidate_reassembly'],
                                        node_count=len(r['candidate'])) for r in corpus])
    with output.open('x') as handle:
        json.dump(summary, handle, ensure_ascii=True, indent=2)
    print(output.name, output.stat().st_size)
