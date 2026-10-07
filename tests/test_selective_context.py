"""Consumer-directed evidence projection must preserve scope and negative evidence."""
import json
import subprocess
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from agent_runtime.handoff_basis import basis_context, check_handoff_basis, make_token_counter
from agent_runtime.knowledge import KnowledgeStore
import test_handoff_basis as basis_fixture


class SelectiveContextTests(unittest.TestCase):
    def setUp(self):
        self.f = basis_fixture.BasisTests(); self.f.setUp(); self.addCleanup(self.f.doCleanups)
        self.request = dict(self.f.request, context_claim_ids=['paper'])
        refs = KnowledgeStore(self.f.root / 'corpus').get('math.contraction-residual-certificate')['knowledge_refs']
        self.extra_refs = refs
        self.f.record['knowledge_refs'] += [r for r in refs if r not in self.f.refs]
        self.f.record['artifacts'].append(self.f.save('unrelated.json', {'history': 'large unrelated evidence ' * 100}, 'extra'))
        self.f.record['evidence_claims'].append(dict(id='other', status='supported', knowledge_ids=[refs[-1]['id']],
            memory_ids=[], artifact_ids=['extra'], depends_on=[], assumptions=[]))

    def pack(self, request=None, **kwargs):
        return basis_context(self.f.root, self.f.record, request or self.request, max_chars=100000, **kwargs)

    def test_selected_claim_keeps_transitive_basis_and_original_bytes(self):
        full = self.pack(dict(self.f.request))
        chosen = self.pack()
        a, b = json.loads(full['payload']), json.loads(chosen['payload'])
        self.assertEqual([c['id'] for c in b['evidence_claims']], ['certificate', 'paper'])
        for claim in b['evidence_claims']:
            self.assertIn(claim, a['evidence_claims'])
        self.assertEqual(b['knowledge_refs'], self.f.refs)
        self.assertEqual({m['id'] for m in b['memory_entries']}, {'input-v1', 'derived-v1'})
        self.assertEqual([a['id'] for a in b['artifacts']], ['result'])
        self.assertEqual(chosen['selection']['excluded_claim_ids'], ['independent', 'other'])
        self.assertLess(chosen['usage']['chars'], full['usage']['chars'])

    def test_required_claims_and_refs_cannot_be_pruned_by_projection(self):
        chosen = self.pack(dict(self.request, context_claim_ids=['other']))
        ids = chosen['selection']['included_claim_ids']
        self.assertTrue({'other', 'certificate', 'paper'} <= set(ids))
        # Required knowledge is retained even if no selected claim declares it.
        chosen = self.pack(dict(self.request, context_claim_ids=['independent'], required_claim_ids=[],
                                memory_required=False))
        payload = json.loads(chosen['payload'])
        self.assertEqual(payload['knowledge_refs'], self.f.refs)
        self.assertEqual(payload['memory_refs'], ['derived-v1'])

    def test_candidates_and_refutations_and_their_parents_are_always_retained(self):
        for status in ('rejected', 'candidate'):
            self.f.record['evidence_claims'][-1]['status'] = status
            chosen = self.pack(); payload = json.loads(chosen['payload'])
            self.assertIn('other', chosen['selection']['included_claim_ids'])
            self.assertIn('extra', [a['id'] for a in payload['artifacts']])
            self.assertEqual(payload['evidence_claims'][-1]['status'], status)

    def test_projection_never_waives_full_incoming_validation(self):
        self.f.record['knowledge_refs'][-1]['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'stale'):
            self.pack()

    def test_invalid_empty_unknown_duplicate_selection_is_rejected(self):
        for ids in (None, [], ['unknown'], ['paper', 'paper'], 'paper'):
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                self.pack(dict(self.request, context_claim_ids=ids))

    def test_producer_selection_field_has_no_authority(self):
        self.f.record['context_claim_ids'] = ['other']
        self.assertEqual(self.pack()['selection']['included_claim_ids'], ['certificate', 'paper'])

    def test_consumer_can_require_artifacts_not_attached_to_selected_claim(self):
        chosen = self.pack(dict(self.request, context_artifact_ids=['extra']))
        self.assertEqual([a['id'] for a in json.loads(chosen['payload'])['artifacts']], ['result', 'extra'])
        with self.assertRaisesRegex(ValueError, 'unknown artifacts'):
            self.pack(dict(self.request, context_artifact_ids=['missing']))

    def test_mandatory_basis_cannot_be_empty_after_selection(self):
        request = dict(self.request, context_claim_ids=['independent'], required_claim_ids=[],
                       knowledge_refs=[], memory_refs=[])
        with self.assertRaisesRegex(ValueError, 'required knowledge basis'):
            self.pack(request)

    def test_no_projection_matches_existing_payload_and_complete_cache_contract(self):
        first = self.pack(dict(self.f.request))
        self.assertIsNone(first['selection'])
        full_refs = self.f.record['knowledge_refs']
        second = self.pack(known_knowledge_refs=full_refs, known_memory_ids=['input-v1', 'derived-v1'])
        payload = json.loads(second['payload'])
        self.assertEqual(payload['knowledge_refs'], self.f.refs)
        self.assertFalse(payload['knowledge_entries']); self.assertFalse(payload['memory_entries'])

    def test_projection_budget_keeps_objections_instead_of_silently_dropping_them(self):
        self.f.record['evidence_claims'][-1]['status'] = 'candidate'
        with self.assertRaisesRegex(ValueError, 'character budget'):
            basis_context(self.f.root, self.f.record, self.request, max_chars=100)

    def test_tokenizer_binding_is_consumer_owned(self):
        request = dict(self.request, context_tokenizer='expected')
        counter = lambda text: 10
        with self.assertRaisesRegex(ValueError, 'tokenizer binding'):
            self.pack(request, token_counter=counter)
        counter.tokenizer_name = 'expected'
        self.assertEqual(self.pack(request, token_counter=counter)['usage']['tokenizer'], 'expected')
        for name in (None, ''):
            with self.assertRaisesRegex(ValueError, 'context_tokenizer'):
                check_handoff_basis(self.f.root, self.f.record, dict(self.request, context_tokenizer=name))

    def test_optional_tokenizer_factory_fails_closed_without_dependency(self):
        with patch.dict('sys.modules', {'tiktoken': None}), self.assertRaisesRegex(ValueError, 'unavailable'):
            make_token_counter('o200k_base')

    def test_tokenizer_factory_counts_literal_special_tokens_as_data(self):
        # Mock tests the adapter contract, not a model encoding measurement.
        calls = []
        def encode(text, **options):
            calls.append(options); return list(text.encode())
        module = SimpleNamespace(__version__='test-only', get_encoding=lambda name: SimpleNamespace(encode=encode))
        with patch.dict('sys.modules', {'tiktoken': module}):
            counter = make_token_counter('test-only')
            self.assertEqual(counter('<|endoftext|>'), 13)
        self.assertEqual(calls, [{'disallowed_special': ()}])

    def test_valid_delivery_projection_registers_basis_but_does_not_ack(self):
        seq = self.f.send()
        pack = self.f.box.prepare_context('writer', seq, self.request, max_chars=100000)
        self.assertEqual(pack['selection']['included_claim_ids'], ['certificate', 'paper'])
        self.assertIsNone(self.f.box.status()[1]['receipt'])
        self.assertEqual(self.f.box.impact(), [])

    def test_cli_token_budget_without_counter_blocks_dispatch(self):
        seq = self.f.send()
        for name, value in [('plan', self.f.plan), ('request', self.request)]:
            (self.f.root / (name + '.json')).write_text(json.dumps(value))
        result = subprocess.run([sys.executable, '-m', 'agent_runtime.communication',
            '--db', str(self.f.box.path), '--plan', str(self.f.root / 'plan.json'),
            '--root', str(self.f.root), 'context', 'writer', str(seq),
            '--request', str(self.f.root / 'request.json'), '--max-tokens', '1'],
            capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('actual token_counter', result.stdout + result.stderr)
        self.assertIsNone(self.f.box.status()[1]['receipt'])


if __name__ == '__main__':
    unittest.main()
