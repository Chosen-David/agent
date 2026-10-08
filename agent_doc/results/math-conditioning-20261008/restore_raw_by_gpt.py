"""Restore exact archived development case JSON; never overwrite differing files."""
import gzip
from pathlib import Path
base=Path(__file__).resolve().parent
for archive,names in [("raw_cases.json.gz",["validation_results_raw_cases.json","independent_results_raw_cases.json"]),("raw_cases_v2.json.gz",["validation_results_v2_raw_cases.json","independent_results_v2_raw_cases.json"])]:
    data=gzip.decompress((base/archive).read_bytes())
    for name in names:
        target=base/name
        if target.exists():
            if target.read_bytes()!=data:raise RuntimeError(f"preserve differing file: {target}")
        else:target.write_bytes(data)
print("Exact raw case copies available; no frozen summary/review modified.")
