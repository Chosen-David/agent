"""Protected CPU correction chain across mailbox, memory and durable tasks."""
import contextlib
import copy
import io
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
from agent_runtime import project_docs as docs
from agent_runtime.communication import Mailbox
from agent_runtime.core import Engine, Outcome, Store
from agent_runtime.plan_review import ReviewSession
from agent_runtime.project_memory import MemoryLedger
from agent_runtime.task_manifest import ReportingHandler, atomic_json, prepare, review
from tests import test_handoff_basis as handoff_fixtures
from tests.test_plan_review_independent import CPUHost


def main():
    case = handoff_fixtures.BasisTests()
    case.setUp()
    try:
        root = case.root
        (root / 'TASK.md').write_text('# CPU correction fixture\n\n## 2026-10-20\n\n'
                                      '- [ ] [R1] Preserve correction and recovery evidence\n')
        docs.migrate(root, '2026-10-20')
        case.memory.add('intent-v1', 'intention', '{"minimum": 0.4}', 'synthetic:user-1',
                        evidence='user_confirmed')
        case.memory.add('decision-v1', 'claim', 'Margin 0.5 satisfies minimum 0.4',
                        'synthetic:checked-formula', deps=['intent-v1', 'input-v1'], evidence='verified')
        case.record['memory_refs'] = ['decision-v1']
        case.record['evidence_claims'][0]['memory_ids'] = ['decision-v1']
        case.request['memory_refs'] = ['decision-v1']
        event = dict(event_id='E1', run_id='basis', input_version='v1', sender='code', task_id='T1',
                     kind='artifact', summary='Read actual bounded margin fixture', action='Check premises',
                     refs=[case.save('handoff.json', case.record, 'handoff')])
        original_raw = (root / 'result.json').read_bytes()
        calls = []
        host = CPUHost()
        now = lambda: 1000.0
        plan = prepare(root, 'correction-chain', 'manual', 'CPU correction probe only')
        template = plan['tasks'][0]
        tasks = []
        for tid, deps, refs in [('publish', [], ['decision-v1']),
                                ('writer', ['publish'], ['decision-v1']),
                                ('reviewer', ['writer'], ['decision-v1']),
                                ('unrelated', [], ['input-v1'])]:
            task = copy.deepcopy(template)
            task.update(task_id=tid, action='bounded_handoff', owner='cpu-' + tid,
                        depends_on=deps, memory_refs=refs, allowed_writes=['reports/'],
                        report_path='reports/' + tid + '.json', max_attempts=2,
                        inputs={'intent_id': 'intent-v1', 'decision_id': 'decision-v1',
                                'writer_report': 'reports/writer.json'},
                        estimated_seconds=1, done_when={'bound_fixture': True})
            tasks.append(task)
        plan['tasks'] = tasks
        session = ReviewSession(root, plan['plan_review']['lineage_id'],
                                planner_identity=host.planner, reviewer=host.reviewer,
                                authenticate=host.authenticate, clock=now)
        plan['plan_review_receipt'] = session.submit(plan)
        store = Store(root / 'chain.sqlite')
        store.create(plan, project_root=root)

        class Handler:
            idempotent = False
            required_capabilities = ()
            def __init__(self, communication_plan, envelope, request):
                self.communication_plan = copy.deepcopy(communication_plan)
                self.envelope = copy.deepcopy(envelope)
                self.request = copy.deepcopy(request)
            def run(self, task, context):
                tid = task['task_id']
                box = Mailbox(case.box.path, self.communication_plan, root)
                if tid == 'publish':
                    seq = box.publish(self.envelope)['seq']
                    observed = {'seq': seq}
                elif tid in ('writer', 'reviewer'):
                    recipient = 'writer' if tid == 'writer' else 'review'
                    pending = box.inbox(recipient)
                    if len(pending) != 1:
                        raise ValueError('exactly one routed delivery required')
                    seq = pending[0]['seq']
                    packet = box.prepare_context(recipient, seq, self.request)
                    payload = json.loads(packet['payload'])
                    actual_ids = {entry['id'] for entry in payload['memory_entries']}
                    if not {task['inputs']['intent_id'], 'input-v1',
                            task['inputs']['decision_id']} <= actual_ids:
                        raise ValueError('incomplete intent/measurement dependency closure')
                    intent = json.loads(MemoryLedger(root).check([task['inputs']['intent_id']])[0]['content'])
                    margin = json.loads((root / 'result.json').read_text())['margin']
                    if tid == 'reviewer':
                        writer = json.loads((root / task['inputs']['writer_report']).read_text())
                        if writer['decision'] != (margin >= intent['minimum']):
                            raise ValueError('writer decision disagrees with original inputs')
                    observed = {'seq': seq, 'decision': margin >= intent['minimum']}
                    box.acknowledge(recipient, seq, {'status': 'consumed',
                                                   'reason': 'bounded CPU input check; not model acceptance'})
                else:
                    observed = {'raw_sha256': hashlib.sha256(original_raw).hexdigest()}
                report = dict(task_id=tid, summary='CPU handoff state inspected',
                              data=[{'kind': 'synthetic', 'description': 'Finite control-flow fixture'}],
                              **observed)
                atomic_json(root / task['report_path'], report)
                calls.append(tid)
                return Outcome('complete', evidence=[tid])

            def verify(self, task, evidence):
                data = json.loads((root / task['report_path']).read_text())
                return evidence == [task['task_id']] and data['task_id'] == task['task_id']

        def restart(communication_plan=case.plan, envelope=event, request=case.request):
            wrapped = ReportingHandler(Handler(communication_plan, envelope, request), root)
            return Engine(Store(store.path), {'bounded_handoff': wrapped}, authorize=lambda *_: True,
                          project_root=root, plan_review_verifier=session.verify, clock=now)

        engine = restart()
        for i in range(4):
            state = engine.tick(plan['run_id'], 'complete-' + str(i))
        if state['status'] != 'done' or len(calls) != 4:
            raise AssertionError(state)
        old_state = copy.deepcopy(state)
        old_status = Mailbox(case.box.path, case.plan, root).status()
        old_reports = {tid: (root / ('reports/' + tid + '.json')).read_bytes() for tid in calls}
        correction = MemoryLedger(root).correct('intent-v1', 'intent-v2', '{"minimum": 0.8}',
                                                'synthetic:user-correction-2', 'New declared minimum')
        box = Mailbox(case.box.path, case.plan, root)
        impact = box.impact()
        if {row['recipient'] for row in impact} != {'writer', 'review'}:
            raise AssertionError(impact)
        if not all(row['claim_ids'] == ['certificate', 'paper'] for row in impact):
            raise AssertionError(impact)
        if box.status() != old_status or (root / 'result.json').read_bytes() != original_raw:
            raise AssertionError('correction rewrote historical delivery/raw data')
        engine = restart()
        state = engine.tick(plan['run_id'], 'corrected')
        for tid in ('publish', 'writer', 'reviewer'):
            node = state['tasks'][tid]
            if node['status'] != 'blocked' or not node['requires_reconciliation']:
                raise AssertionError((tid, node))
            if node['evidence'] != old_state['tasks'][tid]['evidence']:
                raise AssertionError('old evidence lost')
        if state['tasks']['unrelated']['status'] != 'done' or len(calls) != 4:
            raise AssertionError('unrelated data rejected or action replayed')
        if review(store.snapshot(plan['run_id']), root, plan_review_verifier=session.verify)['all_reportable']:
            raise AssertionError('stale chain remains reportable')
        try:
            engine.reconcile(plan['run_id'], 'publish', old_state['tasks']['publish']['evidence'],
                             'attempt old evidence after correction')
        except ValueError:
            pass
        else:
            raise AssertionError('stale memory accepted by reconciliation')
        state = restart().tick(plan['run_id'], 'still-stale')
        if state['status'] != 'blocked' or len(calls) != 4:
            raise AssertionError('restart undid correction fence')
        for tid, raw in old_reports.items():
            if (root / ('reports/' + tid + '.json')).read_bytes() != raw:
                raise AssertionError('old report silently rewritten')
        MemoryLedger(root).check(['input-v1'])
        store.cancel(plan['run_id'], 'CPU host migrates corrected intent to a newly reviewed run')
        case.memory.add('decision-v2', 'claim', 'Margin 0.5 fails new minimum 0.8',
                        'synthetic:checked-formula-v2', deps=['intent-v2', 'input-v1'], evidence='verified')
        communication_v2 = dict(case.plan, run_id='basis-v2', input_version='v2')
        record_v2 = copy.deepcopy(case.record)
        record_v2.update(run_id='basis-v2', input_version='v2', memory_refs=['decision-v2'])
        record_v2['evidence_claims'][0]['memory_ids'] = ['decision-v2']
        request_v2 = dict(case.request, input_version='v2', memory_refs=['decision-v2'])
        event_v2 = dict(event, event_id='E2', run_id='basis-v2', input_version='v2',
                        refs=[case.save('handoff-v2.json', record_v2, 'handoff')])
        plan_v2 = prepare(root, 'correction-chain-v2', 'manual', 'CPU corrected intent replay')
        plan_v2['tasks'] = copy.deepcopy(tasks)
        for task in plan_v2['tasks']:
            tid = task['task_id']
            task['report_path'] = 'reports/v2-' + tid + '.json'
            task['inputs'] = {'intent_id': 'intent-v2', 'decision_id': 'decision-v2',
                              'writer_report': 'reports/v2-writer.json'}
            if tid != 'unrelated':
                task['memory_refs'] = ['decision-v2']
        plan_v2['plan_review_receipt'] = session.submit(plan_v2)
        store.create(plan_v2, project_root=root)
        recovered = restart(communication_v2, event_v2, request_v2)
        for i in range(4):
            recovered_state = recovered.tick(plan_v2['run_id'], 'fresh-version-' + str(i))
        if recovered_state['status'] != 'done' or len(calls) != 8 or len(host.requests) != 2:
            raise AssertionError(recovered_state)
        old_decision = json.loads(old_reports['writer'])['decision']
        new_decision = json.loads((root / 'reports/v2-writer.json').read_text())['decision']
        if old_decision is not True or new_decision is not False:
            raise AssertionError('correction did not change the observed consumer decision')
        if restart().tick(plan['run_id'], 'old-run-stays-cancelled')['status'] != 'cancelled':
            raise AssertionError('new run resurrected cancelled old run')
        if Mailbox(case.box.path, case.plan, root).status() != old_status:
            raise AssertionError('new run rewrote old receipts')
        if Mailbox(case.box.path, communication_v2, root).impact():
            raise AssertionError('fresh corrected basis is stale')
        if (root / 'result.json').read_bytes() != original_raw:
            raise AssertionError('new interpretation rewrote original measurement')
        for tid, raw in old_reports.items():
            if (root / ('reports/' + tid + '.json')).read_bytes() != raw:
                raise AssertionError('new version overwrote historical report')
        print(json.dumps({'scope': 'CPU protected plan + actual SQLite mailbox/ledger only',
                          'initial': old_state['status'], 'after_correction': state['status'],
                          'unrelated': state['tasks']['unrelated']['status'],
                          'calls': calls, 'affected_memory': correction['affected'],
                          'recipients': sorted(row['recipient'] for row in impact),
                          'old_ack_reports_raw_preserved': True, 'automatic_replay': False}))
        print(json.dumps({'recovered_run': recovered_state['status'], 'old_decision': old_decision,
                          'new_decision': new_decision, 'plan_reviews': len(host.requests),
                          'old_run': 'cancelled', 'new_message_id': event_v2['event_id']}))
    finally:
        case.doCleanups()


class CorrectionChainTests(unittest.TestCase):
    def test_declared_correction_fences_old_consumers_and_rechecks_new_version(self):
        with contextlib.redirect_stdout(io.StringIO()):
            main()


if __name__ == '__main__':
    unittest.main()
