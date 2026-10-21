import hashlib, json, math, os, platform, statistics, subprocess, sys, time
from pathlib import Path
P=Path(__file__).resolve().parents[1]
ROOT=P.parents[1]
OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((P/'manifest.json').read_text())
initial={}
for category,base in [('artifacts',P),('dependencies',ROOT)]:
    for name,h in m[category].items():
        actual=sha(base/name)
        assert actual==h,(name,actual,h)
        initial[str((base/name).resolve())]=actual
(OUT/'verified-original-hashes.json').write_text(json.dumps(initial,indent=2)+'\n')
for mode in [[],['-O']]:
    r=subprocess.run([sys.executable,*mode,'-m','unittest','tests.test_discover_backends','tests.test_backend_registry','-v'],cwd=ROOT,capture_output=True,timeout=30)
    name='tests-O' if mode else 'tests'
    (OUT/(name+'.stdout')).write_bytes(r.stdout)
    (OUT/(name+'.stderr')).write_bytes(r.stderr)
    assert r.returncode==0,(name,r.stderr.decode())
WRAPPER="import sys;from pathlib import Path;s=Path(sys.argv.pop(1)).read_bytes();p=sys.argv.pop(1);sys.argv[0]=p;exec(compile(s,p,'exec'),{'__name__':'__main__','__file__':p})"
rows=[]
for i in range(6):
    tag='warmup' if i==0 else f'pair{i}'
    runs={}
    for label in (['baseline','candidate'] if i%2==0 else ['candidate','baseline']):
        t=time.perf_counter()
        r=subprocess.run([sys.executable,'-c',WRAPPER,str(P/(label+'.py')),str(ROOT/'scripts/discover_backends.py')],cwd=ROOT,capture_output=True,timeout=20)
        elapsed=time.perf_counter()-t
        (OUT/f'{tag}-{label}.stdout').write_bytes(r.stdout)
        (OUT/f'{tag}-{label}.stderr').write_bytes(r.stderr)
        assert r.returncode==0
        assert math.isfinite(elapsed) and elapsed>0
        runs[label]={'wall_seconds':elapsed,'stdout_sha256':hashlib.sha256(r.stdout).hexdigest(),'value':json.loads(r.stdout),'exit_code':r.returncode,'stderr_bytes':len(r.stderr)}
    assert runs['baseline']['value']==runs['candidate']['value']
    for value in runs.values():value.pop('value')
    rows.append({'tag':tag,'runs':runs})
    (OUT/'samples.json').write_text(json.dumps(rows,indent=2)+'\n')
measured=rows[1:]
b=[r['runs']['baseline']['wall_seconds'] for r in measured]
c=[r['runs']['candidate']['wall_seconds'] for r in measured]
reductions=[1-y/x for x,y in zip(b,c)]
assert min(reductions)>=.05
assert 1-statistics.median(c)/statistics.median(b)>=.1
assert all(sha(Path(p))==h for p,h in initial.items()),'evidence changed during review'
result={'baseline_seconds':b,'candidate_seconds':c,'baseline_median_seconds':statistics.median(b),'candidate_median_seconds':statistics.median(c),'pair_reductions':reductions,'median_reduction':1-statistics.median(c)/statistics.median(b),'environment':{'python':sys.version,'platform':platform.platform()},'frozen_hashes_unchanged':True,'tests':'13 ordinary and 13 -O passed','output_equivalence':'all warmup and five pairs exact parsed JSON equality'}
(OUT/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
