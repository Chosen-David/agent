"""Reproduce this round's integration checks; nonzero retrieval exits are retained."""
import json
from pathlib import Path
import subprocess
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def main():
    commands=[
      ('validate',[sys.executable,'-m','agent_runtime.knowledge','--root','knowledge','validate']),
      ('sync',[sys.executable,'scripts/sync_plugin_references.py']),
      ('sync-check',[sys.executable,'scripts/sync_plugin_references.py','--check']),
      ('index',[sys.executable,'-m','agent_runtime.knowledge','--root','knowledge','index','--db','.knowledge-cache/search.sqlite']),
    ]
    for name,case,extra in [('original','queries.json',['--accept-context','--context-limit','8']),('round2','round2-queries.json',['--accept-context','--context-limit','8']),('morphology','morphology-queries.json',['--require-backends','sqlite'])]:
        commands.append((name,[sys.executable,'scripts/eval_knowledge.py','--cases','evals/knowledge/'+case,*extra,'--output',str(HERE/('final-'+name+'.json'))]))
    commands.extend([
      ('full-tests',[sys.executable,'-m','unittest','discover','-s','tests','-v']),
      ('reader-tests',[sys.executable,'-m','unittest','discover','-s','apps/paper-reader/tests','-v']),
      ('diff-check',['git','diff','--check']),
    ])
    receipts=[]
    for name,cmd in commands:
        log=HERE/(name+'.log')
        with log.open('w') as stream:
            p=subprocess.run(cmd,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
        receipts.append({'name':name,'argv':cmd,'exit_code':p.returncode,'log':log.name})
        (HERE/'final-commands.json').write_text(json.dumps(receipts,indent=2)+'\n')
        print(name,p.returncode,flush=True)
    # This runner records failures; callers must inspect every receipt.
    return 0 if all(r['exit_code']==0 for r in receipts) else 1

if __name__=='__main__':raise SystemExit(main())
