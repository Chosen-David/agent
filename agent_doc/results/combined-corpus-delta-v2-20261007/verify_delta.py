#!/usr/bin/env python3
"""Scoped actual-907 corpus delta evidence; old failures remain failures."""
import ast
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import sqlite3
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
REPORT = ROOT / 'docs/document_architecture_validation/knowledge/upstream-v2'
BASE = '907890831929a5d200d3fb64c6299449391a1ee8'
AIK = ROOT / 'docs/knowledge_learning/2026-10-07-ai-algorithms'
CASES = AIK / 'evaluation/frozen_tasks.json'
ENV = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
COMMANDS = []


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha(p):
    return sha_bytes(Path(p).read_bytes())


def write(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def run(cmd, name, *, cwd=ROOT):
    start = time.perf_counter()
    cp = subprocess.run([str(x) for x in cmd], cwd=cwd, env=ENV,
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    (OUT / (name + '.log')).write_text(cp.stdout)
    record = {'name': name, 'command': [str(x) for x in cmd],
              'cwd': str(cwd), 'exit_code': cp.returncode,
              'elapsed_seconds': time.perf_counter() - start,
              'log': str((OUT / (name + '.log')).relative_to(ROOT))}
    COMMANDS.append(record)
    write(OUT / 'commands.json', COMMANDS)
    return cp


def files(root):
    return {p.relative_to(root).as_posix(): sha(p)
            for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in str(p)}


def metadata_gate(corpus, holdouts):
    hits = []
    counts = Counter()
    ids = []
    for p in sorted((corpus / 'entries').rglob('*.json')):
        d = json.loads(p.read_text())
        counts[d['status']] += 1
        if d['status'] != 'published':
            ids.append({'id': d['id'], 'status': d['status'], 'metadata_sha256': sha(p)})
        source_text = json.dumps(d['sources'], ensure_ascii=False).lower()
        for target in holdouts['targets']:
            for key in ('doi', 'url'):
                if key in target and target[key].lower() in source_text:
                    hits.append({'entry': d['id'], 'target': target['id'], 'field': key})
    assert not hits, hits
    return {'counts': dict(counts), 'unpublished': ids,
            'reserved_source_collisions': hits, 'metadata_checked_before_body_access': True}


def compare(a, b, suite, mode):
    rows = []
    regressions = []
    for backend in ('files', 'sqlite'):
        ab = a['backends'][backend]
        bb = b['backends'][backend]
        assert len(ab['queries']) == len(bb['queries'])
        detail = []
        for x, y in zip(ab['queries'], bb['queries']):
            assert (x['case'], x['query'], x['expected']) == (y['case'], y['query'], y['expected'])
            worse = [key for key in ('recall_at_3', 'context_recall', 'reciprocal_rank')
                     if x[key] is not None and y[key] < x[key]]
            if x['no_hit_correct'] is True and y['no_hit_correct'] is not True:
                worse.append('no_hit_correct')
            item = {'case': x['case'], 'baseline': x, 'candidate': y,
                    'regressed_metrics': worse}
            detail.append(item)
            if worse:
                regressions.append({'suite': suite, 'mode': mode, 'backend': backend, **item})
        rows.append({'backend': backend,
                     'baseline': {k: v for k, v in ab.items() if k.startswith('mean_')},
                     'candidate': {k: v for k, v in bb.items() if k.startswith('mean_')},
                     'queries': detail})
    return rows, regressions


def function_dumps(source):
    tree = ast.parse(source)
    return {n.name: ast.dump(n, include_attributes=False) for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.ClassDef))}


