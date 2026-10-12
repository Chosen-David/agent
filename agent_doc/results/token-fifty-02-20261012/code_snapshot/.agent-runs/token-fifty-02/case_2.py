import hashlib,json,tempfile
from pathlib import Path
SOURCES=['agent_runtime/record_context.py','scripts/record_context.py','agent_runtime/token_usage.py','tests/test_record_context.py']
TESTS=['tests.test_record_context']
COUNT=17
MECHANISM='Strict whole-source SHA-bound NDJSON validation and explicit physical current/global record selection'
HISTORY='Historical discussion from different code/input. Prior approval is scoped to that older run. Retain counterexamples and original records; it never approves the current run. '
GLOBAL={'type':'global','rule':'All experimental results remain pending until independent verification; historical decisions never authorize current run.','unit':'tokens'}
CURRENT={'issue_id':'CURRENT','run_id':'run-new','status':'cancelled','verification':'pending','code_sha':'a'*40,'input_id':'input-new','action':'fix data and independently verify before publication or scientific consumption'}
VALUES=[GLOBAL]+[CURRENT if i==17 else {'issue_id':'OLD-'+str(i),'status':'historical','discussion':HISTORY} for i in range(2,33)]
TEXT=''.join(json.dumps(v,ensure_ascii=False,separators=(',',':'))+'\n' for v in VALUES)
QUESTION='Synthetic meeting record navigation. Host declares the entire required closure for this task: global physical line1 and CURRENT physical line17. Read only their current/global facts, not historical approvals. Return current run_id, publish=false if cancelled or pending verification, blockers in order ["cancelled","pending_verification"], and the global metric unit. No tools. JSON only.\n'
ORACLE_VALUE={'run_id':'run-new','publish':False,'blockers':['cancelled','pending_verification'],'unit':'tokens'}

def build(root):
    from agent_runtime.record_context import record_view
    with tempfile.TemporaryDirectory() as d:
        p=Path(d).resolve();rel='agent_doc/advice/meeting.ndjson';f=p/rel;f.parent.mkdir(parents=True);f.write_bytes(TEXT.encode())
        h=hashlib.sha256(f.read_bytes()).hexdigest();candidate=record_view(p,rel,h,lines=[17],global_lines=[1]);candidate['project_root']='fixture-project'
        baseline={'schema_version':'record-full/v1','project_root':'fixture-project','source':candidate['source'],'selection':candidate['selection'],'total_records':32,'text':TEXT,'scope':'complete raw source; host declares required records; no validity or closure inference'}
    values={'baseline':baseline,'candidate':candidate}
    return {'report':{'run_id':'fifty-record-selection','required_lines':[1,17],'historical_records':30},'oracle':ORACLE_VALUE,'prompts':{n:QUESTION+json.dumps(v,ensure_ascii=False,separators=(',',':')) for n,v in values.items()},'packets':values}

def replay(root):
    from agent_runtime.record_context import record_view
    data=build(root);a=data['packets']['baseline'];b=data['packets']['candidate']
    assert a['source']==b['source'] and a['selection']==b['selection']
    rows=a['text'].splitlines(keepends=True)
    assert b['records']==[{'line':n,'text':rows[n-1]} for n in (1,17)]
    assert json.loads(b['records'][0]['text'])==GLOBAL and json.loads(b['records'][1]['text'])==CURRENT
    assert b['total_records']==32 and b['omitted_records']==30
    assert len(data['prompts']['candidate'])<len(data['prompts']['baseline'])
    return {'same_current_and_global_raw_records':True,'whole_source_sha_and_explicit_selection_equal':True,'global_unit_and_cancelled_pending_gate_preserved':True,'recovery_calls_in_explicit_complete_fixture':0,'no_claim_host_enumeration_is_automatically_complete':True}
