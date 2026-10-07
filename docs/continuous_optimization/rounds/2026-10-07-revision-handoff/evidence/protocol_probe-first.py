"""Bounded existing-API protocol controls, not a production adapter/model harness."""
import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from agent_runtime.communication import Mailbox
RECEIPT = {'status': 'needs_revision', 'reason': 'F1 requires variance evidence'}

def apply(root, fault=None):
    intent = json.loads((root/'intent.json').read_text())
    box = Mailbox(root/'inbox.sqlite', intent['plan'], root)
    old = next(x['receipt'] for x in box.status() if x['seq']==intent['seq'] and x['recipient']=='reviewer')
    if old is not None and old != intent['receipt']:
        raise ValueError('incoming receipt conflict; accountable reconciliation required')
    if fault == 'before_publish': os._exit(73)
    sent = box.publish(intent['event'])
    if fault == 'after_publish': os._exit(73)
    box.acknowledge('reviewer', intent['seq'], intent['receipt'])
    if fault == 'after_ack': os._exit(73)
    return sent

def run():
    cls = runpy.run_path(str(ROOT/'tests/test_communication.py'))['CommunicationTests']
    results=[]
    for name in ('before_publish','after_publish','after_ack','conflicting_receipt','mutated_ref','multi_subscriber_at_budget'):
        f=cls(); f.setUp()
        try:
            plan=deepcopy(f.plan)
            if name=='multi_subscriber_at_budget':
                plan['max_events']=2
                plan['routes'].append(dict(sender='reviewer',recipient='writer',task_id='T1',kind='review'))
                f.box=Mailbox(f.db,plan,f.root)
            incoming=f.box.publish(f.event)['seq']
            ref=f.save('finding.json',{'finding_id':'F1','status':'open','required_test':'add variance'},'F1')
            event=dict(f.event,event_id='revision:F1',sender='reviewer',kind='review',refs=[ref])
            intent={'plan':plan,'seq':incoming,'event':event,'receipt':RECEIPT}
            (f.root/'intent.json').write_text(json.dumps(intent))
            intermediate=None; error=None; exit_code=None
            if name in ('before_publish','after_publish','after_ack'):
                child=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--worker',str(f.root),'--fault',name],cwd=ROOT,capture_output=True,text=True,timeout=15)
                exit_code=child.returncode
                assert exit_code==73,child.stderr
                intermediate=Mailbox(f.db,plan,f.root).status()
                sent=apply(f.root)
                rows=Mailbox(f.db,plan,f.root).status()
                assert len(rows)==3 and len({x['seq'] for x in rows})==2
                assert next(x['receipt'] for x in rows if x['seq']==incoming and x['recipient']=='reviewer')==RECEIPT
                assert len(Mailbox(f.db,plan,f.root).inbox('code'))==1
                assert sent['duplicate']==(name!='before_publish')
            elif name=='conflicting_receipt':
                f.box.acknowledge('reviewer',incoming,{'status':'consumed','reason':'Already handled'})
                intermediate=f.box.status()
                try: apply(f.root)
                except ValueError as e: error=str(e)
                assert error and 'receipt conflict' in error
                assert f.box.status()==intermediate and f.box.inbox('code')==[]
                rows=f.box.status()
            elif name=='mutated_ref':
                sent=f.box.publish(event)
                (f.root/'finding.json').write_text('{}')
                intermediate=f.box.status()
                try: apply(f.root)
                except ValueError as e: error=str(e)
                assert error and 'sha256 mismatch' in error
                assert f.box.status()==intermediate and len(f.box.inbox('reviewer'))==1
                rows=f.box.status()
            else:
                sent=apply(f.root)
                f.box.acknowledge('writer',sent['seq'],{'status':'consumed','reason':'Synthetic request read; not scientific completion'})
                intermediate=f.box.status()
                retry=apply(f.root)
                assert retry['duplicate'] and f.box.status()==intermediate
                assert len(f.box.inbox('code'))==1 and len(f.box.inbox('writer'))==1 # original artifact remains independently pending
                rows=f.box.status()
            results.append({'case':name,'assertions':'pass','exit_code':exit_code,'error':error,'intermediate':intermediate,'final':rows,'actual_responsible_model_handling':False,'original_reviewer_closure':False})
        finally:f.doCleanups()
    return {'evidence_type':'program_execution_synthetic_records','head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'runtime_sha256':hashlib.sha256((ROOT/'agent_runtime/communication.py').read_bytes()).hexdigest(),'probe_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'cases':results,'asserted':len(results),'model_tasks':0,'scope':'Single owned consumer and saved exact intent; no atomicity against competing ACK, external exactly-once or scientific closure claim'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--worker',type=Path);p.add_argument('--fault');p.add_argument('--output',type=Path);a=p.parse_args()
    if a.worker:apply(a.worker,a.fault);sys.exit()
    if not a.output:p.error('--output required')
    data=run()
    with a.output.open('x') as out:json.dump(data,out,indent=2);out.write('\n')
    print(json.dumps({'asserted':data['asserted'],'model_tasks':0}))
