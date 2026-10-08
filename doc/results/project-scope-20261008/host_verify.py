"""Explicit controller-selected separate-process review, not a second AI."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

REL = 'doc/results/project-scope-20261008'


def ref(root, path):
    return {'path': path, 'sha256': hashlib.sha256((root / path).read_bytes()).hexdigest()}


def verify(root, manifest, plan):
    root = Path(root)
    base = root / REL
    for item in json.loads((base / 'source-inventory.json').read_text())['files']:
        data = (root / item['path']).read_bytes().decode('utf-8').replace('\r\n', '\n').encode('utf-8')
        assert hashlib.sha256(data).hexdigest() == item['sha256'], item['path']
    spec = importlib.util.spec_from_file_location('reviewed_verbose_accounting',
        root / 'doc/results/codex-pull-sync-20261007/host_verify.py')
    accounting = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(accounting)
    totals = {name: accounting.counts(base / (name + '.log')) for name in ('repository', 'reader')}
    assert totals['repository'][0] > 0 and totals['reader'] == (3, 0)
    checks = json.loads((base / 'checks.json').read_text())
    assert [c['name'] for c in checks] == ['repository', 'reader', 'plugin', 'knowledge']
    assert all(c['exit_code'] == 0 for c in checks)
    # Fresh actual initialization and negative cases in another process; commands
    # are selected here by the controller, never from worker-controlled manifests.
    result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests',
                             '-p', 'test_project_docs_init.py', '-v'], cwd=root,
                            capture_output=True, text=True, encoding='utf-8', timeout=60)
    (base / 'independent-init.log').write_bytes((result.stdout + result.stderr).encode('utf-8'))
    assert result.returncode == 0, result.stdout + result.stderr
    total, skips = accounting.counts(base / 'independent-init.log')
    assert total == 9 and skips in (0, 1)
    observations = [ref(root, REL + '/' + name) for name in
                    ('repository.log', 'reader.log', 'checks.json', 'independent-init.log')]
    bindings = {manifest['validation_plan']['path']: manifest['validation_plan']['sha256']}
    for rows in manifest['artifacts'].values():
        for item in rows:
            assert ref(root, item['path']) == item
            bindings[item['path']] = item['sha256']
    reasons = {
        'implementation': 'Bound init/CLI source inspected; independent actual CLI run selects target despite source cwd.',
        'reference_boundary': 'Fresh nine-case suite checks A/B isolation, preserved bytes/mtime, guide exclusion, missing root, symlink and legacy/conflict refusals.',
        'data_integrity': f'Exact source inventory and artifact hashes agree; raw unique verbose IDs account for test totals {totals}.',
        'numerical_sanity': 'Positive integer totals equal successful plus skipped verbose outcomes; no errors or failures.',
        'measurement_validity': 'Functional authored checks only; no timing, model-compliance or universal correctness claim.',
        'reproducibility': f'Fresh separate-process init suite: {total} cases, {skips} unavailable-platform skips; all required Linux producer checks exit0.'}
    return {'schema_version': 'experiment-validation/v1',
            'manifest_sha256': ref(root, REL + '/manifest.json')['sha256'],
            'artifact_hashes': bindings, 'validation_plan_sha256': manifest['validation_plan']['sha256'],
            'scope': plan['scope'],
            'verifier': {'actor': 'host-project-scope-reviewer', 'independent': True,
                         'source': 'explicit controller-injected separate-process deterministic checker',
                         'run_id': 'host-project-scope-20261008',
                         'method': 'bound source inspection, raw outcome accounting, fresh actual init/refusal replay'},
            'limitations': ['Deterministic host review is not independent AI review.',
                            'Instructions and installation do not prove actual model compliance.',
                            'Application guards are not OS ACLs or hostile-concurrency transactions.'],
            'checks': {key: {'verdict': 'not_applicable' if key == 'measurement_validity' else 'pass',
                             'reason': reason, 'evidence': observations} for key, reason in reasons.items()}}
