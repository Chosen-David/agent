import hashlib,json,subprocess,sys,time
from pathlib import Path
D=Path(__file__).resolve().parent;R=D.parents[2];phase=sys.argv[1];py=sys.executable
cmds=[('catalog',[py,'-m','unittest','discover','-s','tests','-p','test_eval_catalog.py','-v']),('sync',[py,'scripts/sync_plugin_references.py']),('sync-check',[py,'scripts/sync_plugin_references.py','--check']),('links',[py,str(D/'verify_links.py')]),('full-tests',[py,'-m','unittest','discover','-s','tests','-v']),('reader-tests',[py,'-m','unittest','discover','-s','apps/paper-reader/tests','-v']),('diff-check',['git','diff','--check'])]
receipts=[]
for name,argv in cmds:
 t=time.monotonic();r=subprocess.run(argv,cwd=R,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);p=D/f'{phase}-{name}.log';p.write_text(r.stdout)
 receipts.append(dict(name=name,argv=argv,cwd=str(R),exit_code=r.returncode,seconds=time.monotonic()-t,log=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 (D/f'{phase}-commands.json').write_text(json.dumps(receipts,indent=2)+'\n');print(phase,name,r.returncode,flush=True)
sys.exit(any(x['exit_code'] for x in receipts))
