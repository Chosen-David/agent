"""Reproducible synthetic IO checks; character/byte costs, no LLM token claims."""
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests'))
from test_handoff_basis import BasisTests
from agent_runtime.handoff_basis import basis_context
from agent_runtime.knowledge import KnowledgeStore


def main():
    fixture = BasisTests(); fixture.setUp()
    started = time.perf_counter()
    try:
        seq = fixture.send()
        full = fixture.box.prepare_context('writer', seq, fixture.request, max_chars=100000)
        warm = fixture.box.prepare_context('writer', seq, fixture.request, max_chars=100000,
                known_knowledge_refs=fixture.refs, known_memory_ids=['derived-v1', 'input-v1'])
        assert warm['usage']['chars'] < full['usage']['chars']
        assert warm['usage']['tokens'] is None
        fixture.box.consume_handoff('review', seq, fixture.request)
        assert fixture.box.impact() == []
        # Exercise the concurrently added nested engineering corpus with the
        # same consumer contract, without a second retrieval implementation.
        store = KnowledgeStore(fixture.root / 'corpus')
        engineering = None
        if 'infra.flashattention-io' in store.records:
            refs = store.get('infra.flashattention-io')['knowledge_refs']
            record = dict(fixture.record, knowledge_refs=refs, memory_refs=[], evidence_claims=[])
            request = dict(fixture.request, knowledge_refs=refs, memory_refs=[], memory_required=False,
                           required_claim_ids=[])
            pack = basis_context(fixture.root, record, request, max_chars=100000)
            assert any(e['path'].startswith('entries/ai-infra/')
                       for e in json.loads(pack['payload'])['knowledge_entries'])
            engineering = {'id': 'infra.flashattention-io', 'status': 'basis/context checked',
                           'usage': pack['usage'], 'scientific_applicability': 'unchecked'}
        fixture.memory.correct('input-v1', 'input-v2', 'Corrected margin', 'synthetic:fixture', 'wrong units')
        impact = fixture.box.impact()
        assert len(impact) == 2
        assert all(x['claim_ids'] == ['certificate', 'paper'] for x in impact)
        rejected = False
        try:
            fixture.box.prepare_context('writer', seq, fixture.request, max_chars=100000,
                                        known_knowledge_refs=fixture.refs)
        except ValueError:
            rejected = True
        assert rejected
        output = {'data_kind': 'synthetic', 'input': 'public tests/test_handoff_basis.py fixture',
                  'elapsed_seconds': time.perf_counter() - started,
                  'cold_payload': full['usage'], 'warm_payload': warm['usage'],
                  'saved_payload_chars_on_repeat': full['usage']['chars'] - warm['usage']['chars'],
                  'two_consumers_two_rounds': {
                      'repeat_full_payload_chars': 4 * full['usage']['chars'],
                      'one_cold_one_warm_each_chars': 2 * (full['usage']['chars'] + warm['usage']['chars'])},
                  'unchanged_fields': ['knowledge_refs', 'memory_refs', 'evidence_claims', 'artifacts'],
                  'message_usage': fixture.box.usage(), 'correction_impact': impact,
                  'concurrent_engineering_integration': engineering,
                  'stale_reuse_rejected': rejected, 'automatic_ack': False,
                  'actual_tokenizer': 'unavailable', 'model_input_output_tokens': None,
                  'quality_AB': 'not_run', 'limitations': [
                      'Warm hints valid only when the full evidence remains in this same consumer context.',
                      'Counts exact payload characters/UTF-8 bytes, not actual tokens or tool envelopes.',
                      'No measured LLM latency, quality, tokenizer or total session costs.',
                      'Corrections target declared dependencies only; scientific premise truth remains independently reviewed.']}
        print(json.dumps(output, ensure_ascii=False, indent=2))
    finally:
        fixture.doCleanups()


if __name__ == '__main__':
    main()
