import json
SOURCES=['agent_runtime/context_serialization.py','scripts/task_context.py','scripts/log_context.py','scripts/advice_context.py','agent_runtime/knowledge.py','tests/test_context_serialization.py','scripts/sync_plugin_references.py','tests/test_knowledge.py','plugins/research-assistant/skills/model-with-knowledge/scripts/knowledge.py','plugins/research-assistant/skills/model-with-knowledge/scripts/context_serialization.py']
TESTS=['tests.test_context_serialization','tests.test_task_context','tests.test_log_context','tests.test_advice_context','tests.test_knowledge.KnowledgeTests.test_bundle_exact_and_cli_without_repository','tests.test_plugin_reference_sync']
COUNT=27
SCOPE='One structured pending-context fixture with identical parsed payload in pretty/compact JSON; preserves blockers, Unicode and nested values; fresh short turns only, no multi-turn/deployment/cash claim'
MECHANISM='One explicit whitespace-only compact serializer across task/log/advice/knowledge context CLIs'
def fixture():
    return {'status':'pending','scope':'navigation only; not accepted evidence','errors':['BLOCK_VERIFY','BLOCK_CANCEL'],'items':[{'id':f'T-{i}','status':'pending','depends_on':[f'V-{i}'],'budget':None,'cancelled':i==3} for i in range(6)],'global_rule':'人类指南优先; preserve corrections and negative results.'}
def build(root):
    from agent_runtime.context_serialization import render_context
    value=fixture();q='Fictional structured observation only. Return JSON publish=false if status is pending or invalid, blockers exactly errors in listed order, and cancelled_ids listing item IDs whose cancelled=true. Do not promote this display to evidence. No tools.\n'
    return {'report':{'run_id':'ten-compact-json'},'oracle':{'publish':False,'blockers':['BLOCK_VERIFY','BLOCK_CANCEL'],'cancelled_ids':['T-3']},'prompts':{name:q+render_context(value,compact=flag,indent=2) for name,flag in [('baseline',False),('candidate',True)]}}
def replay(root):
    data=build(root);a,b=[json.loads(p.split('\n',1)[1]) for p in data['prompts'].values()]
    assert a==b==fixture()
    return {'all_json_values_exact':True,'global_rule_and_cancelled_item_preserved':True}
