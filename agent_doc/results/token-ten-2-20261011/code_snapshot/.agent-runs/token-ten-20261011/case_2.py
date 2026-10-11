import hashlib,json,tempfile
from pathlib import Path
SOURCES=['agent_runtime/artifact_context.py','scripts/artifact_context.py','tests/test_artifact_context.py','tests/test_artifact_identity.py','tests/test_artifact_edits.py']
TESTS=['tests.test_artifact_context','tests.test_artifact_identity','tests.test_artifact_edits'];COUNT=22
SCOPE='One artifact with two separated current blocker edits; complete same-packet base plus exact host-bound target restoration; short fresh turns only, not deployment/long-context/cash savings'
MECHANISM='Bounded multiple artifact edits avoid reinjecting their unchanged middle'
def build(root):
    from agent_runtime.artifact_context import compare_artifacts,restore_comparison
    before='Status: open.\n'+''.join(f'Observation {i:02}: preserve evidence.\n' for i in range(14))+'Verification: usable.\n'
    after=before.replace('Status: open.','Status: cancelled. BLOCK_CANCEL').replace('Verification: usable.','Verification: pending. BLOCK_VERIFY')
    with tempfile.TemporaryDirectory() as d:
        r=Path(d).resolve();refs=[]
        for name,text in [('before.md',before),('current.md',after)]:
            (r/name).write_bytes(text.encode());refs.append({'path':name,'sha256':hashlib.sha256(text.encode()).hexdigest()})
        views=[compare_artifacts(r,*refs,multi_edit=flag) for flag in (False,True)]
        assert all(restore_comparison(r,v,*refs)==(before,after) for v in views)
        for v in views:v['project_root']='fixture-project'
    q='Fictional data only. Decode current after from full text, a splice, or patch.edits applied to before at ORIGINAL line positions. Return JSON publish=false and blockers with BLOCK_* codes in current occurrence order when blocked, otherwise publish=true and blockers=[]. No tools.\n'
    return {'report':{'run_id':'ten-artifact-edits'},'oracle':{'publish':False,'blockers':['BLOCK_CANCEL','BLOCK_VERIFY']},'prompts':{name:q+json.dumps(v,separators=(',',':')) for name,v in zip(('baseline','candidate'),views)}}
def replay(root):
    data=build(root);assert '"representation":"edits"' in data['prompts']['candidate']
    return {'separated_edits':2,'complete_old_text_retained':True,'current_blockers':['BLOCK_CANCEL','BLOCK_VERIFY']}
