from pathlib import Path
import json,hashlib
from agent_runtime.communication import Mailbox
R=Path.cwd();H=R/'docs/continuous_optimization/rounds/2026-10-07-revision-handoff/evidence/w9-release/handoff';W=H/'writer'
i=json.loads((W/'immutable-intent.json').read_text());receipt=json.loads((W/'incoming-receipt.json').read_text());published=json.loads((W/'publish-result.json').read_text());assert receipt==i['receipt']
box=Mailbox(i['db'],i['plan'],i['artifact_root']);before=box.status()
assert any(x['seq']==published['seq'] and x['recipient']=='research-review' for x in before)
original=next(x for x in before if x['seq']==2 and x['recipient']=='research-write');assert original['receipt'] is None or original['receipt']==receipt
for ref in i['event']['refs']:assert hashlib.sha256((H/ref['path']).read_bytes()).hexdigest()==ref['sha256']
for ref in json.loads((W/'inbox-before.json').read_text())[0]['event']['refs']:assert hashlib.sha256((H/ref['path']).read_bytes()).hexdigest()==ref['sha256']
box.acknowledge('research-write',2,receipt)
after=box.status();assert next(x for x in after if x['seq']==2 and x['recipient']=='research-write')['receipt']==receipt
inbox=box.inbox('research-write');assert all(x['seq']!=2 for x in inbox)
for name,data in [('status-after-ack.json',after),('inbox-after-ack.json',inbox),('ack-result.json',{'recipient':'research-write','seq':2,'receipt':receipt,'published_revision_seq':published['seq'],'event_id':i['event']['event_id'],'scientific_findings_closed':False})]:
 with (W/name).open('x') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'operation':'Mailbox.acknowledge','recipient':'research-write','seq':2,'exact_receipt':receipt,'status_after':after,'writer_inbox_after':inbox},indent=2))
