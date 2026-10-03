"""Analyze supplied data only; this script performs no performance timing."""
import csv
import json
from pathlib import Path

source = Path(__file__).resolve().parent.parent / "inputs" / "measurements.csv"
rows = []
with source.open(newline="") as handle:
    for row in csv.DictReader(handle):
        baseline = float(row["baseline_ms"])
        candidate = float(row["candidate_ms"])
        rows.append({**row, "baseline_ms": baseline, "candidate_ms": candidate,
                     "speedup": baseline / candidate if candidate > 0 else None,
                     "latency_reduction_pct": 100 * (baseline - candidate) / baseline
                     if baseline > 0 else None})
e2e = [row for row in rows if row["scope"] == "end_to_end"]
baseline = sum(row["baseline_ms"] for row in e2e)
candidate = sum(row["candidate_ms"] for row in e2e)
print(json.dumps({"source": str(source), "rows": rows,
                  "conditional_one_of_each_end_to_end": {
                      "baseline_ms": baseline, "candidate_ms": candidate,
                      "speedup": baseline / candidate,
                      "latency_reduction_pct": 100 * (baseline - candidate) / baseline}},
                 indent=2))
