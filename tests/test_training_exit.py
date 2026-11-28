import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from agent_runtime.training_claim import deliver_training_exit


class TrainingExitTests(unittest.TestCase):
    def test_observe_and_route_only_confirmed_attempt(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'claims.db'
            success, failure = Mock(), Mock()
            def deliver():
                return deliver_training_exit(path, 'job', 'first', on_success=(success, 'analysis'),
                                             on_failure=(failure, 'diagnosis'))
            with sqlite3.connect(path) as db:
                db.execute('CREATE TABLE training_claims(claim, owner, status, rc)')
                db.execute("INSERT INTO training_claims VALUES('job','first','running',NULL)")
                db.commit()
                self.assertIsNone(deliver())
                success.tick.assert_not_called()
                failure.tick.assert_not_called()
                db.execute("UPDATE training_claims SET status='awaiting-validation',rc=0")
                db.commit()
                deliver()
                deliver()
                self.assertEqual(success.tick.call_args_list[0], success.tick.call_args_list[1])
                db.execute("UPDATE training_claims SET status='failed',rc=1")
                db.commit()
                deliver()
                self.assertEqual(failure.tick.call_args.args[0], 'diagnosis')
                db.execute("UPDATE training_claims SET owner='new-attempt'")
                db.commit()
                with self.assertRaisesRegex(ValueError, 'superseded'):
                    deliver()
