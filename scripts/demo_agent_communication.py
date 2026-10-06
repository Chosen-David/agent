"""Synthetic, deterministic host-adapter exercise; no model role simulation."""
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys

REPO = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get('COMMUNICATION_OUTPUT_ROOT', str(REPO / '.agent-runs/communication-demo'))).resolve()
ROOT.mkdir(parents=True, exist_ok=True)
RUN = 'communication-forward-v2'
VERSION = 'synthetic-input-v2'
IMPL = 'research-implement-optimize'
WRITE = 'research-write'
REVIEW = 'research-review'
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONPATH=str(REPO),
           COMMUNICATION_OUTPUT_ROOT=str(ROOT))
LOG = ROOT / 'commands.jsonl'


def save(path, value):
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    return path


def read(path):
    return json.loads((ROOT / path).read_text())


def ref(path, identifier):
    return {'id': identifier, 'path': path, 'sha256': hashlib.sha256((ROOT / path).read_bytes()).hexdigest()}


def call(args, expected=0):
    result = subprocess.run(args, cwd=ROOT, env=ENV, capture_output=True, text=True)
    row = {'argv': args, 'cwd': str(ROOT), 'exit_code': result.returncode,
           'stdout': result.stdout, 'stderr': result.stderr}
    with LOG.open('a') as stream:
        stream.write(json.dumps(row, ensure_ascii=False) + '\n')
    if result.returncode != expected:
        raise RuntimeError(row)
    return json.loads(result.stdout) if result.stdout.strip() else None


def cli(*args, expected=0):
    return call([sys.executable, '-B', '-m', 'agent_runtime.communication',
                 '--db', str(ROOT / 'messages.sqlite'), '--plan', str(ROOT / 'host/plan.json'),
                 '--root', str(ROOT), *map(str, args)], expected)


def event(eid, sender, kind, summary, action, refs, version=VERSION):
    path = f'events/{eid}.json'
    save(path, {'event_id': eid, 'run_id': RUN, 'input_version': version,
               'sender': sender, 'task_id': 'EXP-1', 'kind': kind,
               'summary': summary, 'action': action, 'refs': refs})
    return str(ROOT / path)


def ack(role, seq, status, reason, name):
    path = save(f'receipts/{name}.json', {'status': status, 'reason': reason})
    cli('ack', role, seq, path)


def manifest(path, artifacts, version=VERSION, run=RUN):
    save(path, {'schema_version': 1, 'run_id': run, 'role': IMPL,
                'input_version': version, 'status': 'completed',
                'limitations': ['Explicit synthetic data; no real model or scientific efficacy claim.'],
                'artifacts': artifacts,
                'checks': [{'criterion': 'Synthetic observations and summary available',
                            'status': 'pass', 'artifact_ids': [a['id'] for a in artifacts]}],
                'tasks': [{'task_id': 'EXP-1', 'depends_on': [], 'status': 'done',
                           'evidence': [a['id'] for a in artifacts]}]})


def writer_worker(seq, crash=False):
    """One logical writer consumer process, restarted explicitly by the host."""
    from agent_runtime.communication import Mailbox
    box = Mailbox(ROOT / 'messages.sqlite', read('host/plan.json'), ROOT)
    pending = box.inbox(WRITE)
    assert any(item['seq'] == seq for item in pending)
    record = box.consume_handoff(WRITE, seq, read('host/writer-request.json'))
    raw = read(next(a['path'] for a in record['artifacts'] if a['id'] == 'raw'))
    summary = read(next(a['path'] for a in record['artifacts'] if a['id'] == 'summary'))
    for name, values in raw['observations'].items():
        assert summary['groups'][name]['mean'] == statistics.mean(values)
    ev = next(item['event'] for item in pending if item['seq'] == seq)
    key = [RUN, ev['event_id'], WRITE]
    ledger_path = ROOT / 'writer/action-ledger.json'
    ledger = read('writer/action-ledger.json') if ledger_path.exists() else []
    exists = any(item['key'] == key for item in ledger)
    if not exists:
        # Local draft append is represented by one durable action record. Recovery
        # reads this key before producing the same action again.
        ledger.append({'key': key, 'action': 'draft-evidence-read', 'seq': seq,
                       'synthetic': True, 'means': summary['groups']})
        save('writer/action-ledger.json', ledger)
        (ROOT / 'writer/draft.md').write_text(
            '# Synthetic draft\n\nThese are fabricated observations for a local communication exercise.\n'
            'Baseline mean: 81.5 percentage points; candidate mean: 85.5 percentage points.\n'
            'Difference: 4.0 percentage points. No generalization claim.\n')
    save(f'writer/process-{seq}-{"interrupt" if crash else "resume"}.json',
         {'pid': os.getpid(), 'seq': seq, 'key': key,
          'read_actual_evidence': True, 'duplicate_action_skipped': exists,
          'interruption_before_ack': crash})
    if crash:
        os._exit(73)
    box.acknowledge(WRITE, seq, {'status': 'consumed',
                    'reason': 'Read raw data and means; durable action key prevents duplicate draft on restart. Scientific acceptance remains reviewer-owned.'})
    print(json.dumps({'seq': seq, 'replayed_action': not exists, 'acknowledged': True}))


