#!/usr/bin/env python3
"""Replay historical preparation with the existing pipeline; never invokes models.

First restore the preceding scaling archive using its restore.py. Supply that
directory as --history. The output must be a new scratch directory. Historical
inputs and rubric files are read only; source snapshot duplication stays scratch.
"""
import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--history', type=Path, required=True)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    # Import the pinned source rather than whichever working-tree version exists.
    source = subprocess.check_output(['git', '-C', str(args.repo), 'show',
                                      args.revision + ':scripts/agent_eval_pipeline.py'])
    pinned = args.out / 'pipeline.py'
    pinned.write_bytes(source)
    spec = importlib.util.spec_from_file_location('pinned_pipeline', pinned)
    pipeline = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pipeline)
    histories = ['writer-run', 'writer-corrected-run']
    cases = []
    for name in histories:
        old = args.history / name
        manifest = pipeline.prepare_run(args.repo, args.revision, args.out / name,
            old / 'tasks.json', old / 'rubric.json',
            old / 'cases/chain-writer/inputs', {'name': 'preparation-only', 'model': 'not-invoked'})
        _, errors = pipeline.verify_run(args.out / name)
        rows = list(csv.DictReader((old / 'cases/chain-writer/inputs/aggregate.csv').open()))
        directions = {r['workload']: ('parity' if float(r['baseline_median_ms']) == float(r['candidate_median_ms'])
                     else 'regression' if float(r['candidate_median_ms']) > float(r['baseline_median_ms'])
                     else 'improvement') for r in rows}
        cases.append({'id': name, 'preparation_accepted': True,
            'integrity_errors': errors, 'actual_directions': directions,
            'rubric': json.loads((old / 'rubric.json').read_text())['criteria']['chain-writer'],
            'task_hash': manifest['tasks_hash'], 'rubric_hash': manifest['rubric_hash'],
            'input_hashes': manifest['cases']['chain-writer']['input_hashes']})
    old = args.history / 'run'
    task = next(c for c in json.loads((old / 'tasks.json').read_text())['cases']
                if c['id'] == 'smoke-main-general')
    old_criteria = json.loads((old / 'rubric.json').read_text())['criteria']['smoke-main-general']
    for name, criteria in [('settlement-original', old_criteria), ('settlement-corrected',
        ['each roommate owes30; C transfers24 to user and6 to B or equivalent correct settlement', old_criteria[1]])]:
        tasks, rubric = args.out / (name + '-tasks.json'), args.out / (name + '-rubric.json')
        tasks.write_text(json.dumps({'cases': [task]}))
        rubric.write_text(json.dumps({'criteria': {'smoke-main-general': criteria}}))
        manifest = pipeline.prepare_run(args.repo, args.revision, args.out / name,
            tasks, rubric, adapter={'name': 'preparation-only', 'model': 'not-invoked'})
        _, errors = pipeline.verify_run(args.out / name)
        # Independent net-cost calculation for the exact historical example.
        # This is a factual probe, not a general natural-language rubric parser.
        net = [54, 36, 0]
        transfers = [(1, 0, 6), (2, 0, 24)] if name.endswith('original') else [(2, 0, 24), (2, 1, 6)]
        for payer, receiver, amount in transfers:
            net[payer] += amount
            net[receiver] -= amount
        cases.append({'id': name, 'preparation_accepted': True, 'integrity_errors': errors,
            'illustrative_net_costs': net, 'equal_split_satisfied': net == [30, 30, 30],
            'task_hash': manifest['tasks_hash'], 'rubric_hash': manifest['rubric_hash'],
            'note': 'Original criterion permits an equivalent correct settlement; the illustrative example is defective, not every allowed answer.'})
    result = {'baseline': args.revision, 'pipeline_sha256': sha(pinned), 'probe_sha256': sha(Path(__file__)),
        'scope': 'Program preparation replay only; no model calls or semantic grades.',
        'cases': cases, 'prepared': len(cases),
        'contradictory_material_prepared': 2, 'corrected_material_prepared': 2,
        'interpretation': 'Byte integrity is necessary but does not prove factual grading coherence.'}
    (args.out / 'baseline.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'prepared': len(cases), 'integrity_errors': sum(len(c['integrity_errors']) for c in cases),
                      'model_invocations': 0, 'report': str(args.out / 'baseline.json')}))


if __name__ == '__main__':
    main()
