"""Discovery only: full current Mailbox.impact, no candidate or speedup."""
import argparse
import cProfile
import hashlib
import json
import os
from pathlib import Path
import platform
import pstats
import sqlite3
import statistics
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from agent_runtime.communication import Mailbox, canonical

CASES = [('no-consumption', 0, 'chain', 'none'),
         ('healthy-chain512', 512, 'chain', 'none'),
         ('artifact-chain128', 128, 'chain', 'artifact'),
         ('artifact-chain512', 512, 'chain', 'artifact'),
         ('artifact-star512', 512, 'star', 'artifact'),
         ('manifest-chain512', 512, 'chain', 'manifest')]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def snapshot(box):
    with box.connect() as db:
        tables = [r[0] for r in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        rows = {t: sorted([list(r) for r in db.execute('SELECT * FROM "' + t + '"')],
                          key=canonical) for t in tables}
    files = {p.name: digest(p.read_bytes()) for p in box.root.iterdir()
             if p.name in ('result.txt', 'handoff.json')}
    return {'logical_db': digest(canonical(rows).encode()), 'files': files}


def fixture(root, n, shape, mutation):
    plan = dict(schema_version=1, run_id='impact13', input_version='v1', routes=[
        dict(sender='code', recipient='writer', task_id='T1', kind='artifact')])
    box = Mailbox(root / 'mail.sqlite', plan, root)
    if not n:
        return box, None, None
    data = b'fixture current result\n'
    (root / 'result.txt').write_bytes(data)
    artifact = dict(id='result', path='result.txt', sha256=digest(data))
    claims = []
    for i in range(n):
        if shape == 'shared':
            deps = [f'c{j:04}' for j in range((i//4-1)*4, (i//4)*4)] if i >= 4 else []
        elif shape == 'dense':
            deps = [f'c{j:04}' for j in range(i)]
        elif shape == 'mixed' and i >= n//2:
            deps = []
        else:
            deps = [f'c{(0 if shape == "star" else i-1):04}'] if i else []
        independent = shape == 'mixed' and i >= n//2
        claims.append(dict(id=f'c{i:04}', status='candidate' if independent else 'supported',
                           knowledge_ids=[], memory_ids=[],
                           artifact_ids=['result'] if (i == 0 or shape == 'shared' and i < 4) else [],
                           depends_on=deps, assumptions=[]))
    record = dict(schema_version=1, run_id='impact13', role='code', input_version='v1',
                  status='completed', limitations=[], artifacts=[artifact],
                  checks=[dict(criterion='fixture bytes', status='pass', artifact_ids=['result'])],
                  tasks=[dict(task_id='T1', status='done', evidence=['result'])],
                  evidence_claims=claims)
    request = dict(schema_version=1, input_version='v1', tasks=[dict(task_id='T1')],
                   required_claim_ids=[f'c{(n//2-1 if shape == "mixed" else n-1):04}'])
    raw = canonical(record).encode()
    (root / 'handoff.json').write_bytes(raw)
    event = dict(event_id='E1', run_id='impact13', input_version='v1', sender='code',
                 task_id='T1', kind='artifact', summary='fixture', action='verify',
                 refs=[dict(id='handoff', path='handoff.json', sha256=digest(raw))])
    seq = box.publish(event)['seq']
    if box.consume_handoff('writer', seq, request) != record:
        raise RuntimeError('consume mismatch')
    if mutation == 'artifact':
        (root / 'result.txt').write_bytes(b'fixture changed result\n')
    elif mutation == 'manifest':
        (root / 'handoff.json').write_bytes(b'{}')
    return box, record, request


def oracle(value, n, mutation):
    if mutation == 'none':
        if value != []:
            raise RuntimeError('healthy/no-consumption must have no impact')
        return
    if len(value) != 1:
        raise RuntimeError('expected one consumed delivery')
    row = value[0]
    if (row['seq'] != 1 or row['event_id'] != 'E1' or row['recipient'] != 'writer'
            or row['usage_stage'] != 'validated_handoff' or row['stale'] is not True
            or row['claim_ids'] != [f'c{i:04}' for i in range(n)]):
        raise RuntimeError('fixture independent claim/delivery oracle failed')
    expected_scope = ('shared envelope/manifest provenance changed; whole handoff affected'
                      if mutation == 'manifest' else
                      'declared local claim DAG and project memory dependency closure')
    if row['scope'] != expected_scope or not row['reasons']:
        raise RuntimeError('provenance scope or reasons mismatch')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--correctness-only', action='store_true')
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    result = dict(schema='impact13-discovery/v1', candidate=None, environment=dict(
        python=sys.version, platform=platform.platform(), sqlite=sqlite3.sqlite_version,
        cpu_count=os.cpu_count(), hashseed=os.environ.get('PYTHONHASHSEED'),
        sharing='shared unpinned CPU; no GPU/model'), warmups=3, repeats=9,
        source_hashes={p: digest((ROOT / p).read_bytes()) for p in (
            'agent_runtime/communication.py', 'agent_runtime/handoff_basis.py',
            'agent_runtime/knowledge.py', 'agent_runtime/project_memory.py',
            'scripts/validate_handoff.py')}, harness_sha256=digest(Path(__file__).read_bytes()),
        plan_sha256=digest((Path(__file__).parent / 'plan-v2.md').read_bytes()), cases=[])
    for name, n, shape, mutation in CASES:
        with tempfile.TemporaryDirectory(prefix='impact13-') as temp:
            box, record, request = fixture(Path(temp), n, shape, mutation)
            before = snapshot(box)
            fixture_input = dict(n=n, shape=shape, mutation=mutation, record=record,
                                 request=request)
            entry = dict(name=name, input_sha256=digest(canonical(fixture_input).encode()),
                         fixture_input=fixture_input, before=before, samples_ns=[])
            for _ in range(1 if args.correctness_only else 3):
                oracle(box.impact(), n, mutation)
            if not args.correctness_only:
                for _ in range(9):
                    start = time.perf_counter_ns()
                    value = box.impact()
                    elapsed = time.perf_counter_ns() - start
                    oracle(value, n, mutation)
                    if elapsed <= 0:
                        raise RuntimeError('invalid clock sample')
                    entry['samples_ns'].append(elapsed)
                entry['median_ns'] = statistics.median(entry['samples_ns'])
                entry['min_ns'] = min(entry['samples_ns'])
                entry['max_ns'] = max(entry['samples_ns'])
                if name in ('artifact-chain512', 'artifact-star512'):
                    profile = cProfile.Profile()
                    value = profile.runcall(box.impact)
                    oracle(value, n, mutation)
                    profile.dump_stats(str(args.out / (name + '.pstats')))
                    stats = pstats.Stats(profile)
                    entries = [dict(file=k[0], line=k[1], function=k[2], primitive=v[0],
                                    calls=v[1], self_seconds=v[2], cumulative_seconds=v[3])
                               for k, v in stats.stats.items()]
                    entry['profile_total_seconds'] = stats.total_tt
                    entry['profile'] = sorted(entries, key=lambda x: -x['cumulative_seconds'])
            entry['after'] = snapshot(box)
            if entry['after'] != before:
                raise RuntimeError('audit mutated fixture logical database/files')
            if n and box.status()[0]['receipt'] is not None:
                raise RuntimeError('unexpected ACK')
            result['cases'].append(entry)
    (args.out / 'raw.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([dict(name=e['name'], median_ms=e.get('median_ns', 0)/1e6,
                           unchanged=e['before']==e['after']) for e in result['cases']]))


if __name__ == '__main__':
    main()
