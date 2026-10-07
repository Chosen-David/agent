"""Public structural/encoding benchmark; explicitly not model quality evaluation.

Run from checkout with tiktoken==0.12.0 available. No external model calls.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests'))
import test_handoff_basis as fixtures
from agent_runtime.communication import Mailbox
from agent_runtime.handoff_basis import basis_context, make_token_counter
from agent_runtime.knowledge import KnowledgeStore


def serialized(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def consumer(root, pack, cid):
    payload = json.loads(pack['payload'])
    claims = {c['id']: c for c in payload['evidence_claims']}
    assert claims[cid]['status'] == 'supported'
    assert claims['trend-misuse']['status'] == 'rejected'
    assert claims['trend-misuse']['assumptions'][0]['status'] == 'unsatisfied'
    artifacts = {a['id']: a for a in payload['artifacts']}
    if cid == 'paper':
        assert claims[cid]['depends_on'] == ['certificate']
        evidence = json.loads((root / artifacts['result']['path']).read_text())
        return {'stable': 0.2 < evidence['margin'] / 2}
    if cid == 'thermal':
        evidence = json.loads((root / artifacts['thermal-proof']['path']).read_text())
        assert evidence['units'] == 'K' and 0 <= evidence['q'] < 1
        return {'error_bound_K': evidence['residual'] / (1 - evidence['q'])}
    assert 'infra-proof' in artifacts
    return {'method_located': True, 'local_speedup': 'unmeasured'}


def main():
    plan = json.loads(Path(__file__).with_name('plan.json').read_text())
    counters = {name: make_token_counter(name) for name in plan['encodings']}
    assert all(c.tokenizer_version == plan['tokenizer_version'] for c in counters.values())
    for counter in counters.values():
        counter('知识依据 tokenizer warmup <|endoftext|>')
    f = fixtures.BasisTests(); f.setUp()
    start = time.perf_counter()
    try:
        corpus = KnowledgeStore(f.root / 'corpus')
        # Add independently needed physics and engineering knowledge, not text padding.
        refs = {r['id']: r for r in f.refs}
        for kid in ['math.contraction-residual-certificate', 'physics.dimensionless', 'infra.flashattention-io']:
            refs.update({r['id']: r for r in corpus.get(kid)['knowledge_refs']})
        f.record['knowledge_refs'] = [refs[k] for k in sorted(refs)]
        f.record['artifacts'] += [
            f.save('thermal.json', {'q': 0.5, 'residual': 0.01, 'units': 'K'}, 'thermal-proof'),
            f.save('infra.json', {'method': 'exact attention', 'local_performance': 'unmeasured'}, 'infra-proof'),
            f.save('negative.json', {'reason': 'message counts are not a state-space map or norm'}, 'negative-proof')]
        for cid, status, kids, aid, premise in [
            ('thermal', 'supported', ['math.contraction-residual-certificate', 'physics.dimensionless'], 'thermal-proof', 'verified contraction domain and K units in synthetic input'),
            ('infra', 'supported', ['infra.flashattention-io'], 'infra-proof', 'fixed-source method located, performance not asserted'),
            ('trend-misuse', 'rejected', [], 'negative-proof', 'conversation counts define a verified contraction map')]:
            f.record['evidence_claims'].append(dict(id=cid, status=status, knowledge_ids=kids,
                memory_ids=[], artifact_ids=[aid], depends_on=[], assumptions=[dict(name=premise,
                status='unsatisfied' if status == 'rejected' else 'satisfied', evidence_ids=[aid])]))
        seq = f.send()
        rows = []
        cli_checks = []
        for encoding, counter in counters.items():
            for case in plan['cases']:
                # Separate approved consumers have immutable independent requests.
                box = Mailbox(f.root / (encoding + '-' + case['id'] + '.sqlite'), f.plan, f.root)
                seq = box.publish(f.event)['seq']
                request = dict(f.request, knowledge_refs=[], memory_refs=[], memory_required=False,
                               required_claim_ids=[case['claim']], context_tokenizer=encoding)
                selected_request = dict(request, context_claim_ids=[case['claim']])
                full = box.prepare_context('writer', seq, request, max_chars=100000, token_counter=counter)
                selected = box.prepare_context('review', seq, selected_request, max_chars=100000, token_counter=counter)
                p, s = json.loads(full['payload']), json.loads(selected['payload'])
                for field in ['evidence_claims', 'knowledge_refs', 'knowledge_entries', 'memory_entries', 'artifacts']:
                    assert all(item in p[field] for item in s[field]), field
                assert consumer(f.root, full, case['claim']) == consumer(f.root, selected, case['claim']) == case['expected']
                warm = box.prepare_context('review', seq, selected_request, max_chars=100000, token_counter=counter,
                    known_knowledge_refs=s['knowledge_refs'], known_memory_ids=[m['id'] for m in s['memory_entries']])
                assert not json.loads(warm['payload'])['knowledge_entries']
                assert not json.loads(warm['payload'])['memory_entries']
                # Same-context cached bodies restore the same deterministic result.
                restored = json.loads(warm['payload'])
                restored.update(knowledge_entries=s['knowledge_entries'], memory_entries=s['memory_entries'])
                assert consumer(f.root, {'payload': serialized(restored)}, case['claim']) == case['expected']
                latency = {'full': [], 'selected': []}
                for i in range(plan['local_latency_repeats']):
                    order = ['full', 'selected'] if i % 2 == 0 else ['selected', 'full']
                    for arm in order:
                        before = time.perf_counter()
                        basis_context(f.root, f.record, request if arm == 'full' else selected_request,
                                      max_chars=100000, token_counter=counter)
                        latency[arm].append((time.perf_counter() - before) * 1000)
                metrics = {}
                for arm, pack in [('full', full), ('selected', selected), ('selected_warm', warm)]:
                    metrics[arm] = dict(payload_tokens=pack['usage']['tokens'], payload_bytes=pack['usage']['bytes'],
                        returned_json_tokens=counter(serialized(pack)),
                        cli_json_tokens=counter(json.dumps(pack, ensure_ascii=False, indent=2) + '\n'),
                        payload_sha256=hashlib.sha256(pack['payload'].encode()).hexdigest())
                rows.append(dict(case=case['id'], encoding=encoding, metrics=metrics,
                    included_claims=selected['selection']['included_claim_ids'], result=case['expected'],
                    local_pack_ms={arm: {'samples': vals, 'median': statistics.median(vals)} for arm, vals in latency.items()},
                    two_stage_returned_json_tokens={'repeat_full': 2 * metrics['full']['returned_json_tokens'],
                        'selected_then_warm': metrics['selected']['returned_json_tokens'] + metrics['selected_warm']['returned_json_tokens']},
                    automatic_ack=any(row['receipt'] is not None for row in box.status()), impact=box.impact()))
                assert not rows[-1]['automatic_ack'] and not rows[-1]['impact']
            # Selecting every claim cannot save payload; projection metadata costs extra.
            all_request = dict(request, context_claim_ids=[c['id'] for c in f.record['evidence_claims']])
            all_pack = basis_context(f.root, f.record, all_request, max_chars=100000, token_counter=counter)
            assert all_pack['payload'] == full['payload']
            cli_box = Mailbox(f.root / ('cli-' + encoding + '.sqlite'), f.plan, f.root)
            cli_seq = cli_box.publish(f.event)['seq']
            for name, obj in [('plan', f.plan), ('request', selected_request)]:
                (f.root / (name + '.json')).write_text(serialized(obj))
            command = [sys.executable, '-m', 'agent_runtime.communication', '--db', str(cli_box.path),
                '--plan', str(f.root / 'plan.json'), '--root', str(f.root), 'context', 'review', str(cli_seq),
                '--request', str(f.root / 'request.json'), '--max-chars', '100000', '--encoding', encoding]
            good = subprocess.run(command + ['--max-tokens', '10000'], capture_output=True, text=True, check=True)
            assert json.loads(good.stdout)['usage']['tokens'] == selected['usage']['tokens']
            assert counter(good.stdout) == counter(json.dumps(json.loads(good.stdout), ensure_ascii=False, indent=2) + '\n')
            bad_cli = subprocess.run(command + ['--max-tokens', '1'], capture_output=True, text=True)
            assert bad_cli.returncode != 0 and 'token budget' in bad_cli.stdout + bad_cli.stderr
            cli_checks.append(dict(encoding=encoding, valid_cli=True, hard_cap_rejected=True,
                actual_cli_stdout_tokens=counter(good.stdout),
                no_gain_control={'payload_tokens': all_pack['usage']['tokens'],
                    'returned_json_tokens': counter(serialized(all_pack)),
                    'full_returned_json_tokens': counter(serialized(full))}))
        bad = deepcopy(f.record); bad['knowledge_refs'][-1]['sha256'] = '0' * 64
        stale_rejected = False
        try:
            basis_context(f.root, bad, dict(f.request, knowledge_refs=[], memory_refs=[], memory_required=False,
                context_claim_ids=['paper']), max_chars=100000)
        except ValueError:
            stale_rejected = True
        assert stale_rejected
        for encoding in plan['encodings']:
            gains = [r for r in rows if r['encoding'] == encoding and all(
                r['metrics']['selected'][m] < r['metrics']['full'][m]
                for m in ['payload_tokens', 'returned_json_tokens'])]
            assert len(gains) >= 2
        print(json.dumps(dict(plan_sha256=hashlib.sha256(Path(__file__).with_name('plan.json').read_bytes()).hexdigest(),
            baseline_commit=plan['baseline_commit'], corpus_entries=len(corpus.records),
            tokenizer_version=plan['tokenizer_version'], elapsed_seconds=time.perf_counter() - start,
            input_sha256=hashlib.sha256(serialized(f.record).encode()).hexdigest(), rows=rows,
            cli_checks=cli_checks, python_version=sys.version.split()[0],
            stale_incoming_rejected=stale_rejected, structural_acceptance='pass', quality_AB='not_run',
            model_tokens=None, billing=None, unseen_test=False,
            scope='public synthetic dependency/encoding checks; local pack latency, no model quality or inference claims'),
            ensure_ascii=False, indent=2))
    finally:
        f.doCleanups()


if __name__ == '__main__':
    main()
