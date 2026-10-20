"""Project-local, source-linked memory with transactional correction propagation.

This is an audit ledger, not a model memory API or a scientific verifier. Callers
must record actual sources and supply independent acceptance for scientific claims.
Entry content and dependency IDs never change; corrections create new revisions.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import sqlite3
import stat
import sys

from .project_docs import check_document_refs, guard_write_path


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


def _read_entry(db, entry_id, schema_state=None):
    row = db.execute('SELECT * FROM entries WHERE id=?', (entry_id,)).fetchone()
    if row is None:
        raise MemoryError(f'unknown memory ID: {entry_id}')
    value = dict(row)
    value['scope'] = json.loads(value['scope'])
    value['document_refs'] = None
    # Only an owned check traversal supplies state. Preserve hydration/error
    # order, and remember an absent table distinctly from an unknown schema.
    if schema_state is not None and schema_state:
        documents = schema_state[0]
    else:
        documents = bool(db.execute("SELECT 1 FROM sqlite_master WHERE type='table' "
                                    "AND name='document_dependencies'").fetchone())
        if schema_state is not None:
            schema_state.append(documents)
    if documents:
        binding = db.execute('SELECT snapshot FROM document_dependencies WHERE entry_id=?', (entry_id,)).fetchone()
        if binding:
            value['document_refs'] = json.loads(binding[0])
    value['deps'] = [r[0] for r in db.execute(
        'SELECT parent FROM dependencies WHERE child=? ORDER BY parent', (entry_id,))]
    return value


class MemoryLedger:
    def __init__(self, root, create=False):
        self.root = Path(root).resolve()
        self.path = Path(os.path.abspath(Path(root) / '.agent-memory' / 'memory.sqlite3'))
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
                    CREATE INDEX IF NOT EXISTS memory_dependencies_parent
                        ON dependencies(parent, child);
                    CREATE TABLE IF NOT EXISTS document_dependencies (
                        entry_id TEXT PRIMARY KEY REFERENCES entries(id), snapshot TEXT NOT NULL);
                    CREATE TABLE IF NOT EXISTS events (
                        sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                        entry_id TEXT NOT NULL REFERENCES entries(id),
                        action TEXT NOT NULL, reason TEXT NOT NULL, source TEXT NOT NULL,
                        related_id TEXT, created_at TEXT NOT NULL DEFAULT
                            (strftime('%Y-%m-%dT%H:%M:%fZ','now')));
                    CREATE INDEX IF NOT EXISTS memory_events_entry
                        ON events(entry_id);
                ''')

    def _validate_paths(self):
        """Reject redirected or special ledger paths, including dangling links.

        Repeat before every connection to catch changes since construction. This
        does not claim protection against a concurrent hostile filesystem writer.
        """
        try:
            guard_write_path(self.path)
        except ValueError as exc:
            raise MemoryError(str(exc)) from exc
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
        return _read_entry(db, entry_id)

    @staticmethod
    def _check(db, refs, root=None):
        # External/direct callers keep uncached semantics, including DDL through
        # their own connection between hydration calls.
        return MemoryLedger._walk(db, refs, root)

    @staticmethod
    def _walk(db, refs, root=None, schema_state=None, *, include_dependencies=False):
        refs = _ids(refs, 'memory refs')
        if not refs:
            raise MemoryError('memory refs must be nonempty')
        checked = set()
        requested = set(refs)
        roots = {}
        # Keep the recursive DFS order without retaining full ancestor contents
        # or depending on Python's recursion limit. Iterators keep wide graphs
        # lazy, just like the former per-entry for loop.
        frames = [iter(refs)]
        while frames:
            try:
                entry_id = next(frames[-1])
            except StopIteration:
                frames.pop()
                continue
            if entry_id in checked:
                continue
            entry = (MemoryLedger._get(db, entry_id) if schema_state is None
                     else _read_entry(db, entry_id, schema_state))
            if entry['status'] != 'active':
                raise MemoryError(f'memory {entry_id} is {entry["status"]}; reconciliation required')
            if entry['document_refs'] is not None:
                if root is None:
                    raise MemoryError('document-bound memory requires project context')
                try:
                    check_document_refs(root, entry['document_refs'])
                except (OSError, ValueError) as exc:
                    raise MemoryError(f'memory {entry_id} has stale project document dependencies: {exc}') from exc
            checked.add(entry_id)
            # Ordinary checks retain requested roots only. Context packing
            # explicitly needs every validated entry for its complete payload.
            if include_dependencies or entry_id in requested:
                roots[entry_id] = entry
            frames.append(iter(entry['deps']))
            # Drop the local reference; retained output is owned by roots.
            del entry
        return list(roots.values()) if include_dependencies else [roots[ref] for ref in refs]

    @staticmethod
    def _insert(db, entry_id, kind, content, source, deps, scope, evidence, document_refs=None, root=None):
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
            MemoryLedger._check(db, deps, root)
        if document_refs is not None:
            try:
                check_document_refs(root, document_refs)
            except (OSError, ValueError) as exc:
                raise MemoryError('current project document binding required') from exc
        status = 'candidate' if evidence == 'candidate' else 'active'
        db.execute('INSERT INTO entries(id,kind,content,source,scope,evidence,status) '
                   'VALUES(?,?,?,?,?,?,?)',
                   (entry_id, kind, content, source, json.dumps(scope), evidence, status))
        if document_refs is not None:
            db.execute('CREATE TABLE IF NOT EXISTS document_dependencies '
                       '(entry_id TEXT PRIMARY KEY REFERENCES entries(id), snapshot TEXT NOT NULL)')
            db.execute('INSERT INTO document_dependencies(entry_id,snapshot) VALUES(?,?)',
                       (entry_id, json.dumps(document_refs, sort_keys=True)))
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

    def add(self, entry_id, kind, content, source, deps=(), scope=(), evidence='candidate', document_refs=None):
        with self._connect(write=True) as db:
            return self._insert(db, entry_id, kind, content, source, deps, scope, evidence, document_refs, self.root)

    def _revise(self, old_id, new_id, content, source, reason, accept=False, deps=(), document_refs=None):
        _text(reason, 'reason')
        _text(source, 'source')
        with self._connect(write=True) as db:
            old = self._get(db, old_id)
            if old['status'] not in ('active', 'candidate', 'stale'):
                raise MemoryError('cannot revise an already superseded memory')
            if accept and old['status'] != 'candidate':
                raise MemoryError('accept requires a candidate memory')
            affected = self._descendants(db, old_id)
            # Validate before hashing: malformed refs follow the public error contract.
            deps = _ids(deps, 'deps')
            # A revision may not re-use any of the evidence it invalidates.
            if set(deps) & {old_id, *affected}:
                raise MemoryError('revision depends on its invalidated lineage')
            if old['document_refs'] is not None and not accept and document_refs is None:
                raise MemoryError('document-bound correction requires a new current document_refs snapshot')
            new = self._insert(db, new_id, old['kind'], old['content'] if accept else content,
                               source, old['deps'] if accept else deps, old['scope'],
                               'verified' if accept else 'user_confirmed',
                               old['document_refs'] if accept else document_refs, self.root)
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

    def correct(self, old_id, new_id, content, source, reason, deps=(), document_refs=None):
        """Record a user correction; source must identify the actual user statement.

        Descendants remain stale until independently revalidated as new revisions.
        External data and report files are never rewritten or deleted.
        """
        return self._revise(old_id, new_id, content, source, reason, deps=deps, document_refs=document_refs)

    def accept(self, old_id, new_id, source, reason):
        """Explicit acceptance creates a verified revision, never mutates the candidate."""
        return self._revise(old_id, new_id, None, source, reason, accept=True)

    def check(self, refs):
        with self._connect() as db:
            # _connect owns this ordinary transaction and installs no SQL hooks.
            # Customized entry points retain their original observable calls.
            if (type(self) is MemoryLedger
                    and '_check' not in self.__dict__ and '_connect' not in self.__dict__
                    and MemoryLedger._get is _BUILTIN_GET
                    and MemoryLedger._check is _BUILTIN_CHECK
                    and MemoryLedger._connect is _BUILTIN_CONNECT
                    and _read_entry is _BUILTIN_READ_ENTRY
                    and check_document_refs is _BUILTIN_DOCUMENT_CHECK
                    and sqlite3.connect is _BUILTIN_SQLITE_CONNECT
                    and type(db) is sqlite3.Connection and db.in_transaction
                    and db.row_factory is _BUILTIN_SQLITE_ROW and db.text_factory is str):
                return MemoryLedger._walk(db, refs, self.root, [])
            return self._check(db, refs, self.root)

    def _context_closure(self, refs):
        """Private built-in context path; None requests legacy per-level checks.

        Complete entries are required for the payload. Ordinary check still
        retains only its requested roots. No state survives this transaction.
        """
        if (type(self) is not MemoryLedger
                or any(k in self.__dict__ for k in ('check', '_check', '_get', '_connect'))
                or MemoryLedger.check is not _BUILTIN_PUBLIC_CHECK
                or MemoryLedger._get is not _BUILTIN_GET
                or MemoryLedger._check is not _BUILTIN_CHECK
                or MemoryLedger._walk is not _BUILTIN_WALK
                or MemoryLedger._connect is not _BUILTIN_CONNECT
                or check_document_refs is not _BUILTIN_DOCUMENT_CHECK
                or sqlite3.connect is not _BUILTIN_SQLITE_CONNECT
                or sqlite3.Row is not _BUILTIN_SQLITE_ROW):
            return None
        with self._connect() as db:
            # The helper is an observable extension point: custom readers may
            # take only two arguments or change schema within this transaction.
            schema_state = ([] if _read_entry is _BUILTIN_READ_ENTRY
                            and type(db) is sqlite3.Connection and db.in_transaction
                            and db.row_factory is _BUILTIN_SQLITE_ROW
                            and db.text_factory is str else None)
            return MemoryLedger._walk(db, refs, self.root, schema_state,
                                      include_dependencies=True)

    def list(self, status='active', scope=None):
        """Retrieval defaults to current accepted entries, never candidates or stale history."""
        if status not in ('active', 'candidate', 'stale', 'superseded', 'all'):
            raise MemoryError('unknown status')
        with self._connect() as db:
            filtered = (type(self) is MemoryLedger and type(status) is str and status != 'all'
                        and (db.execute('SELECT 1 FROM entries WHERE status<>? LIMIT 1',
                                        (status,)).fetchone() or
                             (type(scope) is str and db.execute(
                                 'SELECT 1 FROM entries WHERE scope IS NOT '
                                 '(SELECT scope FROM entries LIMIT 1) LIMIT 1').fetchone())))
            # Uniform scopes cannot discriminate among valid rows. Keep the
            # original path there to avoid decoding all metadata twice when
            # every row matches; raw SQL equality is only a routing guard.
            if filtered:
                try:
                    db.execute('SELECT child,parent FROM dependencies LIMIT 0')
                except sqlite3.OperationalError:
                    # Preserve legacy failures even if no requested-status row
                    # exists, rather than hiding a missing dependency table.
                    filtered = False
            if filtered:
                # Decode all JSON metadata first, preserving failures even on
                # excluded historical entries. SQLite json_valid is not a
                # substitute for Python decoding (BLOB/UTF-8/depth semantics).
                documents = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' "
                                       "AND name='document_dependencies'").fetchone()
                scoped = type(scope) is str
                identity = ',e.id,e.status' if scoped else ''
                if documents:
                    metadata = db.execute(
                        'SELECT e.scope,d.entry_id,d.snapshot' + identity + ' FROM entries e '
                        'LEFT JOIN document_dependencies d ON d.entry_id=e.id '
                        'ORDER BY e.created_at,e.id').fetchall()
                else:
                    identity = ',id,status' if scoped else ''
                    metadata = db.execute('SELECT scope,NULL,NULL' + identity +
                                          ' FROM entries ORDER BY created_at,id').fetchall()
                if scoped:
                    decoded = []
                    for entry_scope, document_id, snapshot, entry_id, entry_status in metadata:
                        parsed_scope = json.loads(entry_scope)
                        if document_id is not None:
                            json.loads(snapshot)
                        decoded.append((entry_id, entry_status, parsed_scope))
                    # Complete *all* JSON decoding before membership: a selected
                    # null scope must not hide a later malformed JSON error.
                    # Preserve Python membership and status short-circuiting,
                    # not SQL LIKE/json_each (strings/dicts differ from arrays).
                    rows = [(entry_id,) for entry_id, entry_status, parsed_scope in decoded
                            if entry_status == status and scope in parsed_scope]
                else:
                    for entry_scope, document_id, snapshot in metadata:
                        json.loads(entry_scope)
                        if document_id is not None:
                            json.loads(snapshot)
                    rows = db.execute('SELECT id FROM entries WHERE status=? ORDER BY created_at,id',
                                      (status,)).fetchall()
            else:
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


_BUILTIN_GET = MemoryLedger._get
_BUILTIN_READ_ENTRY = _read_entry
_BUILTIN_PUBLIC_CHECK = MemoryLedger.check
_BUILTIN_WALK = MemoryLedger._walk
_BUILTIN_CHECK = MemoryLedger._check
_BUILTIN_CONNECT = MemoryLedger._connect
_BUILTIN_DOCUMENT_CHECK = check_document_refs
_BUILTIN_SQLITE_CONNECT = sqlite3.connect
_BUILTIN_SQLITE_ROW = sqlite3.Row


def check_task_memory(root, task):
    """Optional task references become a mandatory validity gate when supplied."""
    refs = task.get('memory_refs')
    if refs is None or refs == []:
        return []
    return MemoryLedger(root).check(refs)


def _load_document_refs(path):
    if not path:
        return None
    try:
        return json.loads(Path(path).read_text())
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise MemoryError('document_refs file must contain valid JSON text') from exc


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
    add.add_argument('--document-refs', help='JSON document dependency snapshot, not authorization')
    add.add_argument('--evidence', choices=EVIDENCE, default='candidate')
    for command in ('correct', 'accept'):
        action = sub.add_parser(command)
        action.add_argument('--id', required=True)
        action.add_argument('--new-id', required=True)
        action.add_argument('--source', required=True)
        action.add_argument('--reason', required=True)
        if command == 'correct':
            action.add_argument('--content', required=True)
            action.add_argument('--document-refs', help='current JSON document dependency snapshot')
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
            result = ledger.add(args.id, args.kind, args.content, args.source, args.dep, args.scope, args.evidence,
                                _load_document_refs(args.document_refs))
        elif args.command == 'correct':
            result = ledger.correct(args.id, args.new_id, args.content, args.source, args.reason, args.dep,
                                    _load_document_refs(args.document_refs))
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
