"""Inspect two host-assigned research worktrees before admitting parallel writes."""
import argparse
import json
from pathlib import Path
import subprocess


def git(tree, *args):
    return subprocess.check_output(['git','-C',str(tree),*args],text=True).strip()


def inspect_workers(workers):
    if len(workers) not in (1,2):
        raise ValueError('expected one or two active production slots')
    records=[]
    for worker in workers:
        tree=Path(worker['worktree']).resolve(strict=True)
        output=Path(worker['output']).resolve()
        branch=git(tree,'symbolic-ref','--short','HEAD')
        if tree!=Path(git(tree,'rev-parse','--show-toplevel')).resolve() or branch!=worker['branch']:
            raise ValueError('worktree root or branch differs from task assignment')
        record=dict(worker,worktree=str(tree),output=str(output),head=git(tree,'rev-parse','HEAD'))
        for prior in records:
            if any(prior[k]==record[k] for k in ('identity','task','branch')):
                raise ValueError('duplicate worker, task or branch')
            for a in (tree,output):
                for b in (Path(prior['worktree']),Path(prior['output'])):
                    if a.is_relative_to(b) or b.is_relative_to(a):
                        raise ValueError('overlapping producer worktree or output ownership')
        records.append(record)
    return records


class Admission:
    """Shared host Store for cooperating launchers. Ambiguous claims stay reserved."""

    def __init__(self, store=None):
        if store is None:
            from .core import Store
            store = Store(Path.home() / ".local/share/chosen-agent-experiments/research.sqlite")
        self.store = store
        with store.transaction() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS agent_claims (
                identity TEXT PRIMARY KEY, parent TEXT, project TEXT NOT NULL,
                cycle TEXT NOT NULL, binding TEXT NOT NULL, reserved INTEGER NOT NULL,
                used INTEGER, released INTEGER NOT NULL DEFAULT 0)""")

            if 'outcome' not in {r['name'] for r in db.execute('PRAGMA table_info(agent_claims)')}:
                db.execute('ALTER TABLE agent_claims ADD COLUMN outcome TEXT')

    def reserve(self, worker, *, parent, project, cycle, tokens, budget, final_reserve,
                max_agents=2, max_spawns=4, mode="adaptive", cycle_budget=None, final=False):
        """Limits come from the trusted launcher, never from the worker packet."""
        limits = (tokens, budget, final_reserve, max_agents, max_spawns)
        if any(type(n) is not int or n < 0 for n in limits) or not max_agents:
            raise ValueError('invalid admission limits')
        if mode not in ('single', 'adaptive', 'manual'):
            raise ValueError('unknown scheduling mode')
        if parent is not None and (mode == 'single' or final):
            raise ValueError('worker outside authorized scheduling policy')
        if cycle_budget is not None and (type(cycle_budget) is not int or cycle_budget < 0):
            raise ValueError('invalid cycle budget')
        record = inspect_workers([worker])[0]
        binding = json.dumps(record, sort_keys=True)
        identity = record['identity']
        with self.store.transaction() as db:
            prior = db.execute('SELECT * FROM agent_claims WHERE identity=?', (identity,)).fetchone()
            if prior:
                if (prior['project'], prior['cycle'], prior['parent'], prior['binding'],
                    prior['reserved'], prior['released']) != (project, cycle, parent, binding, tokens, 0):
                    raise ValueError('identity already used with another claim')
                return False
            active = db.execute('SELECT * FROM agent_claims WHERE released=0').fetchall()
            if len(active) >= max_agents:
                raise ValueError('managed host agent limit reached')
            if parent is not None:
                if not any(r['identity'] == parent and r['parent'] is None and
                           r['project'] == project and r['cycle'] == cycle for r in active):
                    raise ValueError('active primary in this cycle required')
                count = db.execute('SELECT COUNT(*) FROM agent_claims WHERE project=? AND cycle=? AND parent IS NOT NULL',
                                   (project, cycle)).fetchone()[0]
                if count >= max_spawns:
                    raise ValueError('cycle worker dispatch limit reached')
            for row in active:
                inspect_workers([json.loads(row['binding']), record])
            committed = db.execute('SELECT COALESCE(SUM(COALESCE(used,reserved)),0) FROM agent_claims WHERE project=?',
                                   (project,)).fetchone()[0]
            if parent is not None and committed >= budget * 0.8:
                raise ValueError('soft budget reached; finish active work')
            protected = 0 if final else final_reserve
            if committed + tokens + protected > budget:
                raise ValueError('project budget or final reserve exhausted')
            if cycle_budget is not None:
                cycle_used = db.execute(
                    'SELECT COALESCE(SUM(COALESCE(used,reserved)),0) FROM agent_claims WHERE project=? AND cycle=?',
                    (project, cycle)).fetchone()[0]
                if cycle_used + tokens + protected > cycle_budget:
                    raise ValueError('cycle budget or final reserve exhausted')
            db.execute('INSERT INTO agent_claims(identity,parent,project,cycle,binding,reserved) VALUES(?,?,?,?,?,?)',
                       (identity, parent, project, cycle, binding, tokens))
            return True

    def settle(self, identity, used, *, outcome="released"):
        """Unknown final usage conservatively retains the full reservation."""
        if outcome not in ('released', 'accepted', 'insufficient'):
            raise ValueError('invalid terminal outcome')
        if used is not None and (type(used) is not int or used < 0):
            raise ValueError('invalid usage')
        with self.store.transaction() as db:
            row = db.execute('SELECT released,used,outcome FROM agent_claims WHERE identity=?', (identity,)).fetchone()
            if not row or row['released'] and (row['used'] != used or (row['outcome'] or 'released') != outcome):
                raise ValueError('unknown or conflicting settlement')
            db.execute('UPDATE agent_claims SET released=1,used=?,outcome=? WHERE identity=?', (used, outcome, identity))


def run_native_worker(admission, worker, *, codex, project, cycle, primary,
                      budget, tokens, final_reserve, root, basis, request, objective, validate_output):
    """Run from the durable host, with an already admitted primary and trusted bindings."""
    from .handoff_basis import basis_context

    if not callable(validate_output):
        raise ValueError('host artifact validator required')
    packet = basis_context(root, basis, request)
    prompt = json.dumps({'task': worker['task'], 'objective': objective,
                         'worktree': worker['worktree'], 'output': worker['output'],
                         'basis': json.loads(packet['payload'])}, ensure_ascii=False)
    output = Path(worker['output']).resolve()
    tree = Path(worker['worktree']).resolve(strict=True)
    if not output.is_relative_to(tree):
        raise ValueError('native worker output must be inside its authorized worktree')
    from . import worker_preflight
    worker_preflight.check(admission.store, codex, tree, output,
                           set(worker.get('required_capabilities', ())))
    if not admission.reserve(worker, parent=primary, project=project, cycle=cycle,
                             budget=budget, tokens=tokens, final_reserve=final_reserve):
        raise ValueError('existing invocation requires reconciliation')
    output.mkdir(parents=True, exist_ok=True)
    with (output / 'codex-events.jsonl').open('x') as events:
        result = subprocess.run([str(codex), *worker_preflight.CONFIG, '-a', 'never',
                                 'exec', '--json', '--sandbox', worker_preflight.MODE,
                                 '--disable', 'multi_agent', '--disable', 'multi_agent_v2',
                                 '-C', str(tree), '-'],
                                input=prompt, text=True, stdout=events, cwd=tree)
    if result.returncode == 0:
        from .token_usage import worker_turn_usage
        with (output / 'codex-events.jsonl').open() as evidence:
            try:
                used = worker_turn_usage(evidence)['total_tokens']
            except ValueError:
                used = None
        accepted = validate_output(output)
        admission.settle(worker['identity'], used, outcome='accepted' if accepted else 'insufficient')
        if not accepted:
            raise ValueError('native turn completed without an accepted artifact')
    return result.returncode


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('assignments',type=Path)
    args=p.parse_args()
    print(json.dumps(inspect_workers(json.loads(args.assignments.read_bytes())),ensure_ascii=False,indent=2))
