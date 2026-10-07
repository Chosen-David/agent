from pathlib import Path
import json,hashlib,sys
from agent_runtime.communication import Mailbox
from scripts.validate_handoff import validate
R=Path.cwd();H=R/'docs/continuous_optimization/rounds/2026-10-07-revision-handoff/evidence/w9-release/handoff';W=H/'writer'
def save(n,x):
 with (W/n).open('x') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
i=json.loads((W/'immutable-intent.json').read_text());ctx=json.loads((H/'host-context.json').read_text())
assert i['plan']==ctx['plan'] and i['db']==ctx['db'] and i['artifact_root']==ctx['artifact_root']
assert hashlib.sha256((H/'inputs/manuscript.md').read_bytes()).hexdigest()==i['original_manuscript_sha256']
assert hashlib.sha256((H/'inputs/measurements.csv').read_bytes()).hexdigest()==i['original_csv_sha256']
box=Mailbox(i['db'],i['plan'],i['artifact_root']);status=box.status();save('status-prepublish.json',status)
r=next(x for x in status if x['seq']==i['incoming_seq'] and x['recipient']==i['recipient'])
assert r['receipt'] is None or r['receipt']==i['receipt'],'Existing receipt conflicts with persisted intent'
manifest=json.loads((W/'handoff.json').read_text());errs=validate(manifest,H);assert not errs,errs
refs=[]
for ref in i['event']['refs']:
 actual=hashlib.sha256((H/ref['path']).read_bytes()).hexdigest();assert actual==ref['sha256'];refs.append(dict(ref,actual_sha256=actual))
save('prepublish-validation.json',{'manifest_integrity_errors':errs,'refs_revalidated':refs,'input_identities_preserved':True,'independent_consumer_scope_validated':False,'authority':'Active parent assignment; sole consumer research-write; no stop/cancel signal received. Engine lease not applicable to this host collaboration diagnostic.'})
result=box.publish(i['event']);save('publish-result.json',result)
status=box.status();save('status-after-publish-before-ack.json',status)
assert next(x for x in status if x['seq']==2 and x['recipient']=='research-write')['receipt'] is None
assert next(x for x in status if x['seq']==result['seq'] and x['recipient']=='research-review')['receipt'] is None
print(json.dumps({'operation':'Mailbox.publish','event_id':i['event']['event_id'],'result':result,'status_after_publish_before_ack':status,'ack_called':False},indent=2))
