"""Independent ATX-BOUNDARY-62 replay and scanner reference; no asserts."""
import argparse
import hashlib
import itertools
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
from agent_runtime import knowledge_index as live
from agent_runtime.knowledge import KnowledgeStore, KnowledgeError
BASE = 'b69b4150e41492183433b1061add742aaa44510b'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def scanner(line):
    """Independent character scanner for one raw line, no production regex."""
    pos = 0
    while pos < len(line) and line[pos] == ' ':
        pos += 1
    if pos > 3:
        return None, 0
    start = pos
    while pos < len(line) and line[pos] == '#':
        pos += 1
    level = pos - start
    if not 1 <= level <= 6 or (pos < len(line) and line[pos] not in ' \t'):
        return None, 0
    end = len(line)
    while end > pos and line[end - 1] in ' \t':
        end -= 1
    hashes = end
    while hashes > pos and line[hashes - 1] == '#':
        hashes -= 1
    if hashes < end and hashes > pos and line[hashes - 1] in ' \t':
        end = hashes
    while pos < end and line[pos] in ' \t':
        pos += 1
    while end > pos and line[end - 1] in ' \t':
        end -= 1
    return line[pos:end], level


def one_node(content, title, level):
    return [dict(node='intro' if title is None else 's1', title='Doc' if title is None else title,
                 level=level, start_line=1, end_line=1, parent=None, text=content)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    output = Path(args.output)
    if output.exists():
        raise SystemExit('existing evidence will not be overwritten')
    paths = ['agent_runtime/knowledge_index.py', 'agent_runtime/knowledge.py',
             'agent_runtime/project_docs.py', 'tests/test_knowledge_atx.py',
             'plugins/research-assistant/skills/model-with-knowledge/scripts/knowledge_index.py',
             'agent_doc/results/atx-boundary62/plan.md', 'agent_doc/results/atx-boundary62/probe.py',
             'agent_doc/results/atx-boundary62/raw.json', 'agent_doc/results/atx-boundary62/raw-O.json',
             'agent_doc/results/atx-boundary62/independent_probe.py']
    hashes = {p: sha((ROOT / p).read_bytes()) for p in paths}
    old_source = subprocess.check_output(['git', 'show', BASE + ':agent_runtime/knowledge_index.py'], cwd=ROOT)
    old = types.ModuleType('agent_runtime._independent_atx_old')
    old.__package__ = 'agent_runtime'
    exec(compile(old_source, BASE + '/knowledge_index.py', 'exec'), old.__dict__)
    failures = []
    def check(ok, label):
        if not ok:
            failures.append(label)
    check((ROOT / paths[0]).read_bytes() == (ROOT / paths[4]).read_bytes(), 'mirror bytes')
    sources = set()
    alphabet = ('#', ' ', '\t', '\\', 'x', '\u00a0')
    for n in range(5):
        for chars in itertools.product(alphabet, repeat=n):
            tail = ''.join(chars)
            for prefix in ('#', '## ', '   ######\t', '    # ', '####### ', '\t# '):
                sources.add(prefix + tail)
    for text in ('', 'ordinary', '# *raw* &amp; ###', '# foo \\###', '# \u2003', '#\u2003foo',
                 '#\u200bfoo', '# foo #\u2003', '######', '# ### #'):
        sources.add(text)
    boundary_count = 0
    boundary_failures = []
    for source in sorted(sources):
        title, level = scanner(source)
        for ending in ('', '\n', '\r\n', '\r'):
            content = source + ending
            actual = live.sections(dict(title='Doc', content=content))
            expected = one_node(content, title, level)
            if not content:
                expected[0]['end_line'] = 0
            boundary_count += 1
            if actual != expected:
                boundary_failures.append(dict(input=content, actual=actual, expected=expected))
    check(not boundary_failures, 'independent scanner equality')
    store = KnowledgeStore(ROOT / 'knowledge')
    corpus = []
    for kid, record in sorted(store.records.items()):
        before, after = old.sections(record), live.sections(record)
        item = dict(id=kid, input_sha256=sha(record['content'].encode()), baseline=before,
                    candidate=after, same=before == after,
                    baseline_reassembly=''.join(n['text'] for n in before) == record['content'],
                    candidate_reassembly=''.join(n['text'] for n in after) == record['content'])
        corpus.append(item)
        check(item['same'] and item['baseline_reassembly'] and item['candidate_reassembly'], 'corpus ' + kid)
    check(len(corpus) == 115 and len({r['id'] for r in corpus}) == 115, 'corpus count/unique')
    raw = [json.loads((ROOT / p).read_text()) for p in paths[7:9]]
    for number, data in enumerate(raw):
        check(data['baseline_source_sha256'] == sha(old_source), 'baseline identity ' + str(number))
        check(data['candidate_source_sha256'] == hashes[paths[0]], 'candidate identity ' + str(number))
        check(data['tests_sha256'] == hashes[paths[3]] and data['probe_sha256'] == hashes[paths[6]], 'test/probe identity')
        check(data['optimized'] == bool(number), 'optimized flag')
        check(data['corpus_snapshot'] == store.snapshot and data['corpus_count'] == 115 and data['corpus_changes'] == [], 'corpus raw')
        check(len(data['rows']) == len({r['input'] for r in data['rows']}) == 72, 'raw uniqueness/denominator')
        for row in data['rows']:
            record = dict(title='Document', content=row['input'])
            check(old.sections(record) == row['baseline'] and live.sections(record) == row['candidate'], 'actual raw replay')
            check(row['baseline_ok'] == (row['baseline'] == row['expected']) and row['candidate_ok'] == (row['candidate'] == row['expected']), 'raw booleans')
        check(sum(r['baseline_ok'] for r in data['rows']) == data['baseline_pass'] == 33, 'baseline count')
        check(sum(r['candidate_ok'] for r in data['rows']) == data['candidate_pass'] == data['total'] == 72, 'candidate count')
    check({k:v for k,v in raw[0].items() if k != 'optimized'} == {k:v for k,v in raw[1].items() if k != 'optimized'}, 'normal/O frozen equivalence')
    with tempfile.TemporaryDirectory(prefix='atx62-independent-') as temp:
        root = Path(temp) / 'corpus'
        entries = root / 'entries'
        entries.mkdir(parents=True)
        template = json.loads((ROOT / 'knowledge/entries/math.cauchy-schwarz.json').read_text())
        template.update(id='test.independent-atx', requires=[], relations=[])
        (entries / 'card.json').write_text(json.dumps(template))
        content = '# Attached#\nroot\n##\nemptyunique\n#\u00a0false\nliteralunique\n# End #\nlast\n'
        (entries / 'card.md').write_text(content)
        fixture = KnowledgeStore(root)
        initial_snapshot = fixture.snapshot
        db = Path(temp) / 'index.sqlite'
        old_build = old.build_index(fixture, db)
        def rows():
            with sqlite3.connect(db) as con:
                return dict(meta=dict(con.execute('SELECT key,value FROM meta')),
                            chunks=[list(r) for r in con.execute('SELECT node,heading,body FROM chunks ORDER BY rowid')])
        old_rows = rows()
        error = None
        try:
            live.indexed_search(fixture, db, 'emptyunique')
        except KnowledgeError as exc:
            error = str(exc)
        rebuilt = live.build_index(fixture, db)
        new_rows = rows()
        noop = live.build_index(fixture, db)
        search = live.indexed_search(fixture, db, 'emptyunique')
        navigation = live.navigate(fixture, 'test.independent-atx')
        fresh_snapshot = KnowledgeStore(root).snapshot
        migration = dict(input=content, old_build=old_build, old_rows=old_rows, error=error,
                         rebuilt=rebuilt, new_rows=new_rows, noop=noop, search=search, navigation=navigation,
                         initial_snapshot=initial_snapshot, fresh_snapshot=fresh_snapshot)
        check(old_rows['meta']['engine_version'].endswith('-v5'), 'real old engine')
        check(error == 'stale index engine; run index to update', 'stale rejection')
        check(old_rows['chunks'] != new_rows['chunks'], 'real changed chunks')
        check(initial_snapshot == fresh_snapshot == rebuilt['snapshot'], 'unchanged fixture')
        check(rebuilt['engine_changed'] and rebuilt['updated'] == 1 and rebuilt['unchanged'] == 0, 'rebuild')
        check(not noop['engine_changed'] and noop['updated'] == 0 and noop['unchanged'] == 1, 'noop')
        check(search['results'][0]['sections'][0]['node'] == 's2', 'search corrected empty section')
        check([n['title'] for n in navigation['nodes']] == ['Attached#', '', 'End'], 'navigation corrected titles')
    check(hashes == {p: sha((ROOT / p).read_bytes()) for p in paths}, 'frozen bytes remain unchanged')
    report = dict(reviewer='/root/atx62_result_review', python=sys.version, platform=platform.platform(),
                  sqlite=sqlite3.sqlite_version, optimized=not __debug__, hashes=hashes,
                  baseline_source_sha256=sha(old_source), corpus_snapshot=store.snapshot,
                  scanner_alphabet=alphabet, scanner_max_tail=4, boundary_count=boundary_count,
                  boundary_failures=boundary_failures, corpus=corpus, migration=migration,
                  failures=failures)
    with output.open('x') as f:
        json.dump(report, f, ensure_ascii=True, indent=2)
    print(json.dumps(dict(boundary_count=boundary_count, corpus_count=len(corpus), failures=failures)))
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
