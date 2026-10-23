"""Pinned knowledge identities must match the snapshot used to hydrate bodies."""
import unittest
from unittest.mock import patch

from agent_runtime import handoff_basis
from agent_runtime.handoff_encoding import decode_basis_payload
from agent_runtime.knowledge import KnowledgeStore
import test_handoff_basis as fixture


class KnowledgeHydrationTests(unittest.TestCase):
    def make_fixture(self):
        value = fixture.BasisTests()
        value.setUp()
        self.addCleanup(value.doCleanups)
        return value

    def edit(self, value, kid):
        path = value.root / 'corpus/entries' / (kid + '.md')
        path.write_text(path.read_text(encoding='utf-8') + '\nHydration mutation marker.\n', encoding='utf-8')

    def assert_coherent(self, packet):
        payload = decode_basis_payload(packet['payload'])
        refs = {ref['id']: ref for ref in payload['knowledge_refs']}
        for entry in payload['knowledge_entries']:
            self.assertEqual({key: entry[key] for key in ('id', 'version', 'sha256')}, refs[entry['id']])
        return payload

    def test_update_between_validation_and_hydration_is_rejected(self):
        for selected in (False, True):
            for encoding in ('json', 'claims-table/v1', 'basis-tables/v1', 'auto-lossless/v1'):
                for kid in ('math.topk-margin', 'math.cauchy-schwarz'):
                    with self.subTest(selected=selected, encoding=encoding, entry=kid):
                        value = self.make_fixture()
                        seq = value.send()
                        request = dict(value.request, context_format=encoding)
                        if selected:
                            request['context_claim_ids'] = ['paper']
                        constructed = []
                        def acquire(root):
                            self.edit(value, kid)
                            constructed.append(root)
                            return KnowledgeStore(root)
                        with patch.object(handoff_basis, 'KnowledgeStore', side_effect=acquire):
                            with self.assertRaisesRegex(ValueError, 'stale knowledge ref: ' + kid):
                                value.box.prepare_context('writer', seq, request, max_chars=100000, token_counter=len)
                        self.assertTrue(constructed)

    def test_unchanged_and_unreferenced_updates_preserve_bodies(self):
        for kid in (None, 'physics.dimensionless'):
            with self.subTest(unreferenced_edit=kid):
                value = self.make_fixture()
                seq = value.send()
                def acquire(root):
                    if kid:
                        self.edit(value, kid)
                    return KnowledgeStore(root)
                with patch.object(handoff_basis, 'KnowledgeStore', side_effect=acquire):
                    packet = value.box.prepare_context('writer', seq, value.request, max_chars=100000)
                payload = self.assert_coherent(packet)
                self.assertEqual(payload['knowledge_refs'], value.refs)
                self.assertNotIn('Hydration mutation marker.', packet['payload'])

    def test_hydrated_snapshot_may_precede_a_later_disk_update(self):
        value = self.make_fixture()
        seq = value.send()
        def acquire(root):
            snapshot = KnowledgeStore(root)
            self.edit(value, 'math.topk-margin')
            return snapshot
        with patch.object(handoff_basis, 'KnowledgeStore', side_effect=acquire):
            packet = value.box.prepare_context('writer', seq, value.request, max_chars=100000)
        self.assert_coherent(packet)
        self.assertNotIn('Hydration mutation marker.', packet['payload'])
        with self.assertRaisesRegex(ValueError, 'stale knowledge ref: math.topk-margin'):
            value.box.prepare_context('writer', seq, value.request, max_chars=100000)

    def test_empty_selected_refs_keep_known_reference_validation(self):
        value = self.make_fixture()
        seq = value.send()
        request = dict(value.request, context_claim_ids=['independent'], required_claim_ids=[],
                       knowledge_refs=[], memory_refs=[], knowledge_required=False, memory_required=False)
        known = KnowledgeStore(value.root / 'corpus').get('physics.dimensionless')['knowledge_refs']
        packet = value.box.prepare_context('writer', seq, request, max_chars=100000,
                                          known_knowledge_refs=known)
        payload = self.assert_coherent(packet)
        self.assertEqual(payload['knowledge_refs'], [])
        self.assertEqual(payload['knowledge_entries'], [])
        self.edit(value, 'physics.dimensionless')
        self.assert_coherent(value.box.prepare_context('writer', seq, request, max_chars=100000))
        with self.assertRaisesRegex(ValueError, 'stale knowledge ref: physics.dimensionless'):
            value.box.prepare_context('writer', seq, request, max_chars=100000,
                                      known_knowledge_refs=known)
