"""Rebuildable SQLite FTS5 index with contextual sections and reciprocal-rank fusion.

No model downloads or network calls. BM25 is SQLite's implementation, not a new
search engine. Fusion combines document, section and curated structural matches;
it is not dense semantic retrieval or a learned reranker.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sqlite3
import unicodedata

if __package__:
    from .knowledge import KnowledgeError, _require, _terms, _text
else:
    from knowledge import KnowledgeError, _require, _terms, _text

INDEX_VERSION = '1'


def sections(record):
    """Heading tree with exact source line ranges; fenced code is not a heading."""
    lines = record['content'].splitlines(keepends=True)
    headings, stack, fence = [], [], None
    for number, line in enumerate(lines, 1):
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
        if marker:
            mark = marker.group(1)
            if fence is None:
                fence = mark
            elif mark[0] == fence[0] and len(mark) >= len(fence):
                fence = None
            continue
        if fence:
            continue
        match = re.match(r'^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$', line)
        if not match:
            continue
        level = len(match.group(1))
        while stack and stack[-1]['level'] >= level:
            stack.pop()
        node = {'node': 's' + str(len(headings)+1), 'title': match.group(2),
                'level': level, 'start_line': number,
                'parent': stack[-1]['node'] if stack else None}
        headings.append(node)
        stack.append(node)
    if not headings or headings[0]['start_line'] > 1:
        headings.insert(0, {'node':'intro','title':record['title'],'level':0,'start_line':1,'parent':None})
    result=[]
    for index, node in enumerate(headings):
        end = headings[index+1]['start_line']-1 if index+1 < len(headings) else len(lines)
        result.append({**node, 'end_line':end, 'text':''.join(lines[node['start_line']-1:end])})
    return result


def _tokenize(text):
    # Chinese bigrams and normalized English terms keep SQLite's tokenizer useful
    # without a platform-specific tokenizer extension. No dense semantics claimed.
    normalized = unicodedata.normalize('NFKC', text).casefold()
    words = re.findall(r'[a-z0-9]+(?:[-_][a-z0-9]+)*', normalized)
    for run in re.findall(r'[\u3400-\u9fff]+', normalized):
        words.extend(run[i:i+2] for i in range(len(run)-1))
        if len(run) == 1:
            words.append(run)
    return ' '.join(words)


def _connect(path, readonly=False):
    path = Path(path).absolute()
    _require(not any(p.is_symlink() for p in (path, *path.parents)), 'index path traverses symlink')
    if readonly:
        _require(path.is_file(), 'knowledge index missing; run index first')
        con = sqlite3.connect(path.as_uri()+'?mode=ro', uri=True, timeout=10)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(path, timeout=10)
    con.row_factory=sqlite3.Row
    con.execute('PRAGMA trusted_schema=OFF')
    return con


def _initialize(con):
    tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if tables:
        _require('meta' in tables, 'refusing to overwrite an unrelated database')
        marker = con.execute("SELECT value FROM meta WHERE key='index_version'").fetchone()
        _require(marker is not None and marker[0] == INDEX_VERSION, 'unsupported knowledge index')
        return
    con.executescript('''
        CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE entries(id TEXT PRIMARY KEY, hash TEXT NOT NULL);
        CREATE VIRTUAL TABLE docs USING fts5(id UNINDEXED, title, context, body);
        CREATE VIRTUAL TABLE chunks USING fts5(id UNINDEXED, node UNINDEXED, heading, context, body);
    ''')
    con.execute('INSERT INTO meta VALUES (?,?)',('index_version',INDEX_VERSION))


def build_index(store, path, *, rebuild=False):
    """Transactional upsert only changed entries; deletion never touches sources."""
    con=_connect(path)
    try:
        _initialize(con)
        oldroot=con.execute("SELECT value FROM meta WHERE key='root'").fetchone()
        _require(oldroot is None or oldroot[0] == str(store.root), 'index belongs to a different corpus')
        old=dict(con.execute('SELECT id, hash FROM entries'))
        current={kid:d['sha256'] for kid,d in store.records.items() if d['status']=='published'}
        changed=[kid for kid,h in current.items() if rebuild or old.get(kid)!=h]
        removed=sorted(set(old)-set(current))
        with con:
            for kid in set(changed)|set(removed):
                con.execute('DELETE FROM docs WHERE id=?',(kid,))
                con.execute('DELETE FROM chunks WHERE id=?',(kid,))
                con.execute('DELETE FROM entries WHERE id=?',(kid,))
            for kid in changed:
                d=store.records[kid]
                context=' '.join([d['summary'],*d['aliases'],*d['domains'],*d['structures'],*d['assumptions']])
                con.execute('INSERT INTO entries VALUES (?,?)',(kid,d['sha256']))
                con.execute('INSERT INTO docs VALUES (?,?,?,?)',(kid,_tokenize(d['title']),_tokenize(context),_tokenize(d['content'])))
                for node in sections(d):
                    con.execute('INSERT INTO chunks VALUES (?,?,?,?,?)',(kid,node['node'],_tokenize(node['title']),_tokenize(d['title']+' '+d['summary']),_tokenize(node['text'])))
            for key,value in [('root',str(store.root)),('snapshot',store.snapshot)]:
                con.execute('INSERT OR REPLACE INTO meta VALUES (?,?)',(key,value))
        return {'backend':'sqlite-fts5-rrf-v1','snapshot':store.snapshot,'indexed':len(current),
                'updated':len(changed),'removed':len(removed),'unchanged':len(current)-len(changed)}
    finally:
        con.close()


def indexed_search(store, path, query, *, domain=None, structure=None, limit=5):
    _require(_text(query) and len(query)<=2000, 'query must contain 1..2000 characters')
    _require(type(limit) is int and 1<=limit<=20, 'limit must be 1..20')
    con=_connect(path,readonly=True)
    try:
        meta=dict(con.execute('SELECT key,value FROM meta'))
        _require(meta.get('index_version')==INDEX_VERSION and meta.get('root')==str(store.root), 'index schema/corpus mismatch')
        _require(meta.get('snapshot')==store.snapshot, 'stale knowledge index; run index to update')
        terms=_terms(query)
        if not terms:
            return {'schema_version':1,'snapshot':store.snapshot,'backend':'sqlite-fts5-rrf-v1','applicability':'unchecked','results':[]}
        # Terms are bound data, not raw FTS syntax; input cannot inject SQL/MATCH.
        expression=' OR '.join('"'+term.replace('"','""')+'"' for term in sorted(terms))
        # Filter before limiting so nonmatching domains cannot crowd out hits.
        allowed={k for k,d in store.records.items() if d['status']=='published'
                 and (not domain or domain in d['domains']) and (not structure or structure in d['structures'])}
        ranks=[]
        for table,weights in [('docs','0,5,3,1'),('chunks','0,0,4,2,1')]:
            rows=con.execute(f'SELECT id, bm25({table},{weights}) AS distance FROM {table} WHERE {table} MATCH ? ORDER BY distance,id',(expression,))
            ordered=[];seen=set()
            for row in rows:
                if row['id'] in allowed and row['id'] not in seen:
                    ordered.append(row['id']);seen.add(row['id'])
                    if len(ordered)==max(50,limit*5): break
            ranks.append(ordered)
        structural=[]
        for kid in allowed:
            d=store.records[kid]
            overlap=terms&_terms(' '.join([*d['aliases'],*d['structures'],d['title']]))
            if overlap: structural.append((len(overlap),kid))
        ranks.append([kid for score,kid in sorted(structural,key=lambda x:(-x[0],x[1]))[:max(50,limit*5)]])
        scores={};reasons={}
        for lane,ranked in zip(('document-bm25','section-bm25','curated-structure'),ranks):
            for rank,kid in enumerate(ranked,1):
                scores[kid]=scores.get(kid,0)+1/(60+rank)
                reasons.setdefault(kid,[]).append({'retriever':lane,'rank':rank})
        results=[]
        for kid in sorted(scores,key=lambda k:(-scores[k],k))[:limit]:
            d=store.get(kid)
            ranked_sections=sorted(sections(d),key=lambda n:(-len(terms&_terms(n['text']+' '+n['title'])),n['start_line']))
            excerpts=[{k:n[k] for k in ('node','title','start_line','end_line')} | {'excerpt':n['text'][:900]}
                      for n in ranked_sections[:2] if terms&_terms(n['text']+' '+n['title'])]
            results.append({**store.ref(kid),'title':d['title'],'summary':d['summary'],
                            'status':d['status'],'assumptions':d['assumptions'],'verification':d['verification'],
                            'matches':reasons[kid],'score':scores[kid],'sections':excerpts})
        return {'schema_version':1,'snapshot':store.snapshot,'backend':'sqlite-fts5-rrf-v1',
                'applicability':'unchecked','results':results}
    except sqlite3.DatabaseError as exc:
        raise KnowledgeError('invalid knowledge index: '+str(exc)) from exc
    finally:
        con.close()


def navigate(store, kid, node=None):
    d=store.get(kid)
    tree=sections(d)
    if node is not None:
        selected=next((n for n in tree if n['node']==node),None)
        _require(selected is not None, 'unknown section node')
        return {**store.ref(kid),'section':selected,'knowledge_refs':d['knowledge_refs']}
    return {**store.ref(kid),'nodes':[{k:v for k,v in n.items() if k!='text'} for n in tree]}
