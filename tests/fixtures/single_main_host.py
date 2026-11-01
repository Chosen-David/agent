"""Synthetic CPU host for CLI tests only; no model or platform identity claims."""
import hashlib
import hmac
from pathlib import Path
import time

from agent_runtime.plan_review import CHECKS, ReviewSession, canonical, sha


def build(root, store, run_id):
    root = Path(root)
    actor = {'invocation_id': 'cpu-main-' + run_id, 'context_id': 'cpu-main-context',
             'host_source': 'synthetic-local-fixture'}
    def signature(request, value):
        return hmac.new(b'PUBLIC-CPU-FIXTURE-NOT-A-SECRET',
                        canonical({'request': request, 'review': value}), hashlib.sha256).hexdigest()
    def planner(plan):
        with (root / 'host-calls.txt').open('a') as stream:
            stream.write('planner\n')
        return actor
    def self_check(request, plan, previous):
        with (root / 'host-calls.txt').open('a') as stream:
            stream.write('self-check\n')
        value = {'full_review': 'Synthetic local self-check; no model was called.',
                 'verdict': {'decision': 'approve', 'summary': 'Finite CPU fixture only', 'findings': [],
                             'checks': {key: {'status': 'pass', 'reason': 'CPU fixture ' + key} for key in CHECKS}}}
        return {'review': value, 'proof': signature(request, value)}
    def authenticate(request, value, proof):
        if not isinstance(proof, str) or not hmac.compare_digest(proof, signature(request, value)):
            return None
        return {'request_sha256': sha(request), 'review_sha256': sha(value),
                'planner': actor, 'reviewer': actor, 'fresh_context': False,
                'single_main': True, 'budget_valid': time.time() <= request['deadline']}
    session = ReviewSession(root, 'logical-T1', planner_identity=planner, reviewer=self_check,
                            authenticate=authenticate, max_seconds=90, single_main=True)
    return {'plan_review_session': session}
