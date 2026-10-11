import hashlib,json,tempfile
from pathlib import Path
SOURCES=['agent_runtime/advice_context.py','scripts/advice_context.py','tests/test_advice_context.py','agent_runtime/maintenance_observer.py','agent_runtime/advice_poll.py']
TESTS=['tests.test_advice_context'];COUNT=7
SCOPE='One 12-topic advice fixture with selected ISSUE-VERIFY, all leading rules and full source-version recovery; no automatic assessment, authority or general meeting-closure claim'
MECHANISM='Explicit advice topic selection retains shared leading rules and current issue, avoids replaying unrelated meeting paragraphs'
def build(root):
 from agent_runtime.advice_context import advice_view
 text='# Advice meeting\nHuman GUIDE overrides advice; proposals do not grant permission.\n'
 for i in range(12):
  if i==7:text+='## ISSUE-VERIFY\nDecision: defer. Reason: independent verification pending.\n'
  else:text+=f'## ISSUE-{i}\nPast: '+ ' '.join(f'observation{j:02d}' for j in range(8))+'; prior discussion retained in this file.\n'
 with tempfile.TemporaryDirectory() as d:
  r=Path(d).resolve();p=r/'agent_doc/advice/meeting.md';p.parent.mkdir(parents=True);p.write_bytes(text.encode())
  view=advice_view(r,'agent_doc/advice/meeting.md',['ISSUE-VERIFY'],hashlib.sha256(text.encode()).hexdigest());view['project_root']='explicit-fixture-project'
 question='For ISSUE-VERIFY, return JSON decision (adopt/adapt/reject/defer) and reason using the exact text after Reason: without the final period. No tools.\n'
 return {'report':{'run_id':'five-advice-view'},'oracle':{'decision':'defer','reason':'independent verification pending'},'prompts':{'baseline':question+text,'candidate':question+json.dumps(view,separators=(',',':'))}}
def replay(root):
 data=build(root);assert 'Human GUIDE overrides advice' in data['prompts']['candidate']
 assert 'Decision: defer' in data['prompts']['candidate'] and '## ISSUE-0' not in data['prompts']['candidate']
 return {'selected_issue':'ISSUE-VERIFY','leading_priority_retained':True,'omitted_sections':11}