def run():
    if LOG.exists():
        raise RuntimeError('Preserve this run: do not overwrite an existing execution.')
    # Trusted host establishes independent task scope before producer artifacts.
    save('host/task-dag.json', {'root_task': 'COMM-02 bounded local usage exercise',
         'synthetic': True, 'nodes': [
             {'id': 'EXP-1', 'depends_on': []},
             {'id': 'WRITE-1', 'depends_on': ['EXP-1']},
             {'id': 'REVIEW-1', 'depends_on': ['EXP-1']},
             {'id': 'FIX-F1', 'depends_on': ['REVIEW-1']},
             {'id': 'RECHECK-F1', 'depends_on': ['FIX-F1']},
             {'id': 'FINAL', 'depends_on': ['WRITE-1', 'RECHECK-F1']}],
         'criteria': ['Both groups: raw observations, percentage-point units, n=4, mean, sample variance (n-1).',
                      'Reviewer closes original finding after recomputing from raw observations.',
                      'Writer restart produces one action per event and refuses stale results.'],
         'max_revisions_per_finding': 2,
         'identity_registry': {IMPL: 'synthetic-implementation-instance-1',
                               WRITE: 'synthetic-writing-instance-1', REVIEW: 'synthetic-review-instance-1'},
         'owners': {'host/': 'trusted-host', 'events/': 'trusted-host-adapter',
                    'producer/': IMPL, 'writer/': WRITE, 'reviewer/': REVIEW,
                    'receipts/': 'trusted-host-adapter', 'messages.sqlite': 'Mailbox'},
         'host_model': 'One deterministic Python harness; identities are logical roles, not independent models.'})
    routes = [{'sender': IMPL, 'recipient': role, 'task_id': 'EXP-1', 'kind': 'artifact'}
              for role in [WRITE, REVIEW]]
    routes += [{'sender': REVIEW, 'recipient': IMPL, 'task_id': 'EXP-1', 'kind': 'review'}]
    save('host/plan.json', {'schema_version': 1, 'run_id': RUN, 'input_version': VERSION,
                           'max_message_bytes': 8192, 'max_events': 12, 'routes': routes})
    request = {'schema_version': 1, 'input_version': VERSION, 'tasks': [{'task_id': 'EXP-1'}]}
    save('host/writer-request.json', request)
    save('host/reviewer-request.json', request)
    save('host/missing-task-request.json', dict(request, tasks=[{'task_id': 'EXP-1'}, {'task_id': 'EXP-REQUIRED'}]))

    raw = {'synthetic': True, 'input_version': VERSION, 'unit': 'percentage points',
           'observations': {'baseline': [80, 82, 81, 83], 'candidate': [84, 86, 85, 87]},
           'generation': 'Fixed literal values, fabricated for this exercise; no experiment/backend executed.'}
    save('producer/raw-v2.json', raw)
    summary = {'synthetic': True, 'unit': raw['unit'], 'groups': {
        name: {'n': len(values), 'mean': statistics.mean(values)} for name, values in raw['observations'].items()}}
    save('producer/summary-r0.json', summary)
    manifest('producer/handoff-r0.json', [ref('producer/raw-v2.json', 'raw'), ref('producer/summary-r0.json', 'summary')])
    initial = event('E-initial', IMPL, 'artifact', 'Synthetic raw observations and means available; dispersion omitted.',
                    'Read evidence and assess original task criteria.', [ref('producer/handoff-r0.json', 'handoff')])
    published = cli('publish', initial)
    seq = published['seq']
    duplicate = cli('publish', initial)
    assert duplicate['duplicate'] and duplicate['seq'] == seq
    assert cli('inbox', IMPL) == []
    missing = cli('consume', WRITE, seq, '--request', ROOT / 'host/missing-task-request.json', expected=1)
    assert 'EXP-REQUIRED' in missing['error']

    # Real process termination after durable local side effect, before receipt.
    call([sys.executable, '-B', str(Path(__file__)), 'writer', str(seq), '--crash'], expected=73)
    pending = cli('inbox', WRITE)
    assert [e['seq'] for e in pending] == [seq]
    save('host/writer-recovery-pending.json', pending)
    resumed = call([sys.executable, '-B', str(Path(__file__)), 'writer', str(seq)])
    assert resumed['replayed_action'] is False
    assert len(read('writer/action-ledger.json')) == 1

    cli('consume', REVIEW, seq, '--request', ROOT / 'host/reviewer-request.json')
    reread = read('producer/summary-r0.json')
    assert all('sample_variance' not in g for g in reread['groups'].values())
    finding = {'finding_id': 'F-variance-001', 'status': 'open', 'severity': 'major',
               'location': 'producer/summary-r0.json: groups[*]', 'evidence': ref('producer/summary-r0.json', 'missing-variance'),
               'finding': 'Mean and n are present; required sample variance is missing.',
               'repair': 'Add unbiased sample variance for both groups, squared percentage-point units, n and ddof=1.',
               'recheck_conditions': 'Read raw data; recompute variance with n-1; verify each result, unit, n and ddof.',
               'formed_before_reading_writer_opinion': True,
               'judgment_source': 'Deterministic adapter checks; not an independent model judgment.'}
    save('reviewer/finding-F1.json', finding)
    revision = event('E-revision-F1', REVIEW, 'review', 'F-variance-001: required variance missing.',
                     'Implement the repair and return evidence for review under original conditions.',
                     [ref('reviewer/finding-F1.json', 'finding')])
    revision_seq = cli('publish', revision)['seq']
    ack(REVIEW, seq, 'needs_revision', 'F-variance-001: supplement sample variance; revision event E-revision-F1 is published.', 'initial-review')
    impl_pending = cli('inbox', IMPL)
    assert [item['seq'] for item in impl_pending] == [revision_seq]
    cited = impl_pending[0]['event']['refs'][0]
    assert ref(cited['path'], cited['id']) == cited
    assert read(cited['path'])['finding_id'] == 'F-variance-001'
    for name, values in raw['observations'].items():
        summary['groups'][name].update(sample_variance=statistics.variance(values), ddof=1,
                                      variance_unit='squared percentage points')
    summary['addresses_finding_id'] = 'F-variance-001'
    save('producer/summary-r1.json', summary)
    manifest('producer/handoff-r1.json', [ref('producer/raw-v2.json', 'raw'), ref('producer/summary-r1.json', 'summary')])
    repaired = event('E-repair-F1', IMPL, 'artifact', 'F-variance-001: sample variance added from the same synthetic observations.',
                     'Reviewer recheck original conditions; writer read updated evidence.',
                     [ref('producer/handoff-r1.json', 'handoff')])
    repaired_seq = cli('publish', repaired)['seq']
    ack(IMPL, revision_seq, 'consumed', 'Read and hash-checked F-variance-001; repair returned as E-repair-F1; finding remains reviewer-owned.', 'revision-implemented')
    cli('consume', REVIEW, repaired_seq, '--request', ROOT / 'host/reviewer-request.json')
    values = read('producer/raw-v2.json')['observations']
    revised = read('producer/summary-r1.json')
    results = {}
    for name, observations in values.items():
        group = revised['groups'][name]
        mean = sum(observations) / len(observations)
        variance = sum((x - mean) ** 2 for x in observations) / (len(observations) - 1)
        assert group['sample_variance'] == variance
        assert group['n'] == 4 and group['ddof'] == 1
        assert group['variance_unit'] == 'squared percentage points'
        results[name] = {'mean': mean, 'recomputed_sample_variance': variance, 'pass': True}
    save('reviewer/recheck-F1.json', {'finding_id': 'F-variance-001', 'status': 'closed',
         'closed_by': REVIEW, 'repair_event_id': 'E-repair-F1', 'revision_count': 1,
         'original_conditions_rechecked': True, 'results': results,
         'evidence': [ref('producer/raw-v2.json', 'raw'), ref('producer/summary-r1.json', 'summary')],
         'independent_model_evidence': False})
    ack(REVIEW, repaired_seq, 'consumed', 'Original F-variance-001 criteria recomputed and satisfied; reviewer/recheck-F1.json closes finding.', 'repair-review')
    call([sys.executable, '-B', str(Path(__file__)), 'writer', str(repaired_seq)])

    # Late artifact is not relabeled: current-run envelope explicitly carries an
    # old-run manifest so the writer actually receives and rejects old evidence.
    save('producer/old-v1-result.json', {'synthetic': True, 'input_version': 'synthetic-input-v1',
         'groups': {'baseline': {'mean': 70}, 'candidate': {'mean': 99}}, 'unit': 'percentage points'})
    manifest('producer/old-v1-handoff.json', [ref('producer/old-v1-result.json', 'summary')],
             version='synthetic-input-v1', run='communication-forward-v1')
    stale_envelope = event('E-stale-envelope', IMPL, 'artifact', 'Late v1 evidence.',
                           'Do not reuse old input as current.', [ref('producer/old-v1-handoff.json', 'handoff')],
                           version='synthetic-input-v1')
    stale_publish = cli('publish', stale_envelope, expected=1)
    assert 'stale' in stale_publish['error']
    late = event('E-late-old-manifest', IMPL, 'artifact', 'Explicit late v1 result attached to v2 routing; old manifest remains unchanged.',
                 'Check version and reject this artifact for current writing and review.',
                 [ref('producer/old-v1-handoff.json', 'handoff')])
    late_seq = cli('publish', late)['seq']
    finish(late_seq)


