import json
SOURCES=['agent_runtime/maintenance_observer.py','agent_runtime/maintenance_gate.py','agent_runtime/advice_poll.py','tests/test_maintenance_observer.py','tests/test_maintenance_gate.py']
TESTS=['tests.test_maintenance_observer','tests.test_maintenance_gate']
COUNT=15
SCOPE='One fixed two-observation unchanged maintenance event trace, with explicit real project file/advice observer; no long-context, full deployment or cash claim'
MECHANISM='Required project document/advice/event observer plus typed handled maintenance ACK; avoid a repeated model decision'
def build(root):
 report={'run_id':'token-five-maintenance','runtime_status':'blocked','source_error':None,'remaining':['T1'],
         'requirements':[{'id':'T1','done':False,'result_validation':'pending','gpu_idle':True}],'updated_at':1}
 text='Decide whether this task result may be published now. Choose action from wait_for_verification/publish and return JSON with action and boolean publish. GPU idle alone is not completion. No tools. Observation:\n'+json.dumps({k:v for k,v in report.items() if k!='updated_at'},sort_keys=True,separators=(',',':'))
 return {'report':report,'oracle':{'action':'wait_for_verification','publish':False},'prompts':{'baseline1':text,'baseline2':text,'candidate1':text}}
def replay(root):
 from agent_runtime.maintenance_observer import maintenance_observer
 from agent_runtime.maintenance_gate import MaintenanceGate,MaintenanceOutcome
 calls=[];event={'evidence':'pending','due':False};report=build(root)['report']
 gate=MaintenanceGate(lambda r:(calls.append(r),MaintenanceOutcome('handled'))[1],maintenance_observer(root,report['run_id'],[],lambda:event),project_root=root,run_id=report['run_id'],max_quiet_seconds=5,clock=lambda:0)
 assert gate(report).status=='handled';report['updated_at']=2;assert gate(report).status=='unchanged'
 assert len(calls)==1;event['due']=True;assert gate(report).status=='handled';assert len(calls)==2
 return {'independent_callback_counts':[1,1,2]}
