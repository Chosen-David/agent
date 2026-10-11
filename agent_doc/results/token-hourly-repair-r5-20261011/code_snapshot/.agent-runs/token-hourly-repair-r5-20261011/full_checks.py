"""Independent full-suite host on an exact isolated source snapshot, no model."""
import hashlib,json,os,platform,subprocess,sys,tempfile,time
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def full_suite(root,results,inventory):
    assert os.name=='posix'
    cache=Path(tempfile.mkdtemp(prefix='agent-hourly-full-'))
    checkout=cache/'checkout';venv=cache/'venv'
    env=dict(os.environ,PYTHONUTF8='1',PYTHONWARNINGS='ignore::ResourceWarning')
    log=results/'independent-setup.log'
    with log.open('wb') as stream:
        for command in ([sys.executable,'-m','venv',str(venv)],
                        [str(venv/'bin/python'),'-m','pip','install','pymupdf','numpy'],
                        ['git','clone','--no-local','--config','core.autocrlf=true',str(root),str(checkout)]):
            subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,env=env,check=True,timeout=120)
    for row in inventory['files']:
        source=root/row['path'];assert sha(source)==row['sha256']
        target=checkout/row['path'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
        assert sha(target)==row['sha256']
    command=[str(venv/'bin/python'),'-m','unittest','discover','-s','tests','-v']
    with (results/'independent-tests.log').open('wb') as stream:
        p=subprocess.run(command,cwd=checkout,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=600)
    packages=subprocess.check_output([str(venv/'bin/python'),'-m','pip','freeze'],env=env).decode()
    value={'actor':'independent-host','pid':os.getpid(),'platform':platform.platform(),'python':sys.version,
           'command':command,'checkout':str(checkout),'cache':str(cache),'source_revision':inventory['revision'],
           'source_overlay':inventory['files'],'packages':packages,'returncode':p.returncode}
    (results/'independent-environment.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    assert p.returncode==0,(results/'independent-tests.log').read_text()[-2500:]
    for row in inventory['files']:assert sha(root/row['path'])==sha(checkout/row['path'])==row['sha256']
