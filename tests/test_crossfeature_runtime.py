"""New holdouts supplement existing runtime faults, with real SQLite/artifact reads."""
import hashlib
import tempfile
from pathlib import Path
import unittest

from agent_runtime.core import ArtifactHandler, Engine, Outcome, Store
from scripts.validate_handoff import validate


def plan():
    return {'schema_version': 'task-dag/v1', 'run_id': 'boundary',
            'user_goal': 'synthetic lease boundary', 'authorization_reference': 'local test',
            'supervision': {'min_seconds': 1, 'max_seconds': 60, 'rationale': 'bounded'},
            'tasks': [{'task_id': 'a', 'action': 'synthetic', 'owner': 'test',
                       'done_when': {'test': True}, 'max_attempts': 3,
                       'estimated_seconds': 20, 'risk': 'low'}]}


class CrossfeatureRuntime(unittest.TestCase):
    def test_exact_expiry_restart_rejects_old_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / 'state.sqlite'
            store = Store(db); store.create(plan())
            now = [100.0]
            contexts = []
            class Handler:
                idempotent = True
                required_capabilities = frozenset()
                def run(self, task, context):
                    contexts.append(context)
                    if len(contexts) == 1:
                        now[0] = 105.0  # Exact equality is expired, not live.
                    return Outcome('complete', evidence=[{'synthetic': True}])
                def verify(self, task, evidence):
                    return evidence == [{'synthetic': True}]
            handler = Handler()
            engine = Engine(store, {'synthetic': handler}, authorize=lambda *_: True,
                            clock=lambda: now[0], lease_seconds=5)
            self.assertEqual(engine.tick('boundary', 'old')['tasks']['a']['status'], 'doing')
            self.assertFalse(contexts[0].current())
            recovered = Engine(Store(db), {'synthetic': handler}, authorize=lambda *_: True,
                               clock=lambda: now[0], lease_seconds=5)
            self.assertEqual(recovered.tick('boundary', 'old')['tasks']['a']['attempts'], 1)
            self.assertEqual(recovered.tick('boundary', 'new')['status'], 'done')
            self.assertEqual(len(contexts), 2)
            self.assertEqual(contexts[0].idempotency_key, contexts[1].idempotency_key)
            self.assertNotEqual(contexts[0].token, contexts[1].token)
            with store.transaction() as conn:
                self.assertEqual(conn.execute("SELECT count(*) FROM journal WHERE kind='stale_result_rejected'").fetchone()[0], 1)

    def test_missing_then_good_then_tampered_real_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); handler = ArtifactHandler(root)
            task = {'done_when': {'artifacts': [{'path': 'payload.dat',
                    'sha256': hashlib.sha256(b'synthetic result').hexdigest()}]}}
            self.assertEqual(handler.run(task, None).status, 'pending')
            (root / 'payload.dat').write_bytes(b'synthetic result')
            actual = handler.run(task, None)
            self.assertEqual(actual.status, 'complete')
            self.assertTrue(handler.verify(task, actual.evidence))
            (root / 'payload.dat').write_bytes(b'other result')
            with self.assertRaisesRegex(ValueError, 'digest'):
                handler.verify(task, actual.evidence)

    def test_empty_artifact_is_integrity_only_holdout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / 'payload').write_bytes(b'')
            task = {'done_when': {'artifacts': [{'path': 'payload',
                    'sha256': hashlib.sha256(b'').hexdigest()}]}}
            handler = ArtifactHandler(root)
            self.assertTrue(handler.verify(task, handler.run(task, None).evidence))

    def test_handoff_real_bytes_good_and_corrupt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / 'result').write_bytes(b'result v1')
            record = {'schema_version': 1, 'run_id': 'test', 'role': 'writer',
                      'input_version': 'v1', 'status': 'completed', 'limitations': [],
                      'artifacts': [{'id': 'a', 'path': 'result',
                                     'sha256': hashlib.sha256(b'result v1').hexdigest()}],
                      'checks': [{'criterion': 'local bytes', 'status': 'pass', 'artifact_ids': ['a']}]}
            self.assertEqual(validate(record, root, True, expected_input_version='v1', consumer_request={'schema_version':1,'input_version':'v1','tasks':[]}), [])
            (root / 'result').write_bytes(b'result v2')
            self.assertIn('artifact 0: sha256 mismatch', validate(record, root, True, expected_input_version='v1', consumer_request={'schema_version':1,'input_version':'v1','tasks':[]}))


if __name__ == '__main__':
    unittest.main()
