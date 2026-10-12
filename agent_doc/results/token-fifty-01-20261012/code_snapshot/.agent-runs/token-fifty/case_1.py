import hashlib,json,tempfile
from pathlib import Path
SOURCES=['agent_runtime/advice_context.py','scripts/advice_context.py','agent_runtime/token_usage.py','tests/test_advice_discovery.py','tests/test_advice_context.py']
TESTS=['tests.test_advice_discovery','tests.test_advice_context']
COUNT=19
MECHANISM='SHA-bound advice H2 discovery before selected topic loading; all leading constraints and every literal title retained'
LEADING='# Research meeting\nGlobal rule: all experimental results remain pending until independent verification.\n'
TITLES=['OLD-1','OLD-2','VERIFY','OLD-3','OLD-4','OLD-5']
HISTORY='Archived proposal discussion. A prior note reports usable-with-scope but that does not approve current results. Different configuration; retain the original failure and source. No current decision is established by this historical body.\n'
SELECTED='## VERIFY\nCurrent run cancelled. Do not publish. Fix data and independently verify before any consumer.\n'
TEXT=LEADING+''.join(SELECTED if title=='VERIFY' else '## '+title+'\n'+HISTORY*4 for title in TITLES)
QUESTION='Fictional advice navigation only. List every literal H2 topic in document order (ignore fenced examples). For the host-selected VERIFY topic, return publish=false and blockers=["cancelled","pending_verification"] if current run is cancelled and global rule requires independent verification. Do not use historical status as approval. Return JSON with topics, publish and blockers. No tools.\n'
ORACLE_VALUE={'topics':TITLES,'publish':False,'blockers':['cancelled','pending_verification']}
def build(root):
    from agent_runtime.advice_context import advice_headings,advice_view
    with tempfile.TemporaryDirectory() as d:
        p=Path(d).resolve();rel='agent_doc/advice/meeting.md';f=p/rel;f.parent.mkdir(parents=True);f.write_bytes(TEXT.encode())
        digest=hashlib.sha256(f.read_bytes()).hexdigest()
        selected=advice_view(p,rel,['VERIFY'],digest);discovery=advice_headings(p,rel,digest)
        for v in (selected,discovery):v['project_root']='fixture-project'
        full={'schema_version':'advice-full/v1','project_root':'fixture-project','source':selected['source'],'text':TEXT,'scope':'complete source; navigation is not assessment, closure or authority'}
        values={'baseline':{'discovery':full,'selected_view':selected},'candidate':{'discovery':discovery,'selected_view':selected}}
    return {'report':{'run_id':'fifty-advice-discovery','selected_heading':'VERIFY','historical_topics':5},'oracle':ORACLE_VALUE,'prompts':{n:QUESTION+json.dumps(v,ensure_ascii=False,separators=(',',':')) for n,v in values.items()},'packets':values}
def replay(root):
    data=build(root);a=data['packets']['baseline'];b=data['packets']['candidate']
    assert a['selected_view']==b['selected_view']
    assert a['discovery']['source']==b['discovery']['source']
    assert [t['heading'] for t in b['discovery']['topics']]==TITLES
    assert b['discovery']['leading_text']==LEADING
    assert a['selected_view']['selected_sections'][0]['text']==SELECTED
    assert len(data['prompts']['candidate'])<len(data['prompts']['baseline'])
    return {'same_selected_view':True,'complete_heading_and_global_oracle':True,'cancelled_and_pending_gate_preserved':True,'recovery_calls_in_this_host_selected_fixture':0,'fixture_not_live_tool_chain':True}
