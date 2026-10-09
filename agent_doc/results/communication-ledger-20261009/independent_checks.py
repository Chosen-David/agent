"""Reviewer-owned numerical/data verification and extra budget/upgrade boundaries."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
from test_communication_usage import UsageTests, legacy_mailbox
from agent_runtime.communication import Mailbox

OUT = Path(__file__).resolve().parent
raw = json.loads((OUT / 'raw.json').read_text())
summary = json.loads((OUT / 'raw-summary.json').read_text())
plan = json.loads((OUT / 'plan.json').read_text())
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert raw['config'] == plan['matrix']
assert raw['plan_sha256'] == digest(OUT / 'plan.json')
assert raw['baseline_sha256'] == digest(OUT / 'baseline_communication.py')
baseline_git = subprocess.check_output(['git', 'show', plan['baseline_sha'] + ':agent_runtime/communication.py'], cwd=ROOT)
assert baseline_git == (OUT / 'baseline_communication.py').read_bytes()
for p, sha in raw['code_hashes'].items():
    assert digest(ROOT / p) == sha, p
assert len(raw['cases']) == len(summary) == 16
assert {(c['backlog'], c['fanout'], c['byte_budget']) for c in raw['cases']} == set(itertools.product([0, 100, 1000, 10000], [1, 8], [False, True]))
medians = {}
for case, stored in zip(raw['cases'], summary):
    assert case['case'] == stored['case']
    assert len(case['order_including_warmups']) == 11
    for order in case['order_including_warmups']:
        assert sorted(order) == sorted(plan['matrix']['arms'])
    medians[case['case']] = {}
    for arm, ops in case['samples'].items():
        assert case['sqlite'][arm]['journal_mode'] == 'delete'
        assert case['sqlite'][arm]['synchronous'] == 2
        accounting = case['final_accounting'][arm]
        assert accounting['events'] == case['backlog'] + 11
        assert accounting['deliveries'] == accounting['events'] * case['fanout']
        assert accounting['delivery_bytes'] == accounting['envelope_bytes'] * case['fanout']
        for op, values in ops.items():
            assert len(values) == 9 and all(math.isfinite(v) and v > 0 for v in values)
            assert stored['stats'][arm][op] == dict(median=statistics.median(values), p95=max(values), minimum=min(values), maximum=max(values))
        medians[case['case']][arm] = statistics.median(ops['publish_ms'])
    m = medians[case['case']]
    assert stored['publish_speedup'] == m['baseline'] / m['candidate']
    assert stored['indexed_publish_speedup'] == m['indexed_scan'] / m['candidate']
primary = medians['n10000-f8-budget1']
support = medians['n1000-f8-budget1']
assert primary['baseline'] / primary['candidate'] >= 1.25
assert primary['indexed_scan'] / primary['candidate'] >= 1.25
assert support['candidate'] <= support['baseline'] * 1.10

case = UsageTests()
case.setUp()
try:
    # Old run with no events must gain a zero row on its eventual first new open.
    old_cls = legacy_mailbox()
    old = old_cls(case.db, case.plan, case.root)
    empty_plan = dict(case.plan, run_id='empty-old')
    old_cls(case.db, empty_plan, case.root)
    old.publish(case.event)
    new = Mailbox(case.db, case.plan, case.root)
    empty = Mailbox(case.db, empty_plan, case.root)
    assert empty.usage()['events'] == 0
    case.assert_scan(empty)
    old.acknowledge('b', 1, dict(status='needs_revision', reason='evidence missing'))
    assert new.usage() == old.usage()
    # Exact retry remains allowed after ACK; changed-content retry stays rejected.
    assert new.publish(case.event)['duplicate']
    try:
        new.publish(dict(case.event, summary='changed'))
    except ValueError:
        pass
    else:
        raise AssertionError('changed retry was accepted')
    case.assert_scan(new)
    cap_plan = dict(case.plan, run_id='event-cap', max_events=3)
    cap_plan.pop('max_delivery_bytes')
    cap = Mailbox(case.db, cap_plan, case.root)
    def send(i):
        try:
            cap.publish(dict(case.event, run_id='event-cap', event_id=str(i)))
            return True
        except ValueError as exc:
            assert 'event budget' in str(exc)
            return False
    with ThreadPoolExecutor(max_workers=8) as pool:
        outcomes = list(pool.map(send, range(12)))
    assert sum(outcomes) == 3
    case.assert_scan(cap)
finally:
    case.doCleanups()

result = dict(verdict='pass', primary_medians_ms=primary, supporting_medians_ms=support,
              publish_regressions=[dict(case=k, percent=(v['candidate']/v['baseline']-1)*100) for k, v in medians.items() if v['candidate'] > v['baseline']],
              hash_bindings={str(p.relative_to(ROOT)): digest(p) for p in [OUT/'plan.json', OUT/'raw.json', OUT/'raw-summary.json', OUT/'baseline_communication.py', ROOT/'agent_runtime/communication.py', ROOT/'tests/test_communication_usage.py', Path(__file__)]},
              checks=['16-case coverage', 'all 1296 retained operation timings and summaries', 'all code/baseline/plan hashes', 'event/delivery fanout conservation', 'unchanged journal/sync', 'empty legacy run', 'legacy ACK and post-ACK duplicate', 'changed retry rejection', 'concurrent exact event cap'])
(OUT/'independent-checks.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
