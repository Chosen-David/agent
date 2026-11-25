import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime.scheduled_review import codex_timer_reviewer


class OwnerHandoff(unittest.TestCase):
    def test_review_persisted_before_owner_queue(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            callback = codex_timer_reviewer(root, profile='profile', writer_model='writer',
                reviewer_model='reviewer', owner_thread='owner', owner_socket=root / 'socket',
                evidence=lambda run: {'requirement': run})
            with patch.dict('os.environ', {'AGENT_DOC_ROOT': ''}), \
                 patch('agent_runtime.scheduled_review.load_profile', return_value={
                     'command': ['/codex'], 'timeout_seconds': 10}), \
                 patch('agent_runtime.scheduled_review.AppServer') as server, \
                 patch('agent_runtime.scheduled_review.subprocess.run') as queue:
                server.return_value.run.return_value = ({'model_id': 'reviewer', 'context_id': 'new'},
                    {'findings': 'pending', 'next_step': 'implement'}, {'status': 'completed'})
                def deliver(command, **kwargs):
                    self.assertEqual(command[:4], ['/codex', 'queue', '--thread', 'owner'])
                    self.assertEqual(command[-1], 'unix://' + str(root / 'socket'))
                    record, = (root / 'agent_doc/advice').glob('*.json')
                    self.assertEqual(json.loads(record.read_text())['event_id'], 'event')
                    return SimpleNamespace(returncode=0, stderr='wake unconfirmed')
                queue.side_effect = deliver
                self.assertEqual(callback('run', 'event')['delivery'], 'queued_unconfirmed')
                server.return_value.close.assert_called_once()
