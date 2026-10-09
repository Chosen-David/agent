"""Cross-layer evidence, correction targeting and real serialized cost contracts."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from agent_runtime.communication import Mailbox, canonical
from agent_runtime.handoff_basis import basis_context, check_handoff_basis
from agent_runtime.knowledge import KnowledgeStore
from agent_runtime.project_memory import MemoryLedger

ROOT = Path(__file__).resolve().parents[1]


class BasisTests(unittest.TestCase):
    def test_consumer_table_format_preserves_full_basis_and_gates(self):
        from agent_runtime.handoff_encoding import decode_basis_payload
        seq = self.send()
        default = self.box.prepare_context('writer', seq, self.request)
        request = {**self.request, 'context_format': 'claims-table/v1'}
        table = self.box.prepare_context('review', seq, request)
        self.assertEqual(decode_basis_payload(table['payload']), json.loads(default['payload']))
        for bad in ('unknown', False, None):
            with self.assertRaises(ValueError):
                self.box.prepare_context('review', seq, {**self.request, 'context_format': bad})
        with self.assertRaisesRegex(ValueError, 'character budget'):
            self.box.prepare_context('review', seq, request, max_chars=20)
        (self.root / 'result.json').write_text('changed')
        with self.assertRaises(ValueError):
            self.box.prepare_context('review', seq, request)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        shutil.copytree(ROOT / 'knowledge', self.root / 'corpus')
        self.refs = KnowledgeStore(self.root / 'corpus').get('math.topk-margin')['knowledge_refs']
        self.memory = MemoryLedger(self.root, create=True)
        self.memory.add('input-v1', 'observation', 'Synthetic margin is 0.5', 'synthetic:fixture',
                        evidence='verified')
        self.memory.add('derived-v1', 'claim', 'Margin certificate', 'synthetic:fixture',
                        deps=['input-v1'], evidence='verified')
        artifact = self.save('result.json', {'margin': 0.5}, 'result')
        self.request = dict(schema_version=1, input_version='v1', tasks=[{'task_id': 'T1'}],
                            knowledge_root='corpus', knowledge_refs=self.refs,
                            memory_refs=['derived-v1'], knowledge_required=True, memory_required=True,
                            required_claim_ids=['paper'])
        def claim(cid):
            return dict(id=cid, status='supported', knowledge_ids=[], memory_ids=[], artifact_ids=[],
                        depends_on=[], assumptions=[])
        self.claims = []
        for cid, changes in [('certificate', dict(knowledge_ids=['math.topk-margin'],
                memory_ids=['derived-v1'], artifact_ids=['result'], assumptions=[
                    dict(name='measured margin bound', status='satisfied', evidence_ids=['result'])])),
                ('paper', dict(depends_on=['certificate'])),
                ('independent', dict(artifact_ids=['result']))]:
            c = claim(cid); c.update(changes); self.claims.append(c)
        self.record = dict(schema_version=1, run_id='basis', role='code', input_version='v1',
                           status='completed', limitations=[], artifacts=[artifact],
                           checks=[dict(criterion='fixture', status='pass', artifact_ids=['result'])],
                           tasks=[dict(task_id='T1', status='done', evidence=['result'])],
                           knowledge_refs=self.refs, memory_refs=['derived-v1'], evidence_claims=self.claims)
        self.plan = dict(schema_version=1, run_id='basis', input_version='v1', routes=[
            dict(sender='code', recipient=r, task_id='T1', kind='artifact') for r in ('writer', 'review')])
        self.box = Mailbox(self.root / 'mail.sqlite', self.plan, self.root)

    def save(self, name, value, aid):
        data = json.dumps(value).encode(); (self.root / name).write_bytes(data)
        return dict(id=aid, path=name, sha256=hashlib.sha256(data).hexdigest())

    def send(self):
        self.event = dict(event_id='E1', run_id='basis', input_version='v1', sender='code', task_id='T1',
                          kind='artifact', summary='Read certificate', action='Verify premises',
                          refs=[self.save('handoff.json', self.record, 'handoff')])
        return self.box.publish(self.event)['seq']

    def test_memory_correction_targets_descendants_and_keeps_history(self):
        seq = self.send()
        for recipient in ('writer', 'review'):
            self.box.consume_handoff(recipient, seq, self.request)
        self.box.acknowledge('writer', seq, dict(status='consumed', reason='read, not scientific acceptance'))
        self.assertEqual(self.box.impact(), [])
        self.memory.correct('input-v1', 'input-v2', 'Margin was wrong', 'synthetic:correction', 'unit error')
        restarted = Mailbox(self.box.path, self.plan, self.root)
        impact = restarted.impact()
        self.assertEqual({x['recipient'] for x in impact}, {'writer', 'review'})
        self.assertTrue(all(x['claim_ids'] == ['certificate', 'paper'] for x in impact))
        self.assertEqual(restarted.status()[1]['receipt']['status'], 'consumed')
        with self.assertRaisesRegex(ValueError, 'stale'):
            restarted.consume_handoff('review', seq, self.request)
        self.assertEqual(len(restarted.inbox('review')), 1)
        self.assertTrue((self.root / 'result.json').exists())

    def test_knowledge_change_targets_only_using_claims_and_cache_does_not_bypass(self):
        seq = self.send(); self.box.consume_handoff('writer', seq, self.request)
        f = self.root / 'corpus/entries/math.topk-margin.md'; f.write_text(f.read_text() + '\ncorrection\n')
        self.assertEqual(self.box.impact()[0]['claim_ids'], ['certificate', 'paper'])
        with self.assertRaisesRegex(ValueError, 'stale'):
            self.box.prepare_context('writer', seq, self.request, known_knowledge_refs=self.refs)

    def test_unrelated_corpus_edit_does_not_invalidate_pinned_dependencies(self):
        seq = self.send(); self.box.consume_handoff('writer', seq, self.request)
        f = self.root / 'corpus/entries/physics.dimensionless.md'; f.write_text(f.read_text() + '\nnew example\n')
        self.assertEqual(self.box.impact(), [])
        self.box.consume_handoff('writer', seq, self.request)

    def test_artifact_change_propagates_all_declared_users(self):
        seq = self.send(); self.box.consume_handoff('writer', seq, self.request)
        (self.root / 'result.json').write_text('changed')
        self.assertEqual(self.box.impact()[0]['claim_ids'], ['certificate', 'independent', 'paper'])

    def test_changed_manifest_remains_a_shared_provenance_failure(self):
        seq = self.send(); self.box.consume_handoff('writer', seq, self.request)
        (self.root / 'handoff.json').write_text('{}')
        self.assertEqual(self.box.impact()[0]['claim_ids'], ['certificate', 'independent', 'paper'])
        self.assertIn('sha256 mismatch', ';'.join(self.box.impact()[0]['reasons']))

    def test_cli_context_impact_and_usage(self):
        seq = self.send()
        for name, obj in [('plan', self.plan), ('request', self.request)]:
            (self.root / (name + '.json')).write_text(json.dumps(obj))
        command = [sys.executable, '-m', 'agent_runtime.communication', '--db', str(self.box.path),
                   '--plan', str(self.root / 'plan.json'), '--root', str(self.root)]
        for args in (['context', 'writer', str(seq), '--request', str(self.root / 'request.json')],
                     ['usage'], ['impact']):
            output = subprocess.run(command + args, text=True, capture_output=True)
            self.assertEqual(output.returncode, 0, output.stdout + output.stderr)
            json.loads(output.stdout)

    def test_consumer_can_require_unknown_at_dispatch_knowledge_and_memory(self):
        for key in ('knowledge_refs', 'memory_refs'):
            record = deepcopy(self.record); record.pop(key)
            request = dict(self.request, knowledge_refs=[], memory_refs=[])
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'missing'):
                check_handoff_basis(self.root, record, request)

    def test_extra_memory_is_validated_and_required_subset_cannot_be_omitted(self):
        with self.assertRaises(ValueError):
            check_handoff_basis(self.root, dict(self.record, memory_refs=['unknown']), self.request)
        with self.assertRaisesRegex(ValueError, 'omits consumer-required'):
            check_handoff_basis(self.root, dict(self.record, memory_refs=['input-v1']), self.request)

    def test_invalid_claims_cannot_pass_supported_premise_gate(self):
        changes = [dict(status='candidate'), dict(depends_on=['paper']),
                   dict(knowledge_ids=['physics.dimensionless']),
                   dict(assumptions=[dict(name='premise', status='unknown', evidence_ids=['result'])]),
                   dict(assumptions=[dict(name='premise', status='satisfied', evidence_ids=[])])]
        for change in changes:
            record = deepcopy(self.record); record['evidence_claims'][0].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                check_handoff_basis(self.root, record, self.request)

    def test_candidate_and_rejected_claims_are_storable_but_not_required_support(self):
        record = deepcopy(self.record)
        for c in record['evidence_claims']:
            c['status'] = 'candidate'
        check_handoff_basis(self.root, record, dict(self.request, required_claim_ids=[]))
        with self.assertRaisesRegex(ValueError, 'unsupported'):
            check_handoff_basis(self.root, record, self.request)

    def test_invalid_consumer_contract_does_not_record_consumption(self):
        seq = self.send()
        for change in (dict(knowledge_required='yes'), dict(memory_required=None),
                       dict(required_claim_ids=['missing']), dict(context_max_chars=True)):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.box.consume_handoff('writer', seq, dict(self.request, **change))
        with self.box.connect() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM communication_basis').fetchone()[0], 0)

    def test_consumer_binding_is_immutable_after_valid_consumption(self):
        seq = self.send(); self.box.consume_handoff('writer', seq, self.request)
        with self.assertRaisesRegex(ValueError, 'basis/request changed'):
            self.box.consume_handoff('writer', seq, dict(self.request, required_claim_ids=[]))

    def test_context_reuses_complete_evidence_without_losing_refs_or_claims(self):
        seq = self.send()
        full = self.box.prepare_context('writer', seq, self.request, max_chars=100000)
        warm = self.box.prepare_context('writer', seq, self.request, max_chars=100000,
                                        known_knowledge_refs=self.refs, known_memory_ids=['derived-v1', 'input-v1'])
        a, b = json.loads(full['payload']), json.loads(warm['payload'])
        for key in ('knowledge_refs', 'memory_refs', 'evidence_claims', 'artifacts'):
            self.assertEqual(a[key], b[key])
        self.assertFalse(b['knowledge_entries']); self.assertFalse(b['memory_entries'])
        self.assertEqual({e['id'] for e in a['memory_entries']}, {'derived-v1', 'input-v1'})
        self.assertLess(warm['usage']['chars'], full['usage']['chars'])
        self.assertIsNone(warm['usage']['tokens'])
        self.assertEqual(full['usage']['bytes'], len(full['payload'].encode()))
        self.assertEqual(self.box.inbox('writer')[0]['seq'], seq)  # no automatic ACK

    def test_cache_of_leaf_alone_does_not_omit_missing_memory_parent(self):
        pack = basis_context(self.root, self.record, self.request, max_chars=100000,
                             known_memory_ids=['derived-v1'])
        self.assertEqual([e['id'] for e in json.loads(pack['payload'])['memory_entries']], ['input-v1'])

    def test_missing_or_changed_knowledge_prerequisite_cannot_be_reused(self):
        with self.assertRaisesRegex(ValueError, 'omit prerequisites'):
            basis_context(self.root, self.record, self.request, max_chars=100000,
                          known_knowledge_refs=[self.refs[-1]])
        seq = self.send(); self.box.consume_handoff('writer', seq, self.request)
        f = self.root / 'corpus/entries/math.cauchy-schwarz.md'; f.write_text(f.read_text() + '\ncorrected\n')
        self.assertEqual(self.box.impact()[0]['claim_ids'], ['certificate', 'paper'])

    def test_budget_rejection_is_atomic_and_never_truncates_prerequisites(self):
        seq = self.send()
        with self.assertRaisesRegex(ValueError, 'character budget'):
            self.box.prepare_context('writer', seq, self.request, max_chars=100)
        self.assertIsNone(self.box.status()[1]['receipt'])
        with self.assertRaisesRegex(ValueError, 'character budget'):
            basis_context(self.root, self.record, dict(self.request, context_max_chars=100), max_chars=100000)

    def test_actual_token_counter_required_and_hard_caps_enforced(self):
        with self.assertRaisesRegex(ValueError, 'actual token_counter'):
            basis_context(self.root, self.record, self.request, max_tokens=1)
        # Synthetic counter tests the adapter contract; it is NOT an actual model tokenizer.
        full = basis_context(self.root, self.record, self.request, max_chars=100000,
                             token_counter=lambda s: len(s.split()))
        count = full['usage']['tokens']
        with self.assertRaisesRegex(ValueError, 'token budget'):
            basis_context(self.root, self.record, dict(self.request, context_max_tokens=count - 1),
                          max_chars=100000, max_tokens=count + 1, token_counter=lambda s: len(s.split()))
        for count in (True, -1, 1.5):
            with self.subTest(count=count), self.assertRaisesRegex(ValueError, 'nonnegative integer'):
                basis_context(self.root, self.record, self.request, max_chars=100000,
                              token_counter=lambda s: count)

    def test_cache_scope_and_freshness_remain_required(self):
        with self.assertRaisesRegex(ValueError, 'project-relative|outside project'):
            basis_context(self.root, dict(self.record, knowledge_refs=[], evidence_claims=[]),
                          dict(self.request, knowledge_root='/tmp', knowledge_required=False,
                               knowledge_refs=[], required_claim_ids=[]), known_knowledge_refs=self.refs)
        self.memory.correct('input-v1', 'v2', 'corrected', 'synthetic:new', 'wrong')
        with self.assertRaisesRegex(ValueError, 'stale'):
            basis_context(self.root, self.record, self.request, known_memory_ids=['derived-v1'])

    def test_delivery_budget_counts_fanout_and_duplicate_once(self):
        self.send(); cost = len(canonical(self.event).encode())
        plan = dict(self.plan, run_id='cap', max_delivery_bytes=2 * cost)
        event = dict(self.event, run_id='cap')
        cost = len(canonical(event).encode()); plan['max_delivery_bytes'] = 2 * cost
        box = Mailbox(self.root / 'cap.sqlite', plan, self.root)
        box.publish(event); self.assertTrue(box.publish(event)['duplicate'])
        self.assertEqual(box.usage()['delivery_bytes'], 2 * cost)
        self.assertEqual(box.usage()['events'], 1)
        with self.assertRaisesRegex(ValueError, 'no partial fan-out'):
            box.publish(dict(event, event_id='E2'))
        self.assertEqual(box.usage()['deliveries'], 2)


if __name__ == '__main__':
    unittest.main()
