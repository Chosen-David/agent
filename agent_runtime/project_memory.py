"""Project-local, source-linked memory with transactional correction propagation.

This is an audit ledger, not a model memory API or a scientific verifier. Callers
must record actual sources and supply independent acceptance for scientific claims.
Entry content and dependency IDs never change; corrections create new revisions.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import re
import sqlite3
import stat
import sys


KINDS = ('intention', 'assumption', 'observation', 'claim', 'procedure', 'artifact')
EVIDENCE = ('candidate', 'user_confirmed', 'verified')


class MemoryError(ValueError):
    """Missing, invalid or unavailable project evidence; callers must fail closed."""


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise MemoryError(f'{field} must be nonempty text')
    return value


def _ids(values, field):
    if (not isinstance(values, (list, tuple)) or
            any(not isinstance(v, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:-]*', v)
                for v in values) or len(set(values)) != len(values)):
        raise MemoryError(f'{field} must contain unique stable IDs')
    return list(values)


class MemoryLedger:
    def __init__(self, root, create=False):
        self.path = Path(root).resolve() / '.agent-memory' / 'memory.sqlite3'
        self._validate_paths()
        if create:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self._connect(create=True) as db:
                db.executescript('''
                    CREATE TABLE IF NOT EXISTS entries (
                        id TEXT PRIMARY KEY, kind TEXT NOT NULL, content TEXT NOT NULL,
                        source TEXT NOT NULL, scope TEXT NOT NULL, evidence TEXT NOT NULL,
                        status TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT
                            (strftime('%Y-%m-%dT%H:%M:%fZ','now')));
                    CREATE TABLE IF NOT EXISTS dependencies (
                        child TEXT NOT NULL REFERENCES entries(id),
                        parent TEXT NOT NULL REFERENCES entries(id),
                        PRIMARY KEY(child, parent));
                    CREATE TABLE IF NOT EXISTS events (
                        sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                        entry_id TEXT NOT NULL REFERENCES entries(id),
                        action TEXT NOT NULL, reason TEXT NOT NULL, source TEXT NOT NULL,
                        related_id TEXT, created_at TEXT NOT NULL DEFAULT
                            (strftime('%Y-%m-%dT%H:%M:%fZ','now')));
                ''')

    def _validate_paths(self):
        """Reject redirected or special ledger paths, including dangling links.

        Repeat before every connection to catch changes since construction. This
        does not claim protection against a concurrent hostile filesystem writer.
        """
        for path, directory in ((self.path.parent, True), (self.path, False)):
            try:
                mode = path.lstat().st_mode
            except FileNotFoundError:
                continue
            if stat.S_ISLNK(mode):
                raise MemoryError(f'project memory path must not be a symlink: {path}')
            if not (stat.S_ISDIR(mode) if directory else stat.S_ISREG(mode)):
                expected = 'directory' if directory else 'regular file'
                raise MemoryError(f'project memory path must be a {expected}: {path}')

    @contextmanager
    def _connect(self, write=False, create=False):
        db = None
        try:
            self._validate_paths()
            if not create and not self.path.is_file():
                raise MemoryError(f'project memory ledger missing: {self.path}')
            # mode=rw prevents a read or correction accidentally creating an empty ledger.
            uri = self.path.as_uri() + ('?mode=rwc' if create else '?mode=rw')
            db = sqlite3.connect(uri, uri=True, timeout=10)
            db.row_factory = sqlite3.Row
            db.execute('PRAGMA foreign_keys=ON')
            db.execute('BEGIN IMMEDIATE' if write else 'BEGIN')
            yield db
            db.commit()
        except sqlite3.Error as exc:
            if db is not None:
                db.rollback()
            raise MemoryError(f'project memory ledger unavailable: {exc}') from exc
        except BaseException:
            if db is not None:
                db.rollback()
            raise
        finally:
            if db is not None:
                db.close()

    @staticmethod
    def _get(db, entry_id):
        row = db.execute('SELECT * FROM entries WHERE id=?', (entry_id,)).fetchone()
        if row is None:
            raise MemoryError(f'unknown memory ID: {entry_id}')
        value = dict(row)
        value['scope'] = json.loads(value['scope'])
        value['deps'] = [r[0] for r in db.execute(
            'SELECT parent FROM dependencies WHERE child=? ORDER BY parent', (entry_id,))]
        return value

    @staticmethod
    def _check(db, refs):
        refs = _ids(refs, 'memory refs')
        if not refs:
            raise MemoryError('memory refs must be nonempty')
        checked = set()
        def visit(entry_id):
            if entry_id in checked:
                return
            entry = MemoryLedger._get(db, entry_id)
            if entry['status'] != 'active':
                raise MemoryError(f'memory {entry_id} is {entry["status"]}; reconciliation required')
            checked.add(entry_id)
            for parent in entry['deps']:
                visit(parent)
        for ref in refs:
            visit(ref)
        return [MemoryLedger._get(db, ref) for ref in refs]

    @staticmethod
    def _insert(db, entry_id, kind, content, source, deps, scope, evidence):
        _ids([entry_id], 'entry ID')
        _text(content, 'content')
        _text(source, 'source')
        deps, scope = _ids(deps, 'deps'), _ids(scope, 'scope')
        if kind not in KINDS or evidence not in EVIDENCE:
            raise MemoryError('unknown kind or evidence class')
        if entry_id in deps:
            raise MemoryError('entry cannot depend on itself')
        if db.execute('SELECT 1 FROM entries WHERE id=?', (entry_id,)).fetchone():
            raise MemoryError(f'memory ID is immutable and already exists: {entry_id}')
        for dep in deps:
            parent = MemoryLedger._get(db, dep)
            if parent['status'] not in ('active', 'candidate'):
                raise MemoryError(f'dependency {dep} is {parent["status"]}')
        if evidence != 'candidate' and deps:
            MemoryLedger._check(db, deps)
        status = 'candidate' if evidence == 'candidate' else 'active'
        db.execute('INSERT INTO entries(id,kind,content,source,scope,evidence,status) '
                   'VALUES(?,?,?,?,?,?,?)',
                   (entry_id, kind, content, source, json.dumps(scope), evidence, status))
        db.executemany('INSERT INTO dependencies(child,parent) VALUES(?,?)',
                       [(entry_id, dep) for dep in deps])
        MemoryLedger._event(db, entry_id, 'created', evidence, source)
        return MemoryLedger._get(db, entry_id)

    @staticmethod
    def _event(db, entry_id, action, reason, source, related_id=None):
        db.execute('INSERT INTO events(entry_id,action,reason,source,related_id) VALUES(?,?,?,?,?)',
                   (entry_id, action, reason, source, related_id))

    @staticmethod
    def _descendants(db, entry_id):
        MemoryLedger._get(db, entry_id)
        return [r[0] for r in db.execute('''
            WITH RECURSIVE affected(id) AS (
                SELECT child FROM dependencies WHERE parent=?
                UNION SELECT d.child FROM dependencies d JOIN affected a ON d.parent=a.id)
            SELECT id FROM affected ORDER BY id''', (entry_id,))]

    def add(self, entry_id, kind, content, source, deps=(), scope=(), evidence='candidate'):
        with self._connect(write=True) as db:
            return self._insert(db, entry_id, kind, content, source, deps, scope, evidence)

    def _revise(self, old_id, new_id, content, source, reason, accept=False, deps=()):
        _text(reason, 'reason')
        _text(source, 'source')
        with self._connect(write=True) as db:
            old = self._get(db, old_id)
            if old['status'] not in ('active', 'candidate', 'stale'):
                raise MemoryError('cannot revise an already superseded memory')
            if accept and old['status'] != 'candidate':
                raise MemoryError('accept requires a candidate memory')
            affected = self._descendants(db, old_id)
            # A revision may not re-use any of the evidence it invalidates.
            if set(deps) & {old_id, *affected}:
                raise MemoryError('revision depends on its invalidated lineage')
            new = self._insert(db, new_id, old['kind'], old['content'] if accept else content,
                               source, old['deps'] if accept else deps, old['scope'],
                               'verified' if accept else 'user_confirmed')
            db.execute("UPDATE entries SET status='superseded' WHERE id=?", (old_id,))
            self._event(db, old_id, 'accepted' if accept else 'corrected', reason, source, new_id)
            self._event(db, new_id, 'revision_of', reason, source, old_id)
            for entry_id in affected:
                # Preserve prior revision history; never resurrect a superseded node.
                status = self._get(db, entry_id)['status']
                if status != 'superseded':
                    db.execute("UPDATE entries SET status='stale' WHERE id=?", (entry_id,))
                    self._event(db, entry_id, 'stale', reason, source, old_id)
            return {'revision': new, 'superseded': old_id, 'affected': affected}

    def correct(self, old_id, new_id, content, source, reason, deps=()):
        """Record a user correction; source must identify the actual user statement.

        Descendants remain stale until independently revalidated as new revisions.
        External data and report files are never rewritten or deleted.
        """
        return self._revise(old_id, new_id, content, source, reason, deps=deps)

    def accept(self, old_id, new_id, source, reason):
        """Explicit acceptance creates a verified revision, never mutates the candidate."""
        return self._revise(old_id, new_id, None, source, reason, accept=True)

    def check(self, refs):
        with self._connect() as db:
            return self._check(db, refs)

    def list(self, status='active', scope=None):
        """Retrieval defaults to current accepted entries, never candidates or stale history."""
        if status not in ('active', 'candidate', 'stale', 'superseded', 'all'):
            raise MemoryError('unknown status')
        with self._connect() as db:
            rows = db.execute('SELECT id FROM entries ORDER BY created_at,id').fetchall()
            values = [self._get(db, r[0]) for r in rows]
            return [v for v in values if (status == 'all' or v['status'] == status)
                    and (scope is None or scope in v['scope'])]

    def history(self, entry_id):
        with self._connect() as db:
            return {'entry': self._get(db, entry_id), 'events': [dict(r) for r in db.execute(
                'SELECT * FROM events WHERE entry_id=? ORDER BY sequence', (entry_id,))]}

    def impact(self, entry_id):
        with self._connect() as db:
            return [self._get(db, ref) for ref in self._descendants(db, entry_id)]


def check_task_memory(root, task):
    """Optional task references become a mandatory validity gate when supplied."""
    refs = task.get('memory_refs')
    if refs is None or refs == []:
        return []
    return MemoryLedger(root).check(refs)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    sub = parser.add_subparsers(dest='command', required=True)
    add = sub.add_parser('add')
    add.add_argument('--id', required=True)
    add.add_argument('--kind', choices=KINDS, required=True)
    add.add_argument('--content', required=True)
    add.add_argument('--source', required=True)
    add.add_argument('--dep', action='append', default=[])
    add.add_argument('--scope', action='append', default=[])
    add.add_argument('--evidence', choices=EVIDENCE, default='candidate')
    for command in ('correct', 'accept'):
        action = sub.add_parser(command)
        action.add_argument('--id', required=True)
        action.add_argument('--new-id', required=True)
        action.add_argument('--source', required=True)
        action.add_argument('--reason', required=True)
        if command == 'correct':
            action.add_argument('--content', required=True)
            action.add_argument('--dep', action='append', default=[])
    listing = sub.add_parser('list')
    listing.add_argument('--status', default='active', choices=('active', 'candidate', 'stale', 'superseded', 'all'))
    listing.add_argument('--scope')
    sub.add_parser('check').add_argument('refs', nargs='+')
    for command in ('history', 'impact'):
        sub.add_parser(command).add_argument('id')
    args = parser.parse_args(argv)
    try:
        ledger = MemoryLedger(args.root, create=args.command == 'add')
        if args.command == 'add':
            result = ledger.add(args.id, args.kind, args.content, args.source, args.dep, args.scope, args.evidence)
        elif args.command == 'correct':
            result = ledger.correct(args.id, args.new_id, args.content, args.source, args.reason, args.dep)
        elif args.command == 'accept':
            result = ledger.accept(args.id, args.new_id, args.source, args.reason)
        elif args.command == 'list':
            result = ledger.list(args.status, args.scope)
        elif args.command == 'check':
            result = ledger.check(args.refs)
        else:
            result = getattr(ledger, args.command)(args.id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (MemoryError, OSError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
