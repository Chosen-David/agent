import csv, hashlib, json, platform, statistics
from pathlib import Path
ROOT = Path(__file__).resolve().parents[5]
INPUT = ROOT / "cases/recovery-initial/inputs"
OUTPUT = Path(__file__).resolve().parent
rows = list(csv.DictReader((INPUT / "measurements.csv").open()))
results = {}
for workload in sorted({r["workload"] for r in rows}):
    group = [r for r in rows if r["workload"] == workload]
    b = [float(r["baseline_ms"]) for r in group]
    c = [float(r["candidate_ms"]) for r in group]
    bm, cm = statistics.mean(b), statistics.mean(c)
    results[workload] = {"n_rows":len(group), "trial_ids":[r["trial"] for r in group], "baseline_mean_ms":bm, "candidate_mean_ms":cm, "candidate_minus_baseline_mean_ms":cm-bm, "latency_reduction_percent_from_means":100*(bm-cm)/bm, "speedup_ratio_from_means":bm/cm, "paired_candidate_minus_baseline_ms":[y-x for x,y in zip(b,c)], "paired_latency_reduction_percent":[100*(x-y)/x for x,y in zip(b,c)]}
b = [float(r["baseline_ms"]) for r in rows]; c = [float(r["candidate_ms"]) for r in rows]
results["pooled_descriptive_only"] = {"baseline_total_ms":sum(b),"candidate_total_ms":sum(c),"latency_reduction_percent":100*(sum(b)-sum(c))/sum(b),"note":"Not a prespecified deployment workload weighting or estimand."}
payload = {"input_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(INPUT.glob("*")) if p.is_file()},"results":results,"inference":"No CI, p-value, accuracy or reliability inference: invented fixtures, independent experimental units and sampling design unestablished."}
(OUTPUT / "calculation-results.json").write_text(json.dumps(payload,indent=2)+"\n")
print(json.dumps(payload,indent=2))
print("Python", platform.python_version())
