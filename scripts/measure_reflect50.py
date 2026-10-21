"""Freeze and measure the local fifty-iteration integration, without model calls.

Use a fresh project-relative result directory for each reproduction. Optional
tokenizer dependencies must already exist in the explicit host-selected path.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from agent_runtime.project_docs import assert_ai_writable
from agent_runtime.result_validation import CHECKS


def write(path, value):
    path.write_bytes((json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False)+'\n').encode())


def ref(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def prepare(out):
    if out.exists():
        raise ValueError('fresh result directory required; preserve previous evidence')
    out.mkdir(parents=True)
    scope = 'REFLECT50 R01-R50 integrated local behavior and exact synthetic payload/storage observations; no total session tokens, cash, QA, latency or bug-free guarantee'
    procedures = {
        'implementation': 'Inspect all fifty actual deltas and repairs; rerun all named reflection tests on final source.',
        'reference_boundary': 'Use original literal sections/full JSON and finite token boundaries; preserve source hashes, errors, dependencies and mandatory global sections.',
        'data_integrity': 'Check every bound source/recipe/raw output/archive hash and keep all failed historical gates and negative controls.',
        'numerical_sanity': 'Independently count actual UTF-8 bytes/o200k_base tokens including native newline; parse both stored JSON receipts and compare complete values.',
        'measurement_validity': 'Large selection may reduce payload, tiny selection may cost more; restrict compression to stored JSON whitespace and local synthetic cases.',
        'reproducibility': 'Independently execute current tests and rebuild deterministic measurement fixtures; compare wire hashes/counts and review actual source.'}
    plan = {'schema_version': 'experiment-validation-plan/v1', 'scope': scope,
            'criteria': {key: {'procedure': value, 'acceptance': 'All current reflection tests and independent scoped checks pass; counts and literal values agree; all fifty actual improvements remain identifiable.', 'allow_not_applicable': False} for key, value in procedures.items()},
            'recipe': 'seed0: large Markdown repeated4000 lines; tiny single section; receipt200 literal proof fields; raw wires stored once in ZIP; optional tiktoken0.12.0/o200k_base',
            'test_pattern': 'test_reflect50_g*.py', 'repeats': 1, 'seeds': [0]}
    write(out/'plan.json', plan)
    write(out/'contract.json', {'result_id': out.name, 'producer_task_id': 'REFLECT50-20261021', 'producer_actor': '/root', 'manifest_path': (out/'manifest.json').relative_to(ROOT).as_posix(), 'scope': scope, 'validation_plan': ref(out/'plan.json')})


def measure(out, tokenizer_path):
    if (out/'manifest.json').exists():
        raise ValueError('result already produced; use a fresh directory')
    if tokenizer_path:
        sys.path.insert(0, str(Path(tokenizer_path).resolve(strict=True)))
    os.environ.setdefault('TIKTOKEN_CACHE_DIR', str(ROOT/'.agent-runs/memory-index96-token-cache'))
    import tiktoken
    from agent_runtime.handoff_basis import make_token_counter
    from agent_runtime.markdown_context import read_sections
    from agent_runtime.validation_context import write_validation_context, restore_validation_context
    counter = make_token_counter('o200k_base')
    contract = json.loads((out/'contract.json').read_bytes())
    env = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
    command = [sys.executable, '-X', 'utf8', '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_reflect50_g*.py', '-v']
    run = subprocess.run(command, cwd=ROOT, env=env, capture_output=True)
    (out/'tests.txt').write_bytes(run.stdout+run.stderr)
    observations, wires = [], {}
    def packet(value):
        return (json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False)+os.linesep).encode()
    def record(name, before, after, **metadata):
        wires[name+'-before.bin'], wires[name+'-after.bin'] = before, after
        observations.append({'case': name, **metadata, 'before_bytes': len(before), 'after_bytes': len(after),
                             'before_tokens': counter(before.decode('utf-8')), 'after_tokens': counter(after.decode('utf-8')),
                             'before_sha256': hashlib.sha256(before).hexdigest(), 'after_sha256': hashlib.sha256(after).hexdigest()})
    with tempfile.TemporaryDirectory(prefix='reflection-measure-') as temporary:
        root = Path(temporary)
        for name, text, selected, mandatory in (
            ('large-selection', '# Global\nretain required global rule\n## Work\ncurrent literal source\n## Archive\n'+'historical unrelated record never used for this selected task.\n'*4000, ['s2'], ['s1']),
            ('tiny-selection', '# A\nx\n', ['s1'], [])):
            raw = text.encode('utf-8'); (root/'source.md').write_bytes(raw)
            source = {'path': 'source.md', 'sha256': hashlib.sha256(raw).hexdigest()}
            view = read_sections(root, source, selected, mandatory=mandatory, max_chars=200000)
            record(name, packet({'source': source, 'text': text}), packet(view), unit='complete compact JSON plus native newline tokens/UTF-8 bytes', semantics='selected literal blocks plus caller-declared globals; omitted body remains original source, not a full-content encoding')
        result = {'status': 'pending', 'scope': 'synthetic display only', 'errors': ['current independent acceptance still required'], 'next_action': 'verify current source', 'proof': {'artifact_hashes': {'file%03d'%i: hashlib.sha256(str(i).encode()).hexdigest() for i in range(200)}, 'review_evidence': {}, 'limitations': ['fixture only']}}
        pretty = write_validation_context(root, result, 'agent_doc/results/pretty')
        compact = write_validation_context(root, result, 'agent_doc/results/compact', compact_storage=True)
        before = (root/pretty['record_ref']['path']).read_bytes(); after = (root/compact['record_ref']['path']).read_bytes()
        assert json.loads(before) == json.loads(after)
        assert restore_validation_context(root, compact['record_ref']) == result
        record('receipt-storage', before, after, unit='physical stored UTF-8 JSON bytes and its tokenizer count', semantics='identical complete JSON values; whitespace only')
    with zipfile.ZipFile(out/'payloads.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, raw in wires.items():
            archive.writestr(name, raw)
    write(out/'observations.json', {'schema_version': 'reflection-observations/v1', 'seed': 0, 'repeats': 1, 'tokenizer': 'o200k_base', 'tiktoken': tiktoken.__version__, 'tests_exit_code': run.returncode, 'cases': observations})
    write(out/'environment.json', {'python': sys.version, 'platform': platform.platform(), 'native_newline': repr(os.linesep), 'tiktoken': tiktoken.__version__, 'tokenizer': 'o200k_base', 'command': command, 'scope': 'local CPU/file behavior; no model calls'})
    ledger = ROOT/'agent_doc/results/reflect50-20261021/iterations.json'
    changes = json.loads(ledger.read_bytes())
    code = {name for change in changes for name in change['changes']}
    code.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'tests').glob('test_reflect50_g*.py'))
    code.add('scripts/measure_reflect50.py')
    code.add('scripts/sync_plugin_references.py')
    changed = subprocess.run(['git','diff','--name-only','-z','HEAD'], cwd=ROOT, check=True, capture_output=True).stdout.decode().split('\0')
    code.update(name for name in changed if name.startswith('plugins/') and name.endswith(('.py','.md')))
    corpus = [ref(path) for path in sorted((ROOT/'knowledge').rglob('*')) if path.is_file() and path.suffix in ('.json','.md','.txt')]
    artifacts = {'code': [ref(ROOT/name) for name in sorted(code)], 'inputs': [ref(out/'plan.json'), ref(ledger), *corpus],
                 'config': [ref(out/'contract.json')], 'raw_data': [ref(out/'tests.txt'), ref(out/'payloads.zip')],
                 'outputs': [ref(out/'observations.json')], 'environment': [ref(out/'environment.json')]}
    metrics = [{'name': 'producer_exit_code', 'value': run.returncode, 'unit': 'exit-code'}, {'name': 'implemented_iterations', 'value': len(changes), 'unit': 'changes'}]
    for case in observations:
        for key in ('before_bytes', 'after_bytes', 'before_tokens', 'after_tokens'):
            metrics.append({'name': case['case']+'.'+key, 'value': case[key], 'unit': 'bytes' if key.endswith('bytes') else 'o200k_base-tokens'})
    write(out/'manifest.json', {'schema_version': 'experiment-result/v1', **{key: contract[key] for key in ('result_id','producer_task_id','producer_actor','scope','validation_plan')}, 'run_id': out.name, 'code_revision': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT).decode().strip()+'+bound-working-sources', 'execution': {'command': command, 'environment_description': platform.platform()+' Python '+platform.python_version()+' tiktoken '+tiktoken.__version__, 'repeats': 1, 'seeds': [0]}, 'artifacts': artifacts, 'metrics': metrics})
    print(json.dumps({'tests_exit_code': run.returncode, 'observations': observations}, ensure_ascii=False))
    return run.returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('prepare','run'))
    parser.add_argument('--out', required=True, help='fresh project-relative agent_doc/results/<run>/ directory')
    parser.add_argument('--tokenizer-path', help='explicit existing isolated optional dependency path')
    args = parser.parse_args()
    relative = Path(args.out)
    if (relative.is_absolute() or '..' in relative.parts or len(relative.parts)<3
            or relative.parts[:2] != ('agent_doc','results')):
        raise ValueError('project result directory required')
    out = assert_ai_writable(ROOT, relative)
    if args.phase == 'prepare':
        prepare(out); return 0
    return measure(out, args.tokenizer_path)

if __name__ == '__main__':
    raise SystemExit(main())
