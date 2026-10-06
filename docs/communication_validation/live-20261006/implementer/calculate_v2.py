#!/usr/bin/env python3
"""Compute descriptive statistics from the supplied paired synthetic latency input."""
import argparse
from fractions import Fraction
from math import sqrt
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--input', type=Path, default=Path(__file__).resolve().parents[1] / 'input.json')
parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parent / 'results_v2.json')
args = parser.parse_args()
raw = args.input.read_bytes()
data = json.loads(raw)
assert data['synthetic'] is True and data['paired'] is True
assert data['unit'] == 'ms'
baseline, candidate = data['baseline'], data['candidate']
assert len(baseline) == len(candidate) and len(baseline) > 0
assert all(isinstance(v, (int, float)) and v > 0 for v in baseline + candidate)
b = sum(map(Fraction, baseline)) / len(baseline)
c = sum(map(Fraction, candidate)) / len(candidate)
s = b / c
b_ss = sum((Fraction(x) - b) ** 2 for x in baseline)
c_ss = sum((Fraction(x) - c) ** 2 for x in candidate)
b_var = b_ss / (len(baseline) - 1)
c_var = c_ss / (len(candidate) - 1)
result = {
    'run_id': 'communication-live-20261006T1432',
    'input_version': 'synthetic-v1',
    'input_sha256': hashlib.sha256(raw).hexdigest(),
    'synthetic': True,
    'paired': True,
    'unit': 'ms',
    'n_baseline': len(baseline),
    'n_candidate': len(candidate),
    'n_pairs': len(baseline),
    'n_latency_values': len(baseline) + len(candidate),
    'baseline_sum_ms': sum(baseline),
    'candidate_sum_ms': sum(candidate),
    'baseline_mean_ms': float(b),
    'candidate_mean_ms': float(c),
    'speedup_ratio_of_means': float(s),
    'baseline_sample_sd_ms': sqrt(b_var),
    'candidate_sample_sd_ms': sqrt(c_var),
    'baseline_sum_squared_deviations_ms2': float(b_ss),
    'candidate_sum_squared_deviations_ms2': float(c_ss),
    'baseline_sample_variance_ms2': float(b_var),
    'candidate_sample_variance_ms2': float(c_var),
    'sample_sd_ddof': 1,
    'finding_id': 'EXP-1-SAMPLE-DISPERSION-001',
    'revision_status': 'evidence supplied; awaiting reviewer reverification',
    'exact': {'baseline_mean_ms': str(b), 'candidate_mean_ms': str(c), 'speedup': str(s)},
    'formulas': {'mean': 'sum(latency_i) / n', 'speedup': 'mean(baseline_ms) / mean(candidate_ms)', 'sample_sd': 'sqrt(sum((x_i - mean(x))**2) / (n - 1))'},
    'speedup_unit': 'dimensionless',
    'limitations': [
        'Synthetic data for communication validation only; not measured system performance.',
        'Descriptive sample SD only; no confidence interval, inferential claim, or statistical significance claim.',
        'Ratio of group means, not mean of per-pair ratios.'
    ]
}
args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False, indent=2))
