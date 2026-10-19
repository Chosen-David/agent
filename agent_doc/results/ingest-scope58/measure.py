"""Paired complete-ingest benchmark; copy-payload tracing is a separate run."""
import hashlib
import json
from pathlib import Path
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from agent_runtime.knowledge import KnowledgeStore
from agent_runtime.knowledge_index import build_index
from agent_runtime.knowledge_ingest import ingest

BASE = 'cacbee7663282bcd17b8e08de6b4a00945a0a9fb'
source = subprocess.check_output(
    ['git', 'show', BASE + ':agent_runtime/knowledge_ingest.py'], cwd=ROOT).decode()
namespace = {'__name__': 'agent_runtime._baseline_ingest', '__package__': 'agent_runtime'}
exec(compile(source, BASE + ':knowledge_ingest.py', 'exec'), namespace)
FUNCTIONS = {'before': namespace['ingest'], 'after': ingest}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def tree_hash(root):
    files = [(p.relative_to(root).as_posix(), digest(p.read_bytes()))
             for p in sorted(root.rglob('*')) if p.is_file()]
    return digest(json.dumps(files, ensure_ascii=False).encode())


def one(template, meta, body, label, trace=False):
    with tempfile.TemporaryDirectory(prefix='ingest58-sample-') as directory:
        root = Path(directory) / 'knowledge'
        shutil.copytree(template, root)
        input_hash = tree_hash(root)
        copies = []
        original = shutil.copyfile
        def counted(src, dst, **kwargs):
            src = Path(src)
            copies.append({'path': src.relative_to(root).as_posix()
                           if src.is_relative_to(root) else 'imported/' + src.name,
                           'bytes': src.stat().st_size})
            return original(src, dst, **kwargs)
        if trace:
            with patch.object(shutil, 'copyfile', counted):
                receipt = FUNCTIONS[label](root, meta, body)
            elapsed = None
        else:
            start = time.perf_counter_ns()
            receipt = FUNCTIONS[label](root, meta, body)
            elapsed = (time.perf_counter_ns() - start) / 1e6
        receipt.pop('imported_at')
        provenance = json.loads((root / receipt['path'] / 'provenance.txt').read_text())
        provenance.pop('imported_at')
        store = KnowledgeStore(root)
        output = {'snapshot': store.snapshot, 'records': store.records,
                  'receipt': receipt, 'provenance': provenance}
        output_hash = digest(json.dumps(output, sort_keys=True, ensure_ascii=False).encode())
        return {'input_sha256': input_hash, 'output_sha256': output_hash,
                'wall_ms': elapsed, 'copies': copies,
                'logical_copy_bytes': sum(x['bytes'] for x in copies) if trace else None}


def main():
    profiles = []
    with tempfile.TemporaryDirectory(prefix='ingest58-input-') as directory:
        base = Path(directory)
        meta, body = base / 'draft.json', base / 'draft.md'
        data = json.loads((ROOT / 'knowledge/entries/math.cauchy-schwarz.json').read_text())
        data.update(id='math.scope-import', status='candidate', requires=[], relations=[])
        meta.write_text(json.dumps(data), encoding='utf-8')
        body.write_text('# Draft\nUnverified.\n', encoding='utf-8')
        for name in ('plain', 'root-attachment-16MiB', 'root-sqlite-index'):
            template = base / name
            shutil.copytree(ROOT / 'knowledge', template)
            if name == 'root-attachment-16MiB':
                (template / 'unused.cache').write_bytes(bytes(range(256)) * 65536)
            if name == 'root-sqlite-index':
                build_index(KnowledgeStore(template), template / 'search.sqlite')
            traced = {label: one(template, meta, body, label, trace=True) for label in FUNCTIONS}
            pairs = []
            # Uninstrumented warmup for each implementation and seven alternating pairs.
            for repeat in range(-1, 7):
                order = ('before', 'after') if repeat % 2 == 0 else ('after', 'before')
                pair = {label: one(template, meta, body, label) for label in order}
                if pair['before']['input_sha256'] != pair['after']['input_sha256']:
                    raise RuntimeError('paired inputs differ')
                if pair['before']['output_sha256'] != pair['after']['output_sha256']:
                    raise RuntimeError('paired output semantics differ')
                for label in FUNCTIONS:
                    if pair[label]['output_sha256'] != traced[label]['output_sha256']:
                        raise RuntimeError('trace and timing outputs differ')
                    if pair[label]['input_sha256'] != traced[label]['input_sha256']:
                        raise RuntimeError('trace and timing inputs differ')
                pairs.append({'repeat': repeat, 'warmup': repeat == -1,
                              'order': order, 'measurements': pair})
            medians = {label: statistics.median(p['measurements'][label]['wall_ms']
                                               for p in pairs if not p['warmup'])
                       for label in FUNCTIONS}
            profiles.append({'name': name, 'trace': traced, 'pairs': pairs,
                             'median_wall_ms': medians})
        result = {'baseline': BASE, 'scope': 'full local ingest; input preparation excluded',
                  'python': sys.version, 'platform': platform.platform(),
                  'machine': platform.machine(), 'draft_sha256': [digest(meta.read_bytes()), digest(body.read_bytes())],
                  'source_sha256': {'baseline_ingest': digest(source.encode()),
                      'current_ingest': digest((ROOT / 'agent_runtime/knowledge_ingest.py').read_bytes()),
                      'knowledge': digest((ROOT / 'agent_runtime/knowledge.py').read_bytes()),
                      'measure': digest(Path(__file__).read_bytes())},
                  'profiles': profiles,
                  'limits': ['Logical copied payload, not physical disk IO or peak memory.',
                             'Warm local standard-library workload, not LLM/request/production speed.',
                             'Root-local SQLite is optional, not README default cache placement.',
                             'Input hashing before each call warms file data; no cold-cache claim.']}
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
