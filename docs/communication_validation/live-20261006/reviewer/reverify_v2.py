"""Independent, fixed-input review; writes only reviewer-owned evidence."""
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
from agent_runtime.communication import Mailbox

root = Path(__file__).resolve().parents[1]
out = root / 'reviewer'
read = lambda path: json.loads((root / path).read_text())
write = lambda path, obj: (root / path).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
box = Mailbox(root / 'messages.sqlite', read('plan.json'), root)
request = read('request.json')
v1 = box.consume_handoff('reviewer', 1, request)
v2 = box.consume_handoff('reviewer', 3, request)
original = read('reviewer/review_v1.json')
data = read('input.json')
results = read('implementer/results_v2.json')
log = read('implementer/execution_v2.log')
report = (root / 'implementer/report_v2.md').read_text()
completed = subprocess.run([sys.executable, str(root / 'implementer/calculate_v2.py'), '--input', str(root / 'input.json'), '--output', str(out / 'recomputed_v2.json')], capture_output=True, text=True, check=True)
(out / 'rerun_v2.log').write_text(completed.stdout)
assert json.loads(completed.stdout) == results == log
verified = {'synthetic': True, 'paired': True, 'unit': 'ms', 'n_pairs': len(data['baseline']), 'sample_sd_ddof': 1, 'groups': {}}
for group in ('baseline', 'candidate'):
    xs = data[group]
    n = len(xs)
    mean = sum(xs) / n
    sum_squares = sum((x - mean) ** 2 for x in xs)
    sd = math.sqrt(sum_squares / (n - 1))
    assert results['n_' + group] == n == 6
    assert math.isclose(results[group + '_mean_ms'], mean, rel_tol=1e-12)
    assert math.isclose(results[group + '_sample_sd_ms'], sd, rel_tol=1e-12)
    assert results[group + '_sum_squared_deviations_ms2'] == sum_squares
    assert math.isclose(results[group + '_sample_variance_ms2'], sum_squares / (n - 1), rel_tol=1e-12)
    verified['groups'][group] = {'n': n, 'mean_ms': mean, 'sample_sd_ms': sd, 'sample_sd_ddof': 1, 'sum_squared_deviations_ms2': sum_squares}
ratio = verified['groups']['baseline']['mean_ms'] / verified['groups']['candidate']['mean_ms']
assert math.isclose(results['speedup_ratio_of_means'], ratio, rel_tol=1e-12)
assert results['sample_sd_ddof'] == 1
assert results['n_pairs'] == 6 and results['n_latency_values'] == 12
assert data['synthetic'] is results['synthetic'] is True
assert data['paired'] is results['paired'] is True
assert data['unit'] == results['unit'] == 'ms'
assert results['speedup_unit'] == 'dimensionless'
assert results['formulas']['sample_sd'] == 'sqrt(sum((x_i - mean(x))**2) / (n - 1))'
assert results['formulas']['speedup'] == 'mean(baseline_ms) / mean(candidate_ms)'
assert results['input_sha256'] == hashlib.sha256((root / 'input.json').read_bytes()).hexdigest()
assert all(s in report for s in ('ddof=1', '4.857983120596447 ms', '2.898275349237888 ms', '不是各配对比值的平均数', '不得由此声称真实系统收益', '不声称统计显著性'))
assert 'Synthetic data for communication validation only; not measured system performance.' in results['limitations']
verified.update({'input_version': 'synthetic-v1', 'input_sha256': results['input_sha256'], 'speedup_ratio_of_means': ratio, 'speedup_definition': 'mean(baseline_ms) / mean(candidate_ms)', 'speedup_unit': 'dimensionless', 'sample_sd_formula': 'sqrt(sum((x_i - mean(x))**2) / (n - 1))', 'limitations': ['Synthetic communication-validation data, not measured system performance; no real-system benefit follows.', 'Sample SD describes sample dispersion; no confidence interval or significance test has been performed.']})
write('reviewer/verified_results_v2.json', verified)
condition_evidence = [
    'New immutable event seq=3 consumed with complete producer handoff, trusted request and all SHA-256 checks passing; original seq=1 also successfully re-consumed, proving original v1 refs remain valid.',
    'Read original input, recomputed n/mean/squared deviations/SD independently in this reviewer script; reran producer code into reviewer/recomputed_v2.json; stdout equals producer results and execution log.',
    'Both groups have n=6; baseline s=sqrt(118/5)=4.857983120596447 ms, candidate s=sqrt(42/5)=2.898275349237888 ms. Code/results/report use ddof=1 and n-1.',
    'Speedup is ratio of means 102/89=1.146067415730337 dimensionless. Code/results/report explicitly preserve synthetic-only boundary; no measured benefit or significance assertion accepted.',
    'All original conditions passed; reviewer closes the original finding in this revision record. Original review_v1.json remains unchanged as historical evidence.'
]
review = {'schema_version': 1, 'run_id': root.name, 'input_version': 'synthetic-v1', 'reviewer': 'reviewer', 'source_seq': 3, 'source_event_id': 'EXP-1-implementer-dispersion-v2', 'decision': 'pass', 'original_v1_references_valid': True, 'producer_rerun_matches_results_and_log': True, 'relative_tolerance': 1e-12, 'findings': [{'finding_id': original['findings'][0]['finding_id'], 'status': 'closed', 'closed_by': 'reviewer', 'original_review': 'reviewer/review_v1.json', 'reverification': [{'condition': c, 'status': 'pass', 'evidence': e} for c, e in zip(original['findings'][0]['reverification_conditions'], condition_evidence)]}], 'limitations': verified['limitations']}
write('reviewer/review_v2.json', review)
print(json.dumps({'decision': review['decision'], 'original_v1_references_valid': True, 'finding': review['findings'][0]['finding_id'], 'status': 'closed', 'verified_results': verified}, ensure_ascii=False, indent=2))
