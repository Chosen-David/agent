#!/usr/bin/env python3
"""Compute descriptive statistics from the supplied paired synthetic latency input."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--input', type=Path, default=Path(__file__).resolve().parents[1] / 'input.json')
parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parent / 'results.json')
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
    'exact': {'baseline_mean_ms': str(b), 'candidate_mean_ms': str(c), 'speedup': str(s)},
    'formulas': {'mean': 'sum(latency_i) / n', 'speedup': 'mean(baseline_ms) / mean(candidate_ms)'},
    'speedup_unit': 'dimensionless',
    'limitations': [
        'Synthetic data for communication validation only; not measured system performance.',
        'Descriptive statistics only; no uncertainty estimate or inferential claim at this stage.',
        'Ratio of group means, not mean of per-pair ratios.'
    ]
}
args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False, indent=2))
