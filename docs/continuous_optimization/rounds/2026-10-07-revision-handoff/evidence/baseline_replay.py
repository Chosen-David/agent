"""Four real-process ordering controls; synthetic records, no model execution.

Run from the repository root with --output pointing to a new JSON file.
Uses the existing communication test fixture; no parallel evaluation runtime.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from agent_runtime.communication import Mailbox


def worker(root, order):
    plan = json.loads((root / 'plan.json').read_text())
    box = Mailbox(root / 'inbox.sqlite', plan, root)
    event = json.loads((root / 'revision.json').read_text())
    receipt = {'status': 'needs_revision', 'reason': 'F1 needs a variance repair'}
    if order == 'ack_first':
        box.acknowledge('reviewer', 1, receipt)
    else:
        box.publish(event)
    # Abrupt process exit after one committed operation, before the other.
    import os
    os._exit(73)


def replay():
    fixture = runpy.run_path(str(ROOT / 'tests/test_communication.py'))['CommunicationTests']
    results = []
    for order, budget_failure in [('ack_first', False), ('publish_first', False),
                                  ('ack_first', True), ('publish_first', True)]:
        case = fixture()
        case.setUp()
        try:
            plan = deepcopy(case.plan)
            if budget_failure:
                plan['max_events'] = 1
                # An immutable new plan must have its own database.
                case.db = case.root / 'budget.sqlite'
                case.box = Mailbox(case.db, plan, case.root)
            seq = case.box.publish(case.event)['seq']
            assert seq == 1
            finding = case.save('finding.json', {'finding_id': 'F1', 'status': 'open',
                                               'required_test': 'add sample variance'}, 'F1')
            revision = dict(case.event, event_id='revision:F1', sender='reviewer',
                            kind='review', refs=[finding])
            receipt = {'status': 'needs_revision', 'reason': 'F1 needs a variance repair'}
            (case.root / 'plan.json').write_text(json.dumps(plan))
            (case.root / 'revision.json').write_text(json.dumps(revision))
            error = None
            exit_code = None
            if budget_failure:
                if order == 'ack_first':
                    case.box.acknowledge('reviewer', seq, receipt)
                try:
                    case.box.publish(revision)
                except ValueError as exc:
                    error = str(exc)
                assert error and 'budget exhausted' in error
            else:
                child = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                                        '--worker', str(case.root), '--order', order],
                                       cwd=ROOT, capture_output=True, text=True, timeout=15)
                exit_code = child.returncode
                assert exit_code == 73, child.stderr
            restored = Mailbox(case.db, plan, case.root)
            reviewer_pending = len(restored.inbox('reviewer'))
            code_pending = len(restored.inbox('code'))
            status = restored.status()
            reviewer_receipt = next(r['receipt'] for r in status
                                    if r['seq'] == seq and r['recipient'] == 'reviewer')
            expected = (0, 0) if order == 'ack_first' else (1, 0 if budget_failure else 1)
            assert (reviewer_pending, code_pending) == expected
            retry = None
            if order == 'publish_first' and not budget_failure:
                retry = restored.publish(revision)
                assert retry['duplicate']
                restored.acknowledge('reviewer', seq, receipt)
                assert len(restored.inbox('code')) == 1
                assert len(restored.inbox('reviewer')) == 0
            results.append(dict(order=order, budget_failure=budget_failure,
                process_exit=exit_code, error=error, reviewer_pending=reviewer_pending,
                implementer_pending=code_pending, original_reviewer_receipt=reviewer_receipt,
                stranded_repair_request=(reviewer_pending == 0 and code_pending == 0),
                status_record_lost=False, duplicate_retry=retry,
                assertion='observed expected baseline/control behavior', status_snapshot=status))
        finally:
            case.doCleanups()
    return dict(schema_version=1, evidence_type='program_execution_synthetic_records',
        baseline_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        runtime_sha256=hashlib.sha256((ROOT / 'agent_runtime/communication.py').read_bytes()).hexdigest(),
        cases=results, cases_asserted=4, stranded_ack_first_cases=2,
        model_tasks_executed=0, conclusion='Ordering hazard, not lost SQLite state; publish-first controls recover')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    parser.add_argument('--worker', type=Path)
    parser.add_argument('--order', choices=['ack_first', 'publish_first'])
    args = parser.parse_args()
    if args.worker:
        worker(args.worker, args.order)
    if not args.output:
        parser.error('--output required')
    value = replay()
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
    print(json.dumps({k: value[k] for k in ('cases_asserted', 'stranded_ack_first_cases', 'model_tasks_executed')}))
