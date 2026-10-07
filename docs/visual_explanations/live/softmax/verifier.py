"""Independent high-precision arithmetic check for EXPL-SOFTMAX-001.

Uses standard-library Decimal, independently of the plotting implementation.
Run: python verifier.py
"""
from decimal import Decimal, getcontext
from pathlib import Path
import json

getcontext().prec = 50
root = Path(__file__).resolve().parent
logits = [Decimal(2), Decimal(1), Decimal(0)]
temperatures = [Decimal('0.5'), Decimal(1), Decimal(2)]
expected_labels = [
    ['86.68', '11.73', '1.59'],
    ['66.52', '24.47', '9.00'],
    ['50.65', '30.72', '18.63'],
]
rows = []
for temperature, expected in zip(temperatures, expected_labels):
    scaled = [z / temperature for z in logits]
    weights = [z.exp() for z in scaled]
    probabilities = [w / sum(weights) for w in weights]
    labels = [f'{p * 100:.2f}' for p in probabilities]
    normalized_error = abs(sum(probabilities) - 1)
    assert normalized_error < Decimal('1e-48')
    assert labels == expected
    assert probabilities[0] > probabilities[1] > probabilities[2]
    # Direct definition and stable-softmax construction independently agree.
    stable_weights = [(z - max(scaled)).exp() for z in scaled]
    stable_probabilities = [w / sum(stable_weights) for w in stable_weights]
    assert max(abs(a-b) for a, b in zip(probabilities, stable_probabilities)) < Decimal('1e-48')
    adjacent_odds = probabilities[0] / probabilities[1]
    assert abs(adjacent_odds - (Decimal(1)/temperature).exp()) < Decimal('1e-47')
    rows.append({
        'T': str(temperature),
        'scaled_logits': [str(z) for z in scaled],
        'probabilities_decimal_50_digits': [str(p) for p in probabilities],
        'percentage_labels': labels,
        'normalization_error': str(normalized_error),
        'adjacent_odds': str(adjacent_odds),
        'entropy_nats': str(-sum(p * p.ln() for p in probabilities)),
    })
assert all(Decimal(rows[i]['probabilities_decimal_50_digits'][0]) > Decimal(rows[i+1]['probabilities_decimal_50_digits'][0]) for i in range(2))
assert all(Decimal(rows[i]['entropy_nats']) < Decimal(rows[i+1]['entropy_nats']) for i in range(2))
result = {
    'explanation_id': 'EXPL-SOFTMAX-001',
    'input_version': 'v1',
    'definition': 'p_i(T)=exp(z_i/T)/sum_j(exp(z_j/T)), T>0',
    'data_kind': 'theoretical calculated teaching example',
    'method': 'Python standard library decimal, 50-digit precision',
    'external_sources': 'Not retrieved; no web requested by parent. Standard definition is explicit and claims are derived from it.',
    'numerical_checks': 'PASS',
    'checks': ['normalization to within 1e-48', 'correct two-decimal percentage labels', 'positive-T category order', 'stable-softmax equivalence', 'adjacent odds identity', 'maximum probability decreases for requested T values', 'entropy increases for requested T values'],
    'rounding_note': 'T=1 displayed percentages sum to 99.99%, while unrounded probabilities normalize to 1.',
    'rows': rows,
}
(root / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
