import json
from pathlib import Path
SOURCES=['agent_runtime/grid_context.py','scripts/grid_context.py','agent_runtime/token_usage.py','tests/test_grid_context.py']
TESTS=['tests.test_grid_context'];COUNT=18
MECHANISM='Complete current-SHA-bound exact nonzero integer arithmetic progression transport with ordered source restoration'
COORDINATES=[100000+i*3 for i in range(64)]
VALUES={'global_rule':'All scientific consumers and publication wait for current independent verification.','current_status':'pending','metric_unit':'tokens','coordinates':COORDINATES,'coordinate_unit':'simulation ticks','unknown_metadata':{'failed_run_preserved':True,'note':'Fictional synthetic coordinates, not accepted scientific results.'}}
TEXT=json.dumps(VALUES,ensure_ascii=False,indent=2)+'\n'
QUESTION='Synthetic complete coordinate collection. For arithmetic encoding coordinates[i]=start+i*step for i=0..count-1; full encoding uses the complete list. Return count, first/last coordinate, step (second minus first), metric unit, and publish=false while current_status pending and global rule requires independent verification. Transport is not scientific acceptance. JSON only; no tools.\n'
ORACLE_VALUE={'coordinate_count':64,'first':100000,'last':100189,'step':3,'publish':False,'unit':'tokens'}

def build(root):
 from agent_runtime.grid_context import grid_view,restore_grid_view
 root=Path(root).resolve();rel='agent_doc/results/token-fifty-04-20261012/fixture.json';f=root/rel
 if f.exists():assert f.read_bytes()==TEXT.encode()
 else:f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(TEXT.encode())
 import hashlib
 sha=hashlib.sha256(f.read_bytes()).hexdigest()
 values={'baseline':grid_view(root,rel,sha,full=True),'candidate':grid_view(root,rel,sha)}
 for v in values.values():assert json.dumps(restore_grid_view(root,json.dumps(v,ensure_ascii=False),rel,sha),ensure_ascii=False)==json.dumps(VALUES,ensure_ascii=False)
 assert values['candidate']['encoding']=='arithmetic'
 return {'report':{'run_id':'fifty-arithmetic-grid','complete_coordinates':64,'step':3},'oracle':ORACLE_VALUE,'prompts':{n:QUESTION+json.dumps(v,ensure_ascii=False,separators=(',',':')) for n,v in values.items()},'packets':values}

def replay(root):
 data=build(root);a=data['packets']['baseline'];b=data['packets']['candidate']
 assert a['source']==b['source'] and a['project_root']==b['project_root']
 grid=b['data']['coordinates'];assert [grid['start']+i*grid['step'] for i in range(grid['count'])]==COORDINATES
 assert all(a['data'][k]==b['data'][k] for k in VALUES if k!='coordinates')
 assert len(data['prompts']['candidate'])<len(data['prompts']['baseline'])
 return {'all64coordinate_values_types_indexes_order_restored':True,'all_rules_metadata_status_units_preserved':True,'exact_live_source_bound_restore_before_transport':True,'no_omissions_or_recovery_inference':True,'no_scientific_acceptance':True}