def finish(late_seq):
    for role in [WRITE, REVIEW]:
        assert any(item['seq'] == late_seq for item in cli('inbox', role))
        request_path = 'host/writer-request.json' if role == WRITE else 'host/reviewer-request.json'
        rejected = cli('consume', role, late_seq, '--request', ROOT / request_path, expected=1)
        assert 'input version mismatch' in rejected['error'] and 'producer/run mismatch' in rejected['error']
        save(f'{"writer" if role == WRITE else "reviewer"}/stale-rejection.json', rejected)
        ack(role, late_seq, 'rejected', 'Old v1 manifest fails current v2 input version and run checks; no scientific or draft action performed.', f'stale-{role}')
    save('receipts/illegal-overwrite.json', {'status': 'consumed', 'reason': 'Attempt to overwrite immutable rejected receipt.'})
    immutable = cli('ack', WRITE, late_seq, ROOT / 'receipts/illegal-overwrite.json', expected=1)
    assert 'immutable' in immutable['error']
    status = cli('status')
    assert all(delivery['receipt'] is not None for delivery in status)
    assert all(cli('inbox', role) == [] for role in [WRITE, REVIEW, IMPL])
    assert read('reviewer/recheck-F1.json')['status'] == 'closed'
    ledger = read('writer/action-ledger.json')
    assert len(ledger) == 2 and len({tuple(entry['key']) for entry in ledger}) == 2
    # Incorporate accepted revision only after original finding is closed.
    draft = ROOT / 'writer/draft.md'
    with draft.open('a') as stream:
        stream.write('\nFor both groups, n=4 and sample variance=1.6666666666666667 squared percentage points (ddof=1).\n')
    save('host/final-audit.json', {'run_id': RUN, 'synthetic': True, 'status': 'passed',
         'all_receipts_present': True, 'open_findings': [], 'revision_rounds': 1,
         'writer_interrupt_exit_code': 73, 'writer_restart_duplicate_action_skipped': True,
         'writer_actions': len(ledger), 'stale_artifact_reused': False,
         'events': len({entry['seq'] for entry in status}), 'deliveries': len(status),
         'checks': ['directed routing', 'duplicate publish', 'missing task rejected',
                    'actual worker exit/restart', 'raw data read', 'needs_revision plus request event',
                    'original-condition reviewer closure', 'old envelope and old manifest rejected',
                    'immutable receipt', 'all inboxes empty'],
         'limitations': ['No multiple models called; this is local interface/host-adapter evidence.',
                         'No real experiment, live Engine integration, malicious concurrency, network or token A/B measured.'],
         'final_status': status})
    print(json.dumps(read('host/final-audit.json'), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'writer':
        writer_worker(int(sys.argv[2]), '--crash' in sys.argv)
    else:
        run()
