"""Bounded v2 remeasurement and isolated-delta regression in owned scratch."""
import json
import os
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[3];RUN=Path(__file__).resolve().parent
temp=RUN/'tmp';temp.mkdir(exist_ok=True)
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONIOENCODING='utf-8',TEMP=str(temp),TMP=str(temp),TMPDIR=str(temp),
         PYTHONPATH=os.pathsep.join([str(ROOT),str(ROOT/'tests'),str(ROOT/'.agent-runs/memory-index96-deps')]),
         TIKTOKEN_CACHE_DIR=str(ROOT/'.agent-runs/memory-index96-token-cache'))
commands=[
 ('rerun.log',[sys.executable,'-B','-X','utf8','agent_doc/results/memory-pack-20261021/measure.py','--output',str(RUN/'rerun-v2')]),
 ('targeted.log',[sys.executable,'-B','-X','utf8','-m','unittest','test_dispatch_context','test_memory_tables.MemoryTableTests','test_handoff_encoding','-v'])]
records=[]
for name,command in commands:
    with (RUN/name).open('xb') as stream:result=subprocess.run(command,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=300)
    records.append({'command':command,'cwd':str(ROOT),'log':name,'exit_code':result.returncode})
    (RUN/'runs.json').write_text(json.dumps({'environment':{k:env[k] for k in ('PYTHONUTF8','PYTHONIOENCODING','PYTHONDONTWRITEBYTECODE','PYTHONPATH','TEMP','TIKTOKEN_CACHE_DIR')},'commands':records},indent=2),encoding='utf-8')
    print(name,result.returncode,flush=True)
sys.exit(int(any(r['exit_code'] for r in records)))
