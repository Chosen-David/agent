"""Full route authority must survive predicate optimization and duplicate retries."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from agent_runtime.communication import Mailbox

class RouteAuthorityTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name);(self.root/'data').write_bytes(b'evidence')
        def route(sender,recipient,task,kind):return dict(sender=sender,recipient=recipient,task_id=task,kind=kind)
        self.plan=dict(schema_version=1,run_id='route',input_version='v1',routes=[
            route('s','z','T','artifact'),route('other','wrong-s','T','artifact'),
            route('s','wrong-t','other','artifact'),route('s','wrong-k','T','question'),
            route('s','a','T','artifact')])
        self.box=Mailbox(self.root/'db',self.plan,self.root)
        self.event=dict(event_id='one',run_id='route',input_version='v1',sender='s',task_id='T',kind='artifact',summary='Read evidence',action='Verify artifact',refs=[dict(id='data',path='data',sha256=hashlib.sha256(b'evidence').hexdigest())])

    def test_all_route_fields_and_fanout_are_required(self):
        sent=self.box.publish(self.event)
        self.assertEqual(sent['recipients'],['a','z'])
        for r in ['wrong-s','wrong-t','wrong-k']:
            self.assertEqual(self.box.inbox(r),[])
        for r in ['a','z']:
            self.assertEqual(self.box.inbox(r),[dict(seq=sent['seq'],event=self.event)])
        self.assertEqual(self.box.usage()['deliveries'],2)

    def test_duplicate_still_checks_current_routes(self):
        sent=self.box.publish(self.event);before=self.box.usage()
        original=self.box.plan['routes']
        self.box.plan['routes']=[r for r in original if r['recipient'].startswith('wrong-')]
        with self.assertRaisesRegex(ValueError,'no approved consumer route'):
            self.box.publish(dict(self.event))
        self.assertEqual(self.box.usage(),before)
        self.box.plan['routes']=original
        retry=self.box.publish(dict(self.event))
        self.assertEqual(retry,dict(seq=sent['seq'],recipients=['a','z'],duplicate=True))
        self.assertEqual(self.box.usage(),before)

if __name__=='__main__':unittest.main()
