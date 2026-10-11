import hashlib,json,tempfile
from pathlib import Path
SOURCES=['agent_runtime/task_context.py','scripts/task_context.py','tests/test_task_context.py','agent_runtime/maintenance_observer.py','agent_runtime/advice_poll.py']
TESTS=['tests.test_task_context'];COUNT=5
SCOPE='One 25-row canonical task-index fixture; host selects T20, preserving all non-row text and source versions; no global task completion or long-paper claim'
MECHANISM='Explicit selected task rows with all global text retained, source SHA and line recovery'
def build(root):
 from agent_runtime.task_context import task_view
 text='# TASK\nGlobal completion needs independent result validation.\n## 2026-10-11\n'
 for i in range(25):
  status='pending verification' if i==20 else 'old task completed'
  text+=f'- [{" " if i==20 else "x"}] [T{i}] {status} ([detail](task_details/T{i}.md))\n'
 with tempfile.TemporaryDirectory() as d:
  r=Path(d).resolve();p=r/'agent_doc/task/TASK.md';p.parent.mkdir(parents=True);p.write_bytes(text.encode())
  view=task_view(r,['T20'],hashlib.sha256(text.encode()).hexdigest())
  # Same serialized explicit project identity in both inputs; tempfile paths are not model content.
  view['project_root']='explicit-fixture-project'
 question='For T20 only, return JSON {"status":"blocked","cause":"pending verification"} if independent verification is pending, else status="ready" and cause="none". Do not infer global completion. No tools.\n'
 return {'report':{'run_id':'five-task-index'},'oracle':{'status':'blocked','cause':'pending verification'},'prompts':{'baseline':question+text,'candidate':question+json.dumps(view,separators=(',',':'))}}
def replay(root):
 data=build(root)
 assert '[T20]' in data['prompts']['candidate'] and '[T19]' not in data['prompts']['candidate']
 assert 'Global completion needs independent result validation.' in data['prompts']['candidate']
 return {'selected':'T20','omitted_rows':24,'global_rule_retained':True}
