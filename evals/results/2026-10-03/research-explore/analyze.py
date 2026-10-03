from pathlib import Path
import csv, hashlib, json
root = Path('/tmp/agent-forward-v1/research-explore')
out = root / 'outputs'
rows = list(csv.DictReader((root/'inputs/measurements.csv').open()))
metrics = []
for r in rows:
    b, c = float(r['baseline_ms']), float(r['candidate_ms'])
    assert b > 0 and c > 0
    metrics.append(dict(workload=r['workload'], scope=r['scope'], baseline_ms=b, candidate_ms=c,
        speedup=b/c, latency_change_pct=(c/b-1)*100, time_saved_ms=b-c, independent_repeats=1))
(out/'descriptive_metrics.json').write_text(json.dumps({'run_id':'agent-forward-v1-research-explore','kind':'derived_from_supplied_synthetic_values','metrics':metrics}, indent=2)+'\n')
paths = ['task.txt', 'inputs/manuscript.md', 'inputs/measurements.csv', 'skill/SKILL.md', 'skill/references/workflow.md', 'skill/references/execution.md']
manifest = {'run_id':'agent-forward-v1-research-explore', 'date':'2026-10-03', 'mode':'offline_fallback; supplied materials only', 'skill':'research-explore', 'selection':'Supplied skill and Python standard library suffice; no external discovery or installation was performed, per task scope.', 'upstream_commit':'unknown; not inspected', 'input_and_skill_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths}}
(out/'provenance.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False)+'\n')
print(json.dumps(metrics, ensure_ascii=False))
