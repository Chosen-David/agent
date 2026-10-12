"""Paired public-entry measurement for the unique single-splice guard."""
import hashlib
import json
import platform
from pathlib import Path
import random
import statistics
import subprocess
import sys
import tempfile
import time
import types

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
import agent_runtime.artifact_context as candidate

BASE = '71496c7b1f42b94616343683c7671b6a0e6e8a3b'
source = subprocess.check_output(
    ['git', 'show', BASE + ':agent_runtime/artifact_context.py'], cwd=ROOT
).decode()
baseline = types.ModuleType('agent_runtime._unique_splice_baseline')
baseline.__package__ = 'agent_runtime'
exec(compile(source, '<frozen-unique-splice-baseline>', 'exec'), baseline.__dict__)

curated = [
    ('', ''), ('', 'new'), ('old', ''), ('old', 'new'),
    ('a\r\nb\n', 'a\r\n新\n'),
    ('head\nbody\ntail\n', 'HEAD\nbody\ntail\n'),
    ('head\nbody\ntail\n', 'head\nbody\nTAIL\n'),
    ('head\nbody\ntail\n', 'head\ninsert\nbody\ntail\n'),
    ('head\nbody\ntail\n', 'head\ntail\n'),
    ('🙂\r\n甲\n乙', '🙂\r\n龙\n乙'),
    ('x\n' * 2048, 'x\n' * 1024 + 'y\n' + 'x\n' * 1023),
    ('x\n' * 2049, 'x\n' * 1024 + 'y\n' + 'x\n' * 1024),
    ('x' * 65536, 'y' + 'x' * 65535),
    ('x' * 65537, 'y' + 'x' * 65536),
    ('same\n' * 80, 'same\n' * 40 + 'different\n' + 'same\n' * 39),
    ('a\nb\na\nb\n' * 40, 'a\nb\na\nQ\n' + 'a\nb\na\nb\n' * 39),
]
rng = random.Random(190823)
alphabet = ['', 'a\n', 'b\n', 'same\n', '\r\n', '甲\n', '🙂\r\n']
random_cases = []
for _ in range(3000):
    old_lines = [rng.choice(alphabet) for _ in range(rng.randrange(0, 129))]
    new_lines = old_lines[:]
    for _ in range(rng.randrange(1, 7)):
        at = rng.randrange(len(new_lines) + 1)
        delete = rng.randrange(0, min(6, len(new_lines) - at) + 1)
        new_lines[at:at + delete] = [
            rng.choice(alphabet) for _ in range(rng.randrange(0, 6))
        ]
    random_cases.append((''.join(old_lines), ''.join(new_lines)))
cases = curated + random_cases

checks = 0
timings = []
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory).resolve()

    def refs(old, new):
        result = []
        for name, text in (('before', old), ('after', new)):
            raw = text.encode()
            (root / name).write_bytes(raw)
            result.append({'path': name, 'sha256': hashlib.sha256(raw).hexdigest()})
        return result

    for old, new in cases:
        before_ref, after_ref = refs(old, new)
        for counted in (False, True):
            kwargs = dict(multi_edit=True, reuse_identical=True, max_chars=500000)
            if counted:
                kwargs['token_counter'] = lambda wire: len(wire.encode())
            old_packet = baseline.compare_artifacts(root, before_ref, after_ref, **kwargs)
            new_packet = candidate.compare_artifacts(root, before_ref, after_ref, **kwargs)
            assert old_packet == new_packet
            assert candidate.restore_comparison(root, new_packet, before_ref, after_ref) == (old, new)
            checks += 1

    old = 'same recurring status line\n' * 1024 + 'Status: old\n' + 'same recurring status line\n' * 1023
    new = 'same recurring status line\n' * 1024 + 'Status: new\n' + 'same recurring status line\n' * 1023
    before_ref, after_ref = refs(old, new)
    kwargs = dict(multi_edit=True, max_chars=500000)
    baseline.compare_artifacts(root, before_ref, after_ref, **kwargs)
    candidate.compare_artifacts(root, before_ref, after_ref, **kwargs)
    for trial in range(7):
        row = {}
        order = [('baseline', baseline.compare_artifacts),
                 ('candidate', candidate.compare_artifacts)]
        if trial % 2:
            order.reverse()
        for name, function in order:
            started = time.perf_counter_ns()
            packet = function(root, before_ref, after_ref, **kwargs)
            row[name] = (time.perf_counter_ns() - started) / 1e6
            assert candidate.restore_comparison(root, packet, before_ref, after_ref) == (old, new)
        timings.append(row)

baseline_median = statistics.median(row['baseline'] for row in timings)
candidate_median = statistics.median(row['candidate'] for row in timings)
result = {
    'schema_version': 'artifact-unique-splice-measurement/v1',
    'baseline': BASE,
    'python': sys.version,
    'platform': platform.platform(),
    'candidate_code_sha256': hashlib.sha256(
        (ROOT / 'agent_runtime/artifact_context.py').read_bytes()
    ).hexdigest(),
    'baseline_code_sha256': hashlib.sha256(source.encode()).hexdigest(),
    'workload_sha256': hashlib.sha256((old + '\0' + new).encode()).hexdigest(),
    'case_seed': 190823,
    'curated_cases': len(curated),
    'random_cases': len(random_cases),
    'complete_entry_checks': checks,
    'packet_mismatches': 0,
    'paired_samples_ms': timings,
    'baseline_median_ms': baseline_median,
    'candidate_median_ms': candidate_median,
    'reduction_fraction': 1 - candidate_median / baseline_median,
    'scope': ('complete compare_artifacts CPU byte-selection entry; synthetic '
              'unique localized line; no token-counter, model, cash, GPU, or '
              'end-to-end gain'),
}
assert checks == 6032
assert candidate_median <= 0.5 * baseline_median
(OUT / 'measurement.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
