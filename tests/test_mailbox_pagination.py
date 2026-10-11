"""Long pending queues remain browsable without acknowledging unseen evidence."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

from agent_runtime.communication import KINDS, Mailbox, canonical


def long_fixture(root, count=120, *, mailbox_type=Mailbox, observe=None):
    """Public synthetic facts; revisions and unresolved objections are explicit."""
    raw=('\n'.join(f'FACT-{i:03d}: value={i}; condition=synthetic; source=fixture-v1. '
                   + ('Long evidence paragraph. ' * 24) for i in range(count))
         +'\nREV-118 contradicts FACT-018: value remains unknown pending repair.\n').encode()
    (root/'dossier.txt').write_bytes(raw)
    ref={'id':'dossier','path':'dossier.txt','sha256':hashlib.sha256(raw).hexdigest()}
    plan={'schema_version':1,'run_id':'long-navigation','input_version':'fixture-v1',
          'max_events':1000,'max_message_bytes':8192,'routes':[
              dict(sender=s,recipient=r,task_id=t,kind=k)
              for s in ('retrieval','review','repair') for r in ('main','independent')
              for t in ('T1','T2') for k in sorted(KINDS)]}
    box=mailbox_type(root/'mail.sqlite',plan,root)
    events=[];deliveries=[]
    for i in range(count):
        event=dict(event_id=f'E-{i:03d}',run_id=plan['run_id'],input_version=plan['input_version'],
                   sender=('retrieval','review','repair')[i%3],task_id='T2' if i%7==0 else 'T1',
                   kind=sorted(KINDS)[i%len(KINDS)],summary=f'FACT-{i:03d}; '+('Evidence retained. '*65),
                   action='Read exact dossier and preserve unresolved conditions.',refs=[ref.copy()])
        if i==118:
            event.update(kind='correction',summary='REV-118 contradicts FACT-018; value unknown, rerun required.')
        start=time.perf_counter_ns();delivery=box.publish(event);elapsed=time.perf_counter_ns()-start
        events.append(event);deliveries.append(delivery)
        if observe:observe(event,delivery,elapsed)
    return box,plan,events,deliveries


class PaginationTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.root=Path(temp.name)
        self.box,self.plan,self.events,self.deliveries=long_fixture(self.root)

    def test_long_full_coverage_exact_bodies_and_pending_state(self):
        before=self.box.status();usage=self.box.usage();cursor=0;seen=[];kinds=set()
        while True:
            page=self.box.inbox_index('main',limit=17,after_seq=cursor)
            self.assertEqual(page['after_seq'],cursor)
            for row in page['items']:
                actual=self.box.read_pending('main',row['seq'],row['body_sha256'])
                self.assertEqual(actual['event'],self.events[len(seen)])
                seen.append(row['seq']);kinds.add(actual['event']['kind'])
            self.assertEqual(page['next_after_seq'],seen[-1])
            cursor=page['next_after_seq']
            if not page['has_more']:break
        self.assertEqual(seen,[d['seq'] for d in self.deliveries]);self.assertEqual(kinds,KINDS)
        self.assertEqual(self.box.status(),before);self.assertEqual(self.box.usage(),usage)
        empty=self.box.inbox_index('main',after_seq=cursor)
        self.assertEqual(empty['items'],[]);self.assertEqual(empty['next_after_seq'],cursor)

    def test_cursor_before_limit_both_sql_branches_and_scope(self):
        for count in (3,120):
            with self.subTest(count=count),tempfile.TemporaryDirectory() as tmp:
                box,plan,events,ds=long_fixture(Path(tmp),count)
                rows=box.inbox('main',limit=20,task_id='T1',after_seq=ds[0]['seq'])
                expected=[{'seq':d['seq'],'event':e} for d,e in zip(ds,events)
                          if d['seq']>ds[0]['seq'] and e['task_id']=='T1'][:20]
                self.assertEqual(rows,expected)
                self.assertEqual(box.inbox('independent',limit=20,task_id='T1',after_seq=ds[0]['seq']),expected)
                foreign=Mailbox(box.path,dict(plan,run_id='foreign'),Path(tmp))
                self.assertEqual(foreign.inbox('main',after_seq=ds[0]['seq']),[])

    def test_resume_retry_and_lookahead_are_not_skipped(self):
        page=self.box.inbox_index('main',limit=20)
        self.assertEqual(page['next_after_seq'],self.deliveries[19]['seq'])
        self.assertEqual(self.box.inbox_index('main',limit=20),page)
        restarted=Mailbox(self.box.path,self.plan,self.root)
        next_page=restarted.inbox_index('main',limit=20,after_seq=page['next_after_seq'])
        self.assertEqual(next_page['items'][0]['seq'],self.deliveries[20]['seq'])
        usage=self.box.usage();retry=restarted.publish(self.events[0])
        self.assertTrue(retry['duplicate']);self.assertEqual(self.box.usage(),usage)

    def test_append_ack_correction_missing_and_body_version(self):
        page=self.box.inbox_index('main',limit=20)
        removed=self.deliveries[20]['seq']
        self.box.acknowledge('main',removed,{'status':'needs_revision','reason':'synthetic review'})
        second=self.box.inbox_index('main',limit=20,after_seq=page['next_after_seq'])
        self.assertEqual(second['items'][0]['seq'],self.deliveries[21]['seq'])
        # ACK for one recipient must not hide the same event from another.
        other=self.box.inbox_index('independent',limit=20,after_seq=page['next_after_seq'])
        self.assertEqual(other['items'][0]['seq'],removed)
        with self.assertRaises(ValueError):self.box.read_pending('main',removed,other['items'][0]['body_sha256'])
        last=self.deliveries[-1]['seq']
        self.assertFalse(self.box.inbox_index('main',after_seq=last)['has_more'])
        new=dict(self.events[-1],event_id='REV-NEW',kind='correction',summary='Missing value; old result invalid.')
        seq=self.box.publish(new)['seq']
        appended=self.box.inbox_index('main',after_seq=last)
        self.assertEqual(appended['items'][0]['seq'],seq)
        row=appended['items'][0]
        with self.assertRaises(ValueError):self.box.read_pending('main',seq,'0'*64)
        self.assertEqual(self.box.read_pending('main',seq,row['body_sha256'])['event'],new)
        with self.assertRaises(ValueError):self.box.read_pending('main',seq+1000,row['body_sha256'])

    def test_validation_and_display_budget_remain_fail_closed(self):
        for value in (-1,True,1.5,'1',None,2**63):
            for method in (self.box.inbox,self.box.inbox_index):
                with self.subTest(value=value,method=method.__name__),self.assertRaises(ValueError):
                    method('main',after_seq=value)
        self.assertEqual(self.box.inbox('main',after_seq=2**63-1),[])
        before=self.box.status()
        with self.assertRaises(ValueError):self.box.inbox_index('main',after_seq=1,max_chars=1)
        with self.assertRaises(ValueError):self.box.inbox_index('unknown',after_seq=1)
        with self.assertRaises(ValueError):self.box.inbox_index('main',task_id='unknown',after_seq=1)
        self.assertEqual(self.box.status(),before)

    def test_cli_pages_and_invalid_cursor(self):
        plan=self.root/'plan.json';plan.write_text(json.dumps(self.plan))
        base=[sys.executable,'-m','agent_runtime.communication','--root',str(self.root),
              '--plan',str(plan),'--db',str(self.box.path)]
        for command in ('inbox','inbox-index'):
            run=subprocess.run(base+[command,'main','--after-seq',str(self.deliveries[99]['seq'])],capture_output=True,text=True,timeout=10)
            self.assertEqual(run.returncode,0,run.stderr)
            value=json.loads(run.stdout);rows=value['items'] if command=='inbox-index' else value
            self.assertEqual([r['seq'] for r in rows],[d['seq'] for d in self.deliveries[100:]])
            bad=subprocess.run(base+[command,'main','--after-seq','-1'],capture_output=True,text=True,timeout=10)
            self.assertEqual(bad.returncode,1);self.assertIn('error',json.loads(bad.stdout))

    def test_stale_artifact_retry_fails_and_restoration_recovers(self):
        page=self.box.inbox_index('main',after_seq=self.deliveries[99]['seq'])
        usage=self.box.usage();path=self.root/'dossier.txt';original=path.read_bytes()
        path.write_bytes(original+b'changed revision')
        with self.assertRaises(ValueError):self.box.publish(self.events[100])
        self.assertEqual(self.box.usage(),usage)
        path.write_bytes(original)
        self.assertTrue(self.box.publish(self.events[100])['duplicate'])
        self.assertEqual(self.box.inbox_index('main',after_seq=self.deliveries[99]['seq']),page)
