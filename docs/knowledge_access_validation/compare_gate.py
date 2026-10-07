"""Run from repository root. Synthetic program comparison, not model A/B."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import types

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
BASE = 'c66b5ce'
old = types.ModuleType('baseline_communication')
exec(compile(subprocess.check_output(
    ['git', 'show', BASE + ':agent_runtime/communication.py'], cwd=ROOT),
    'baseline_communication.py', 'exec'), old.__dict__)
spec = importlib.util.spec_from_file_location('fixture', ROOT / 'tests/test_knowledge_handoff.py')
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)
case = fixture.KnowledgeHandoffTests()
case.setUp()
try:
    seq = case.send()
    baseline = old.Mailbox(case.root / 'mail.sqlite', case.box.plan, case.root)
    path = case.root / 'corpus/entries/math.topk-margin.md'
    path.write_text(path.read_text() + '\nChanged synthetic corpus\n')
    baseline.consume_handoff('review', seq, case.request)
    try:
        case.box.consume_handoff('review', seq, case.request)
    except ValueError as exc:
        error = str(exc)
    else:
        raise AssertionError('changed knowledge was accepted')
    assert 'stale knowledge ref' in error
    assert case.box.status()[0]['receipt'] is None
    print(json.dumps(dict(baseline=BASE, baseline_accepts_stale=True,
                         candidate_rejects_stale=True, error=error,
                         receipt_remains_pending=True,
                         scope='same real files and SQLite; synthetic handoff, no model A/B'), indent=2))
finally:
    case.doCleanups()
