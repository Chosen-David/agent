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


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('assignments',type=Path)
    args=p.parse_args()
    print(json.dumps(inspect_workers(json.loads(args.assignments.read_bytes())),ensure_ascii=False,indent=2))
