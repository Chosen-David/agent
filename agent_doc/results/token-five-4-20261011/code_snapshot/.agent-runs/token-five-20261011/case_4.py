import json,tempfile
from pathlib import Path
SOURCES=['agent_runtime/communication.py','tests/test_mailbox_navigation.py','scripts/validate_handoff.py']
TESTS=['tests.test_mailbox_navigation'];COUNT=5
SCOPE='One three-message pending mailbox fixture; metadata navigates to the blocker, then exact pending body retrieval is CPU-checked; no ACK, scientific validity or global clearance claim'
MECHANISM='Pending inbox metadata navigation plus exact body-version retrieval instead of reinjecting all summaries/actions/references'
def build(root):
 from tests.test_mailbox_navigation import fixture
 with tempfile.TemporaryDirectory() as d:
  box=fixture(Path(d).resolve());full=box.inbox('main');index=box.inbox_index('main');index['project_root']='explicit-fixture-project'
 question='Which seq is the earliest pending blocker for T1 to inspect next? Return JSON with inspect_seq (integer). Metadata only navigates; no publication or evidence acceptance. No tools.\n'
 return {'report':{'run_id':'five-mailbox-index'},'oracle':{'inspect_seq':2},'prompts':{'baseline':question+json.dumps(full,separators=(',',':')),'candidate':question+json.dumps(index,separators=(',',':'))}}
def replay(root):
 from tests.test_mailbox_navigation import fixture
 with tempfile.TemporaryDirectory() as d:
  box=fixture(Path(d).resolve());index=box.inbox_index('main');blocker=[x for x in index['items'] if x['kind']=='blocker'][0]
  restored=box.read_pending('main',blocker['seq'],blocker['body_sha256'])
  assert restored['event']['kind']=='blocker' and 'verification' in restored['event']['summary']
  assert len(box.inbox('main'))==3
 return {'selected_seq':2,'restored_blocker':True,'pending_deliveries_preserved':3}
