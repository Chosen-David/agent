"""Real SQLite and file IO; synthetic research handoffs, no model-quality claims."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from agent_runtime.communication import Mailbox


class CommunicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.plan = dict(schema_version=1, run_id='study', input_version='data:v1',
                         max_events=10, max_message_bytes=8192, routes=[
            dict(sender='code', recipient='writer', task_id='T1', kind='artifact'),
            dict(sender='code', recipient='reviewer', task_id='T1', kind='artifact'),
            dict(sender='reviewer', recipient='code', task_id='T1', kind='review')])
        self.db = self.root/'inbox.sqlite'
        self.box = Mailbox(self.db, self.plan, self.root)
        self.ref = self.save('result.json', {'seconds': 2.5, 'kind': 'synthetic'}, 'result')
        self.request = dict(schema_version=1, input_version='data:v1', tasks=[{'task_id': 'T1'}])
        self.record = dict(schema_version=1, run_id='study', role='code', input_version='data:v1',
            status='completed', limitations=[], artifacts=[self.ref],
            checks=[dict(criterion='fixture exists', status='pass', artifact_ids=['result'])],
            tasks=[dict(task_id='T1', status='done', depends_on=[], evidence=['result'])])
        self.manifest = self.save('handoff.json', self.record, 'handoff')
        self.event = dict(event_id='result:1', run_id='study', input_version='data:v1',
            sender='code', task_id='T1', kind='artifact', summary='Synthetic result available',
            action='Read the measured field and check scope before using it', refs=[self.manifest])

    def save(self, path, value, aid):
        data = json.dumps(value).encode()
        (self.root/path).write_bytes(data)
        return dict(id=aid, path=path, sha256=hashlib.sha256(data).hexdigest())

    def test_research_handoff_and_review_roundtrip(self):
        sent = self.box.publish(self.event)
        self.assertEqual(sent['recipients'], ['reviewer', 'writer'])
        self.assertEqual(self.box.inbox('code'), [])
        received = self.box.consume_handoff('writer', sent['seq'], self.request)
        self.assertEqual(received['artifacts'], [self.ref])
        # Handling one subscriber's delivery must not suppress another's.
        self.box.acknowledge('writer', sent['seq'], {'status': 'consumed', 'reason': 'Fixture parsed'})
        self.assertEqual(self.box.inbox('writer'), [])
        self.assertEqual(len(self.box.inbox('reviewer')), 1)
        review = dict(self.event, event_id='review:1', sender='reviewer', kind='review',
                      refs=[self.save('review.json', {'finding_id': 'F1', 'required_test': 'add variance'}, 'F1')])
        self.box.publish(review)
        self.assertEqual(self.box.inbox('code')[0]['event']['event_id'], 'review:1')

    def test_restart_and_duplicate_retry(self):
        first = self.box.publish(self.event)
        restarted = Mailbox(self.db, self.plan, self.root)
        second = restarted.publish(deepcopy(self.event))
        self.assertTrue(second['duplicate'])
        self.assertEqual(first['seq'], second['seq'])
        self.assertEqual(len(restarted.inbox('writer')), 1)
        with self.assertRaisesRegex(ValueError, 'different content'):
            restarted.publish(dict(self.event, summary='changed'))

    def test_concurrent_publish_is_atomic(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: self.box.publish(self.event), range(16)))
        self.assertEqual(sum(not r['duplicate'] for r in results), 1)
        self.assertEqual(len(self.box.status()), 2)

    def test_stale_and_unrouted_messages_rejected(self):
        for change in ({'input_version': 'data:v0'}, {'run_id': 'elsewhere'},
                       {'sender': 'reader'}, {'task_id': 'T2'}, {'kind': 'question'}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.box.publish(dict(self.event, **change))
        self.assertEqual(self.box.status(), [])

    def test_no_plan_mutation_and_new_run_isolation(self):
        self.box.publish(self.event)
        changed = deepcopy(self.plan); changed['input_version'] = 'v2'
        with self.assertRaisesRegex(ValueError, 'plan/root changed'):
            Mailbox(self.db, changed, self.root)
        changed['run_id'] = 'next'
        other = Mailbox(self.db, changed, self.root)
        self.assertEqual(other.inbox('writer'), [])
        with self.assertRaises(ValueError):
            other.acknowledge('writer', 1, {'status': 'consumed', 'reason': 'wrong run'})

    def test_reference_changed_after_delivery(self):
        seq = self.box.publish(self.event)['seq']
        (self.root/'result.json').write_text('changed artifact')
        with self.assertRaisesRegex(ValueError, 'sha256 mismatch'):
            self.box.consume_handoff('writer', seq, self.request)
        self.assertEqual(len(self.box.inbox('writer')), 1)

    def test_manifest_changed_after_delivery(self):
        seq = self.box.publish(self.event)['seq']
        (self.root/'handoff.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'sha256 mismatch'):
            self.box.consume_handoff('writer', seq, self.request)

    def test_scope_mismatch_does_not_ack(self):
        seq = self.box.publish(self.event)['seq']
        request = dict(self.request, tasks=[{'task_id': 'T1'}, {'task_id': 'T2'}])
        with self.assertRaisesRegex(ValueError, 'consumer task missing'):
            self.box.consume_handoff('writer', seq, request)
        self.assertIsNone(self.box.status()[0]['receipt'])

    def test_wrong_manifest_identity(self):
        self.record['role'] = 'someone-else'
        self.event['refs'] = [self.save('handoff.json', self.record, 'handoff')]
        seq = self.box.publish(self.event)['seq']
        with self.assertRaisesRegex(ValueError, 'producer/run mismatch'):
            self.box.consume_handoff('writer', seq, self.request)

    def test_budget_and_no_partial_delivery(self):
        plan = dict(self.plan, run_id='small', max_events=1)
        box = Mailbox(self.db, plan, self.root)
        event = dict(self.event, run_id='small')
        box.publish(event)
        self.assertTrue(box.publish(event)['duplicate'])
        with self.assertRaisesRegex(ValueError, 'budget exhausted'):
            box.publish(dict(event, event_id='2'))
        with self.assertRaisesRegex(ValueError, 'message budget'):
            self.box.publish(dict(self.event, summary='界'*8192))
        self.assertEqual(len(box.status()), 2)

    def test_path_escape_and_bad_digest(self):
        for refs in ([dict(self.manifest, path='../outside')], [dict(self.manifest, sha256='bad')], []):
            with self.subTest(refs=refs), self.assertRaises(ValueError):
                self.box.publish(dict(self.event, refs=refs))

    def test_ack_is_scoped_immutable_and_not_completion(self):
        seq = self.box.publish(self.event)['seq']
        receipt = {'status': 'needs_revision', 'reason': 'Variance evidence missing'}
        self.box.acknowledge('reviewer', seq, receipt)
        self.box.acknowledge('reviewer', seq, receipt)
        for recipient, value in [('code', receipt), ('writer', {'status': 'done', 'reason': 'ok'}),
                                 ('reviewer', {'status': 'consumed', 'reason': 'changed'})]:
            with self.subTest(recipient=recipient), self.assertRaises(ValueError):
                self.box.acknowledge(recipient, seq, value)

    def test_bounded_ordered_inbox_preserves_pending(self):
        for i in range(5):
            self.box.publish(dict(self.event, event_id=str(i)))
        first = self.box.inbox('writer', limit=2)
        self.assertEqual(len(first), 2)
        self.box.acknowledge('writer', first[0]['seq'], {'status': 'rejected', 'reason': 'duplicate observation'})
        self.assertEqual(self.box.inbox('writer', limit=2)[0], first[1])
        with self.assertRaises(ValueError):
            self.box.inbox('writer', limit=0)

    def test_cli_publish_and_consume(self):
        for name, value in [('plan', self.plan), ('event', self.event), ('request', self.request)]:
            (self.root/(name+'.json')).write_text(json.dumps(value))
        command = [sys.executable, '-m', 'agent_runtime.communication', '--db', str(self.db),
                   '--root', str(self.root), '--plan', str(self.root/'plan.json')]
        result = subprocess.run(command+['publish', str(self.root/'event.json')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        seq = json.loads(result.stdout)['seq']
        result = subprocess.run(command+['consume', 'writer', str(seq), '--request', str(self.root/'request.json')],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        self.assertEqual(json.loads(result.stdout)['artifacts'], [self.ref])


if __name__ == '__main__':
    unittest.main()
