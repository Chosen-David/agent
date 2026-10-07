"""Remaining invalid-intent controls; reuse saved-intent probe and test fixture."""
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import runpy
import subprocess
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('protocol_probe',HERE/'protocol_probe.py')
probe=importlib.util.module_from_spec(spec);spec.loader.exec_module(probe)

def run():
    cls=runpy.run_path(str(ROOT/'tests/test_communication.py'))['CommunicationTests']
    outcomes=[]
    for name in ('missing_ref','stale_version','unapproved_route','exhausted_budget','changed_duplicate_body','conflicting_needs_revision_reason'):
        f=cls();f.setUp()
        try:
            plan=deepcopy(f.plan)
            if name=='exhausted_budget':
                plan['max_events']=1;f.db=f.root/'budget.sqlite';f.box=probe.Mailbox(f.db,plan,f.root)
            seq=f.box.publish(f.event)['seq']
            ref=f.save('finding.json',{'finding_id':'F1','status':'open'},'F1')
            event=dict(f.event,event_id='revision:F1',sender='reviewer',kind='review',refs=[ref])
            if name=='missing_ref':(f.root/'finding.json').unlink()
            elif name=='stale_version':event['input_version']='obsolete'
            elif name=='unapproved_route':event['task_id']='unauthorized-task'
            elif name=='changed_duplicate_body':
                f.box.publish(event);event['summary']='Changed body under same ID'
            elif name=='conflicting_needs_revision_reason':
                f.box.acknowledge('reviewer',seq,dict(probe.RECEIPT,reason='Another immutable intent'))
            intent=dict(db=f.db.name,plan=plan,seq=seq,event=event,receipt=probe.RECEIPT)
            (f.root/'intent.json').write_text(json.dumps(intent))
            before=f.box.status();error=None
            try:probe.apply(f.root)
            except ValueError as exc:error=str(exc)
            assert error,name
            after=f.box.status();assert after==before,name
            expected_pending=0 if name=='conflicting_needs_revision_reason' else 1
            assert len(f.box.inbox('reviewer'))==expected_pending,name
            outcomes.append(dict(case=name,assertions='pass',error=error,before=before,after=after,actual_model_handling=False,reviewer_closed=False))
        finally:f.doCleanups()
    return dict(evidence_type='program_execution_synthetic_records',head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),runtime_sha256=hashlib.sha256((ROOT/'agent_runtime/communication.py').read_bytes()).hexdigest(),probe_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),protocol_dependency_sha256=hashlib.sha256((HERE/'protocol_probe.py').read_bytes()).hexdigest(),cases=outcomes,asserted=6,model_tasks=0)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=run()
    with a.output.open('x') as f:json.dump(d,f,indent=2);f.write('\n')
    print(json.dumps({'asserted':d['asserted'],'model_tasks':0,'errors':[c['error'] for c in d['cases']]}))
