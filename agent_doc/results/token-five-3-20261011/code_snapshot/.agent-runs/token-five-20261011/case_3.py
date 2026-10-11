import hashlib,json,tempfile
from pathlib import Path
SOURCES=['agent_runtime/log_context.py','scripts/log_context.py','tests/test_log_context.py','agent_runtime/maintenance_observer.py','agent_runtime/advice_poll.py']
TESTS=['tests.test_log_context'];COUNT=6
SCOPE='One 32-line log fixture with exact head/tail and all declared ERROR matches; preserves the blocking verification signal; no proof about unspecified errors or long-context/cash savings'
MECHANISM='Recoverable literal-match/head/tail log view; never silently truncate selected evidence'
def build(root):
 from agent_runtime.log_context import log_view
 lines=[f'INFO worker={i:02d} retry=0 state=running cache=warm\n' for i in range(32)]
 lines[15]='ERROR BLOCK_VERIFY result verification pending\n';text=''.join(lines)
 with tempfile.TemporaryDirectory() as d:
  r=Path(d).resolve();(r/'job.log').write_bytes(text.encode())
  view=log_view(r,'job.log',hashlib.sha256(text.encode()).hexdigest(),needles=['ERROR'],head=1,tail=1,context=0)
  view['project_root']='explicit-fixture-project'
 question='Return JSON with publish=false and blockers listing codes from ERROR rows, if any. Otherwise publish=true, blockers=[]. Use exact blocker codes. No tools.\n'
 return {'report':{'run_id':'five-log-view'},'oracle':{'publish':False,'blockers':['BLOCK_VERIFY']},'prompts':{'baseline':question+text,'candidate':question+json.dumps(view,separators=(',',':'))}}
def replay(root):
 data=build(root);assert 'BLOCK_VERIFY' in data['prompts']['candidate']
 assert 'worker=14' not in data['prompts']['candidate'] and 'worker=31' in data['prompts']['candidate']
 return {'blocking_code_retained':'BLOCK_VERIFY','omitted_lines':29,'literal_matches':1}
