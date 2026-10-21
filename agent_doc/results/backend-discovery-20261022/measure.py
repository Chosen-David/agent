import hashlib,json,os,platform,subprocess,sys,time
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
SCRIPT=ROOT/'scripts/discover_backends.py'
WRAPPER="import sys;from pathlib import Path;s=Path(sys.argv.pop(1)).read_bytes();p=sys.argv.pop(1);sys.argv[0]=p;exec(compile(s,p,'exec'),{'__name__':'__main__','__file__':p})"

def once(label, tag):
    t=time.perf_counter()
    r=subprocess.run([sys.executable,'-c',WRAPPER,str(P/(label+'.py')),str(SCRIPT)],cwd=ROOT,capture_output=True,timeout=20)
    elapsed=time.perf_counter()-t
    (P/(tag+'-'+label+'.stdout')).write_bytes(r.stdout)
    (P/(tag+'-'+label+'.stderr')).write_bytes(r.stderr)
    if r.returncode:raise RuntimeError((tag,label,r.returncode))
    return {'label':label,'wall_seconds':elapsed,'stdout_sha256':hashlib.sha256(r.stdout).hexdigest(),'value':json.loads(r.stdout)}

samples=[]
for i in range(6):
    tag='warmup' if i==0 else 'pair'+str(i)
    order=['baseline','candidate'] if i%2==0 else ['candidate','baseline']
    pair=[once(label,tag) for label in order]
    if pair[0]['value']!=pair[1]['value']:raise RuntimeError('outputs differ '+tag)
    for v in pair:v.pop('value')
    samples.append({'tag':tag,'runs':pair})
    (P/'samples.json').write_text(json.dumps(samples,indent=2)+'\n')
print('complete: separate warmup plus five alternating pairs; exact full JSON equality')
