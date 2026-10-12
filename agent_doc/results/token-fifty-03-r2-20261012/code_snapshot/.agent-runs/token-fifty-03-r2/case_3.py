import hashlib,json
from pathlib import Path
SOURCES=['agent_runtime/reference_context.py','scripts/reference_context.py','agent_runtime/token_usage.py','tests/test_reference_context.py']
TESTS=['tests.test_reference_context'];COUNT=18
MECHANISM='Full strict SHA-bound reference collection with self-contained directory-prefix path value factoring and exact ordered source restoration'
PREFIX='agent_doc/results/research-current-independent-reproduction-with-complete-version-bound-evidence/'
VALUES={'global_rule':'All scientific consumers and publication wait for current independent verification.','current_status':'pending','metric_unit':'tokens','references':[{'path':PREFIX+f'part-{i:03}.json','sha256':hashlib.sha256(f'reference-{i}'.encode()).hexdigest()} for i in range(1,33)],'unknown_metadata':{'failed_run_preserved':True,'note':'These are fictional reference identities, not accepted experimental data.'}}
TEXT=json.dumps(VALUES,ensure_ascii=False,indent=2)+'\n'
QUESTION='Synthetic complete reference identity collection. For directory-prefix encoding canonical path=path_prefix+data.references[i].path; for full encoding use path directly. Return number of references, first and last canonical full path, publish=false when current_status pending and global rule requires independent verification, and metric unit. References are not acceptance proof. JSON only; no tools.\n'
ORACLE_VALUE={'reference_count':32,'first_path':PREFIX+'part-001.json','last_path':PREFIX+'part-032.json','publish':False,'unit':'tokens'}

def build(root):
    from agent_runtime.reference_context import reference_view,restore_reference_view
    root=Path(root).resolve();rel='agent_doc/results/token-fifty-03-r2-20261012/fixture.json';f=root/rel
    if f.exists():assert f.read_bytes()==TEXT.encode()
    else:f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(TEXT.encode())
    sha=hashlib.sha256(f.read_bytes()).hexdigest()
    values={'baseline':reference_view(root,rel,sha,full=True),'candidate':reference_view(root,rel,sha)}
    for v in values.values():assert json.dumps(restore_reference_view(root,json.dumps(v,ensure_ascii=False),rel,sha),ensure_ascii=False)==json.dumps(VALUES,ensure_ascii=False)
    assert values['candidate']['encoding']=='directory-prefix'
    return {'report':{'run_id':'fifty-directory-prefix','complete_references':32,'common_directory':PREFIX},'oracle':ORACLE_VALUE,'prompts':{n:QUESTION+json.dumps(v,ensure_ascii=False,separators=(',',':')) for n,v in values.items()},'packets':values}

def replay(root):
    data=build(root);a=data['packets']['baseline'];b=data['packets']['candidate']
    assert a['source']==b['source'] and a['project_root']==b['project_root']
    assert b['path_prefix']==PREFIX
    assert [{**r,'path':PREFIX+r['path']} for r in b['data']['references']]==VALUES['references']
    assert all(a['data'][k]==b['data'][k] for k in VALUES if k!='references')
    assert len(data['prompts']['candidate'])<len(data['prompts']['baseline'])
    return {'all32reference_paths_sha_and_order_restored':True,'all_global_unknown_metadata_units_status_preserved':True,'live_source_bound_decoder_checked_before_packet_transport':True,'no_omitted_references_or_recovery_inference':True,'not_reference_existence_or_scientific_validity':True}
