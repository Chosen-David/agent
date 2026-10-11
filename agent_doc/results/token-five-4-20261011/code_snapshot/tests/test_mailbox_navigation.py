import hashlib,json,tempfile,unittest
from pathlib import Path
from agent_runtime.communication import Mailbox

def fixture(root):
    plan={'schema_version':1,'run_id':'nav-run','input_version':'v1','max_events':20,'max_message_bytes':8192,
          'routes':[{'sender':'code','recipient':r,'task_id':t,'kind':k}
                    for r in ('main','reviewer') for t in ('T1','T2') for k in ('artifact','blocker','review')]}
    box=Mailbox(root/'mailbox.sqlite',plan,root)
    (root/'evidence.json').write_bytes(b'{"validation":"pending"}')
    ref={'id':'pending','path':'evidence.json','sha256':hashlib.sha256((root/'evidence.json').read_bytes()).hexdigest()}
    for i,kind in enumerate(('artifact','blocker','review'),1):
        summary='Pending result; see exact evidence. '+(' '.join(f'observation{j:02d}' for j in range(25)) if i!=2 else 'Independent verification is pending.')
        box.publish({'event_id':f'e{i}','run_id':'nav-run','input_version':'v1','sender':'code','task_id':'T1','kind':kind,'summary':summary,'action':'Inspect evidence; do not publish pending data','refs':[ref]})
    return box

class MailboxNavigationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve();self.box=fixture(self.root)
    def test_navigation_exact_order_and_restore(self):
        full=self.box.inbox('main');index=self.box.inbox_index('main')
        self.assertFalse(index['has_more']);self.assertEqual([x['kind'] for x in index['items']],['artifact','blocker','review'])
        for row,expected in zip(index['items'],full):
            self.assertNotIn('summary',row);self.assertNotIn('refs',row)
            self.assertEqual(self.box.read_pending('main',row['seq'],row['body_sha256']),expected)
        self.assertEqual(self.box.inbox('main'),full)
    def test_limit_has_more_and_budget(self):
        self.assertTrue(self.box.inbox_index('main',limit=1)['has_more'])
        for kwargs in ({'limit':100},{'limit':True},{'max_chars':1}):
            with self.assertRaises(ValueError):self.box.inbox_index('main',**kwargs)
    def test_receipts_cannot_suppress_other_receiver(self):
        row=self.box.inbox_index('main')['items'][0]
        self.box.acknowledge('main',row['seq'],{'status':'consumed','reason':'inspected'})
        with self.assertRaises(ValueError):self.box.read_pending('main',row['seq'],row['body_sha256'])
        self.assertEqual(self.box.read_pending('reviewer',row['seq'],row['body_sha256'])['seq'],row['seq'])
    def test_bad_versions_and_unknown_recipient(self):
        row=self.box.inbox_index('main')['items'][0]
        for recipient,seq,sha in (('unknown',row['seq'],row['body_sha256']),('main',row['seq'],'0'*64),('main',True,row['body_sha256'])):
            with self.assertRaises(ValueError):self.box.read_pending(recipient,seq,sha)
    def test_explicit_other_task_is_not_global_clearance(self):
        self.assertEqual(self.box.inbox_index('main',task_id='T2')['items'],[])
        self.assertEqual(len(self.box.inbox('main')),3)
        with self.assertRaises(ValueError):self.box.inbox_index('main',task_id='unknown')
