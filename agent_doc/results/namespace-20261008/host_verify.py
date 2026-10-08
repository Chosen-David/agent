"""Explicit separate host review: source/migration accounting and fresh replay."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

REL = 'agent_doc/results/namespace-20261008'


def ref(root, name):
    return {'path': name, 'sha256': hashlib.sha256((root / name).read_bytes()).hexdigest()}


def verify(root, manifest, plan):
    root = Path(root)
    base = root / REL
    inventory = json.loads((base / 'source-inventory.json').read_text())
    for item in inventory['files']:
        data = (root / item['path']).read_bytes().decode('utf-8').replace('\r\n', '\n').encode('utf-8')
        assert hashlib.sha256(data).hexdigest() == item['sha256'], item['path']
    producer = json.loads((base / 'producer-source.json').read_text())
    for item in producer['files']:
        data = (root / item['path']).read_bytes().decode('utf-8').replace('\r\n', '\n').encode('utf-8')
        assert hashlib.sha256(data).hexdigest() == item['sha256'], item['path']
    relocation = json.loads((base / 'relocation-inventory.json').read_text())
    marker = json.loads((root / 'agent_doc/legacy-result-paths.json').read_text())
    assert len(relocation['files']) == len(marker['files']) > 0
    requests = ''.join(relocation['baseline_revision'] + ':' + row['old_path'] + '\n' for row in relocation['files'])
    raw = subprocess.check_output(['git', 'cat-file', '--batch'], cwd=root, input=requests.encode())
    offset = 0
    for row in relocation['files']:
        end = raw.index(b'\n', offset)
        header = raw[offset:end].split()
        size = int(header[2])
        canonical = raw[end+1:end+1+size]
        offset = end+size+2
        assert header[0].decode() == row['git_blob_sha']
        assert hashlib.sha256(canonical).hexdigest() == row['canonical_sha256']
        expected = marker['files'][row['old_path']]
        allowed = [expected] if isinstance(expected, str) else expected
        assert set(allowed) == {row['canonical_sha256'], row['original_checkout_sha256']}
        assert hashlib.sha256((root / row['new_path']).read_bytes()).hexdigest() in allowed
    move = json.loads((base / 'move.json').read_text())
    for old, digest in move['guide_hashes_unchanged'].items():
        assert ref(root, 'agent_doc/' + old[4:])['sha256'] == digest
    spec = importlib.util.spec_from_file_location('reviewed_verbose_accounting',
        root / 'agent_doc/results/codex-pull-sync-20261007/host_verify.py')
    accounting = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(accounting)
    totals = {name: accounting.counts(base / (name + '.log')) for name in ('repository', 'reader')}
    assert totals['repository'][0] >= 800 and totals['reader'] == (3, 0)
    checks = json.loads((base / 'checks.json').read_text())
    assert [x['name'] for x in checks] == ['repository', 'reader', 'plugin', 'knowledge']
    assert all(x['exit_code'] == 0 for x in checks)
    focused = {}
    for name, pattern, expected in [('namespace', 'test_agent_doc_namespace.py', 10),
                                    ('init', 'test_project_docs_init.py', 9)]:
        result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests',
                                 '-p', pattern, '-v'], cwd=root, capture_output=True,
                                text=True, encoding='utf-8', timeout=60)
        path = base / ('independent-' + name + '.log')
        path.write_bytes((result.stdout + result.stderr).encode('utf-8'))
        assert result.returncode == 0, result.stdout + result.stderr
        focused[name] = accounting.counts(path)
        assert focused[name][0] == expected and focused[name][1] in (0, 1)
    bindings = {manifest['validation_plan']['path']: manifest['validation_plan']['sha256']}
    for rows in manifest['artifacts'].values():
        for item in rows:
            assert ref(root, item['path']) == item
            bindings[item['path']] = item['sha256']
    observations = [ref(root, REL + '/' + name) for name in
                    ('repository.log', 'reader.log', 'checks.json', 'independent-namespace.log',
                     'independent-init.log', 'relocation-inventory.json', 'move.json')]
    reasons = {
        'implementation': 'Bound actual canonical source and all three legacy readers; separate-process replay exercises canonical task preparation and managed review binding.',
        'reference_boundary': 'Fresh ordinary-doc isolation, both guide namespaces, registered same-suffix relocation, collision/schema/symlink/tamper/third-digest refusal and old contract hash checks.',
        'data_integrity': f'{len(relocation["files"])} canonical Git blobs plus original checkout hashes inventoried; GUIDE unchanged; unique verbose outcomes account for totals {totals}.',
        'numerical_sanity': 'Integer totals and skips recomputed from actual nonempty verbose outcome IDs; no failed producer command.',
        'measurement_validity': 'Functional authored tests only; no timing/performance, scientific conclusion, model compliance or OS enforcement inference.',
        'reproducibility': f'Fresh host replay {focused}; full producer uses frozen Linux source and actual tmux; development failures and encoding correction retained.'}
    return {'schema_version': 'experiment-validation/v1',
            'manifest_sha256': ref(root, REL + '/manifest.json')['sha256'],
            'artifact_hashes': bindings, 'validation_plan_sha256': manifest['validation_plan']['sha256'],
            'scope': plan['scope'],
            'verifier': {'actor': 'host-namespace-reviewer', 'independent': True,
                         'source': 'explicit controller-selected separate-process deterministic checker',
                         'run_id': 'host-namespace-20261008', 'method': 'source/Git/raw accounting and actual fresh boundary replay'},
            'limitations': ['Deterministic result review is not a second scientific AI review.',
                            'Legacy digest representations never waive original bound hashes or establish current acceptance.',
                            'Instructions and file installation do not prove actual model compliance or OS sandboxing.'],
            'checks': {key: {'verdict': 'not_applicable' if key == 'measurement_validity' else 'pass',
                             'reason': reason, 'evidence': observations} for key, reason in reasons.items()}}
