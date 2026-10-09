"""Exact accounting, upgrade and failure checks against independent SQL scans."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest

from agent_runtime.communication import Mailbox, canonical

BASELINE = Path(__file__).resolve().parents[1] / 'agent_doc/results/communication-ledger-20261009/baseline_communication.py'


def legacy_mailbox():
    spec = importlib.util.spec_from_file_location('agent_runtime._legacy_usage_test', BASELINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Mailbox


class UsageTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.db = self.root / 'mail.sqlite'
        (self.root / 'note.txt').write_text('source', encoding='utf-8')
        self.plan = dict(schema_version=1, run_id='r', input_version='v', max_events=500,
                         max_delivery_bytes=1000000, routes=[
            dict(sender='a', recipient=r, task_id='t', kind='question') for r in ['b', 'c']])
        self.event = dict(event_id='one', run_id='r', input_version='v', sender='a',
                          task_id='t', kind='question', summary='中文🙂', action='inspect',
                          refs=[dict(id='note', path='note.txt', sha256=hashlib.sha256(b'source').hexdigest())])

    def scan(self, box):
        with sqlite3.connect(self.db) as db:
            bodies = db.execute('SELECT seq,body FROM communication_events WHERE run_id=?', (box.run_id,)).fetchall()
            counts = dict(db.execute('SELECT seq,COUNT(*) FROM communication_deliveries GROUP BY seq'))
        return dict(events=len(bodies), envelope_bytes=sum(len(b.encode('utf-8')) for _, b in bodies),
                    deliveries=sum(counts.get(s, 0) for s, _ in bodies),
                    delivery_bytes=sum(len(b.encode('utf-8'))*counts.get(s, 0) for s, b in bodies))

    def assert_scan(self, box):
        usage = box.usage()
        for key, value in self.scan(box).items():
            self.assertEqual(usage[key], value, key)
        self.assertIsNone(usage['tokens'])

    def test_unicode_retry_ack_restart_and_isolation(self):
        box = Mailbox(self.db, self.plan, self.root)
        self.assert_scan(box)
        sent = box.publish(self.event)
        before = box.usage()
        box.publish(self.event)
        box.acknowledge('b', sent['seq'], dict(status='consumed', reason='handled'))
        self.assertEqual(before, box.usage())
        self.assert_scan(Mailbox(self.db, self.plan, self.root))
        other = Mailbox(self.db, dict(self.plan, run_id='other'), self.root)
        other.publish(dict(self.event, run_id='other'))
        self.assert_scan(other)
        self.assert_scan(box)

    def test_exact_cap_and_rejection_no_partial_counters(self):
        cost = len(canonical(self.event).encode('utf-8')) * 2
        box = Mailbox(self.db, dict(self.plan, max_delivery_bytes=cost), self.root)
        box.publish(self.event)
        before = box.usage()
        with self.assertRaisesRegex(ValueError, 'delivery byte budget'):
            box.publish(dict(self.event, event_id='two'))
        self.assertEqual(before, box.usage())
        self.assert_scan(box)
        self.assertTrue(box.publish(self.event)['duplicate'])

    def test_event_cap_without_byte_budget(self):
        plan = dict(self.plan, max_events=1)
        del plan['max_delivery_bytes']
        box = Mailbox(self.db, plan, self.root)
        box.publish(self.event)
        with self.assertRaisesRegex(ValueError, 'event budget'):
            box.publish(dict(self.event, event_id='two'))
        self.assert_scan(box)

    def test_trigger_failure_rolls_back_event_and_partial_fanout(self):
        box = Mailbox(self.db, self.plan, self.root)
        with box.connect() as db:
            db.execute("""CREATE TRIGGER injected_failure BEFORE INSERT ON communication_deliveries
                WHEN NEW.recipient='c' BEGIN SELECT RAISE(ABORT,'injected'); END""")
        with self.assertRaisesRegex(sqlite3.IntegrityError, 'injected'):
            box.publish(self.event)
        self.assertEqual(box.usage()['events'], 0)
        self.assert_scan(box)
        with box.connect() as db:
            db.execute('DROP TRIGGER injected_failure')
        box.publish(self.event)
        self.assert_scan(box)

    def test_concurrent_unique_and_duplicate_publish(self):
        box = Mailbox(self.db, self.plan, self.root)
        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(lambda i: box.publish(dict(self.event, event_id=str(i % 20))), range(80)))
        self.assertEqual(box.usage()['events'], 20)
        self.assertEqual(box.usage()['deliveries'], 40)
        self.assert_scan(box)

    def test_concurrent_publish_at_byte_cap(self):
        cost = len(canonical(dict(self.event, event_id='0')).encode('utf-8')) * 2
        box = Mailbox(self.db, dict(self.plan, max_delivery_bytes=cost * 3), self.root)
        def send(i):
            try:
                box.publish(dict(self.event, event_id=str(i)))
                return True
            except ValueError:
                return False
        with ThreadPoolExecutor(max_workers=8) as pool:
            success = list(pool.map(send, range(8)))
        self.assertEqual(sum(success), 3)
        self.assert_scan(box)

    def test_populated_legacy_all_runs_and_old_writer(self):
        old_cls = legacy_mailbox()
        old = old_cls(self.db, self.plan, self.root)
        old.publish(self.event)
        other_plan = dict(self.plan, run_id='other')
        other_old = old_cls(self.db, other_plan, self.root)
        other_old.publish(dict(self.event, run_id='other'))
        # Prepared connection predates migration, as does the old Mailbox object.
        connection = sqlite3.connect(self.db)
        self.addCleanup(connection.close)
        connection.execute('SELECT COUNT(*) FROM communication_events').fetchone()
        box = Mailbox(self.db, self.plan, self.root)
        self.assert_scan(box)
        other = Mailbox(self.db, other_plan, self.root)
        self.assert_scan(other)
        old.publish(dict(self.event, event_id='legacy-after-upgrade'))
        with connection:
            event = dict(self.event, event_id='old-connection')
            seq = connection.execute('INSERT INTO communication_events(run_id,event_id,body) VALUES (?,?,?)',
                                     ('r', event['event_id'], canonical(event))).lastrowid
            connection.executemany('INSERT INTO communication_deliveries(seq,recipient) VALUES (?,?)', [(seq, 'b'), (seq, 'c')])
        self.assert_scan(box)
        self.assertEqual(box.usage()['events'], 3)
        self.assertEqual(old.usage(), box.usage())

    def test_simultaneous_first_upgrade_and_legacy_write(self):
        old_cls = legacy_mailbox()
        old = old_cls(self.db, self.plan, self.root)
        old.publish(self.event)
        barrier = threading.Barrier(6)
        def action(i):
            barrier.wait()
            if i == 0:
                return old.publish(dict(self.event, event_id='racing-old-writer'))
            return Mailbox(self.db, self.plan, self.root)
        with ThreadPoolExecutor(max_workers=6) as pool:
            list(pool.map(action, range(6)))
        box = Mailbox(self.db, self.plan, self.root)
        self.assertEqual(box.usage()['events'], 2)
        self.assert_scan(box)

    def test_migration_failure_is_atomic_and_retryable(self):
        old = legacy_mailbox()(self.db, self.plan, self.root)
        old.publish(self.event)
        # A conflicting trigger name fails migration after table creation/backfill.
        with old.connect() as db:
            db.execute('''CREATE TRIGGER communication_usage_delivery_v1
                AFTER INSERT ON communication_deliveries BEGIN SELECT 1; END''')
        with self.assertRaises(sqlite3.OperationalError):
            Mailbox(self.db, self.plan, self.root)
        with old.connect() as db:
            self.assertIsNone(db.execute("SELECT name FROM sqlite_master WHERE name='communication_usage_v1'").fetchone())
            self.assertIsNone(db.execute("SELECT name FROM sqlite_master WHERE name='communication_usage_event_v1'").fetchone())
            db.execute('DROP TRIGGER communication_usage_delivery_v1')
        box = Mailbox(self.db, self.plan, self.root)
        self.assert_scan(box)
        self.assertEqual(old.usage(), box.usage())


if __name__ == '__main__':
    unittest.main()
