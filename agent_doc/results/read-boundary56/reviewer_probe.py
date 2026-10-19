"""Independent deterministic boundary audit; run from the repository root."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from agent_runtime import knowledge as current
from agent_runtime import knowledge_ingest as current_ingest

BASE = 'ffd9abfeb2264a21e46322e4bedf310947229b2b'
OUT = Path(__file__).with_name('reviewer-probe.json')
L = current.MAX_BYTES
rows = []

def module_at(name, filename):
    raw = subprocess.check_output(['git', 'show', BASE + ':' + filename], cwd=ROOT)
    module = types.ModuleType(name)
    module.__package__ = 'agent_runtime'
    exec(compile(raw, filename, 'exec'), module.__dict__)
    return module

legacy = module_at('agent_runtime.reviewer_legacy', 'agent_runtime/knowledge.py')
legacy_ingest = module_at('agent_runtime.reviewer_legacy_ingest', 'agent_runtime/knowledge_ingest.py')
legacy_ingest.KnowledgeStore = legacy.KnowledgeStore

template = json.loads((ROOT / 'knowledge/entries/math.cauchy-schwarz.json').read_text())
template.update(id='math.audit-source', requires=[], relations=[])
draft = dict(template, id='math.audit-import', status='candidate')

def init(base):
    root = base / 'corpus'
    entries = root / 'entries'
    entries.mkdir(parents=True)
    sm, sb = entries / 'one.json', entries / 'one.md'
    im, ib = base / 'import.json', base / 'import.md'
    sm.write_text(json.dumps(template)); sb.write_text('Valid body.\n')
    im.write_text(json.dumps(draft)); ib.write_text('Candidate body.\n')
    return root, {'store_metadata': sm, 'store_body': sb, 'ingest_metadata': im, 'ingest_body': ib}

def tree(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            if p.is_file() else 'directory' for p in root.rglob('*')}

@contextlib.contextmanager
def inject(target, extra, events):
    original = Path.open
    fired = False
    class Recording:
        def __init__(self, stream): self.stream = stream
        def __enter__(self): return self
        def __exit__(self, *exc): return self.stream.__exit__(*exc)
        def read(self, size=-1):
            value = self.stream.read(size)
            events.append({'request': size, 'returned': len(value), 'kind': type(value).__name__})
            return value
    def opened(path, *a, **kw):
        nonlocal fired
        if path == target and not fired:
            fired = True
            with original(path, 'ab') as f: f.write(extra)
            return Recording(original(path, *a, **kw))
        return original(path, *a, **kw)
    with patch.object(Path, 'open', opened): yield
    assert fired

for version, km, im in [('baseline', legacy, legacy_ingest), ('patched', current, current_ingest)]:
    for entry in ('store_metadata', 'store_body', 'ingest_metadata', 'ingest_body'):
        for growth in (1, 4096):
            with tempfile.TemporaryDirectory() as tmp:
                root, targets = init(Path(tmp)); target = targets[entry]
                raw = target.read_bytes(); gap = L - len(raw)
                target.write_bytes(raw + b'\r\n' * (gap // 2) + b' ' * (gap % 2))
                before = tree(root); events = []
                with inject(target, b' ' * growth, events):
                    try:
                        result = km.KnowledgeStore(root) if entry.startswith('store') else im.ingest(root, targets['ingest_metadata'], targets['ingest_body'])
                        outcome = 'accepted'
                    except Exception as exc:
                        outcome = type(exc).__name__ + ': ' + str(exc)
                if version == 'patched':
                    assert outcome == 'KnowledgeError: ' + ('entry' if entry.startswith('store') else 'import') + ' exceeds byte budget', outcome
                    assert events == [{'request': L+1, 'returned': L+1, 'kind': 'bytes'}]
                    if entry.startswith('ingest'): assert tree(root) == before
                else:
                    assert outcome == 'accepted', outcome
                    assert events[0]['request'] == -1 and events[0]['kind'] == 'str'
                rows.append({'version':version,'entry':entry,'growth':growth,'outcome':outcome,'events':events})

# Independently challenge the import path with exact byte limits and malformed
# UTF-8, which are only partially cross-producted in the producer's test suite.
extras = []
for entry in ('ingest_metadata','ingest_body'):
    for case in ('exact_utf8','invalid_short','invalid_growth'):
        with tempfile.TemporaryDirectory() as tmp:
            root, targets = init(Path(tmp)); target = targets[entry]
            if case == 'exact_utf8':
                if entry.endswith('metadata'):
                    value = dict(draft, title='多字节标题')
                    raw = json.dumps(value, ensure_ascii=False).encode()
                    target.write_bytes(raw + b' ' * (L-len(raw)))
                else:
                    target.write_bytes('😀'.encode() * (L//4))
                current_ingest.ingest(root, targets['ingest_metadata'], targets['ingest_body'])
                outcome='accepted'
            elif case == 'invalid_short':
                target.write_bytes(b'\xf0\x9f')
                try: current_ingest.ingest(root, targets['ingest_metadata'], targets['ingest_body'])
                except UnicodeDecodeError: outcome='UnicodeDecodeError'
                else: raise AssertionError('invalid import accepted')
            else:
                raw=target.read_bytes(); target.write_bytes(raw+b' '*(L-len(raw)))
                events=[]; before=tree(root)
                with inject(target,b'\xff',events):
                    try: current_ingest.ingest(root,targets['ingest_metadata'],targets['ingest_body'])
                    except current.KnowledgeError as exc:
                        assert str(exc)=='import exceeds byte budget'; outcome='budget error before decode'
                    else: raise AssertionError('oversized invalid import accepted')
                assert tree(root)==before
            extras.append({'entry':entry,'case':case,'outcome':outcome})

# Reference decoder, independent of the implementation's replace sequence.
newline_cases=0
with tempfile.TemporaryDirectory() as tmp:
    p=Path(tmp)/'input'
    import itertools
    for parts in itertools.product(['\r','\n','\r\n','\u0085','\u2028','\u2029','😀'],repeat=3):
        raw=''.join(parts).encode(); p.write_bytes(raw)
        with io.TextIOWrapper(io.BytesIO(raw),encoding='utf-8',newline=None) as text:
            expected=text.read()
        assert current._read_utf8_bounded(p,L,'overflow')==expected
        newline_cases+=1

before=legacy.KnowledgeStore(ROOT/'knowledge')
after=current.KnowledgeStore(ROOT/'knowledge')
assert before.records==after.records and before.snapshot==after.snapshot
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'agent_runtime/knowledge.py',ROOT/'agent_runtime/knowledge_ingest.py',ROOT/'tests/test_knowledge_read_boundary.py']}
report={'baseline':BASE,'growth_cases':rows,'additional_import_cases':extras,'newline_reference_cases':newline_cases,'corpus_records':len(after.records),'corpus_snapshot':after.snapshot,'corpus_exact_match':True,'code_hashes':hashes,'python':sys.version,'status':'pass'}
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':'pass','growth_cases':len(rows),'additional_import_cases':len(extras),'newline_reference_cases':newline_cases,'corpus_records':len(after.records)}))
