"""Public finite checks, not a general proof or an unseen model evaluation.

Run from repository root, optionally provide output directory for independent rerun.
"""
import json
import platform
from pathlib import Path
import sys
import time
import numpy as np

HERE = Path(__file__).resolve().parent
cfg = json.loads((HERE / 'config.json').read_text())
out = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE
out.mkdir(parents=True, exist_ok=True)
started = time.perf_counter()
rng = np.random.default_rng(cfg['seed'])
records = []

def softmax(x):
    x = np.asarray(x, dtype=float)
    if x.ndim != 1 or not len(x) or not np.isfinite(x).all():
        raise ValueError('nonempty finite logits required')
    z = np.exp(x - x.max())
    return z / z.sum()

def add(name, observed, bound, equality=False):
    observed, bound = float(observed), float(bound)
    ok = np.isfinite([observed, bound]).all() and observed <= bound + cfg['tolerance']
    if equality:
        ok = ok and abs(observed - bound) <= cfg['tolerance']
    records.append({'id': name, 'observed': observed, 'bound': bound,
                    'equality': equality, 'pass': bool(ok)})
    assert ok, records[-1]

for case in range(cfg['random_cases']):
    n = int(rng.integers(2, 15))
    s = rng.normal(size=n) * 4
    e = rng.normal(size=n) * 3
    v = rng.normal(size=(n, 4))
    W = rng.normal(size=(4, 3))
    u = v @ W
    a, b = softmax(s), softmax(s+e)
    D = np.linalg.norm(u[:, None] - u[None, :], axis=-1).max()
    tv = abs(a-b).sum()/2
    add(f'{case}-tv', tv, np.tanh(np.ptp(e)/4))
    add(f'{case}-output', np.linalg.norm((a-b)@u), D*tv)
    ids = rng.choice(n, size=int(rng.integers(1, n+1)), replace=False)
    p = a[ids].sum()
    ac = a[ids]/p
    bc = softmax((s+e)[ids])
    qv = v[ids] + rng.normal(size=(len(ids), 4)) * .01
    DS = np.linalg.norm(u[ids, None] - u[None, ids], axis=-1).max()
    bound = D*(1-p) + DS*np.tanh(np.ptp(e[ids])/4) + bc@np.linalg.norm((v[ids]-qv)@W, axis=1)
    add(f'{case}-combined', np.linalg.norm(a@u-bc@(qv@W)), bound)
    restricted = np.zeros(n)
    restricted[ids] = ac
    add(f'{case}-prune-tv', abs(a-restricted).sum()/2, 1-p, True)

for w in [0, 1e-8, .1, 2, 10, 40, 800]:
    a, b = softmax([0, w/2]), softmax([w, w/2])
    add(f'sharp-{w}', abs(a-b).sum()/2, np.tanh(w/4), True)
add('constant-shift', np.linalg.norm(softmax([1, 2, 3])-softmax([1001,1002,1003])), 0, True)
a = np.array([.45,.30,.20,.05]); v = np.array([0.,1.,0.,-6.])
add('full-cancellation', abs(a@v), 0, True)
add('top-mass-error', abs(a[[0,1]]@v[[0,1]]/a[[0,1]].sum()-a@v), .4, True)
add('lower-overlap-error', abs(a[[0,2]]@v[[0,2]]/a[[0,2]].sum()-a@v), 0, True)
add('force-output-N', abs((softmax([0,1])-softmax([2,1]))@np.array([0.,3.])), 3*np.tanh(.5), True)
add('large-logits', abs(softmax([10000,10001]).sum()-1), 0, True)
for name, x in [('empty',[]),('inf',[0,np.inf]),('nan',[np.nan])]:
    try:
        softmax(x)
    except ValueError:
        add('reject-'+name, 1, 1, True)
    else:
        raise AssertionError('premise not rejected')
raw = {'config': cfg, 'records': records}
(out/'raw.json').write_text(json.dumps(raw, indent=2, allow_nan=False)+'\n')
summary = {'checks': len(records), 'passed': sum(x['pass'] for x in records),
           'seconds': time.perf_counter()-started, 'claim': cfg['scope']}
(out/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
(out/'environment.json').write_text(json.dumps({'python':sys.version, 'numpy':np.__version__,
    'platform':platform.platform(), 'processor':platform.processor(), 'device':'CPU; no accelerator measured'}, indent=2)+'\n')
print(json.dumps(summary))
