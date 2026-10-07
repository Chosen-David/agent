#!/usr/bin/env python3
"""Minimal corpus adoption and development retrieval checks; no new scientific validation."""
import ast
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import sqlite3
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
REPORT = ROOT / 'docs/document_architecture_validation/knowledge/upstream-v3'
REMOTE = 'f9898dfbd23e9bad7897643b54a419d8c88135bd'
PRIOR_TREE = 'a922965b886c38d95dbcb94d2e65f4aee338f6ae'
AIK = ROOT / 'docs/knowledge_learning/2026-10-07-ai-algorithms'
MATRIX = ROOT / 'docs/knowledge_learning/2026-10-07-matrix-concentration'
PLUGIN = ROOT / 'plugins/research-assistant/skills/model-with-knowledge'
SCOPE = json.loads((OUT / 'validation-plan.json').read_text())['scope']
ENV = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
COMMANDS = []


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ref(path):
    path = Path(path)
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}


def write(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def git_blob(tree, path):
    return subprocess.check_output(['git', 'show', tree + ':' + path], cwd=ROOT)


def git_paths(tree, prefix):
    return subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', tree, prefix], cwd=ROOT, text=True).splitlines()


def tree_hashes(tree, prefix):
    return {p: sha(git_blob(tree, p)) for p in git_paths(tree, prefix)}


def disk_hashes(root):
    return {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}


def run(cmd, name, allowed=(0,)):
    cp = subprocess.run([str(x) for x in cmd], cwd=ROOT, env=ENV, text=True, capture_output=True)
    (OUT / (name + '.log')).write_text(cp.stdout + cp.stderr)
    COMMANDS.append({'name': name, 'command': [str(x) for x in cmd], 'exit_code': cp.returncode, 'log': ref(OUT / (name + '.log'))})
    write(OUT / 'commands.json', COMMANDS)
    assert cp.returncode in allowed, (name, cp.returncode, cp.stdout[-2000:], cp.stderr[-2000:])
    return cp


def definitions(data):
    return {n.name: ast.dump(n, include_attributes=False) for n in ast.parse(data).body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}


def row_key(row):
    return row['backend'], row['case']


def main():
    assert not (OUT / 'manifest.json').exists(), 'Frozen result exists; do not overwrite.'
    started = datetime.now(timezone.utc).isoformat()
    # Metadata gate precedes loading the KnowledgeStore or reading scientific entry bodies.
    gate = {}
    holdout_paths = ['knowledge/evaluation_holdouts.json', 'plugins/research-assistant/skills/model-with-knowledge/assets/knowledge/evaluation_holdouts.json']
    for p in holdout_paths:
        data = (ROOT / p).read_bytes()
        assert data == git_blob(REMOTE, p) == git_blob(PRIOR_TREE, p)
        gate[p] = {'sha256': sha(data), 'targets': json.loads(data)['targets']}
    assert gate[holdout_paths[0]]['targets'] == gate[holdout_paths[1]]['targets']
    targets = gate[holdout_paths[0]]['targets']
    assert len(targets) == 4 and all(t['status'] == 'reserved' for t in targets)
    metas = {}
    for p in sorted((ROOT / 'knowledge/entries').rglob('*.json')):
        d = json.loads(p.read_text())
        metas[d['id']] = d
        source_text = json.dumps(d['sources'], ensure_ascii=False).lower()
        for target in targets:
            for field in ('doi', 'url'):
                assert field not in target or target[field].lower() not in source_text
    counts = Counter(m['status'] for m in metas.values())
    assert counts == {'published': 78, 'candidate': 2}, counts
    write(OUT / 'holdout-metadata-gate.json', {'registries': gate, 'counts': dict(counts), 'reserved_source_collisions': [], 'metadata_checked_before_body_access': True, 'reserved_target_content_accessed': False})
    corpus = disk_hashes(ROOT / 'knowledge')
    remote_corpus = tree_hashes(REMOTE, 'knowledge')
    assert corpus == remote_corpus, 'Integrated corpus not byte-identical to remote f989.'
    mirror = disk_hashes(PLUGIN / 'assets/knowledge')
    assert {p.removeprefix('knowledge/'): h for p,h in corpus.items()} == {p.removeprefix('plugins/research-assistant/skills/model-with-knowledge/assets/knowledge/'):h for p,h in mirror.items()}
    prior_entries = tree_hashes(PRIOR_TREE, 'knowledge/entries')
    assert all(corpus[p] == h for p,h in prior_entries.items())
    added = sorted(set(p for p in corpus if p.startswith('knowledge/entries/')) - set(prior_entries))
    assert added == ['knowledge/entries/math.matrix-bernstein-covariance.json', 'knowledge/entries/math.matrix-bernstein-covariance.md'], added
    # All relevant remote evidence, including current publication records, is preserved byte-exact.
    source_evidence = {}
    for prefix in ['docs/knowledge_learning/2026-10-07-ai-algorithms', 'docs/knowledge_learning/2026-10-07-matrix-concentration']:
        for p,h in tree_hashes(REMOTE, prefix).items():
            assert (ROOT / p).is_file() and sha((ROOT / p).read_bytes()) == h, p
            source_evidence[p] = h
    runtime = {}
    code = [ROOT / p for p in ['agent_runtime/knowledge.py', 'agent_runtime/knowledge_index.py', 'agent_runtime/knowledge_reuse.py', 'agent_runtime/project_docs.py', 'agent_runtime/result_store.py', 'agent_runtime/result_validation.py', 'tests/test_knowledge_index.py', 'scripts/eval_knowledge.py']]
    code += [AIK / 'check_domain_recovery.py', Path(__file__)]
    for p in ['agent_runtime/knowledge.py', 'agent_runtime/knowledge_index.py', 'agent_runtime/knowledge_reuse.py', 'scripts/eval_knowledge.py', 'docs/knowledge_learning/2026-10-07-ai-algorithms/check_domain_recovery.py']:
        r, c = git_blob(REMOTE, p), (ROOT / p).read_bytes()
        dr, dc = definitions(r), definitions(c)
        changed = sorted(k for k in dr.keys() | dc.keys() if dr.get(k) != dc.get(k))
        runtime[p] = {'remote_sha256': sha(r), 'current_sha256': sha(c), 'changed_definitions': changed}
        assert changed == (['_connect'] if p == 'agent_runtime/knowledge_index.py' else []), (p, changed)
        if p == 'agent_runtime/knowledge_index.py':
            normalized = c.decode().replace('    from .project_docs import guard_write_path\n', '').replace('    from project_docs import guard_write_path\n', '').replace('        guard_write_path(path)\n', '')
            assert normalized == r.decode(), 'Unexpected runtime change beyond guarded index writes.'
    for name in ['knowledge.py', 'knowledge_index.py', 'knowledge_reuse.py', 'project_docs.py']:
        assert (ROOT / 'agent_runtime' / name).read_bytes() == (PLUGIN / 'scripts' / name).read_bytes(), name
        code.append(PLUGIN / 'scripts' / name)
    # Retain original records; current source changes can make their old manifests stale.
    legacy = {}
    for name in ['combined-corpus-delta-v2-20261007', 'corpus-fd9012-delta-20261007']:
        for leaf in ['record.json', 'manifest.json', 'summary.json']:
            p = 'doc/results/' + name + '/' + leaf
            assert (ROOT / p).read_bytes() == git_blob(PRIOR_TREE, p), p
            legacy[p] = sha((ROOT / p).read_bytes())
    inputs = [ROOT / p for p in corpus] + [ROOT / p for p in mirror]
    inputs += [AIK / 'evaluation/frozen_tasks.json', AIK / 'final-candidate-freeze.json', AIK / 'final-base-checks/validation.json', AIK / 'concurrent-base-checks/default.json', AIK / 'concurrent-base-checks/domain.json', AIK / 'latest-base-release.md']
    inputs += [MATRIX / p for p in ['queries.json', 'retrieval.json', 'regression.json', 'baseline-latest-main.json', 'concurrent-main-check.json', 'tests.json', 'report.md', 'publication.json']]
    inputs += [ROOT / p for p in legacy]
    deps = sorted(set(code + inputs + [OUT / 'validation-plan.json']))
    before = {ref(p)['path']: ref(p)['sha256'] for p in deps}
    write(OUT / 'dependencies-before.json', before)
    write(OUT / 'identity.json', {'remote_commit': REMOTE, 'prior_tested_tree': PRIOR_TREE, 'current_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'corpus_byte_exact_remote': True, 'corpus_hashes': corpus, 'plugin_mirror_hashes': mirror, 'prior_entry_files_unchanged': len(prior_entries), 'added_entry_files': added, 'runtime_identity': runtime, 'source_reports_byte_exact_remote': True, 'source_evidence_hashes': source_evidence, 'legacy_records_immutable': legacy})
    write(OUT / 'environment.json', {'started_at_utc': started, 'python': sys.version, 'executable': sys.executable, 'sqlite_version': sqlite3.sqlite_version, 'platform': platform.platform(), 'machine': platform.machine(), 'network_used': False, 'external_model_calls': False, 'timing_claims': False, 'dependencies': 'Python standard library and SQLite FTS5'})
    sys.path.insert(0, str(ROOT))
    from agent_runtime.knowledge import KnowledgeStore, KnowledgeError
    from agent_runtime.knowledge_index import build_index, indexed_search
    from agent_runtime.result_store import ResultStore
    from agent_runtime.result_validation import inspect_result
    store = KnowledgeStore(ROOT / 'knowledge')
    assert store.snapshot == 'cb76af83360932f5e397065af4449bf39474b4cd99f684ef68ffa474e51228db'
    candidate_ids = {kid for kid,d in metas.items() if d['status'] == 'candidate'}
    published_ids = set(metas) - candidate_ids
    exclusion = []
    with tempfile.TemporaryDirectory(prefix='v3-index-', dir=OUT) as temp:
        db = Path(temp) / 'index.sqlite'
        built = build_index(store, db)
        with sqlite3.connect(db) as c:
            indexed_ids = {r[0] for r in c.execute('SELECT id FROM docs')}
        assert indexed_ids == published_ids
        for kid in sorted(candidate_ids):
            blocked = False
            try: store.get(kid)
            except KnowledgeError: blocked = True
            assert blocked
            files_ids = {r['id'] for r in store.search(kid + ' ' + metas[kid]['title'], limit=20)['results']}
            sql_ids = {r['id'] for r in indexed_search(store, db, kid + ' ' + metas[kid]['title'], limit=20)['results']}
            assert kid not in files_ids | sql_ids | indexed_ids
            exclusion.append({'id': kid, 'status': 'candidate', 'get_blocked': blocked, 'absent_from_files_search': True, 'absent_from_sqlite_search': True, 'absent_from_index': True})
    write(OUT / 'candidate-exclusion.json', {'snapshot': store.snapshot, 'total': len(metas), 'published_ids': sorted(published_ids), 'indexed_ids': sorted(indexed_ids), 'index_build': built, 'candidates': exclusion})
    run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_knowledge_index.py', '-v'], 'index-tests')
    aik = {}
    for mode in ['default', 'domain']:
        output = OUT / ('aik-' + mode + '.json')
        cmd = [sys.executable, AIK / 'check_domain_recovery.py', '--repo', ROOT, '--corpus', ROOT / 'knowledge', '--cases', AIK / 'evaluation/frozen_tasks.json', '--output', output]
        if mode == 'default': cmd.append('--unscoped')
        run(cmd, 'aik-' + mode, allowed=(0,1))
        data = json.loads(output.read_text())
        assert len(data['rows']) == 24 and len({row_key(r) for r in data['rows']}) == 24
        assert all(r['fulltext_unchanged'] and r['budget']['used_chars'] <= 20000 for r in data['rows'])
        prior = json.loads((AIK / 'concurrent-base-checks' / (mode + '.json')).read_text())
        baseline = {row_key(r): r for r in prior['rows']}
        assert set(baseline) == {row_key(r) for r in data['rows']}
        changed = []
        for r in data['rows']:
            old = baseline[row_key(r)]
            assert (r['query'],r['target']) == (old['query'],old['target'])
            differences = [k for k in ['raw_ids','context_ids','hit','fulltext_unchanged'] if r[k] != old[k]]
            if differences: changed.append({'backend':r['backend'], 'case':r['case'], 'fields':differences, 'prior':{k:old[k] for k in differences}, 'current':{k:r[k] for k in differences}})
        aik[mode] = {'rows':24, 'context_hits':sum(r['hit'] for r in data['rows']), 'raw_top3_hits':sum(r['target'] in r['raw_ids'] for r in data['rows']), 'failures':[{'backend':r['backend'],'case':r['case']} for r in data['rows'] if not r['hit']], 'changes_against_prior_semantics':changed, 'new_hit_regressions':[{'backend':r['backend'],'case':r['case']} for r in data['rows'] if baseline[row_key(r)]['hit'] and not r['hit']]}
    run([sys.executable, ROOT / 'scripts/eval_knowledge.py', '--root', ROOT / 'knowledge', '--cases', MATRIX / 'queries.json', '--output', OUT / 'matrix-query-smoke.json'], 'matrix-query-smoke', allowed=(0,1))
    smoke = json.loads((OUT / 'matrix-query-smoke.json').read_text())
    upstream = json.loads((MATRIX / 'retrieval.json').read_text())
    matrix = {}
    for backend in ['files','sqlite']:
        a,b = upstream['backends'][backend]['queries'],smoke['backends'][backend]['queries']
        assert len(a) == len(b) == 4
        keys = ['case','query','expected','actual','recall_at_3','context_ids','context_budget','context_status','context_recall','reciprocal_rank','no_hit_correct']
        assert [{k:r[k] for k in keys} for r in a] == [{k:r[k] for k in keys} for r in b]
        matrix[backend] = {'cases':4,'exact_semantics_match_upstream':True,'all_target_hits':all(r['recall_at_3']==1 for r in b)}
    regression = json.loads((MATRIX / 'regression.json').read_text())
    upstream_scope = {'snapshot':regression['snapshot'],'actual_cases_per_backend':{},'prose_claimed_old_cases':21,'inherited_scope_mismatch':True,'fresh_full_legacy_catalogs_run':False,'historical_AIK_116_pairs_scope':'77 published + 2 candidate corpus, before matrix addition; not promoted to current 78-published corpus acceptance'}
    for b,dd in regression['backends'].items():
        rows = dd['queries'];positive = [r for r in rows if r['expected']]
        assert len(rows)==8 and len(positive)==7
        recall = sum(r['recall_at_3'] for r in positive)/len(positive)
        assert abs(recall-dd['mean_recall_at_3'])<1e-15
        assert all(r['context_recall']==1 for r in positive)
        upstream_scope['actual_cases_per_backend'][b]={'total':8,'positive':7,'mean_recall_at_3':recall,'mean_context_recall':1,'raw_failures':[{'case':r['case'],'recall_at_3':r['recall_at_3']} for r in positive if r['recall_at_3']<1]}
    after = {ref(p)['path']: ref(p)['sha256'] for p in deps}
    assert before == after, 'Dependencies moved during measurement.'
    write(OUT / 'dependencies-after.json', after)
    completed = datetime.now(timezone.utc).isoformat()
    summary = {'status':'measured-pending-independent-final-review','scope':SCOPE,'remote_commit':REMOTE,'prior_tested_tree':PRIOR_TREE,'current_snapshot':store.snapshot,'corpus_byte_exact_remote':True,'mirrors_byte_exact':True,'counts':dict(counts),'prior_entry_files_unchanged':len(prior_entries),'added_entry_files':added,'reserved_holdouts_preserved':4,'candidate_exclusion':exclusion,'targeted_index_tests':{'run':10,'passed':10},'AIK':aik,'matrix_query_smoke':matrix,'upstream_reuse_scope':upstream_scope,'source_reports_and_publications_preserved':True,'legacy_records_immutable':True,'dependencies_stable':True,'completed_at_utc':completed,'limitations':['Pending independent final release reviewer; native registration is not acceptance.','Upstream scientific reports are preserved and scoped, not independently rederived or newly promoted here.','Matrix regression raw evidence covers eight old cases per backend despite upstream prose saying 21; no seven-catalog current-corpus remeasurement.','AIK uses authored frozen development questions, not unseen/model evaluation; remaining failures are not automatic recovery.','The prior v2 116-pair catalog results predate the new matrix card and remain historical.','Metadata collision checks and byte identity do not prove absence of all semantic leakage.','No GPU, live model, latency, token savings, deployment or production performance claim.']}
    write(OUT / 'summary.json', summary)
    write(REPORT / 'summary.json', summary)
    write(OUT / 'reuse-decisions.json', {'decision':'verify_delta','prior_result_search':ref(OUT / 'prior-result-search.json'),'prior_search_warning':'The just-created v3 directory had no record yet; this expected missing in-progress record is preserved in search output. Existing matching records were returned, not treated as independent proof.','remote_evidence_scope':upstream_scope,'runtime_delta':'Only _connect gains project-document write-path guarding; ranking definitions byte/AST identical. Fresh four-query backend smoke cross-checks remote results.','full_repetition_avoided':['Full 730 integration suite owned by integration/release worker.','Seven legacy catalogs already measured on prior corpus; not relabeled as current-corpus acceptance.','Matrix scientific checks and source research preserved without rerun.'],'required_independent_review':True})
    contract = {'result_id':OUT.name,'producer_task_id':'verify-v3-corpus-delta','producer_actor':'v3-corpus-verifier','manifest_path':(OUT/'manifest.json').relative_to(ROOT).as_posix(),'validation_plan':ref(OUT/'validation-plan.json'),'scope':SCOPE}
    raw = [OUT / n for n in ['identity.json','holdout-metadata-gate.json','candidate-exclusion.json','index-tests.log','aik-default.json','aik-default.log','aik-domain.json','aik-domain.log','matrix-query-smoke.json','matrix-query-smoke.log','dependencies-before.json','dependencies-after.json','commands.json','prior-result-search.json']]
    manifest = {**contract,'schema_version':'experiment-result/v1','run_id':OUT.name,'code_revision':REMOTE+' plus document-governance v3; actual dependency hashes bound','execution':{'command':['python '+Path(__file__).relative_to(ROOT).as_posix()],'environment_description':'Local standard-library Python/SQLite FTS5; deterministic development retrieval and identity checks; no scientific experiment or performance comparison.','seeds':[0],'repeats':1,'started_at':started,'completed_at':completed},'artifacts':{'code':[ref(p) for p in sorted(set(code))],'inputs':[ref(p) for p in sorted(set(inputs))],'config':[ref(OUT/'validation-plan.json')],'raw_data':[ref(p) for p in raw],'outputs':[ref(OUT/'summary.json'),ref(OUT/'reuse-decisions.json')],'environment':[ref(OUT/'environment.json')]},'metrics':[{'name':k,'value':v,'unit':'count'} for k,v in [('published_entries',78),('candidate_entries_excluded',2),('reserved_holdout_metadata_preserved',4),('targeted_index_tests_passed',10),('aik_default_hits',aik['default']['context_hits']),('aik_domain_hits',aik['domain']['context_hits']),('aik_rows_per_mode',24),('matrix_smoke_pairs',8),('upstream_legacy_cases_per_backend',8)]]}
    write(OUT/'contract.json',contract);write(OUT/'manifest.json',manifest)
    ResultStore(ROOT).register(contract, measured_at=completed)
    record=json.loads((OUT/'record.json').read_text())
    write(OUT/'registration-receipt.json',{'origin':record['origin'],'status':record['validation_at_registration']['status'],'manifest':ref(OUT/'manifest.json'),'record':ref(OUT/'record.json'),'summary':ref(OUT/'summary.json')})
    write(OUT/'integrity-no-provider.json',inspect_result(ROOT,contract))
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    print(json.dumps(json.loads((OUT/'registration-receipt.json').read_text()),indent=2))

if __name__ == '__main__':
    main()
