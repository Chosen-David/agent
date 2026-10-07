from pathlib import Path
import csv,json,statistics,hashlib
base=Path(__file__).resolve().parents[3]
rows=list(csv.DictReader((base/'inputs/measurements.csv').open()))
result={'input_sha256':hashlib.sha256((base/'inputs/measurements.csv').read_bytes()).hexdigest(),'descriptive_only':True,'groups':{},'paired_rows':[]}
for r in rows:
 b=float(r['baseline_ms']); c=float(r['candidate_ms'])
 result['paired_rows'].append({'workload':r['workload'],'trial':r['trial'],'baseline_ms':b,'candidate_ms':c,'candidate_minus_baseline_ms':c-b,'time_reduction_percent':100*(b-c)/b,'speedup_ratio':b/c})
for w in sorted(set(r['workload'] for r in rows)):
 rr=[r for r in result['paired_rows'] if r['workload']==w]
 b=statistics.mean(r['baseline_ms'] for r in rr); c=statistics.mean(r['candidate_ms'] for r in rr)
 result['groups'][w]={'n_rows':len(rr),'baseline_mean_ms':b,'candidate_mean_ms':c,'candidate_minus_baseline_ms':c-b,'time_reduction_percent':100*(b-c)/b,'speedup_ratio':b/c}
b=sum(r['baseline_ms'] for r in result['paired_rows']); c=sum(r['candidate_ms'] for r in result['paired_rows'])
result['equal_row_totals_not_deployment_estimate']={'baseline_ms':b,'candidate_ms':c,'time_reduction_percent':100*(b-c)/b,'speedup_ratio':b/c}
print(json.dumps(result,indent=2))
