"""Follow a bounded series of registered attempts and enqueue one independent review.

A trusted host supplies the intended request and review template at initial binding.
Reconciliation only reads training claims. It never launches or terminates a trainer.
"""
import argparse
import json
from pathlib import Path
import time

from .experiment_catalog import fingerprint
from .research_handoff import ResearchHandoff


def identity(request):
    value = {key: request[key] for key in ('family', 'goal', 'scientific_context')}
    for key in ('benchmark_protocol', 'input_artifact', 'bound_recovery'):
        if key in request:
            value[key] = request[key]
    return value


def snapshot(db, claim, owner):
    row = db.execute('SELECT status, rc, request FROM training_claims WHERE claim=? AND owner=?',
                     (claim, owner)).fetchone()
    if row:
        return row['status'], row['rc'], json.loads(row['request'])
    # A legitimate checkpoint recovery can rotate the owner of the same claim.
    history = db.execute('SELECT previous FROM training_attempt_history WHERE claim=? ORDER BY sequence DESC', (claim,))
    for entry, in history:
        prior = json.loads(entry)
        if prior['owner'] == owner:
            return prior['status'], prior['rc'], json.loads(prior['request'])
    raise ValueError('exact claim/owner receipt unavailable')


def terminal_failure(status, rc):
    return status == 'launch-failed' or (status == 'failed' and type(rc) is int and rc != 0)


