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
from .project_docs import guard_write_path


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
    if 'max_delivery_bytes' in plan:
        value = plan['max_delivery_bytes']
        if type(value) is not int or value < 1:
            raise ValueError('max_delivery_bytes must be a positive integer')


class Mailbox:
    def __init__(self, db_path, plan, artifact_root):
        check_plan(plan)
        # Freeze caller data as well as the persisted plan.
        self.plan = json.loads(canonical(plan))
        self.run_id = self.plan['run_id']
        self.root = Path(artifact_root).resolve()
        self.path = guard_write_path(db_path)
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
                CREATE TABLE IF NOT EXISTS communication_basis (
                    seq INTEGER NOT NULL, recipient TEXT NOT NULL,
                    record TEXT NOT NULL, request TEXT NOT NULL,
                    PRIMARY KEY(seq,recipient));
                CREATE INDEX IF NOT EXISTS communication_pending_recipient
                    ON communication_deliveries(recipient,seq)
                    WHERE receipt IS NULL;
            ''')
            db.execute('BEGIN IMMEDIATE')
            db.execute('INSERT OR IGNORE INTO communication_plans VALUES (?,?,?)',
                       (self.run_id, canonical(self.plan), str(self.root)))
            row = db.execute('SELECT body,root FROM communication_plans WHERE run_id=?', (self.run_id,)).fetchone()
            if tuple(row) != (canonical(self.plan), str(self.root)):
                raise ValueError('plan/root changed: create a new run and reconcile outstanding messages')
            self._init_usage(db)
            db.execute('INSERT OR IGNORE INTO communication_usage_v1 VALUES (?,0,0,0,0)',
                       (self.run_id,))

    @staticmethod
    def _init_usage(db):
        """Backfill once under the caller's IMMEDIATE transaction.

        The table is the migration marker: creation, backfill and triggers commit
        together. Do not use executescript here (it commits pending transactions).
        Triggers also account for append-only writes by older Mailbox processes.
        Direct SQL edits/deletes/replaces of historical events are unsupported.
        """
        if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='communication_usage_v1'").fetchone():
            return
        db.execute('''CREATE TABLE communication_usage_v1 (
            run_id TEXT PRIMARY KEY, events INTEGER NOT NULL,
            envelope_bytes INTEGER NOT NULL, deliveries INTEGER NOT NULL,
            delivery_bytes INTEGER NOT NULL)''')
        db.execute('''INSERT INTO communication_usage_v1
            SELECT run_id,COUNT(*),SUM(length(CAST(body AS BLOB))),0,0
            FROM communication_events GROUP BY run_id''')
        db.execute('''UPDATE communication_usage_v1 SET
            deliveries=(SELECT COUNT(*) FROM communication_events e
                JOIN communication_deliveries d ON e.seq=d.seq
                WHERE e.run_id=communication_usage_v1.run_id),
            delivery_bytes=(SELECT COALESCE(SUM(length(CAST(e.body AS BLOB))),0)
                FROM communication_events e JOIN communication_deliveries d ON e.seq=d.seq
                WHERE e.run_id=communication_usage_v1.run_id)''')
        db.execute('''CREATE TRIGGER communication_usage_event_v1
            AFTER INSERT ON communication_events BEGIN
                INSERT INTO communication_usage_v1 VALUES (
                    NEW.run_id,1,length(CAST(NEW.body AS BLOB)),0,0)
                ON CONFLICT(run_id) DO UPDATE SET
                    events=events+1,
                    envelope_bytes=envelope_bytes+length(CAST(NEW.body AS BLOB));
            END''')
        db.execute('''CREATE TRIGGER communication_usage_delivery_v1
            AFTER INSERT ON communication_deliveries BEGIN
                UPDATE communication_usage_v1 SET deliveries=deliveries+1,
                    delivery_bytes=delivery_bytes+(
                        SELECT length(CAST(body AS BLOB)) FROM communication_events WHERE seq=NEW.seq)
                WHERE run_id=(SELECT run_id FROM communication_events WHERE seq=NEW.seq);
            END''')

    @contextmanager
    def connect(self):
        guard_write_path(self.path)
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
            usage = db.execute('SELECT events,delivery_bytes FROM communication_usage_v1 WHERE run_id=?',
                               (self.run_id,)).fetchone()
            if usage['events'] >= self.plan.get('max_events', 1000):
                raise ValueError('run event budget exhausted; reconcile before extending the plan')
            if 'max_delivery_bytes' in self.plan:
                spent = usage['delivery_bytes']
                if spent + len(body.encode('utf-8')) * len(recipients) > self.plan['max_delivery_bytes']:
                    raise ValueError('run delivery byte budget exhausted; no partial fan-out')
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
                ORDER BY d.seq LIMIT ?''', (self.run_id, recipient, limit)).fetchall()
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
            if row['receipt'] == body:
                return
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
        from .handoff_basis import check_handoff_basis
        check_handoff_basis(self.root, record, request)
        # Identity/dependency records only, never private memory contents or CoT.
        # An ACK remains independent. Keep the original consumer binding immutable.
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            stored = db.execute('SELECT record,request FROM communication_basis WHERE seq=? AND recipient=?',
                                (seq, recipient)).fetchone()
            value = (canonical(record), canonical(request))
            if stored is not None and tuple(stored) != value:
                raise ValueError('consumed basis/request changed: use a new event or run')
            db.execute('INSERT OR IGNORE INTO communication_basis VALUES (?,?,?,?)',
                       (seq, recipient, *value))
        return record

    def impact(self):
        """Return stale consumed evidence and actual affected recipients; no auto-ACK."""
        from .handoff_basis import basis_impact
        with self.connect() as db:
            rows = db.execute('''SELECT b.*,e.event_id,e.body FROM communication_basis b
                JOIN communication_events e ON b.seq=e.seq WHERE e.run_id=? ORDER BY b.seq,b.recipient''',
                              (self.run_id,)).fetchall()
        result = []
        for row in rows:
            record = json.loads(row['record'])
            impact = basis_impact(self.root, record, json.loads(row['request']))
            event = json.loads(row['body'])
            errors = validate({'schema_version': 1, 'run_id': self.run_id, 'role': event['sender'],
                               'input_version': event['input_version'], 'status': 'partial',
                               'limitations': ['basis audit'], 'artifacts': event['refs'],
                               'tasks': [], 'checks': []}, self.root)
            if errors:
                impact['stale'] = True
                impact['claim_ids'] = sorted(c['id'] for c in record.get('evidence_claims', []))
                impact['reasons'].extend(errors)
                impact['scope'] = 'shared envelope/manifest provenance changed; whole handoff affected'
            if impact['stale']:
                result.append({'seq': row['seq'], 'event_id': row['event_id'],
                               'recipient': row['recipient'], 'usage_stage': 'validated_handoff', **impact})
        return result

    def prepare_context(self, recipient, seq, request, **budget_and_cache):
        """Validate delivery, then build a budgeted evidence payload for the host."""
        from .handoff_basis import basis_context
        record = self.consume_handoff(recipient, seq, request)
        return basis_context(self.root, record, request, **budget_and_cache)

    def usage(self):
        """Exact envelope bytes including fan-out; deliberately no token estimate."""
        with self.connect() as db:
            row = db.execute('SELECT * FROM communication_usage_v1 WHERE run_id=?',
                             (self.run_id,)).fetchone()
        return {'events': row['events'], 'envelope_bytes': row['envelope_bytes'],
                'deliveries': row['deliveries'], 'delivery_bytes': row['delivery_bytes'], 'tokens': None,
                'scope': 'stored envelopes only; excludes artifacts, model input/output and reasoning'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', required=True)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--root', type=Path, required=True)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('status')
    sub.add_parser('impact')
    sub.add_parser('usage')
    p = sub.add_parser('publish'); p.add_argument('event', type=Path)
    p = sub.add_parser('inbox'); p.add_argument('recipient'); p.add_argument('--limit', type=int, default=20)
    p = sub.add_parser('ack'); p.add_argument('recipient'); p.add_argument('seq', type=int); p.add_argument('receipt', type=Path)
    p = sub.add_parser('consume'); p.add_argument('recipient'); p.add_argument('seq', type=int); p.add_argument('--request', type=Path, required=True)
    p = sub.add_parser('context'); p.add_argument('recipient'); p.add_argument('seq', type=int)
    p.add_argument('--request', type=Path, required=True); p.add_argument('--max-chars', type=int, default=20000)
    p.add_argument('--known', type=Path, help='trusted current-context refs; not producer input')
    p.add_argument('--encoding', help='explicit optional tiktoken encoding; no model inference')
    p.add_argument('--max-tokens', type=int)
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
        elif args.command == 'context':
            from .handoff_basis import make_token_counter
            known = _load_json(args.known) if args.known else {}
            result = box.prepare_context(args.recipient, args.seq, _load_json(args.request),
                                         max_chars=args.max_chars,
                                         max_tokens=args.max_tokens,
                                         token_counter=make_token_counter(args.encoding) if args.encoding else None,
                                         known_knowledge_refs=known.get('knowledge_refs', []),
                                         known_memory_ids=known.get('memory_refs', []))
        elif args.command == 'impact':
            result = box.impact()
        elif args.command == 'usage':
            result = box.usage()
        else:
            result = box.status()
    except (ValueError, OSError, sqlite3.Error) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False)); return 1
    print(json.dumps(result, ensure_ascii=False, indent=2)); return 0


if __name__ == '__main__':
    raise SystemExit(main())
