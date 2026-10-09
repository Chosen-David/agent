"""Public boundary counterexamples discovered during communication candidate review."""
from copy import deepcopy
import hashlib
from pathlib import Path
import tempfile
import unittest

from agent_runtime.communication import Mailbox


class CommunicationRegressionTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.plan = dict(schema_version=1, run_id='regression', input_version='v1',
                         routes=[dict(sender='s', recipient='r', task_id='T', kind='artifact')])
        self.path = self.root / 'messages.db'

    def test_reopen_with_normalized_nested_numeric_plan_keys(self):
        self.plan['extension'] = {1: 'one', 2: 'two', 10: 'ten'}
        box = Mailbox(self.path, self.plan, self.root)
        self.assertEqual(box.plan['extension'], {'1': 'one', '2': 'two', '10': 'ten'})
        # Both the caller's original plan and the exposed frozen plan remain restartable.
        for plan in (self.plan, deepcopy(box.plan)):
            reopened = Mailbox(self.path, plan, self.root)
            self.assertEqual(reopened.plan, box.plan)
            self.assertEqual(reopened.inbox('r'), [])

    def test_duplicate_retry_revalidates_mutated_reference_without_writes(self):
        artifact = self.root / 'data.txt'
        artifact.write_bytes(b'original')
        event = dict(event_id='once', run_id='regression', input_version='v1',
                     sender='s', task_id='T', kind='artifact', summary='Read artifact',
                     action='Read and verify the reference',
                     refs=[dict(id='data', path='data.txt',
                                sha256=hashlib.sha256(b'original').hexdigest())])
        box = Mailbox(self.path, self.plan, self.root)
        sent = box.publish(event)
        before = box.usage()
        artifact.write_bytes(b'changed')
        with self.assertRaises(ValueError):
            box.publish(deepcopy(event))
        self.assertEqual(box.usage(), before)
        self.assertEqual(box.inbox('r'), [{'seq': sent['seq'], 'event': event}])


if __name__ == '__main__':
    unittest.main()
