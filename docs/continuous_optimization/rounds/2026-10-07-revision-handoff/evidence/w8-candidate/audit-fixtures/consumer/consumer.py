#!/usr/bin/env python3
"""Owned stdlib-only synthetic local Mailbox consumer. No repository edits.
Run once in fresh assigned outputs; child restart is bounded to one replay.
"""
import argparse, hashlib, json, os, selectors, signal, sqlite3, subprocess, sys, time, traceback
from pathlib import Path
sys.dont_write_bytecode = True
BASE = Path('/workspace/scratch/c12f3d9f92bd')
CASE = BASE / 'revision-w8-consumer-run/cases/revision-protocol-consumer'
OUT = CASE / 'attempts/0001/outputs'
PRIVATE = BASE / 'revision-w8-consumer-private'
REPO = BASE / 'agent'
sys.path.insert(0, str(REPO))
from agent_runtime.communication import Mailbox, canonical
from agent_runtime.core import Context, Engine, Outcome, Store
INPUTS = CASE / 'inputs'
TASK_HASH = hashlib.sha256((CASE / 'task.txt').read_bytes()).hexdigest()
OWNER = 'owned-local-review-consumer'

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text())
def save(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as f:
        json.dump(value, f, indent=2, ensure_ascii=False); f.write('\n'); f.flush(); os.fsync(f.fileno())
    return path

def log(directory, operation, **data):
    row = dict(at=time.time(), pid=os.getpid(), operation=operation, **data)
    with (directory / 'api.jsonl').open('a') as f:
        f.write(json.dumps(row, sort_keys=True) + '\n'); f.flush(); os.fsync(f.fileno())
    return row

def mailbox(directory):
    return Mailbox(PRIVATE / (directory.name + '-mailbox.sqlite'), read(directory / 'plan.json'), OUT)

def authorized(plan, task, handler):
    return (plan['authorization_reference'] == TASK_HASH and task['owner'] == OWNER
            and handler.required_capabilities == frozenset({'owned_local_mailbox'}))

def guard(directory, context):
    snap = context.store.snapshot(context.run_id)
    task = next(t for t in snap['plan']['tasks'] if t['task_id'] == context.task_id)
    ok = context.current() and authorized(snap['plan'], task, LocalHandler(directory))
    log(directory, 'host_guard', current=context.current(), authorized=authorized(snap['plan'], task, LocalHandler(directory)),
        engine=snap, task_sha256=TASK_HASH)
    if not ok: raise RuntimeError('lost owned current lease or authorization')
    intent = read(directory / 'intent.json'); box = mailbox(directory)
    if box.run_id != intent['run_id'] or box.plan['input_version'] != intent['input_version']:
        raise RuntimeError('immutable intent no longer matches run/input')
    if intent['recipient'] != OWNER: raise RuntimeError('consumer ownership mismatch')
    # Ordinary review events have no completion manifest. Read the actual content.
    for event in (intent['incoming_event'], intent['outgoing']):
        for ref in event['refs']:
            target = (OUT / ref['path']).resolve()
            if not target.is_relative_to(OUT) or sha(target) != ref['sha256']:
                raise RuntimeError('original reference changed; stop and reconcile')
            log(directory, 'reference_readback', event_id=event['event_id'], ref=ref, content=read(target))
    return box, intent

def consume(directory, context, interrupt):
    box, intent = guard(directory, context)
    pending = box.inbox(OWNER); status = box.status()
    log(directory, 'inbox/status/preflight', inbox=pending, status=status)
    original = next((r for r in status if r['seq'] == intent['incoming_seq'] and r['recipient'] == OWNER), None)
    if original is None: raise RuntimeError('original delivery missing')
    if original['receipt'] is not None and original['receipt'] != intent['receipt']:
        log(directory, 'stop_receipt_conflict', saved=intent['receipt'], existing=original['receipt'],
            action='main AI reconcile; do not publish or overwrite')
        save(directory / 'blocked.json', dict(status='unresolved_conflict', existing=original['receipt'], expected=intent['receipt']))
        return 4
    # Still current before the first local effect. Original receipt precheck above is
    # under one host-owned consumer, not an atomic lock across publish and ACK.
    box, intent = guard(directory, context)
    try:
        result = box.publish(intent['outgoing'])
    except ValueError as exc:
        log(directory, 'publish_rejected', error=str(exc), status=box.status(), inbox=box.inbox(OWNER))
        save(directory / 'blocked.json', dict(status='unresolved_publication', error=str(exc), intent='intent.json'))
        return 3
    log(directory, 'publish', event=intent['outgoing'], result=result, status=box.status())
    if interrupt:
        # Parent waits for this flushed marker, then sends SIGKILL to this PID.
        # Blocking stdin prevents ACK races without time-based fault guessing.
        print(json.dumps({'fault_ready': True, 'pid': os.getpid(), 'publish': result}), flush=True)
        sys.stdin.readline()
        raise RuntimeError('parent unexpectedly released fault gate')
    box, intent = guard(directory, context)
    box.acknowledge(OWNER, intent['incoming_seq'], intent['receipt'])
    log(directory, 'acknowledge', seq=intent['incoming_seq'], receipt=intent['receipt'], status=box.status(), inbox=box.inbox(OWNER))
    save(directory / 'handled.json', dict(status='transport_handled', publish=result, original_receipt=intent['receipt'],
         finding_status='open; responsibility recipient has not handled the request; no scientific closure'))
    return 0

class LocalHandler:
    idempotent = True
    required_capabilities = frozenset({'owned_local_mailbox'})
    def __init__(self, directory): self.directory = directory
    def run(self, task, context):
        d = self.directory
        args = [sys.executable, '-B', str(OUT / 'consumer.py'), '--child', str(d), '--token', context.token,
                '--idempotency-key', context.idempotency_key]
        save(d / 'child-command.json', dict(command=args, cwd=str(OUT), environment={'PYTHONDONTWRITEBYTECODE':'1'},
             child_restarts_allowed=1 if d.name == 'interruption' else 0, local_corrections_allowed=1))
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        if d.name == 'interruption':
            command = args + ['--interrupt']
            proc = subprocess.Popen(command, cwd=OUT, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=True)
            selector = selectors.DefaultSelector(); selector.register(proc.stdout, selectors.EVENT_READ)
            if not selector.select(30):
                proc.kill(); stdout, stderr = proc.communicate(timeout=10)
                save(d / 'unexpected-fault-timeout.json', dict(stdout=stdout, stderr=stderr, returncode=proc.returncode))
                raise RuntimeError('child did not reach publication gate')
            marker_line = proc.stdout.readline(); marker = json.loads(marker_line)
            if not marker.get('fault_ready'): raise RuntimeError('unexpected child marker')
            before = mailbox(d).status()
            intent = read(d / 'intent.json')
            assert next(r for r in before if r['seq'] == intent['incoming_seq'])['receipt'] is None
            assert len(before) == 2
            os.kill(proc.pid, signal.SIGKILL)
            rest, stderr = proc.communicate(timeout=10)
            save(d / 'fault-process.json', dict(command=command, pid=proc.pid, signal='SIGKILL',
                stdout=marker_line+rest, stderr=stderr, returncode=proc.returncode, status_after_publish_before_ack=before))
            assert proc.returncode == -signal.SIGKILL
            replay = subprocess.run(args, cwd=OUT, env=env, text=True, capture_output=True, timeout=30)
            save(d / 'replay-process.json', dict(command=args, stdout=replay.stdout, stderr=replay.stderr,
                returncode=replay.returncode, child_restart_count=1))
            if replay.returncode: raise RuntimeError('bounded replay failed')
        else:
            process = subprocess.run(args, cwd=OUT, env=env, text=True, capture_output=True, timeout=30)
            save(d / 'process.json', dict(command=args, stdout=process.stdout, stderr=process.stderr, returncode=process.returncode))
            expected = {'budget':3, 'conflict':4}[d.name]
            if process.returncode != expected: raise RuntimeError('unexpected bounded stop result')
        return Outcome('complete', 'local scenario evidence captured; transport only', [str(d / 'intent.json')])
    def verify(self, task, evidence):
        # Engine done applies only to this bounded local scenario observation.
        return bool(evidence) and (self.directory / ('handled.json' if self.directory.name == 'interruption' else 'blocked.json')).is_file()

def setup(name):
    d = OUT / name; d.mkdir()
    run = 'revision-w8-consumer-' + name + '-' + str(time.time_ns())
    version = 'synthetic-evidence-' + TASK_HASH[:16]
    ref_file = save(d / 'synthetic-evidence.json', dict(synthetic=True, finding_id='SYNTHETIC-FINDING-001',
        original_claim='Seed intentionally omits an uncertainty statement', condition='responsibility author supplies uncertainty and reviewer rereads it',
        real_experiment=False, scientific_status='not assessed'))
    ref = dict(id='synthetic-review-record', path=str(ref_file.relative_to(OUT)), sha256=sha(ref_file))
    routes = [dict(sender='synthetic-author', recipient=OWNER, task_id='REV-02', kind='review'),
              dict(sender=OWNER, recipient='synthetic-author', task_id='REV-02', kind='review')]
    plan = dict(schema_version=1, run_id=run, input_version=version, max_message_bytes=8192,
                max_events=1 if name == 'budget' else 10, routes=routes)
    save(d / 'plan.json', plan)
    save(d / 'ownership.json', dict(owner=OWNER, effective_consumers_per_recipient=1,
          mode='trusted single-host synthetic local adapter', authorization_task_sha256=TASK_HASH,
          task_refs=['REV-02','REV-03'], refs_immutable=True, no_external_effects=True))
    box = mailbox(d)
    incoming = dict(event_id=run+'-seed', run_id=run, input_version=version, sender='synthetic-author',
         task_id='REV-02', kind='review', summary='Synthetic seed review evidence is ready',
         action='Read synthetic finding and request revision; do not scientifically close it', refs=[ref])
    publication = box.publish(incoming)
    log(d, 'seed_publish', event=incoming, result=publication, status=box.status(), inbox=box.inbox(OWNER))
    seq = publication['seq']
    outgoing = dict(event_id=run+'-revision-request', run_id=run, input_version=version, sender=OWNER,
         task_id='REV-02', kind='review', summary='SYNTHETIC-FINDING-001 requires revision',
         action='Author: revise uncertainty statement; original reviewer must later check original finding against old and new hashes', refs=[ref])
    receipt = dict(status='needs_revision', reason='SYNTHETIC-FINDING-001 is synthetic and remains open; request delivered before this receipt')
    save(d / 'intent.json', dict(run_id=run, input_version=version, recipient=OWNER, incoming_seq=seq,
         incoming_event=incoming, finding_id='SYNTHETIC-FINDING-001', original_artifact_sha256=ref['sha256'],
         action_idempotency_key=[run,incoming['event_id'],OWNER], outgoing=outgoing, receipt=receipt))
    if name == 'conflict':
        conflict = dict(status='rejected', reason='Synthetic pre-existing conflicting receipt: main AI reconciliation required')
        box.acknowledge(OWNER, seq, conflict)
        log(d, 'fixture_conflicting_receipt', seq=seq, receipt=conflict, status=box.status())
    host_plan = dict(schema_version='task-dag/v1', run_id=run, user_goal='Bounded local '+name+' scenario observation only',
         authorization_reference=TASK_HASH, tasks=[dict(task_id='REV-02', action='owned_local_consumer', owner=OWNER,
         done_when={'scope':'only local scenario logs recorded, no scientific acceptance'}, max_attempts=1,
         estimated_seconds=30, risk='low', depends_on=[])],
         supervision=dict(min_seconds=1,max_seconds=30,rationale='one synchronous owned local scenario; no service installed'))
    save(d / 'engine-plan.json', host_plan)
    store = Store(PRIVATE / (name+'-engine.sqlite')); store.create(host_plan)
    engine = Engine(store, {'owned_local_consumer':LocalHandler(d)}, authorize=authorized, lease_seconds=120)
    state = engine.tick(run, run+'-single-authorized-dispatch')
    save(d / 'engine-readback.json', store.snapshot(run))
    assert state['status'] == 'done', state
    final_status = box.status(); pending_consumer = box.inbox(OWNER); pending_author = box.inbox('synthetic-author')
    save(d / 'final-readback.json', dict(status=final_status, inbox_consumer=pending_consumer, inbox_responsibility=pending_author))
    with box.connect() as db:
        raw = {table:[dict(r) for r in db.execute('SELECT * FROM '+table)] for table in
               ('communication_plans','communication_events','communication_deliveries')}
    save(d / 'sqlite-readback.json', raw)
    if name == 'interruption':
        handled=read(d/'handled.json'); assert handled['publish']['duplicate'] is True
        assert len(raw['communication_events'])==2 and not pending_consumer and len(pending_author)==1
        assert next(r for r in final_status if r['seq']==seq)['receipt']==receipt
        outcome='transport_recovered; finding remains open'
    elif name == 'budget':
        assert len(raw['communication_events'])==1 and len(pending_consumer)==1
        assert final_status[0]['receipt'] is None
        assert 'budget exhausted' in read(d/'blocked.json')['error']
        outcome='unresolved budget; original remains pending, no request and no ACK'
    else:
        assert len(raw['communication_events'])==1 and final_status[0]['receipt']['status']=='rejected'
        assert not (d/'handled.json').exists()
        outcome='unresolved conflict; existing receipt preserved, no request publication'
    return dict(scenario=name, run_id=run, generated_incoming_seq=seq, observation='executed', outcome=outcome,
         events=len(raw['communication_events']), task_refs=['REV-02','REV-03'], scientific_finding='open/not evaluated')

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--child', type=Path); parser.add_argument('--token'); parser.add_argument('--idempotency-key'); parser.add_argument('--interrupt', action='store_true'); args=parser.parse_args()
    if args.child:
        plan=read(args.child/'engine-plan.json'); store=Store(PRIVATE/(args.child.name+'-engine.sqlite'))
        context=Context(store, plan['run_id'], 'REV-02', args.token, args.idempotency_key, time.time)
        return consume(args.child, context, args.interrupt)
    PRIVATE.mkdir(parents=True,exist_ok=True)
    candidate=read(INPUTS/'candidate.json')
    assert sha(REPO/'agent_runtime/communication.py') == sha(INPUTS/'communication.py') == candidate['runtime_sha256']
    assert sha(INPUTS/'candidate-workflow.md') == candidate['production_files']['workflows/agent_communication_workflow.md']
    save(OUT/'identity.json', dict(candidate=candidate, source_commit=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip(),
         python=sys.version, task_sha256=TASK_HASH, consumer_sha256=sha(OUT/'consumer.py'),
         runtime_sha256=sha(REPO/'agent_runtime/communication.py'), owned_mutable_db_directory=str(PRIVATE),
         read_only_repo=True, child_restart_budget=1, local_corrections=0))
    results=[]
    try:
        for name in ['interruption','budget','conflict']: results.append(setup(name))
    except BaseException:
        save(OUT/'unexpected-failure.json',dict(traceback=traceback.format_exc(),partial_results=results)); raise
    save(OUT/'results.json', dict(status='three bounded observations executed', scenarios=results, child_restarts=1,
         local_corrections=0, science_acceptance=False, model_session_restart=False, network=False,
         next_action='Main AI reconcile budget and receipt conflict separately. Responsibility author must actually handle request then original reviewer revalidate before any scientific closure.'))
    print(json.dumps(read(OUT/'results.json'),indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
