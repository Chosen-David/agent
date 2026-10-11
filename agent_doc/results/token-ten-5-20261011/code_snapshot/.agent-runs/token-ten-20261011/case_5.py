import hashlib,json,tempfile
from pathlib import Path
SOURCES=['agent_runtime/log_context.py','scripts/log_context.py','tests/test_log_runs.py']
TESTS=['tests.test_log_context','tests.test_log_chunks','tests.test_log_runs','tests.test_context_serialization']
COUNT=23
MECHANISM='Opt-in repeated-log-line runs preserve every occurrence and original position without repeating literal pending lines'
SCOPE='One complete bound log with repeated pending observations and both blockers; fresh short turns only, no task-success/cash claim'
TEXT='OBS pending\n'*20+'BLOCK_VERIFY\nBLOCK_CANCEL\n'
QUESTION='Fictional log display only. Decode lines or runs (start,count,text) at original positions. Return JSON publish=false, blockers listing lines starting BLOCK_ in source order, and records=total selected lines. Repetition retains all occurrences. No tools.\n'
def build(root):
    from agent_runtime.log_context import log_view
    with tempfile.TemporaryDirectory() as d:
        p=Path(d).resolve();(p/'run.log').write_bytes(TEXT.encode());sha=hashlib.sha256(TEXT.encode()).hexdigest()
        views={n:log_view(p,'run.log',sha,head=100,tail=0,context=0,needles=['BLOCK_'],encoding=e) for n,e in [('baseline','lines'),('candidate','runs')]}
        for v in views.values():v['project_root']='fixture-project'
    return {'report':{'run_id':'ten-log-runs'},'oracle':{'publish':False,'blockers':['BLOCK_VERIFY','BLOCK_CANCEL'],'records':22},'prompts':{n:QUESTION+json.dumps(v,separators=(',',':')) for n,v in views.items()}}
def replay(root):
    from agent_runtime.log_context import restore_log_lines
    rows=[restore_log_lines(json.loads(p.split('\n',1)[1])) for p in build(root)['prompts'].values()]
    assert rows[0]==rows[1]==[{'line':i+1,'text':t} for i,t in enumerate(TEXT.splitlines(keepends=True))]
    return {'all_occurrences_and_positions':True,'both_negative_blockers':True}
