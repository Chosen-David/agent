"""Concurrent publication cannot split the ledger and inbox read snapshots."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import hashlib
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest

from agent_runtime.communication import Mailbox


class AdaptiveInboxTests(unittest.TestCase):
    def exercise(self, journal, initial):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'data').write_bytes(b'x')
            ref = dict(id='data', path='data', sha256=hashlib.sha256(b'x').hexdigest())
            plan = dict(schema_version=1, run_id='snapshot', input_version='v1',
                        max_events=100, routes=[dict(sender='s', recipient='r',
                                                    task_id='T', kind='artifact')])
            box = Mailbox(root / 'db', plan, root)
            with sqlite3.connect(box.path) as db:
                self.assertEqual(db.execute('PRAGMA journal_mode=' + journal).fetchone()[0].upper(), journal)

            def event(i):
                return dict(event_id=str(i), run_id='snapshot', input_version='v1',
                            sender='s', task_id='T', kind='artifact', summary='Read data',
                            action='Verify the reference', refs=[dict(ref)])

            for i in range(initial):
                box.publish(event(i))
            old = box.inbox('r', limit=3)
            connect = box.connect
            started = threading.Event()
            jobs = []

            def writer():
                started.set()
                return [box.publish(event(i)) for i in range(initial, initial + 5)]

            with ThreadPoolExecutor(max_workers=1) as pool:
                class Cursor:
                    def __init__(self, cursor):
                        self.cursor = cursor

                    def fetchone(self):
                        count = self.cursor.fetchone()
                        if not jobs:
                            jobs.append(pool.submit(writer))
                            if not started.wait(3):
                                raise AssertionError('writer did not start')
                            if journal == 'WAL':
                                jobs[0].result(timeout=10)
                        return count

                class Connection:
                    def __init__(self, db):
                        self.db = db

                    def execute(self, sql, *args):
                        cursor = self.db.execute(sql, *args)
                        return Cursor(cursor) if sql.startswith('SELECT events FROM communication_usage_v1') else cursor

                @contextmanager
                def interleave():
                    with connect() as db:
                        yield Connection(db)

                box.connect = interleave
                try:
                    current = box.inbox('r', limit=3)
                finally:
                    box.connect = connect
                self.assertTrue(jobs)
                self.assertEqual(current, old)
                self.assertEqual(len(jobs[0].result(timeout=10)), 5)
            self.assertEqual(box.inbox('r', limit=3),
                             [{'seq': i + 1, 'event': event(i)}
                              for i in range(min(3, initial + 5))])
            # All three read branches release their transaction for future writes.
            box.publish(event(initial + 10))

    def test_wal_writer_commits_between_ledger_and_rows(self):
        for initial in (0, 1, 4):
            with self.subTest(initial_events=initial):
                self.exercise('WAL', initial)

    def test_rollback_writer_completes_after_reader_releases_snapshot(self):
        for initial in (0, 1, 4):
            with self.subTest(initial_events=initial):
                self.exercise('DELETE', initial)
