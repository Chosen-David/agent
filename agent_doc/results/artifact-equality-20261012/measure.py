"""Paired public-entry CPU comparison against a frozen git version."""
import hashlib
import json
import platform
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import time
import types

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from agent_runtime.artifact_context import compare_artifacts, restore_comparison

BASE = 'bd65a2348e32d8a70af9e003cbc309064363dd9e'
source = subprocess.check_output(['git', 'show', BASE + ':agent_runtime/artifact_context.py'], cwd=ROOT).decode()
baseline = types.ModuleType('agent_runtime._frozen_artifact_baseline')
baseline.__package__ = 'agent_runtime'
exec(compile(source, '<frozen-baseline>', 'exec'), baseline.__dict__)
samples = []
checks = 0
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory).resolve()
    def refs(old, new):
        out = []
        for name, text in (('a', old), ('b', new)):
            raw = text.encode()
            (root / name).write_bytes(raw)
            out.append({'path': name, 'sha256': hashlib.sha256(raw).hexdigest()})
        return out
    cases = ['', 'same\n', '取消\r\n保留预算\n', 'x\n' * 2048,
             'x\n' * 2049, 'x' * 65536, 'x' * 65537]
    pairs = [(s, s) for s in cases] + [('a\nb\n', 'a\nchanged\n'), ('', 'new')]
    for old, new in pairs:
        a, b = refs(old, new)
        for full in (False, True):
            for reuse in (False, True):
                for use_counter in (False, True):
                    wires = [[], []]
                    kwargs = dict(full=full, multi_edit=True, reuse_identical=reuse, max_chars=500000)
                    def counter(i):
                        return lambda wire: wires[i].append(wire) or len(wire)
                    before = baseline.compare_artifacts(root, a, b, **kwargs,
                                token_counter=counter(0) if use_counter else None)
                    after = compare_artifacts(root, a, b, **kwargs,
                                token_counter=counter(1) if use_counter else None)
                    assert before == after and wires[0] == wires[1]
                    assert restore_comparison(root, after, a, b) == (old, new)
                    checks += 1
    text = 'same recurring status line\n' * 2048
    a, b = refs(text, text)
    kwargs = dict(multi_edit=True, reuse_identical=True, max_chars=200000)
    baseline.compare_artifacts(root, a, b, **kwargs)
    compare_artifacts(root, a, b, **kwargs)
    for trial in range(7):
        times = {}
        order = [('baseline', baseline.compare_artifacts), ('candidate', compare_artifacts)]
        if trial % 2:
            order.reverse()
        for name, fn in order:
            start = time.perf_counter_ns()
            packet = fn(root, a, b, **kwargs)
            times[name] = (time.perf_counter_ns() - start) / 1e6
            assert packet['after']['representation'] == 'identical'
        samples.append(times)
b = statistics.median(s['baseline'] for s in samples)
c = statistics.median(s['candidate'] for s in samples)
out = dict(base=BASE, python=sys.version, platform=platform.platform(),
           code_sha256=hashlib.sha256((ROOT/'agent_runtime/artifact_context.py').read_bytes()).hexdigest(),
           baseline_code_sha256=hashlib.sha256(source.encode()).hexdigest(),
           workload_sha256=hashlib.sha256(text.encode()).hexdigest(),
           equivalence_checks=checks, paired_samples_ms=samples,
           baseline_median_ms=b, candidate_median_ms=c, reduction_fraction=1-c/b,
           scope='complete compare_artifacts CPU entry; synthetic identical repeated lines; no model/token/cash gain')
assert checks >= 20 and c <= .5*b
Path(__file__).with_name('measurement.json').write_text(json.dumps(out, indent=2)+'\n')
print(json.dumps(out, indent=2))
