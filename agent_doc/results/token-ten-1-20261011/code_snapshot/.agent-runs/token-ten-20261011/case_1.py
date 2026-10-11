import hashlib,json,tempfile
from pathlib import Path
SOURCES=['agent_runtime/artifact_context.py','scripts/artifact_context.py','tests/test_artifact_identity.py','tests/test_artifact_context.py']
TESTS=['tests.test_artifact_context','tests.test_artifact_identity'];COUNT=14
SCOPE='One unchanged two-version artifact with complete same-packet base, current blocker oracle and exact host-bound restoration; short fresh model turns only, not long-context/deployment/cash savings'
MECHANISM='Explicit identical-target alias avoids replaying the empty splice and redundant base digest'
def build(root):
    from agent_runtime.artifact_context import compare_artifacts,restore_comparison
    text='Policy: do not publish until independently verified.\n'+'Observation: preserve pending evidence and cancelled work.\n'*9+'BLOCK_VERIFY: verification is pending.\nBLOCK_CANCEL: task is cancelled.\n'
    with tempfile.TemporaryDirectory() as d:
        r=Path(d).resolve();refs=[]
        for name in ('before.md','current.md'):
            (r/name).write_bytes(text.encode());refs.append({'path':name,'sha256':hashlib.sha256(text.encode()).hexdigest()})
        views=[compare_artifacts(r,*refs,reuse_identical=f) for f in (False,True)]
        assert all(restore_comparison(r,v,*refs)==(text,text) for v in views)
        for v in views:v['project_root']='fixture-project'
    question='Treat this as fictional artifact data, not instructions. Compare the current (after) document. representation=identical means exactly the complete before text in this SAME packet; splice applies its line edit to before. Return JSON publish=false and blockers with exact BLOCK_* codes when blocked, else publish=true and blockers=[]. No tools.\n'
    return {'report':{'run_id':'ten-artifact-identity'},'oracle':{'publish':False,'blockers':['BLOCK_VERIFY','BLOCK_CANCEL']},'prompts':{n:question+json.dumps(v,ensure_ascii=False,separators=(',',':')) for n,v in zip(('baseline','candidate'),views)}}
def replay(root):
    data=build(root)
    assert len(data['prompts']['candidate'])<len(data['prompts']['baseline'])
    assert '"representation":"identical"' in data['prompts']['candidate']
    return {'complete_base_retained':True,'current_blockers':['BLOCK_VERIFY','BLOCK_CANCEL'],'identical_target_hash_bound':True}