class TrainingSupervisor:
    def __init__(self, database):
        self.reviews = ResearchHandoff(database)
        self.db = self.reviews.db
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS logical_training_tasks(
                task TEXT PRIMARY KEY, contract TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS logical_training_attempts(
                task TEXT NOT NULL, seq INTEGER NOT NULL, claim TEXT NOT NULL, owner TEXT NOT NULL,
                evidence TEXT NOT NULL, reason TEXT NOT NULL, bound REAL NOT NULL,
                PRIMARY KEY(task,seq), UNIQUE(task,claim,owner));
        """)

    def bind(self, task, claim, owner, *, request=None, review=None, evidence_relative=None,
             max_attempts=None, after_owner=None, reason=None):
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            existing = self.db.execute('SELECT contract FROM logical_training_tasks WHERE task=?', (task,)).fetchone()
            if after_owner is None:
                ResearchHandoff.validate(review)
                if not task.strip() or review['task'] != task or review['evidence'] != '{attempt_evidence}':
                    raise ValueError('review must bind this task and the {attempt_evidence} placeholder')
                relative = Path(evidence_relative)
                if relative.is_absolute() or '..' in relative.parts:
                    raise ValueError('evidence path must be relative to the managed attempt')
                if type(max_attempts) is not int or not 1 <= max_attempts <= 20:
                    raise ValueError('invalid total attempt limit')
                contract = dict(expected=identity(request), review=review, evidence=str(relative), limit=max_attempts)
                if existing and contract != json.loads(existing[0]):
                    raise ValueError('logical task already bound to a different contract')
                if not existing:
                    self.db.execute('INSERT INTO logical_training_tasks VALUES(?,?)',
                                    (task, json.dumps(contract, sort_keys=True)))
            else:
                if not existing or not reason or not reason.strip():
                    raise ValueError('successor needs an existing logical task and a reason')
                contract = json.loads(existing[0])
            latest = self.db.execute('SELECT * FROM logical_training_attempts WHERE task=? ORDER BY seq DESC LIMIT 1',
                                     (task,)).fetchone()
            if latest and (latest['claim'], latest['owner']) == (claim, owner):
                if after_owner is None and latest['seq'] != 1:
                    raise ValueError('task already advanced beyond original attempt')
                if after_owner is not None:
                    prior = self.db.execute('SELECT owner FROM logical_training_attempts WHERE task=? AND seq=?',
                                            (task, latest['seq'] - 1)).fetchone()
                    if not prior or prior[0] != after_owner or reason != latest['reason']:
                        raise ValueError('successor replay changed predecessor or reason')
                return latest['seq']
            if latest:
                if latest['owner'] != after_owner:
                    raise ValueError('predecessor changed')
                status, rc, _ = snapshot(self.db, latest['claim'], latest['owner'])
                if not terminal_failure(status, rc):
                    raise ValueError('previous attempt has no terminal failure receipt')
            seq = latest['seq'] + 1 if latest else 1
            if seq > contract['limit']:
                raise ValueError('attempt budget exhausted')
            status, rc, actual = snapshot(self.db, claim, owner)
            expected = contract['expected']
            if identity(actual) != expected:
                # The first attempt may be the documented misconfigured failure being repaired.
                if (seq != 1 or not terminal_failure(status, rc) or actual['family'] != expected['family']
                        or actual['goal'] != expected['goal']
                        or actual['scientific_context']['scope'] != expected['scientific_context']['scope']):
                    raise ValueError('attempt differs from intended scientific contract')
            plan = json.loads(Path(actual['artifact_plan']).read_text())
            output = Path(plan['physical_output'])
            if not output.is_absolute():
                raise ValueError('managed output must be absolute')
            evidence = (output / contract['evidence']).resolve()
            if not evidence.is_relative_to(output.resolve()):
                raise ValueError('evidence escaped managed physical output')
            self.db.execute('INSERT INTO logical_training_attempts VALUES(?,?,?,?,?,?,?)',
                            (task,seq,claim,owner,str(evidence),reason or 'initial binding',time.time()))
            return seq

    def follow_retry(self, task, *, remediate=None):
        """Reconcile a registered successor or dispatch a trusted idempotent remediation DAG.

        A successor declares retry_of={task, claim, owner} in its training request.
        Only its original logical task can adopt it, within the original attempt budget.
        The host callback must use the supplied event key for single-flight dispatch.
        """
        result = self.tick(task)
        if result['state'] != 'retry-needed':
            return result
        predecessor = {field: result[field] for field in ('task', 'claim', 'owner')}

        def successors():
            return self.db.execute("""SELECT claim,owner FROM training_claims
                WHERE json_extract(request,'$.retry_of.task')=?
                  AND json_extract(request,'$.retry_of.claim')=?
                  AND json_extract(request,'$.retry_of.owner')=?""",
                (task, result['claim'], result['owner'])).fetchall()

        attempts = successors()
        if not attempts and remediate is not None:
            remediate(predecessor.copy(), 'training-remediation:' + fingerprint(predecessor))
            attempts = successors()
        if len(attempts) > 1:
            raise ValueError('ambiguous registered successors require reconciliation')
        if attempts:
            claim, owner = attempts[0]
            self.bind(task, claim, owner, after_owner=result['owner'], reason='registered retry lineage')
            return self.tick(task)
        return result

    def tick(self, task):
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            row = self.db.execute("""SELECT a.*, t.contract FROM logical_training_attempts a
                JOIN logical_training_tasks t ON a.task=t.task WHERE a.task=? ORDER BY seq DESC LIMIT 1""",
                (task,)).fetchone()
            if not row:
                raise ValueError('unknown logical training task')
            contract = json.loads(row['contract'])
            status, rc, request = snapshot(self.db, row['claim'], row['owner'])
            result = dict(task=task, attempt=row['seq'], claim=row['claim'], owner=row['owner'],
                          evidence=row['evidence'], training_status=status, rc=rc,
                          expected_sha256=fingerprint(contract['expected']))
            if terminal_failure(status, rc):
                state = 'retry-needed' if row['seq'] < contract['limit'] else 'attempts-exhausted'
            elif status == 'awaiting-validation' and rc == 0:
                if identity(request) != contract['expected'] or not Path(row['evidence']).exists():
                    state = 'blocked-evidence'
                else:
                    spec = dict(contract['review'], evidence=row['evidence'])
                    self.reviews.insert(self.db, spec, time.time())
                    state = 'review-enqueued'
            elif status in ('claimed', 'running') and rc is None:
                state = 'waiting-attempt'
            else:
                state = 'blocked-unknown'
            return dict(result, state=state)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('database', type=Path)
    ops = cli.add_subparsers(dest='op', required=True)
    for name in ('bind','rebind','tick','watch','follow-retry'):
        op = ops.add_parser(name)
        op.add_argument('task')
        if name == 'watch':
            op.add_argument('--interval', type=int, default=20)
            op.add_argument('--retry-wait', type=int, default=300)
            op.add_argument('--timeout', type=int, default=86400)
        if name in ('bind','rebind'):
            op.add_argument('claim')
            op.add_argument('owner')
        if name == 'rebind':
            op.add_argument('--after-owner', required=True)
            op.add_argument('--reason', required=True)
        if name == 'bind':
            op.add_argument('--expected-request', type=Path, required=True)
            op.add_argument('--review', type=Path, required=True)
            op.add_argument('--evidence-relative', required=True)
            op.add_argument('--max-attempts', type=int, required=True)
    args = cli.parse_args()
    if not args.database.is_file():
        cli.error('existing training claim registry required')
    supervisor = TrainingSupervisor(args.database)
    try:
        if args.op == 'bind':
            seq = supervisor.bind(args.task,args.claim,args.owner,request=json.loads(args.expected_request.read_text()),
                                  review=json.loads(args.review.read_text()),evidence_relative=args.evidence_relative,
                                  max_attempts=args.max_attempts)
            print(json.dumps(dict(attempt=seq)))
        elif args.op == 'rebind':
            seq = supervisor.bind(args.task,args.claim,args.owner,after_owner=args.after_owner,reason=args.reason)
            print(json.dumps(dict(attempt=seq)))
        else:
            if args.op in ('tick', 'follow-retry'):
                result = (supervisor.follow_retry(args.task) if args.op == 'follow-retry'
                          else supervisor.tick(args.task))
                print(json.dumps(result), flush=True)
                return 0 if result['state'] in ('waiting-attempt','review-enqueued') else 75
            if min(args.interval, args.timeout) < 1 or args.retry_wait < 0:
                cli.error('invalid watch bounds')
            deadline = time.monotonic() + args.timeout
            retry_deadline = None
            previous_attempt = None
            while True:
                result = supervisor.follow_retry(args.task)
                print(json.dumps(result), flush=True)
                if result['state'] == 'review-enqueued':
                    return 0
                if result['state'] not in ('waiting-attempt', 'retry-needed'):
                    return 75
                now = time.monotonic()
                if previous_attempt != result['attempt']:
                    retry_deadline = None
                    previous_attempt = result['attempt']
                if result['state'] == 'retry-needed' and retry_deadline is None:
                    retry_deadline = now + args.retry_wait
                left = min(deadline, retry_deadline if retry_deadline is not None else deadline) - now
                if left <= 0:
                    print(json.dumps(dict(task=args.task, state='watch-deadline', last=result['state'])), flush=True)
                    return 75
                time.sleep(min(args.interval, left))
    finally:
        supervisor.db.close()


if __name__ == '__main__':
    raise SystemExit(main())
