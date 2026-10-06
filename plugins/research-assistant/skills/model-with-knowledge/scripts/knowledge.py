"""File-first knowledge retrieval, validation and explicit candidate maintenance.

File search needs no database; the optional SQLite index is rebuildable.
No operation makes network requests or downloads a model.

Relevance is lexical, never evidence of applicability or mathematical correctness.
The same API can be implemented by an indexed backend without changing consumers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import sqlite3
import unicodedata

# Standalone bundle remains usable under Python -I as well as normal execution.
if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

SCHEMA_VERSION = 1
MAX_BYTES = 1_048_576
STATUSES = {'candidate', 'published', 'deprecated'}
KINDS = {'definition', 'theorem', 'method', 'modeling-pattern', 'case', 'counterexample'}
RELATIONS = {'prerequisite', 'corollary', 'special-case', 'counterexample', 'application', 'related'}


class KnowledgeError(ValueError):
    """Invalid corpus, unavailable record, or stale pinned reference."""


def _require(ok, message):
    if not ok:
        raise KnowledgeError(message)


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _strings(value, nonempty=False):
    return (isinstance(value, list) and (bool(value) or not nonempty)
            and all(_text(x) for x in value) and len(value) == len(set(value)))


def _positive(value):
    return type(value) is int and value > 0


def _json(text):
    def pairs(items):
        out = {}
        for key, value in items:
            _require(key not in out, 'duplicate JSON key: ' + key)
            out[key] = value
        return out
    return json.loads(text, object_pairs_hook=pairs)


def _digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


def _terms(text):
    normalized = unicodedata.normalize('NFKC', text).casefold()
    terms = set(re.findall(r'[a-z0-9]+(?:[-_][a-z0-9]+)*', normalized))
    for run in re.findall(r'[\u3400-\u9fff]+', normalized):
        terms.update(run[i:i+2] for i in range(len(run)-1))
        if len(run) == 1:
            terms.add(run)
    return terms


class KnowledgeStore:
    """A validated in-memory snapshot of one explicit corpus root.

    Each entry is a JSON metadata file paired with same-stem Markdown. Results
    pin both bytes by semantic content hash. No implicit cwd fallback/merging.
    Validation checks structure and declared dependencies, not scientific truth.
    """

    def __init__(self, root):
        supplied = Path(root).absolute()
        _require(not any(p.is_symlink() for p in [supplied, *supplied.parents]),
                 'corpus root must not traverse symlinks')
        self.root = supplied.resolve()
        _require(self.root.is_dir(), 'knowledge root missing')
        entries = self.root / 'entries'
        _require(entries.is_dir() and not entries.is_symlink(), 'entries directory missing or redirected')
        files = sorted(entries.rglob('*'))
        _require(not any(p.is_symlink() for p in files), 'symlinks are not allowed in entries')
        self.records = {}
        metadata = [p for p in files if p.suffix == '.json']
        _require(bool(metadata), 'empty knowledge corpus')
        for path in metadata:
            data = _json(self._read(path))
            self._validate(data)
            kid = data['id']
            _require(kid not in self.records, 'duplicate knowledge ID: ' + kid)
            body = self._read(path.with_suffix('.md'))
            _require(bool(body.strip()), 'empty Markdown: ' + kid)
            self.records[kid] = {**data, 'content': body,
                                 'path': path.relative_to(self.root).as_posix(),
                                 'sha256': _digest({'metadata': data, 'content': body})}
        for path in files:
            if path.suffix == '.md':
                _require(path.with_suffix('.json').is_file(), 'orphan Markdown: ' + str(path))
        self._validate_links()
        self.snapshot = _digest([self.ref(k) for k in sorted(self.records)])

    def _read(self, path):
        _require(path.resolve().is_relative_to(self.root) and not path.is_symlink(),
                 'path outside corpus: ' + str(path))
        _require(path.is_file(), 'missing entry file: ' + str(path))
        _require(path.stat().st_size <= MAX_BYTES, 'entry exceeds byte budget')
        return path.read_text(encoding='utf-8')

    @staticmethod
    def _validate(d):
        _require(isinstance(d, dict), 'metadata must be an object')
        fields = {'schema_version', 'id', 'version', 'status', 'kind', 'title', 'summary',
                  'aliases', 'domains', 'structures', 'assumptions', 'sources',
                  'verification', 'requires', 'relations'}
        _require(set(d) == fields, 'metadata fields mismatch: ' + str(sorted(set(d) ^ fields)))
        _require(type(d['schema_version']) is int and d['schema_version'] == SCHEMA_VERSION,
                 'unsupported knowledge schema')
        _require(isinstance(d['id'], str) and re.fullmatch(r'[a-z][a-z0-9.-]{2,100}', d['id']), 'invalid ID')
        _require(_positive(d['version']), 'version must be a positive integer')
        _require(isinstance(d['status'], str) and isinstance(d['kind'], str)
                 and d['status'] in STATUSES and d['kind'] in KINDS, 'invalid status or kind')
        for key in ('title', 'summary'):
            _require(_text(d[key]), 'missing ' + key)
        for key in ('aliases', 'domains', 'structures', 'assumptions'):
            _require(_strings(d[key], key in ('domains', 'structures', 'assumptions')), 'invalid ' + key)
        _require(isinstance(d['sources'], list) and bool(d['sources']), 'sources required')
        for s in d['sources']:
            _require(isinstance(s, dict) and set(s) == {'url', 'locator', 'accessed'}, 'invalid source fields')
            _require(all(_text(v) for v in s.values()) and re.match(r'^https?://[^/\s]+', s['url']), 'invalid source')
            _require(re.fullmatch(r'\d{4}-\d{2}-\d{2}', s['accessed']), 'invalid source date')
        v = d['verification']
        _require(isinstance(v, dict) and set(v) == {'source', 'proof', 'checks'}, 'invalid verification fields')
        _require(v['source'] in ('checked', 'unverified'), 'invalid source verification')
        _require(v['proof'] in ('not-applicable', 'not-checked', 'derivation-reviewed', 'formal'), 'invalid proof status')
        _require(_strings(v['checks']), 'invalid verification checks')
        if d['status'] == 'published':
            _require(v['source'] == 'checked' and bool(v['checks']), 'published entries need source and check evidence')
        if v['proof'] == 'formal':
            _require(bool(v['checks']), 'formal proof needs evidence; label alone is not proof')
        for field in ('requires', 'relations'):
            _require(isinstance(d[field], list), 'invalid ' + field)
        for dep in d['requires']:
            _require(isinstance(dep, dict) and set(dep) == {'id', 'version'}
                     and _text(dep['id']) and _positive(dep['version']), 'invalid prerequisite')
        _require(len({x['id'] for x in d['requires']}) == len(d['requires']), 'duplicate prerequisite')
        for rel in d['relations']:
            _require(isinstance(rel, dict) and set(rel) == {'type', 'id'}
                     and isinstance(rel['type'], str) and rel['type'] in RELATIONS and _text(rel['id']), 'invalid relation')

    def _validate_links(self):
        for kid, d in self.records.items():
            for rel in [*d['requires'], *d['relations']]:
                _require(rel['id'] in self.records and rel['id'] != kid, 'missing or self-linked target: ' + kid)
            for dep in d['requires']:
                target = self.records[dep['id']]
                if d['status'] == 'published':
                    _require(target['status'] == 'published' and target['version'] == dep['version'],
                             'stale prerequisite: ' + kid + ' -> ' + dep['id'])
        # Iterative topological check also supports deep prerequisite chains.
        from collections import deque
        remaining = {kid: len(d['requires']) for kid, d in self.records.items()}
        dependents = {kid: [] for kid in self.records}
        for kid, d in self.records.items():
            for dep in d['requires']:
                dependents[dep['id']].append(kid)
        ready = deque(kid for kid, count in remaining.items() if count == 0)
        count = 0
        while ready:
            kid = ready.popleft()
            count += 1
            for child in dependents[kid]:
                remaining[child] -= 1
                if remaining[child] == 0:
                    ready.append(child)
        _require(count == len(self.records), 'cyclic prerequisites')

    def ref(self, kid):
        _require(isinstance(kid, str) and kid in self.records, 'unknown knowledge ID: ' + str(kid))
        return {k: self.records[kid][k] for k in ('id', 'version', 'sha256')}

    def get(self, kid, *, include_unpublished=False):
        self.ref(kid)
        d = self.records[kid]
        _require(include_unpublished or d['status'] == 'published', 'entry is not published: ' + kid)
        # Return an isolated value so a consumer cannot mutate the pinned snapshot.
        out = json.loads(json.dumps(d))
        closure, pending = set(), [kid]
        while pending:
            key = pending.pop()
            if key in closure:
                continue
            closure.add(key)
            pending.extend(dep['id'] for dep in self.records[key]['requires'])
        out['knowledge_refs'] = [self.ref(key) for key in sorted(closure)]
        return out

    def search(self, query, *, domain=None, structure=None, limit=5, include_unpublished=False):
        _require(_text(query) and len(query) <= 2000, 'query must contain 1..2000 characters')
        _require(type(limit) is int and 1 <= limit <= 20, 'limit must be 1..20')
        terms = _terms(query)
        rows = []
        for kid, d in self.records.items():
            if d['status'] != 'published' and not include_unpublished:
                continue
            if domain and domain not in d['domains']:
                continue
            if structure and structure not in d['structures']:
                continue
            matches, score = [], 0
            for field, weight in [('title', 5), ('aliases', 5), ('structures', 4),
                                  ('summary', 3), ('domains', 2), ('content', 1)]:
                text = ' '.join(d[field]) if isinstance(d[field], list) else d[field]
                overlap = terms & _terms(text)
                if overlap:
                    matches.append({'field': field, 'terms': sorted(overlap)})
                    score += weight * len(overlap)
            if score:
                rows.append({**self.ref(kid), 'title': d['title'], 'summary': d['summary'],
                             'status': d['status'], 'assumptions': d['assumptions'],
                             'verification': d['verification'], 'matches': matches, 'score': score})
        rows.sort(key=lambda x: (-x['score'], x['id']))
        return {'schema_version': 1, 'snapshot': self.snapshot, 'backend': 'files-lexical-v1',
                'applicability': 'unchecked', 'results': json.loads(json.dumps(rows[:limit]))}

    def related(self, kid, *, limit=20):
        _require(type(limit) is int and 1 <= limit <= 20, 'limit must be 1..20')
        d = self.get(kid)
        edges = [{'type': 'prerequisite', **x} for x in d['requires']] + d['relations']
        results = []
        for edge in edges:
            target = self.records[edge['id']]
            if target['status'] == 'published':
                results.append({'type': edge['type'], **self.ref(edge['id']), 'title': target['title']})
        return {'snapshot': self.snapshot, 'results': results[:limit], 'truncated': len(results) > limit}

    def check_refs(self, refs):
        _require(isinstance(refs, list) and bool(refs), 'nonempty knowledge_refs list required')
        seen = set()
        for ref in refs:
            _require(isinstance(ref, dict) and set(ref) == {'id', 'version', 'sha256'}, 'invalid knowledge ref')
            _require(_text(ref['id']) and ref['id'] not in seen, 'duplicate or invalid knowledge ref')
            _require(_positive(ref['version']) and isinstance(ref['sha256'], str)
                     and re.fullmatch(r'[a-f0-9]{64}', ref['sha256']), 'invalid pinned version/hash')
            seen.add(ref['id'])
            current = self.ref(ref['id'])
            _require(self.records[ref['id']]['status'] == 'published', 'entry is not published: ' + ref['id'])
            _require(ref == current, 'stale knowledge ref: ' + ref['id'])
        for kid in seen:
            _require(all(x['id'] in seen for x in self.records[kid]['requires']),
                     'knowledge refs omit prerequisites: ' + kid)
        return {'valid': True, 'snapshot': self.snapshot, 'knowledge_refs': refs,
                'scope': 'content identity and published prerequisites; applicability unchecked'}


def check_task_knowledge(root, task):
    """Optional task refs become a gate; unreferenced old tasks stay compatible.

    Corpus must be materialized inside the project. This field grants no access
    to an external path and never downloads or installs a knowledge backend.
    """
    refs = task.get('knowledge_refs')
    if refs is None or refs == []:
        return []
    relative = task.get('knowledge_root', 'knowledge')
    _require(_text(relative) and not Path(relative).is_absolute(), 'knowledge_root must be project-relative')
    project = Path(root).resolve()
    target = project / relative
    _require(target.resolve().is_relative_to(project), 'knowledge_root outside project')
    return KnowledgeStore(target).check_refs(refs)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, help='explicit knowledge directory')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('validate')
    sub.add_parser('snapshot')
    index = sub.add_parser('index')
    index.add_argument('--db', required=True)
    index.add_argument('--rebuild', action='store_true')
    tree = sub.add_parser('tree')
    tree.add_argument('id')
    section = sub.add_parser('section')
    section.add_argument('id')
    section.add_argument('node')
    ingest = sub.add_parser('ingest')
    ingest.add_argument('metadata')
    ingest.add_argument('body')
    search = sub.add_parser('search')
    search.add_argument('query')
    search.add_argument('--index', help='SQLite index built with index command')
    search.add_argument('--domain')
    search.add_argument('--structure')
    search.add_argument('--limit', type=int, default=5)
    search.add_argument('--include-unpublished', action='store_true')
    get = sub.add_parser('show')
    get.add_argument('id')
    get.add_argument('--include-unpublished', action='store_true')
    get.add_argument('--version', type=int)
    get.add_argument('--sha256')
    related = sub.add_parser('related')
    related.add_argument('id')
    related.add_argument('--limit', type=int, default=20)
    check = sub.add_parser('check-refs')
    check.add_argument('file', help='JSON object with nonempty knowledge_refs')
    args = parser.parse_args(argv)
    try:
        store = KnowledgeStore(args.root)
        if args.command in ('index', 'tree', 'section') or (args.command == 'search' and args.index):
            if __package__:
                from .knowledge_index import build_index, indexed_search, navigate
            else:
                from knowledge_index import build_index, indexed_search, navigate
            if args.command == 'index':
                out = build_index(store, args.db, rebuild=args.rebuild)
            elif args.command in ('tree', 'section'):
                out = navigate(store, args.id, getattr(args, 'node', None))
            else:
                _require(not args.include_unpublished, 'index contains published entries only')
                out = indexed_search(store, args.index, args.query, domain=args.domain,
                                     structure=args.structure, limit=args.limit)
        elif args.command == 'ingest':
            if __package__:
                from .knowledge_ingest import ingest
            else:
                from knowledge_ingest import ingest
            out = ingest(args.root, args.metadata, args.body)
        elif args.command == 'search':
            out = store.search(args.query, domain=args.domain, structure=args.structure,
                               limit=args.limit, include_unpublished=args.include_unpublished)
        elif args.command == 'show':
            out = store.get(args.id, include_unpublished=args.include_unpublished)
            _require((args.version is None) == (args.sha256 is None), 'pin both version and sha256')
            if args.version is not None:
                _require(store.ref(args.id) == {'id': args.id, 'version': args.version, 'sha256': args.sha256},
                         'stale knowledge ref: ' + args.id)
        elif args.command == 'related':
            out = store.related(args.id, limit=args.limit)
        elif args.command == 'check-refs':
            doc = _json(Path(args.file).read_text(encoding='utf-8'))
            _require(isinstance(doc, dict), 'refs document must be an object')
            out = store.check_refs(doc.get('knowledge_refs'))
        else:
            out = {'valid': True, 'entries': len(store.records), 'snapshot': store.snapshot,
                   'scope': 'structural validation only; not scientific proof'}
            if args.command == 'snapshot':
                out['knowledge_refs'] = [store.ref(k) for k in sorted(store.records)
                                         if store.records[k]['status'] == 'published']
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0
    except (KnowledgeError, OSError, ValueError, TypeError, RecursionError, sqlite3.DatabaseError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
