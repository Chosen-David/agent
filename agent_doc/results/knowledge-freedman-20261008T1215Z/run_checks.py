"""Record required checks and raw receipts; failed gates remain failures."""
import hashlib,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
phase=sys.argv[1]
py=sys.executable
cmds=[('validate',[py,'-m','agent_runtime.knowledge','--root','knowledge','validate']),('sync',[py,'scripts/sync_plugin_references.py']),('sync-check',[py,'scripts/sync_plugin_references.py','--check']),('index',[py,'-m','agent_runtime.knowledge','--root','knowledge','index','--db','.knowledge-cache/search.sqlite'])]
for name,fixture in [('original','queries'),('round2','round2-queries'),('morphology','morphology-queries')]:
    extra=['--require-backends','sqlite'] if name=='morphology' else ['--accept-context']
    cmds.append((name,[py,'scripts/eval_knowledge.py','--cases',f'evals/knowledge/{fixture}.json',*extra,'--output',str(OUT/f'{phase}-{name}.json')]))
    if name!='morphology':
        cmds.append((name+'-context8',[py,'scripts/eval_knowledge.py','--cases',f'evals/knowledge/{fixture}.json',*extra,'--context-limit','8','--output',str(OUT/f'{phase}-{name}-context8.json')]))
if '--quick' not in sys.argv:
    cmds += [('full-tests',[py,'-m','unittest','discover','-s','tests','-v']),('reader-tests',[py,'-m','unittest','discover','-s','apps/paper-reader/tests','-v'])]
cmds.append(('diff-check',['git','diff','--check']))
receipts=[]
for name,argv in cmds:
    start=time.time();r=subprocess.run(argv,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    log=OUT/f'{phase}-{name}.log';log.write_text(r.stdout)
    receipts.append(dict(name=name,argv=argv,exit_code=r.returncode,seconds=time.time()-start,log=log.name,sha256=hashlib.sha256(log.read_bytes()).hexdigest()))
    (OUT/f'{phase}-commands.json').write_text(json.dumps(receipts,indent=2)+'\n')
    print(phase,name,r.returncode,flush=True)
