import hashlib,json,tempfile
from pathlib import Path
SOURCES=['agent_runtime/log_context.py','scripts/log_context.py','tests/test_log_chunks.py']
TESTS=['tests.test_log_context','tests.test_log_chunks','tests.test_context_serialization']
COUNT=18
MECHANISM='Opt-in contiguous log chunks preserving selected line positions, literal text and all scope metadata'
SCOPE='One bound log excerpt with every line retained; fresh short turns, not long-context/cash or task-success evidence'
TEXT=''.join(f'OBS {i:02d} pending\n' for i in range(14))+'BLOCK_VERIFY\nBLOCK_CANCEL\n'
QUESTION='Fictional log display only. Decode lines or chunks by original line positions. Return JSON publish=false, blockers listing lines starting BLOCK_ in source order, and records=total selected lines. Omitted text is not evidence of success. No tools.\n'
def build(root):
    from agent_runtime.log_context import log_view
    with tempfile.TemporaryDirectory() as d:
        p=Path(d).resolve();(p/'run.log').write_bytes(TEXT.encode());sha=hashlib.sha256(TEXT.encode()).hexdigest()
        views={name:log_view(p,'run.log',sha,head=100,tail=0,context=0,needles=['BLOCK_'],encoding=encoding) for name,encoding in [('baseline','lines'),('candidate','chunks')]}
        for view in views.values():view['project_root']='fixture-project'
    return {'report':{'run_id':'ten-log-chunks'},'oracle':{'publish':False,'blockers':['BLOCK_VERIFY','BLOCK_CANCEL'],'records':16},'prompts':{n:QUESTION+json.dumps(v,ensure_ascii=False,separators=(',',':')) for n,v in views.items()}}
def replay(root):
    from agent_runtime.log_context import restore_log_lines
    data=build(root);values=[json.loads(p.split('\n',1)[1]) for p in data['prompts'].values()]
    assert restore_log_lines(values[0])==restore_log_lines(values[1])==[{'line':i+1,'text':text} for i,text in enumerate(TEXT.splitlines(keepends=True))]
    return {'all_line_positions_and_literal_bytes':True,'metadata_and_scope_retained':True}
