"""Independent raw-sample arithmetic and binding audit; not a native verifier."""
import hashlib
import json
import math
from pathlib import Path
import statistics
import subprocess

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def key(row):
    c = row['config']
    return (c['sections'], c['words'], c['query'])

def audit(name, expected_sections):
    rows = [json.loads(line) for line in (HERE / name).read_text().splitlines()]
    env, boundary, *cases = rows
    assert env['baseline_commit'] == 'de05d95c725029cca53239f0eb6e0f63d4fb9c19'
    assert env['environment']['hashseed'] == '0'
    for p, h in env['dependencies'].items():
        assert sha(ROOT / p) == h, p
    assert boundary['parity'] and len(boundary['boundaries']) == 96
    boundary_keys = [(b['sections'], b['query'], json.dumps(b['options'], sort_keys=True))
                     for b in boundary['boundaries']]
    assert len(set(boundary_keys)) == 96
    expected = {(None, None, q) for q in
                ('memory retrieval', 'low rank', '量纲', 'topk', 'zzqxnonexistent', '!!!')}
    expected |= {(s, w, 'memory retrieval') for s in expected_sections for w in (16, 512)}
    assert len(cases) == len(expected) and {key(c) for c in cases} == expected
    baseline_hash = hashlib.sha256(subprocess.check_output(
        ['git', 'show', env['baseline_commit'] + ':agent_runtime/knowledge_index.py'], cwd=ROOT)).hexdigest()
    result = []
    for c in cases:
        cfg, samples = c['config'], c['samples_ms']
        assert cfg['repeats'] == 7 and cfg['inner'] == 5 and cfg['options'] == {'limit': 5}
        assert cfg['candidate_sha256'] == sha(ROOT / 'agent_runtime/knowledge_index.py')
        assert cfg['baseline_sha256'] == baseline_hash
        assert cfg['records'] == (8 if cfg['sections'] is not None else 115)
        assert c['parity'] and len(samples) == 7
        assert [s['pair'] for s in samples] == list(range(7))
        medians, ranges = {}, {}
        for i, s in enumerate(samples):
            assert s['order'] == (['baseline', 'candidate'] if i % 2 == 0 else ['candidate', 'baseline'])
            assert all(math.isfinite(s[a]) and s[a] > 0 for a in ('baseline', 'candidate'))
        for arm in ('baseline', 'candidate'):
            vals = [s[arm] for s in samples]
            medians[arm] = statistics.median(vals)
            ranges[arm] = [min(vals), max(vals)]
        reduction = 1 - medians['candidate'] / medians['baseline']
        target = cfg['sections'] in (1, 2) and cfg['words'] == 512
        threshold = medians['baseline'] * .85 if target else max(medians['baseline'] * 1.15, medians['baseline'] + .5)
        passed = medians['candidate'] <= threshold
        assert c['median_ms'] == medians and c['range_ms'] == ranges
        assert c['reduction'] == reduction and c['threshold_ms'] == threshold
        assert c['performance_pass'] == passed
        result.append(dict(key=key(c), medians_ms=medians, ranges_ms=ranges,
                           reduction=reduction, threshold_ms=threshold, threshold_pass=passed,
                           paired_reductions=[1-s['candidate']/s['baseline'] for s in samples],
                           order_medians_ms={order: {arm: statistics.median(
                               s[arm] for s in samples if ''.join(a[0].upper() for a in s['order']) == order)
                               for arm in ('baseline', 'candidate')} for order in ('BC', 'CB')}))
    return rows, dict(file=name, sha256=sha(HERE/name), case_count=len(cases),
                     sample_pairs=sum(len(c['samples_ms']) for c in cases), all_thresholds_pass=all(r['threshold_pass'] for r in result),
                     cases=result)

primary_rows, primary = audit('raw.jsonl', (1, 2, 16, 256))
repeat_rows, repeat = audit('independent-raw.jsonl', (1, 2, 256))
assert primary_rows[0] == repeat_rows[0], 'environment or dependency mismatch'
assert primary_rows[1] == repeat_rows[1], 'boundary output mismatch'
primary_cases = {key(c): c for c in primary_rows[2:]}
for row in repeat_rows[2:]:
    p = primary_cases[key(row)]
    assert p['config'] == row['config'], ('input/config/seed mismatch', key(row))
    assert p['output_sha256'] == row['output_sha256'] and p['results'] == row['results']

paths = ['agent_runtime/knowledge_index.py', 'plugins/research-assistant/skills/model-with-knowledge/scripts/knowledge_index.py',
         'agent_runtime/knowledge.py', 'agent_runtime/project_docs.py', 'scripts/benchmark_knowledge_index.py',
         'scripts/benchmark_knowledge_search.py', 'tests/test_knowledge_excerpt_selection.py',
         'agent_doc/task/task_details/FTS-SECTION-22.md', 'agent_doc/results/fts-section22-20261019/validation-plan.json',
         'agent_doc/results/fts-section22-20261019/plan-review.md', 'agent_doc/results/fts-section22-20261019/research.md',
         'agent_doc/results/fts-section22-20261019/contended.jsonl',
         'agent_doc/results/fts-section22-20261019/independent-audit.py']
bindings = {p: sha(ROOT/p) for p in paths}
bindings.update({str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT/'knowledge').rglob('*')) if p.is_file()})
assert bindings[paths[0]] == bindings[paths[1]], 'mirror mismatch'
stable = (ROOT/'agent_doc/task/task_details/FTS-SECTION-22.md').read_bytes().split(b'## Progress')[0]
assert hashlib.sha256(stable).hexdigest() == 'b1318599c07a88bc45f384c0a6dd382926fbd3e3e7fadc5dc2b117ab66d4232e'
print(json.dumps(dict(schema='independent-manual-audit/v1', primary=primary, independent=repeat,
                     current_artifact_hashes=bindings, shared_config_input_db_and_output_hashes_equal=True,
                     contamination_exclusion='contended.jsonl retained, hashed only, excluded entirely from every calculation'),
                 ensure_ascii=False, indent=2))
