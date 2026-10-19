"""Frozen baseline/candidate boundary and genuine old-engine migration probe."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sqlite3
import subprocess
import sys
import tempfile
import types

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from agent_runtime import knowledge_index as candidate
from agent_runtime.knowledge import KnowledgeStore, KnowledgeError

BASE = 'b69b4150e41492183433b1061add742aaa44510b'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        raise SystemExit('refusing to overwrite existing evidence')
    source = subprocess.check_output(
        ['git', 'show', BASE + ':agent_runtime/knowledge_index.py'], cwd=ROOT)
    baseline = types.ModuleType('agent_runtime._atx_baseline')
    baseline.__package__ = 'agent_runtime'
    exec(compile(source, BASE + '/knowledge_index.py', 'exec'), baseline.__dict__)
    test_path = ROOT / 'tests/test_knowledge_atx.py'
    spec = importlib.util.spec_from_file_location('atx_cases', test_path)
    cases = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cases)
    rows = []
    for text, title, level in cases.CASES:
        for ending in ('', '\n', '\r\n'):
            content = text + ending
            record = {'title': 'Document', 'content': content}
            expected = cases.expected_single(content, title, level)
            old, new = baseline.sections(record), candidate.sections(record)
            rows.append(dict(input=content, expected=expected, baseline=old, candidate=new,
                             baseline_ok=old == expected, candidate_ok=new == expected))
    store = KnowledgeStore(ROOT / 'knowledge')
    changes = []
    for kid, record in store.records.items():
        old, new = baseline.sections(record), candidate.sections(record)
        if old != new:
            changes.append(dict(id=kid, baseline=old, candidate=new))
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / 'corpus'
        entries = root / 'entries'
        entries.mkdir(parents=True)
        template = json.loads((ROOT / 'knowledge/entries/math.cauchy-schwarz.json').read_text())
        template.update(id='test.atx', requires=[], relations=[])
        (entries / 'card.json').write_text(json.dumps(template))
        (entries / 'card.md').write_text('# C#\nfirst\n##\nsecond\n#\u00a0false\nlast\n')
        synthetic = KnowledgeStore(root)
        db = Path(temp) / 'index.sqlite'
        baseline.build_index(synthetic, db)

        def chunks():
            with sqlite3.connect(db) as con:
                return [list(r) for r in con.execute('SELECT node,heading,body FROM chunks ORDER BY rowid')]

        old_chunks = chunks()
        try:
            candidate.indexed_search(synthetic, db, 'second')
            stale_error = None
        except KnowledgeError as exc:
            stale_error = str(exc)
        rebuilt = candidate.build_index(synthetic, db)
        new_chunks = chunks()
        noop = candidate.build_index(synthetic, db)
        search = candidate.indexed_search(synthetic, db, 'second')
        navigation = candidate.navigate(synthetic, 'test.atx')
        migration = dict(old_chunks=old_chunks, new_chunks=new_chunks, stale_error=stale_error,
                         rebuilt=rebuilt, noop=noop, search=search, navigation=navigation,
                         snapshot=synthetic.snapshot)
    record = dict(base=BASE, python=sys.version, platform=platform.platform(),
                  optimized=not __debug__, baseline_source_sha256=digest(source),
                  candidate_source_sha256=digest(Path(candidate.__file__).read_bytes()),
                  tests_sha256=digest(test_path.read_bytes()),
                  probe_sha256=digest(Path(__file__).read_bytes()),
                  input_sha256=digest(json.dumps(cases.CASES, ensure_ascii=True).encode()),
                  corpus_snapshot=store.snapshot, corpus_count=len(store.records),
                  corpus_changes=changes, rows=rows, migration=migration,
                  baseline_pass=sum(r['baseline_ok'] for r in rows),
                  candidate_pass=sum(r['candidate_ok'] for r in rows), total=len(rows))
    with output.open('x') as handle:
        json.dump(record, handle, ensure_ascii=True, indent=2)
    print(json.dumps({k: record[k] for k in ('baseline_pass', 'candidate_pass', 'total', 'corpus_count')}))
    print('corpus_changed', len(changes), 'stale_error', stale_error)
    if not (record['candidate_pass'] == len(rows) and not changes
            and stale_error == 'stale index engine; run index to update'
            and rebuilt['engine_changed'] and rebuilt['updated'] == 1
            and noop['unchanged'] == 1 and not noop['engine_changed']
            and old_chunks != new_chunks and search['results']
            and [n['title'] for n in navigation['nodes']] == ['C#', '']):
        raise SystemExit('candidate or migration acceptance failed; evidence preserved')


if __name__ == '__main__':
    main()
