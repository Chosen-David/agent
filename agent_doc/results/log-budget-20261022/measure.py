import hashlib, json, os, subprocess, sys, time, types
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
ENCODINGS=('lines','chunks','runs')

def load(path):
    module=types.ModuleType('agent_runtime._frozen_log_budget')
    module.__package__='agent_runtime'
    module.__file__=str(ROOT/'agent_runtime/log_context.py')
    sys.path.insert(0,str(ROOT))
    exec(compile(path.read_bytes(),module.__file__,'exec'),module.__dict__)
    observer=types.ModuleType('agent_runtime._frozen_observer')
    observer.__package__='agent_runtime'
    observer_path=P/(path.stem+'-observer.py')
    exec(compile(observer_path.read_bytes(),str(observer_path),'exec'),observer.__dict__)
    module.read_bound=observer.read_bound
    return module

if len(sys.argv)>1 and sys.argv[1]=='child':
    source,encoding,traced=sys.argv[2:]
    module=load(P/source)
    payload=(P/'job.log').read_bytes();digest=hashlib.sha256(payload).hexdigest()
    if traced=='yes':
        import tracemalloc
        tracemalloc.start()
    start=time.perf_counter()
    try:
        module.log_view(P,'job.log',digest,needles=['ERROR'],head=2,tail=2,context=1,max_chars=1000,encoding=encoding)
    except ValueError as exc:
        error=str(exc)
    else:
        raise AssertionError('expected complete-context budget rejection')
    elapsed=time.perf_counter()-start
    peak=tracemalloc.get_traced_memory()[1] if traced=='yes' else None
    print(json.dumps({'source':source,'encoding':encoding,'traced':traced,'seconds':elapsed,'python_peak_bytes':peak,'error':error,'input_sha256':digest}))
    raise SystemExit(0)

def child(source,encoding,traced=False):
    p=subprocess.run([sys.executable,str(Path(__file__).resolve()),'child',source,encoding,'yes' if traced else 'no'],capture_output=True,text=True,timeout=30)
    if p.returncode:raise RuntimeError(p.stderr)
    return json.loads(p.stdout)

(P/'job.log').write_bytes(b'ERROR\n'*50000)
records=[]
for encoding in ENCODINGS:
    for source in ('baseline.py','candidate.py'):
        records.append(dict(phase='warmup',**child(source,encoding)))
    for pair in range(5):
        order=('baseline.py','candidate.py') if pair%2==0 else ('candidate.py','baseline.py')
        for source in order:
            records.append(dict(phase='measured',pair=pair,**child(source,encoding)))
    for source in ('baseline.py','candidate.py'):
        records.append(dict(phase='traced-diagnostic',**child(source,encoding,True)))
(P/'raw.json').write_text(json.dumps(records,indent=2)+'\n')
(P/'environment.json').write_text(json.dumps({'python':sys.version,'platform':sys.platform,'clock':time.get_clock_info('perf_counter')._asdict() if hasattr(time.get_clock_info('perf_counter'),'_asdict') else str(time.get_clock_info('perf_counter')),'timing_scope':'full log_view call; source load and subprocess startup excluded; traced time not part of comparison','hashes':{name:hashlib.sha256((P/name).read_bytes()).hexdigest() for name in ('baseline.py','candidate.py','baseline-observer.py','candidate-observer.py','measure.py','job.log','plan.md','validation-plan.json','contract.json')}},indent=2)+'\n')
print('Raw pending observations saved; no acceptance assigned.')
