#!/usr/bin/env python3
"""Deterministic differential validator cases; preserves every raw decision.
Case generation seed and script hash bind inputs without storing fixture blobs.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import tempfile


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    old, new = load('baseline', args.baseline), load('candidate', args.candidate)
    rng = random.Random(1807241)
    rows = []
    with tempfile.TemporaryDirectory(prefix='handoff-decisions-') as directory:
        root = Path(directory)
        (root / 'data').write_bytes(b'fixed-data')
        base = dict(schema_version=1, run_id='differential', role='code-organization', input_version='fixed',
                    status='completed', limitations=[], artifacts=[dict(id='data', path='data',
                    sha256=hashlib.sha256(b'fixed-data').hexdigest())],
                    checks=[dict(criterion='fixture', status='pass', artifact_ids=['data'])], tasks=[])
        for index in range(360):
            record = copy.deepcopy(base)
            n = rng.randint(0, 24)
            nodes = [str(i) for i in range(n)]
            record['tasks'] = [dict(task_id=node, status='done', evidence=['data'],
                                   depends_on=[dep for dep in (nodes[:i] if index % 2 else nodes) if rng.random() < .1])
                               for i, node in enumerate(nodes)]
            request = dict(schema_version=1, input_version='fixed', tasks=[dict(task_id=node) for node in nodes])
            variant = index % 12
            if record['tasks']:
                task = rng.choice(record['tasks'])
                if variant == 0:
                    task['depends_on'] += ['unknown', 'unknown']
                elif variant == 1 and task['depends_on']:
                    task['depends_on'] *= 3
                elif variant == 2:
                    task['depends_on'] = {'invalid': 'type'}
                elif variant == 3:
                    task['status'] = 'skipped'
                    task['reason'] = 'producer says skip'
                elif variant == 4:
                    task['evidence'] = ['missing']
                elif variant == 5:
                    record['tasks'].append(copy.deepcopy(task))
                elif variant == 6:
                    record['tasks'].pop()
                elif variant == 7:
                    record['status'] = 'partial'
                    record['limitations'] = ['remaining work']
            if variant == 8:
                request['input_version'] = 'changed'
            elif variant == 9:
                record['artifacts'][0]['sha256'] = 'mismatch'
            elif variant == 10:
                record['artifacts'][0]['path'] = '../escape'
            elif variant == 11:
                record['checks'][0]['status'] = 'not_run'
            before = sorted(old.validate(record, root, True, consumer_request=request))
            after = sorted(new.validate(record, root, True, consumer_request=request))
            input_sha = hashlib.sha256(json.dumps([record, request], sort_keys=True).encode()).hexdigest()
            rows.append(dict(case=index, input_sha256=input_sha, before_errors=before, after_errors=after,
                             identical=before == after))
        # Actual byte hashing differential, with empty/chunk boundary/multi-chunk inputs.
        for size in (0, 1, 1048575, 1048576, 1048593, 3145737):
            content = rng.randbytes(size)
            (root / 'data').write_bytes(content)
            record = copy.deepcopy(base)
            record['artifacts'][0]['sha256'] = hashlib.sha256(content).hexdigest()
            before = old.validate(record, root)
            after = new.validate(record, root)
            rows.append(dict(case='file-' + str(size), input_sha256=record['artifacts'][0]['sha256'],
                             before_errors=before, after_errors=after, identical=before == after))
    result = dict(seed=1807241, baseline_sha256=hashlib.sha256(args.baseline.read_bytes()).hexdigest(),
                  candidate_sha256=hashlib.sha256(args.candidate.read_bytes()).hexdigest(),
                  generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  comparison='sorted diagnostic lists with multiplicity, not just accepted/rejected',
                  count=len(rows), identical=sum(row['identical'] for row in rows), rows=rows)
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'count': result['count'], 'identical': result['identical']}))
    return 0 if result['identical'] == result['count'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
