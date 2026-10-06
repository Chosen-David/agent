"""Opt-in, local durable communication for trusted host adapters.

Routes are consumer-owned, immutable per run. This is an at-least-once inbox,
not an agent launcher, authentication boundary or semantic acceptance engine.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import sqlite3

from scripts.validate_handoff import _load_json, validate


KINDS = {'artifact', 'question', 'review', 'blocker', 'correction'}


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False,
                      separators=(',', ':'))


def nonblank(value):
    return isinstance(value, str) and bool(value.strip())


def check_plan(plan):
    if not isinstance(plan, dict) or type(plan.get('schema_version')) is not int or plan['schema_version'] != 1:
        raise ValueError('unsupported communication plan')
    if any(not nonblank(plan.get(k)) for k in ('run_id', 'input_version')):
        raise ValueError('run_id and input_version required')
    routes = plan.get('routes')
    if not isinstance(routes, list) or not routes:
        raise ValueError('explicit consumer-owned routes required')
    seen = set()
    for route in routes:
        if not isinstance(route, dict) or any(not nonblank(route.get(k)) for k in ('sender', 'recipient', 'task_id', 'kind')):
            raise ValueError('route needs sender, recipient, task_id and kind')
        key = tuple(route[k] for k in ('sender', 'recipient', 'task_id', 'kind'))
        if route['kind'] not in KINDS or route['sender'] == route['recipient'] or key in seen:
            raise ValueError('invalid, self or duplicate route')
        seen.add(key)
    for key, default in (('max_message_bytes', 8192), ('max_events', 1000)):
        value = plan.get(key, default)
        if type(value) is not int or value < 1:
            raise ValueError(f'{key} must be a positive integer')


class Mailbox:
    def __init__(self, db_path, plan, artifact_root):
        check_plan(plan)
        # Freeze caller data as well as the persisted plan.
        self.plan = json.loads(canonical(plan))
        self.run_id = self.plan['run_id']
        self.root = Path(artifact_root).resolve()
        self.path = Path(db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS communication_plans (
                    run_id TEXT PRIMARY KEY, body TEXT NOT NULL, root TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS communication_events (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL,
                    event_id TEXT NOT NULL, body TEXT NOT NULL,
                    UNIQUE(run_id,event_id));
                CREATE TABLE IF NOT EXISTS communication_deliveries (
                    seq INTEGER NOT NULL, recipient TEXT NOT NULL, receipt TEXT,
                    PRIMARY KEY(seq,recipient));
            ''')
            db.execute('BEGIN IMMEDIATE')
            db.execute('INSERT OR IGNORE INTO communication_plans VALUES (?,?,?)',
                       (self.run_id, canonical(self.plan), str(self.root)))
            row = db.execute('SELECT body,root FROM communication_plans WHERE run_id=?', (self.run_id,)).fetchone()
            if tuple(row) != (canonical(self.plan), str(self.root)):
                raise ValueError('plan/root changed: create a new run and reconcile outstanding messages')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=30)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def publish(self, event):
        if not isinstance(event, dict):
            raise ValueError('event must be an object')
        required = {'event_id', 'run_id', 'input_version', 'sender', 'task_id',
                    'kind', 'summary', 'action', 'refs'}
        if set(event) != required or any(not nonblank(event.get(k)) for k in required - {'refs'}):
            raise ValueError('event needs exact envelope fields and a concrete action')
        if event['run_id'] != self.run_id or event['input_version'] != self.plan['input_version']:
            raise ValueError('stale or cross-run event')
        recipients = sorted({r['recipient'] for r in self.plan['routes']
                             if all(r[k] == event[k] for k in ('sender', 'task_id', 'kind'))})
        if not recipients:
            raise ValueError('no approved consumer route')
        body = canonical(event)
        if len(body.encode('utf-8')) > self.plan.get('max_message_bytes', 8192):
            raise ValueError('message budget exceeded: put detail in referenced artifacts')
        refs = event['refs']
        if not isinstance(refs, list) or not refs:
            raise ValueError('reference the artifact, question, review or blocker record')
        # Reuse existing path/digest/ID checks instead of a divergent validator.
        errors = validate({'schema_version': 1, 'run_id': self.run_id,
                           'role': event['sender'], 'input_version': event['input_version'],
                           'status': 'partial', 'limitations': ['communication, not completion'],
                           'artifacts': refs, 'checks': [], 'tasks': []}, self.root)
        if errors:
            raise ValueError('; '.join(errors))
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            old = db.execute('SELECT seq,body FROM communication_events WHERE run_id=? AND event_id=?',
                             (self.run_id, event['event_id'])).fetchone()
            if old:
                if old['body'] != body:
                    raise ValueError('event_id reused with different content')
                return {'seq': old['seq'], 'recipients': recipients, 'duplicate': True}
            count = db.execute('SELECT COUNT(*) FROM communication_events WHERE run_id=?', (self.run_id,)).fetchone()[0]
            if count >= self.plan.get('max_events', 1000):
                raise ValueError('run event budget exhausted; reconcile before extending the plan')
            seq = db.execute('INSERT INTO communication_events(run_id,event_id,body) VALUES (?,?,?)',
                             (self.run_id, event['event_id'], body)).lastrowid
            db.executemany('INSERT INTO communication_deliveries(seq,recipient) VALUES (?,?)',
                           [(seq, recipient) for recipient in recipients])
            return {'seq': seq, 'recipients': recipients, 'duplicate': False}

    def inbox(self, recipient, *, limit=20):
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError('limit must be 1..100')
        if recipient not in {r['recipient'] for r in self.plan['routes']}:
            raise ValueError('unknown recipient')
        with self.connect() as db:
            rows = db.execute('''SELECT e.seq,e.body FROM communication_events e
                JOIN communication_deliveries d ON e.seq=d.seq
                WHERE e.run_id=? AND d.recipient=? AND d.receipt IS NULL
                ORDER BY e.seq LIMIT ?''', (self.run_id, recipient, limit)).fetchall()
        return [{'seq': r['seq'], 'event': json.loads(r['body'])} for r in rows]

    def acknowledge(self, recipient, seq, receipt):
        # Receipt records handling, never task completion or scientific validity.
        if type(seq) is not int or not isinstance(receipt, dict) or set(receipt) != {'status', 'reason'}:
            raise ValueError('receipt needs status and reason')
        if receipt['status'] not in ('consumed', 'rejected', 'needs_revision') or not nonblank(receipt['reason']):
            raise ValueError('invalid receipt')
        body = canonical(receipt)
        if len(body.encode('utf-8')) > self.plan.get('max_message_bytes', 8192):
            raise ValueError('receipt budget exceeded')
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('''SELECT d.receipt FROM communication_deliveries d
                JOIN communication_events e ON e.seq=d.seq
                WHERE e.run_id=? AND d.seq=? AND d.recipient=?''', (self.run_id, seq, recipient)).fetchone()
            if row is None:
                raise ValueError('delivery not found in this run')
            if row['receipt'] is not None and row['receipt'] != body:
                raise ValueError('receipt is immutable; publish a correction event')
            db.execute('UPDATE communication_deliveries SET receipt=? WHERE seq=? AND recipient=?',
                       (body, seq, recipient))

    def status(self):
        with self.connect() as db:
            rows = db.execute('''SELECT e.seq,d.recipient,d.receipt FROM communication_events e
                JOIN communication_deliveries d ON e.seq=d.seq WHERE e.run_id=?
                ORDER BY e.seq,d.recipient''', (self.run_id,)).fetchall()
        return [{'seq': r['seq'], 'recipient': r['recipient'],
                 'receipt': json.loads(r['receipt']) if r['receipt'] else None} for r in rows]

    def consume_handoff(self, recipient, seq, request, *, require_complete=True):
        """Re-read immutable references and validate against trusted consumer scope.

        Returns data without ACK: the host must separately read/verify semantics,
        perform an idempotent action, then acknowledge. A failed check stays pending.
        """
        with self.connect() as db:
            row = db.execute('''SELECT e.body FROM communication_events e
                JOIN communication_deliveries d ON e.seq=d.seq
                WHERE e.run_id=? AND e.seq=? AND d.recipient=?''', (self.run_id, seq, recipient)).fetchone()
        if row is None:
            raise ValueError('delivery not found in this run')
        event = json.loads(row['body'])
        refs = event['refs']
        manifests = [r for r in refs if r['id'] == 'handoff']
        if len(manifests) != 1:
            raise ValueError('handoff reference required')
        ref = manifests[0]
        # Recheck all original references at consumption, including the manifest.
        errors = validate({'schema_version': 1, 'run_id': self.run_id,
                           'role': event['sender'], 'input_version': event['input_version'],
                           'status': 'partial', 'limitations': ['pending consumption'],
                           'artifacts': refs, 'checks': [], 'tasks': []}, self.root)
        if errors:
            raise ValueError('; '.join(errors))
        record = _load_json(self.root / ref['path'])
        errors = validate(record, self.root, require_complete,
                          expected_input_version=self.plan['input_version'], consumer_request=request)
        if isinstance(record, dict) and (record.get('run_id') != self.run_id or record.get('role') != event['sender']):
            errors.append('handoff producer/run mismatch')
        if errors:
            raise ValueError('; '.join(errors))
        return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', required=True)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--root', type=Path, required=True)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('status')
    p = sub.add_parser('publish'); p.add_argument('event', type=Path)
    p = sub.add_parser('inbox'); p.add_argument('recipient'); p.add_argument('--limit', type=int, default=20)
    p = sub.add_parser('ack'); p.add_argument('recipient'); p.add_argument('seq', type=int); p.add_argument('receipt', type=Path)
    p = sub.add_parser('consume'); p.add_argument('recipient'); p.add_argument('seq', type=int); p.add_argument('--request', type=Path, required=True)
    args = parser.parse_args()
    try:
        box = Mailbox(args.db, _load_json(args.plan), args.root)
        if args.command == 'publish':
            result = box.publish(_load_json(args.event))
        elif args.command == 'inbox':
            result = box.inbox(args.recipient, limit=args.limit)
        elif args.command == 'ack':
            box.acknowledge(args.recipient, args.seq, _load_json(args.receipt)); result = {'acknowledged': True}
        elif args.command == 'consume':
            result = box.consume_handoff(args.recipient, args.seq, _load_json(args.request))
        else:
            result = box.status()
    except (ValueError, OSError, sqlite3.Error) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False)); return 1
    print(json.dumps(result, ensure_ascii=False, indent=2)); return 0


if __name__ == '__main__':
    raise SystemExit(main())
