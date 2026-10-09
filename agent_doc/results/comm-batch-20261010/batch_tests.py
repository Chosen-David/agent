"""Atomic batch correctness contracts; no latency claims."""
import copy,json,sqlite3,tempfile,unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from agent_runtime.communication import Mailbox,canonical
import hashlib

class BatchTests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name)
        (self.root/'ref').write_bytes(b'evidence')
        self.plan=dict(schema_version=1,run_id='batch',input_version='v1',routes=[dict(sender='s',recipient=r,task_id='T',kind='artifact') for r in ['z','a']])
        self.box=Mailbox(self.root/'db',self.plan,self.root)
        self.event=dict(event_id='one',run_id='batch',input_version='v1',sender='s',task_id='T',kind='artifact',summary='界',action='Verify',refs=[dict(id='ref',path='ref',sha256=hashlib.sha256(b'evidence').hexdigest())])
    def ev(self,i,**kw):return dict(self.event,event_id=str(i),**kw)
    def state(self):
        with self.box.connect() as db:
            return {t:[list(r) for r in db.execute('SELECT * FROM '+t+' ORDER BY 1,2')] for t in ['communication_events','communication_deliveries','communication_usage_v1','communication_basis','sqlite_sequence']}
    def assert_atomic_failure(self,events,error=ValueError):
        old=self.state()
        with self.assertRaises(error):self.box.publish_many(events)
        self.assertEqual(self.state(),old)
    def test_order_fanout_duplicate_and_exact_unicode_usage(self):
        events=[self.ev(1),self.ev(2),self.ev(1)]
        rows=self.box.publish_many(events)
        self.assertEqual([r['seq'] for r in rows],[1,2,1]);self.assertEqual([r['duplicate'] for r in rows],[False,False,True])
        self.assertTrue(all(r['recipients']==['a','z'] for r in rows))
        for r in ['a','z']:self.assertEqual(self.box.inbox(r),[dict(seq=i+1,event=e) for i,e in enumerate(events[:2])])
        size=sum(len(canonical(e).encode()) for e in events[:2]);u=self.box.usage()
        self.assertEqual((u['events'],u['envelope_bytes'],u['deliveries'],u['delivery_bytes']),(2,size,4,2*size));self.assertIsNone(u['tokens'])
        self.assertEqual(Mailbox(self.root/'db',self.plan,self.root).status(),self.box.status())
    def test_all_invalid_midbatch_paths_roll_back(self):
        invalid=[self.ev(2,sender='other'),self.ev(2,task_id='wrong'),self.ev(2,kind='question'),self.ev(2,run_id='other'),self.ev(2,input_version='old'),self.ev(2,refs=[]),self.ev(2,summary=''),dict(self.ev(2),extra=True)]
        for bad in invalid:
            with self.subTest(bad=bad):self.assert_atomic_failure([self.ev(1),bad])
        self.assert_atomic_failure([self.ev(1),dict(self.ev(1),summary='conflict')])
        self.assert_atomic_failure([self.ev(1),None])
    def test_limits_and_cumulative_budget_rollback(self):
        for x in [[],{},(self.ev(1),),[self.ev(i) for i in range(101)]]:self.assert_atomic_failure(x)
        self.box.plan['max_events']=1;self.assert_atomic_failure([self.ev(1),self.ev(2)])
        self.box.publish(self.ev(1));old=self.state()
        self.assertTrue(self.box.publish_many([self.ev(1)])[0]['duplicate']);self.assertEqual(self.state(),old)
        self.assert_atomic_failure([self.ev(1),self.ev(2)])
    def test_delivery_and_message_budgets(self):
        size=len(canonical(self.ev(1)).encode());self.box.plan['max_delivery_bytes']=size*3
        self.assert_atomic_failure([self.ev(1),self.ev(2)])
        self.box.plan['max_message_bytes']=size-1;self.assert_atomic_failure([self.ev(1)])
    def test_duplicate_revalidates_refs_and_current_routes(self):
        self.box.publish(self.ev(1));(self.root/'ref').write_bytes(b'changed')
        self.assert_atomic_failure([self.ev(1)])
        (self.root/'ref').write_bytes(b'evidence');self.box.plan['routes'][0]['task_id']='other';self.box.plan['routes'][1]['task_id']='other'
        self.assert_atomic_failure([self.ev(1)])
    def test_cross_thread_batch_retries_and_connection_recovery(self):
        events=[self.ev(1),self.ev(2)]
        with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(lambda _:self.box.publish_many(copy.deepcopy(events)),range(4)))
        self.assertEqual(sum(not r['duplicate'] for batch in rows for r in batch),2);self.assertEqual(self.box.usage()['events'],2)
        self.assert_atomic_failure([self.ev(3),self.ev(1,summary='conflict')])
        self.assertFalse(self.box.publish_many([self.ev(3)])[0]['duplicate'])
    def test_cap_100_is_accepted(self):
        self.assertEqual(len(self.box.publish_many([self.ev(i) for i in range(100)])),100)
    def test_cli_batch_entry_and_failure_exit(self):
        import subprocess,sys
        (self.root/'plan.json').write_text(json.dumps(self.plan));(self.root/'events.json').write_text(json.dumps([self.ev(1),self.ev(2)]))
        command=[sys.executable,'-m','agent_runtime.communication','--db',str(self.root/'cli.db'),'--plan',str(self.root/'plan.json'),'--root',str(self.root),'publish-many',str(self.root/'events.json')]
        run=subprocess.run(command,capture_output=True,text=True);self.assertEqual(run.returncode,0,run.stdout+run.stderr);self.assertEqual(len(json.loads(run.stdout)),2)
        (self.root/'events.json').write_text('[]');bad=subprocess.run(command,capture_output=True,text=True);self.assertEqual(bad.returncode,1);self.assertIn('error',json.loads(bad.stdout))
