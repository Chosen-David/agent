import json,tempfile,unittest
from pathlib import Path
from agent_runtime.crash_restart import read_crash_state,record_crash

class CrashRestartTests(unittest.TestCase):
    def test_three_failures_persist_and_stop_restarts(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'guard-failure.json'
            self.assertEqual(read_crash_state(p,'run')['failures'],0)
            self.assertEqual(record_crash(p,'run',1)['retry_seconds'],5)
            self.assertEqual(record_crash(p,'run',1)['retry_seconds'],10)
            blocked=record_crash(p,'run',1)
            self.assertEqual(blocked['status'],'blocked');self.assertIsNone(blocked['retry_seconds'])
            self.assertEqual(read_crash_state(p,'run'),blocked)
            self.assertEqual(record_crash(p,'run',2)['failures'],3)
    def test_bad_or_foreign_state_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'guard-failure.json'
            for n in (True,-1,4,None):
                p.write_text(json.dumps({'run_id':'run','failures':n,'status':'retry'}))
                with self.assertRaises(ValueError):read_crash_state(p,'run')
            p.write_text(json.dumps({'run_id':'foreign','failures':1,'status':'retry'}))
            with self.assertRaises(ValueError):read_crash_state(p,'run')
            p.write_text(json.dumps({'run_id':'run','failures':3,'status':'ready'}))
            with self.assertRaises(ValueError):read_crash_state(p,'run')
    def test_zero_or_bool_exit_is_not_a_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'guard-failure.json'
            for code in (0,True,None):
                with self.assertRaises(ValueError):record_crash(p,'run',code)
            self.assertFalse(p.exists())
