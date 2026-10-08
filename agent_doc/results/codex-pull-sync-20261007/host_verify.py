"""Explicit host checker for this frozen integration result, not a general verifier.

The controller invokes this reviewed file explicitly. No commands are loaded
from the experiment manifest. The independent process checks source control
flow, raw test denominators and a separate focused rerun before acceptance.
"""
import ast
import hashlib
import json
import math
from pathlib import Path
import re

REL = 'doc/results/codex-pull-sync-20261007'


def ref(root, path):
    return {'path': path, 'sha256': hashlib.sha256((root/path).read_bytes()).hexdigest()}


def check_source(root):
    base = root/REL
    sources = json.loads((base/'sources.json').read_text())
    for current, saved in sources.items():
        assert (root/current).read_text() == (root/saved).read_text(), current
    tree = ast.parse((root/'scripts/run_knowledge_windows.py').read_text())
    funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    calls = lambda f, name: [n for n in ast.walk(funcs[f]) if isinstance(n, ast.Call)
                             and (isinstance(n.func, ast.Name) and n.func.id == name or
                                  isinstance(n.func, ast.Attribute) and n.func.attr == name)]
    assert calls('main', 'prepare_host')[0].lineno < calls('main', 'Popen')[0].lineno
    assert calls('prepare_host', 'git_sync')[0].lineno < calls('prepare_host', 'sync_host_skills')[0].lineno
    assert any(k.arg == 'before' and isinstance(k.value, ast.Constant) and k.value.value is True
               for k in calls('prepare_host', 'sync_host_skills')[0].keywords)
    sync = ast.get_source_segment((root/'scripts/run_knowledge_windows.py').read_text(), funcs['sync_host_skills'])
    assert "'--check'" in sync and 'host-skills-before.json' in sync and 'host-skills.json' in sync
    template = (root/'templates/codex_global_instructions.md').read_text()
    assert all(s in template for s in ('After each successful pull', 'doc/task/TASK.md', 'doc/guide/'))


def counts(path):
    raw = path.read_text()
    total = int(re.search(r'Ran (\d+) tests?', raw)[1])
    assert re.search(r'^OK(?: \(skipped=\d+\))?$', raw, re.M), path
    assert not re.search(r'^(FAIL|ERROR):', raw, re.M), path
    rows, current = [], None
    for line in raw.splitlines():
        start = re.match(r'^(test\S+) \(([^)]+)\)', line)
        if start:
            assert current is None, (path, current)
            current = (start[1], start[2])
        end = re.search(r'(?:\.\.\. |^)(ok|skipped[^\n]*)$', line)
        if current and end:
            rows.append((*current, end[1])); current = None
    assert current is None and len(rows) == total and len({(a,b) for a,b,_ in rows}) == total, (path,len(rows),total)
    return total, sum(c.startswith('skipped') for _,_,c in rows)


def verify(root, manifest, plan):
    root = Path(root); base = root/REL
    check_source(root)
    config = json.loads((base/'config.json').read_text())
    assert counts(base/'repository.log') == (config['repository_total'], config['repository_skipped'])
    assert counts(base/'reader.log') == (3, 0)
    assert counts(base/'independent-runner.log') == (12, 0)
    setup_total, setup_skipped = counts(base/'independent-installer.log')
    assert setup_total >= 13
    receipts = json.loads((base/'checks.json').read_text())
    assert len(receipts) == 4 and all(x['exit_code'] == 0 and math.isfinite(x['seconds']) and x['seconds'] > 0 for x in receipts)
    host = json.loads((base/'host-process.json').read_text())
    assert host['pid'] > 0 and host['completed'] and host['focused_exit_codes'] == [0,0]
    assert host['scope'] == plan['scope']
    bindings = {manifest['validation_plan']['path']: manifest['validation_plan']['sha256']}
    for rows in manifest['artifacts'].values():
        for item in rows:
            assert ref(root, item['path']) == item
            bindings[item['path']] = item['sha256']
    observations = [ref(root, REL+'/'+p) for p in ('host-process.json','independent-runner.log','independent-installer.log','repository.log')]
    reasons = {
        'implementation': 'AST independently checks pull/sync/Popen ordering and stage separation; current source equals frozen source.',
        'reference_boundary': 'Separate focused execution covers real temporary Git pulls, local edit/layout protection, failed verification and human-guide exclusion.',
        'data_integrity': 'All verbose test IDs are unique and match raw summary denominators; four command receipts and artifact bindings agree.',
        'numerical_sanity': 'Counts are finite integers with explicit skipped denominator; elapsed times finite and positive, without performance claims.',
        'measurement_validity': 'No speed, model-quality, scientific or statistical measurement is claimed; unit-test execution only.',
        'reproducibility': 'Host checker separately reran runner and installer tests on frozen merged source; current implementation bytes still match.'}
    return {'schema_version':'experiment-validation/v1',
            'manifest_sha256':ref(root, REL+'/manifest.json')['sha256'],
            'artifact_hashes':bindings,'validation_plan_sha256':manifest['validation_plan']['sha256'],
            'scope':plan['scope'],
            'verifier':{'actor':'host-static-and-replay-checker','independent':True,
                        'source':'Explicit controller subprocess; deterministic checks, not an independent AI/human review',
                        'run_id':host['run_id'],'method':'AST control-flow checks, exact raw-count accounting, separate Git/installer replay'},
            'limitations':['Finite fixtures do not guarantee bug-free code or model compliance.',
                           'Full suite logs attest execution in the frozen environment; targeted source review covers integration paths only.',
                           'First merged full run had a supervisor restart timeout; retained separately, focused and subsequent full reruns passed.'],
            'checks':{name:{'verdict':'not_applicable' if name=='measurement_validity' else 'pass',
                            'reason':reason,'evidence':observations} for name,reason in reasons.items()}}
