"""Capture real UTF-8 process bytes, including child Python encoding policy."""
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[3]
RUN=Path(__file__).resolve().parent
env={**os.environ,'PYTHONUTF8':'1','PYTHONIOENCODING':'utf-8',
     'PYTHONPATH':str(ROOT/'.agent-runs/memory-index96-deps')+os.pathsep+str(ROOT/'tests'),
     'TIKTOKEN_CACHE_DIR':str(ROOT/'.agent-runs/memory-index96-token-cache')}
commands=[('targeted-tests.txt',[sys.executable,'-X','utf8','-m','unittest',
    'test_memory_tables','test_handoff_encoding','test_handoff_basis','test_selective_context',
    'test_memory_context_closure','-v']),
    ('strict-boundaries-wsl.txt',['wsl','--cd','/mnt/c/Users/WI/Desktop/home_work/AI_LLM/agent',
        'python3','-m','unittest','discover','-s','tests','-p','test_external_json_boundaries.py','-v'])]
failed=False
for name,command in commands:
    result=subprocess.run(command,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=600)
    (RUN/name).write_bytes(result.stdout)
    print(name,'exit',result.returncode,flush=True)
    failed|=result.returncode!=0
raise SystemExit(int(failed))