def main():
    REPORT.mkdir(parents=True, exist_ok=True)
    assert not (OUT / 'summary.json').exists(), 'Immutable run exists; create a new run for retest'
    start = datetime.now(timezone.utc).isoformat()
    deps = [*ROOT.glob('agent_runtime/*.py'), ROOT / 'scripts/eval_knowledge.py',
            AIK / 'check_domain_recovery.py', AIK / 'compare_retrieval.py', CASES,
            ROOT / 'docs/document_architecture_validation/knowledge/verify_manual_recovery.py',
            *ROOT.glob('tests/test_knowledge*.py'), *ROOT.glob('evals/knowledge/*.json'),
            ROOT / 'knowledge/evaluation_holdouts.json', OUT / 'validation-plan.json',
            AIK / 'final-candidate-freeze.json', Path(__file__)]
    before = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(set(deps))}
    corpus_before = files(ROOT / 'knowledge')
    write(OUT / 'dependencies-before.json', before)
    write(OUT / 'environment.json', {'started_at_utc': start,
          'python': sys.version, 'python_executable': sys.executable,
          'platform': platform.platform(), 'machine': platform.machine(),
          'sqlite_version': sqlite3.sqlite_version, 'network_used': False,
          'third_party_dependencies': [], 'timing_claims': False,
          'runtime_dependency': 'Python standard library and SQLite FTS5',
          'repository_base_commit': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()})
    holdouts = json.loads((ROOT / 'knowledge/evaluation_holdouts.json').read_text())
    with tempfile.TemporaryDirectory(prefix='baseline907-', dir=OUT) as temp:
        temp = Path(temp)
        ENV['TMPDIR'] = str(temp)
        archive = subprocess.check_output(['git', 'archive', BASE, 'knowledge',
                    'agent_runtime', 'scripts/eval_knowledge.py', 'evals/knowledge'], cwd=ROOT)
        # Trusted repository archive; extract only already-selected prefixes.
        cp = subprocess.run(['tar', '-x', '-C', str(temp)], input=archive, capture_output=True)
        assert cp.returncode == 0, cp.stderr
        baseline = temp / 'knowledge'
        candidate = ROOT / 'knowledge'
        gates = {label: metadata_gate(corpus, holdouts)
                 for label, corpus in [('baseline', baseline), ('candidate', candidate)]}
        assert gates['baseline']['counts'] == {'published': 75, 'candidate': 1}, gates
        assert gates['candidate']['counts'] == {'published': 77, 'candidate': 1}, gates
        base_files = files(baseline)
        candidate_files = files(candidate)
        changed = [p for p, h in base_files.items() if candidate_files.get(p) != h]
        added = sorted(set(candidate_files) - set(base_files))
        assert set(changed) <= {'README.md', 'coverage.json', 'learning_state.json'}, changed
        assert all(not p.startswith('entries/') for p in changed), changed
        expected_added = sorted(['entries/ai-algorithms/' + stem + ext
            for stem in ('ai.speculative-decoding-cost-bound', 'ai.speculative-sampling-residual-exactness')
            for ext in ('.json', '.md')] + ['evaluation_holdouts.json'])
        assert added == expected_added, added
        accepted_hashes = json.loads((AIK / 'final-candidate-freeze.json').read_text())['files']
        assert all(candidate_files['entries/ai-algorithms/' + name] == h
                   for name, h in accepted_hashes.items())
        code_diff = {}
        for file in ('knowledge.py', 'knowledge_index.py', 'knowledge_reuse.py'):
            b = (temp / 'agent_runtime' / file).read_text()
            c = (ROOT / 'agent_runtime' / file).read_text()
            fb, fc = function_dumps(b), function_dumps(c)
            code_diff[file] = {'baseline_sha256': sha_bytes(b.encode()),
                 'candidate_sha256': sha_bytes(c.encode()),
                 'changed_definitions': [k for k in set(fb) | set(fc) if fb.get(k) != fc.get(k)]}
        assert code_diff['knowledge.py']['changed_definitions'] == []
        assert code_diff['knowledge_reuse.py']['changed_definitions'] == []
        assert set(code_diff['knowledge_index.py']['changed_definitions']) <= {'_connect'}
        assert sha(temp / 'scripts/eval_knowledge.py') == sha(ROOT / 'scripts/eval_knowledge.py')
        catalogs = sorted((ROOT / 'evals/knowledge').glob('*.json'))
        assert len(catalogs) == 7
        assert all(sha(p) == sha(temp / 'evals/knowledge' / p.name) for p in catalogs)
        # Two different runtime imports are exercised by separate evaluator processes.
        suites, regressions = [], []
        for mode, selected in [('default', catalogs), ('context8', [p for p in catalogs
                if p.name in ('queries.json', 'round2-queries.json', 'morphology-queries.json')])]:
            for cases in selected:
                data = {}
                for label, corpus, script in [('baseline', baseline, temp / 'scripts/eval_knowledge.py'),
                        ('candidate', candidate, ROOT / 'scripts/eval_knowledge.py')]:
                    name = mode + '-' + cases.stem + '-' + label
                    output = OUT / (name + '.json')
                    cmd = [sys.executable, script, '--root', corpus, '--cases', cases, '--output', output]
                    if mode == 'context8':
                        cmd += ['--accept-context', '--context-limit', '8']
                    res = run(cmd, name)
                    assert res.returncode in (0, 1), res.stdout
                    data[label] = json.loads(output.read_text())
                rows, worse = compare(data['baseline'], data['candidate'], cases.stem, mode)
                regressions.extend(worse)
                suites.append({'mode': mode, 'suite': cases.stem, 'cases_sha256': sha(cases),
                               'backends': rows})
        write(OUT / 'catalog-comparison.json', {'scope': 'Actual907 runtime and corpus versus combined runtime and corpus; authored regression, not blind/model/semantic validation.',
            'no_new_regressions': not regressions, 'regressions': regressions, 'suites': suites})
        # Run current replay script against both corpora: baseline lacks the two intentionally new AIK targets.
        development = {}
        for label, corpus in [('baseline', baseline), ('candidate', candidate)]:
            for mode in ('default', 'domain'):
                name = 'aik-' + mode + '-' + label
                output = OUT / (name + '.json')
                cmd = [sys.executable, AIK / 'check_domain_recovery.py', '--repo', ROOT,
                       '--corpus', corpus, '--cases', CASES, '--output', output]
                if mode == 'default':
                    cmd += ['--unscoped']
                res = run(cmd, name)
                assert res.returncode in (0, 1), res.stdout
                d = json.loads(output.read_text())
                development[name] = {'exit_code': res.returncode, 'context_hits': sum(x['hit'] for x in d['rows']),
                    'raw_hits': sum(x['target'] in x['raw_ids'] for x in d['rows']),
                    'checks': len(d['rows']), 'failures': [{'case': x['case'], 'backend': x['backend']} for x in d['rows'] if not x['hit']],
                    'backends': {b: {'context_hits': sum(x['hit'] for x in d['rows'] if x['backend'] == b),
                                    'raw_hits': sum(x['target'] in x['raw_ids'] for x in d['rows'] if x['backend'] == b)} for b in ('files','sqlite')}}
        res = run([sys.executable, ROOT / 'docs/document_architecture_validation/knowledge/verify_manual_recovery.py',
            '--repo', ROOT, '--corpus', candidate, '--cases', CASES,
            '--output', OUT / 'manual-recovery.json'], 'manual-recovery')
        assert res.returncode == 0, res.stdout
        sys.path.insert(0, str(ROOT))
        from agent_runtime.knowledge import KnowledgeStore, KnowledgeError
        from agent_runtime.knowledge_index import build_index, indexed_search
        exclusion = []
        for label, corpus in [('baseline', baseline), ('candidate', candidate)]:
            store = KnowledgeStore(corpus)
            db = temp / (label + '-exclusion.sqlite')
            build_index(store, db)
            kid = 'neuro.cephalopod-arm-segmentation'
            query = '头足类 腕部 分段 神经连接 cephalopod arm segmentation'
            blocked = False
            try:
                store.get(kid)
            except KnowledgeError:
                blocked = True
            file_ids = [r['id'] for r in store.search(query, limit=20)['results']]
            sqlite_ids = [r['id'] for r in indexed_search(store, db, query, limit=20)['results']]
            con = sqlite3.connect(db)
            indexed_ids = [r[0] for r in con.execute('SELECT id FROM entries')]
            con.close()
            assert blocked and kid not in file_ids and kid not in sqlite_ids and kid not in indexed_ids
            exclusion.append({'corpus': label, 'snapshot': store.snapshot,
                'metadata_count': len(store.records), 'indexed_published_count': len(indexed_ids),
                'candidate_id': kid, 'candidate_get_blocked': blocked,
                'file_results': file_ids, 'sqlite_results': sqlite_ids,
                'candidate_absent_from_index': kid not in indexed_ids,
                'candidate_status': store.records[kid]['status'],
                'candidate_ref': store.ref(kid)})
        write(OUT / 'candidate-exclusion.json', exclusion)
        preservation = {'base_commit': BASE, 'archive_sha256': sha_bytes(archive),
            'metadata': gates, 'baseline_file_hashes': base_files,
            'candidate_file_hashes': candidate_files, 'unchanged_baseline_files': len(base_files) - len(changed),
            'changed_baseline_files': changed, 'added_files': added,
            'accepted_aik_card_hashes_match': True, 'catalogs_match_base': True,
            'holdout_registry_sha256': sha(ROOT / 'knowledge/evaluation_holdouts.json'),
            'reserved_target_contents_read': False, 'code_comparison': code_diff}
        write(OUT / 'preservation.json', preservation)
        # Knowledge-related suite only; parent owns the full730 suite.
        res = run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests',
                   '-p', 'test_knowledge*.py', '-v'], 'knowledge-tests')
        tests_passed = res.returncode == 0
        test_match = re.search(r'Ran (\d+) tests? in ([0-9.]+)s', res.stdout)
        assert test_match, res.stdout[-1000:]
        test_count = int(test_match.group(1))
    after = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(set(deps))}
    write(OUT / 'dependencies-after.json', after)
    assert before == after, 'Test dependencies changed during measurement'
    assert corpus_before == files(ROOT / 'knowledge'), 'Candidate corpus changed during measurement'
    snapshot = {x['corpus']: x['snapshot'] for x in exclusion}
    summary = {'schema_version': 1, 'task_refs': ['AIK-03', 'DOC-04'],
        'started_at_utc': start, 'completed_at_utc': datetime.now(timezone.utc).isoformat(),
        'status': 'measured-pending-release-review', 'base_commit': BASE,
        'snapshots': snapshot, 'published_counts': {'baseline':75, 'candidate':77},
        'unpublished_candidate_counts': {'baseline':1, 'candidate':1},
        'default_catalog_queries': sum(len(json.loads(p.read_text())['cases']) for p in catalogs),
        'default_query_backend_pairs': sum(len(json.loads(p.read_text())['cases']) for p in catalogs) * 2,
        'context8_legacy_query_backend_pairs': 42,
        'no_new_regressions': not regressions, 'regression_pairs': len(regressions),
        'development': development, 'manual_recovery': json.loads((OUT / 'manual-recovery.json').read_text())['all_recovered'],
        'focused_tests': {'passed': tests_passed, 'test_count': test_count},
        'candidate_excluded': True, 'source_dependencies_stable': before == after,
        'limitations': ['Authored synthetic/development retrieval, not unseen task evaluation or live model quality.',
            'Raw timings are recorded for provenance only; no latency, token, GPU, or performance claim.',
            'Historical recall failures remain failures; manual recovery is informed relevance selection, not automatic repair.',
            'Cephalopod card remains candidate; no external source review, source-data reproduction, scientific promotion, or animal/AI experiment.',
            'Holdout metadata identity checks do not prove complete absence of semantic leakage.',
            'Focused tests do not replace the parent full-suite run or final independent result gate.']}
    write(OUT / 'summary.json', summary)
    write(REPORT / 'summary.json', summary)
    write(OUT / 'artifact-manifest.json', {p.relative_to(ROOT).as_posix(): sha(p)
        for p in sorted(OUT.rglob('*')) if p.is_file() and p.name != 'artifact-manifest.json'})
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not regressions and tests_passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
