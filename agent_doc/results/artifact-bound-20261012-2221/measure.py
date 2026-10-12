"""Frozen-baseline public-entry parity and paired timing; emit raw JSON."""
import hashlib
import itertools
import json
from pathlib import Path
import platform
import random
import statistics
import subprocess
import sys
import tempfile
import time
import types

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
import agent_runtime.artifact_context as candidate
BASE = 'f8c92dc15bd948f0b50f748991cac782a913af0a'
source = subprocess.check_output(['git', 'show', BASE + ':agent_runtime/artifact_context.py'], cwd=ROOT)
baseline = types.ModuleType('agent_runtime._bound_baseline')
baseline.__package__ = 'agent_runtime'
exec(compile(source, '<frozen-baseline>', 'exec'), baseline.__dict__)

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

rng = random.Random(2221)
words = ['', 'a\n', 'b\n', '\r\n', '甲\n', '🙂\r\n']
small = [''.join(x) for n in range(4) for x in itertools.product(('a\n', 'b\n'), repeat=n)]
cases = list(itertools.product(small, repeat=2))
for _ in range(1000):
    old = [rng.choice(words) for _ in range(rng.randrange(65))]
    new = old[:]
    for _ in range(rng.randrange(1, 5)):
        at = rng.randrange(len(new)+1)
        new[at:at+rng.randrange(5)] = [rng.choice(words) for _ in range(rng.randrange(5))]
    cases.append((''.join(old), ''.join(new)))
cases += [('x\n'*2048, 'x\n'*2046), ('x\n'*2049, 'x\n'*2047),
          ('x'*65536, 'y'+'x'*65535), ('x'*65537, 'y'+'x'*65536)]
checks = 0
samples = []
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory).resolve()
    def refs(old, new):
        result = []
        for name, text in (('old', old), ('new', new)):
            raw = text.encode()
            (root/name).write_bytes(raw)
            result.append({'path':name, 'sha256':hashlib.sha256(raw).hexdigest()})
        return result
    for old, new in cases:
        a,b = refs(old,new)
        for counter in (None, lambda wire: len(wire.encode()),
                        lambda wire: 0 if '"representation":"edits"' in wire else 1):
            kw = dict(multi_edit=True, reuse_identical=True, max_chars=500000, token_counter=counter)
            expected = baseline.compare_artifacts(root,a,b,**kw)
            actual = candidate.compare_artifacts(root,a,b,**kw)
            require(expected == actual, 'packet mismatch')
            require(candidate.restore_comparison(root,actual,a,b) == (old,new), 'restore mismatch')
            checks += 1
    old,new = 'x\n'*2048, 'x\n'*2046
    a,b = refs(old,new)
    kw = dict(multi_edit=True,max_chars=500000)
    for mod in (baseline,candidate):
        mod.compare_artifacts(root,a,b,**kw)
    for trial in range(7):
        order = [('baseline',baseline),('candidate',candidate)]
        if trial%2:
            order.reverse()
        row = {}
        packets = []
        for name,mod in order:
            t = time.perf_counter_ns()
            packet = mod.compare_artifacts(root,a,b,**kw)
            row[name] = (time.perf_counter_ns()-t)/1e6
            packets.append(packet)
        require(packets[0] == packets[1], 'timed packet mismatch')
        samples.append(row)
bm = statistics.median(r['baseline'] for r in samples)
cm = statistics.median(r['candidate'] for r in samples)
require(cm <= .5*bm, 'performance threshold failed')
print(json.dumps({'baseline':BASE, 'baseline_sha256':hashlib.sha256(source).hexdigest(),
    'candidate_sha256':hashlib.sha256((ROOT/'agent_runtime/artifact_context.py').read_bytes()).hexdigest(),
    'workload_sha256':hashlib.sha256((old+'\0'+new).encode()).hexdigest(),
    'seed':2221,'cases':len(cases),'checks':checks,'packet_mismatches':0,
    'python':sys.version,'platform':platform.platform(),'processor':platform.processor(),
    'paired_samples_ms':samples,'baseline_median_ms':bm,'candidate_median_ms':cm,
    'reduction_fraction':1-cm/bm},indent=2))
