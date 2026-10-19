"""Run from repository root; record actual read requests and deterministic input hashes."""
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import types
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from agent_runtime import knowledge, knowledge_ingest

BASE = 'ffd9abfeb2264a21e46322e4bedf310947229b2b'
spec = importlib.util.spec_from_file_location('boundary_tests', ROOT / 'tests/test_knowledge_read_boundary.py')
fixtures = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixtures)


def legacy():
    modules = []
    for name in ('knowledge', 'knowledge_ingest'):
        source = subprocess.check_output(['git', 'show', f'{BASE}:agent_runtime/{name}.py'], cwd=ROOT)
        module = types.ModuleType('agent_runtime.' + name)
        module.__package__ = 'agent_runtime'
        with patch.dict(sys.modules, {'agent_runtime.knowledge': modules[0]} if modules else {}):
            exec(compile(source, f'{BASE}/{name}.py', 'exec'), module.__dict__)
        modules.append(module)
    return modules


def measure(km, im):
    rows = []
    for entry in ('store_metadata', 'store_body', 'ingest_metadata', 'ingest_body'):
        for growth in (1, 4096):
            fixture = fixtures.ReadBoundaryTests()
            fixture.setUp()
            try:
                if entry.startswith('store'):
                    target = fixture.root / ('entries/math.cauchy-schwarz.' + ('json' if entry.endswith('metadata') else 'md'))
                    run = lambda: km.KnowledgeStore(fixture.root)
                else:
                    meta, body = fixture.draft()
                    target = meta if entry.endswith('metadata') else body
                    run = lambda: im.ingest(fixture.root, meta, body)
                raw = target.read_bytes()
                remain = km.MAX_BYTES - len(raw)
                raw += b'\r\n' * (remain // 2) + b' ' * (remain % 2)
                target.write_bytes(raw)
                extra = b' ' * growth
                calls = []
                error = None
                with fixture.growth_hook(target, extra, calls):
                    try:
                        run()
                    except Exception as exc:
                        error = f'{type(exc).__name__}: {exc}'
                rows.append({'entry': entry, 'growth': growth,
                             'input_sha256': hashlib.sha256(raw).hexdigest(),
                             'grown_sha256': hashlib.sha256(raw + extra).hexdigest(),
                             'actual_file_bytes': target.stat().st_size,
                             'accepted': error is None, 'error': error,
                             'read_calls_size_returned_length': calls,
                             'returned_unit': 'text_characters' if km is not knowledge else 'bytes'})
            finally:
                fixture.doCleanups()
    return rows


before = measure(*legacy())
after = measure(knowledge, knowledge_ingest)
assert [(r['input_sha256'], r['grown_sha256']) for r in before] == [(r['input_sha256'], r['grown_sha256']) for r in after]
print(json.dumps({'baseline': BASE, 'python': sys.version, 'platform': platform.platform(),
                  'budget': knowledge.MAX_BYTES, 'scope': 'Application read requests/returned buffer, not physical read-ahead or total memory/time',
                  'before': before, 'after': after}, indent=2))
