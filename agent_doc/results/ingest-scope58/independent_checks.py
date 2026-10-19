"""Independent INGEST-SCOPE-58 source/data/boundary cross-check; no timing claims."""
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from agent_runtime.knowledge import KnowledgeError, KnowledgeStore
from agent_runtime.knowledge_ingest import ingest

OUT = Path(__file__).parent
BASE = 'cacbee7663282bcd17b8e08de6b4a00945a0a9fb'
def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    result = {'reviewer': '/root/ingest58_review', 'checks': [], 'profiles': []}
    def checked(name):
        result['checks'].append(name)
    source = subprocess.check_output(['git', 'show', BASE + ':agent_runtime/knowledge_ingest.py'], cwd=ROOT)
    namespace = {'__name__': 'agent_runtime._independent_baseline', '__package__': 'agent_runtime'}
    exec(compile(source, '<independent-baseline>', 'exec'), namespace)
    old_ingest = namespace['ingest']
    data = json.loads((OUT / 'measurements.json').read_text())
    source_map = {'baseline_ingest': sha(source),
                  'current_ingest': sha((ROOT / 'agent_runtime/knowledge_ingest.py').read_bytes()),
                  'knowledge': sha((ROOT / 'agent_runtime/knowledge.py').read_bytes()),
                  'measure': sha((OUT / 'measure.py').read_bytes())}
    assert source_map == data['source_sha256']
    assert data['baseline'] == BASE
    assert (ROOT / 'agent_runtime/knowledge_ingest.py').read_bytes() == (ROOT / 'plugins/research-assistant/skills/model-with-knowledge/scripts/knowledge_ingest.py').read_bytes()
    checked('baseline/current/consumer/harness hashes and exact plugin mirror')
    for profile in data['profiles']:
        pairs = profile['pairs']
        assert [p['repeat'] for p in pairs] == list(range(-1, 7))
        assert sum(p['warmup'] for p in pairs) == 1 and pairs[0]['warmup']
        before_trace, after_trace = profile['trace']['before'], profile['trace']['after']
        assert before_trace['input_sha256'] == after_trace['input_sha256']
        assert before_trace['output_sha256'] == after_trace['output_sha256']
        for label, trace in profile['trace'].items():
            assert trace['logical_copy_bytes'] == sum(x['bytes'] for x in trace['copies'])
            assert trace['wall_ms'] is None
            assert all(type(x['bytes']) is int and x['bytes'] > 0 for x in trace['copies'])
            assert len({x['path'] for x in trace['copies']}) == len(trace['copies'])
            if label == 'after':
                assert all(x['path'].startswith(('entries/', 'imported/')) for x in trace['copies'])
        values = {label: [] for label in ('before', 'after')}
        for pair in pairs:
            expected = ['before', 'after'] if pair['repeat'] % 2 == 0 else ['after', 'before']
            assert pair['order'] == expected
            for label, sample in pair['measurements'].items():
                assert sample['copies'] == [] and sample['logical_copy_bytes'] is None
                assert sample['input_sha256'] == profile['trace'][label]['input_sha256']
                assert sample['output_sha256'] == profile['trace'][label]['output_sha256']
                assert math.isfinite(sample['wall_ms']) and sample['wall_ms'] > 0
                if not pair['warmup']:
                    values[label].append(sample['wall_ms'])
        medians = {k: statistics.median(v) for k, v in values.items()}
        assert medians == profile['median_wall_ms']
        result['profiles'].append({'name': profile['name'], 'medians_ms': medians,
                                  'ranges_ms': {k: [min(v), max(v)] for k, v in values.items()},
                                  'logical_bytes': {k: v['logical_copy_bytes'] for k, v in profile['trace'].items()}})
    checked('all three profiles, 48 timed observations including warmups, hashes/order/medians/logical sums')
    with tempfile.TemporaryDirectory(prefix='independent-ingest58-') as temp:
        work = Path(temp)
        meta, body = work / 'draft.json', work / 'draft.md'
        draft = json.loads((ROOT / 'knowledge/entries/math.cauchy-schwarz.json').read_text())
        draft.update(id='math.scope-import', status='candidate', requires=[], relations=[])
        meta.write_text(json.dumps(draft), encoding='utf-8')
        body.write_text('# Draft\nUnverified.\n', encoding='utf-8')
        assert [sha(meta.read_bytes()), sha(body.read_bytes())] == data['draft_sha256']
        def corpus(name):
            root = work / name
            shutil.copytree(ROOT / 'knowledge', root)
            return root
        result['corpus_entries'] = len(KnowledgeStore(ROOT / 'knowledge').records)
        outputs, amounts = [], []
        for name, function in [('old', old_ingest), ('new', ingest)]:
            root = corpus(name)
            (root / 'ignored.bin').write_bytes(b'x' * 8192)
            attachment = root / 'entries/nested-extra/file.bin'
            attachment.parent.mkdir()
            attachment.write_bytes(b'retain attachment')
            seen = []
            original_copy = shutil.copyfile
            def count(src, dst, **kwargs):
                seen.append((Path(src), Path(src).stat().st_size))
                return original_copy(src, dst, **kwargs)
            with patch.object(shutil, 'copyfile', count):
                receipt = function(root, meta, body)
            assert attachment in [p for p, n in seen]
            assert attachment.read_bytes() == b'retain attachment'
            receipt.pop('imported_at')
            provenance = json.loads((root / receipt['path'] / 'provenance.txt').read_text())
            provenance.pop('imported_at')
            store = KnowledgeStore(root)
            outputs.append((store.records, store.snapshot, receipt, provenance))
            amounts.append(sum(n for p, n in seen))
        assert outputs[0] == outputs[1]
        root_sibling_bytes = sum(p.stat().st_size for p in (ROOT / 'knowledge').rglob('*') if p.is_file() and not p.is_relative_to(ROOT / 'knowledge/entries'))
        assert amounts[0] - amounts[1] == root_sibling_bytes + 8192
        assert amounts[1] - len(b'retain attachment') == data['profiles'][0]['trace']['after']['logical_copy_bytes']
        result['independent_copy_bytes'] = {'before': amounts[0], 'after': amounts[1], 'avoided': amounts[0] - amounts[1]}
        checked('independent old/new record/ref/provenance oracle and nested nonrecord attachment; exact byte-difference oracle')
        for special in ('link', 'fifo'):
            for name, function in [('old', old_ingest), ('new', ingest)]:
                root = corpus(special + '-' + name)
                sibling = root / 'unrelated'
                if special == 'link':
                    sibling.symlink_to(work / 'missing')
                else:
                    os.mkfifo(sibling)
                if name == 'old':
                    try:
                        function(root, meta, body)
                    except shutil.Error:
                        pass
                    else:
                        raise AssertionError('baseline unexpectedly accepted special root object')
                    assert not (root / 'entries/math.scope-import').exists()
                else:
                    original_scan = os.scandir
                    def guarded_scan(path):
                        assert not isinstance(path, (str, bytes, os.PathLike)) or Path(path) != root, 'visited corpus root siblings'
                        return original_scan(path)
                    with patch.object(os, 'scandir', guarded_scan):
                        assert function(root, meta, body)['status'] == 'candidate'
                    assert sibling.is_symlink() if special == 'link' else sibling.exists()
        checked('independent root dangling-link/FIFO failure-before success-after; no root scandir')
        for special in ('link', 'fifo'):
            root = corpus('inside-' + special)
            target = root / 'entries/invalid.bin'
            target.symlink_to(work / 'missing') if special == 'link' else os.mkfifo(target)
            try:
                ingest(root, meta, body)
            except (KnowledgeError, shutil.Error):
                pass
            else:
                raise AssertionError('invalid entries object accepted')
            assert not (root / 'entries/math.scope-import').exists()
        checked('independent unchanged entries symlink/FIFO refusal')
        root = corpus('plugin')
        (root / 'unrelated.link').symlink_to(work / 'missing')
        command = [sys.executable, '-I', str(ROOT / 'plugins/research-assistant/skills/model-with-knowledge/scripts/knowledge.py'), '--root', str(root), 'ingest', str(meta), str(body)]
        run = subprocess.run(command, cwd=work, capture_output=True, text=True)
        assert run.returncode == 0, run.stderr
        assert json.loads(run.stdout)['status'] == 'candidate'
        checked('isolated python -I plugin entrypoint accepts unrelated dangling link')
    run = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_knowledge_ingest_scope.py', '-v'], cwd=ROOT, capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    result['focused_rerun'] = run.stdout + run.stderr
    checked('independent rerun all seven focused tests including mutation fence')
    files = ['agent_runtime/knowledge_ingest.py', 'agent_runtime/knowledge.py', 'agent_runtime/knowledge_index.py', 'agent_runtime/project_docs.py', 'agent_runtime/knowledge_reuse.py', 'tests/test_knowledge_ingest_scope.py', 'plugins/research-assistant/skills/model-with-knowledge/scripts/knowledge_ingest.py']
    files += [str(p.relative_to(ROOT)) for p in OUT.iterdir() if p.name in ('plan_v1.md', 'measure.py', 'measurements.json', 'before.log', 'after.log', 'independent_checks.py')]
    result['artifact_hashes'] = {p: sha((ROOT / p).read_bytes()) for p in files}
    result['status'] = 'pass'
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
