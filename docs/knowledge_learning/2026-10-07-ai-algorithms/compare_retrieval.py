#!/usr/bin/env python3
"""Replay unchanged retrieval catalogs on two explicit corpora, preserving failures."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=False)
    suites = [('original', 'queries.json'), ('round2', 'round2-queries.json'),
              ('morphology', 'morphology-queries.json'), ('engineering', 'engineering-queries.json')]
    results, regressions = [], []
    for suite, filename in suites:
        cases = a.repo / 'evals/knowledge' / filename
        case_hash = sha(cases)
        runs = {}
        for label, corpus in [('baseline', a.baseline), ('candidate', a.candidate)]:
            output = a.out / f'{suite}-{label}.json'
            cmd = [sys.executable, str(a.repo/'scripts/eval_knowledge.py'), '--root', str(corpus),
                   '--cases', str(cases), '--output', str(output)]
            cp = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                env={**os.environ, 'PYTHONDONTWRITEBYTECODE':'1'})
            (a.out / f'{suite}-{label}.log').write_text(cp.stdout)
            runs[label] = {'data': json.loads(output.read_text()), 'command': cmd, 'exit_code': cp.returncode}
        assert sha(cases) == case_hash
        summary = {'suite': suite, 'query_sha256': case_hash, 'runs': {
            k: {x: v[x] for x in ['command','exit_code']} for k,v in runs.items()}, 'backends': {}}
        for backend in ['files','sqlite']:
            before = runs['baseline']['data']['backends'][backend]
            after = runs['candidate']['data']['backends'][backend]
            assert len(before['queries']) == len(after['queries'])
            rows = []
            for b, c in zip(before['queries'], after['queries']):
                assert (b['case'],b['query'],b['expected']) == (c['case'],c['query'],c['expected'])
                worse = [key for key in ['recall_at_3','context_recall','reciprocal_rank']
                         if b[key] is not None and c[key] < b[key]]
                if b['no_hit_correct'] is True and c['no_hit_correct'] is not True:
                    worse.append('no_hit_correct')
                row = {'case':b['case'], 'baseline': b, 'candidate':c, 'regressed_metrics':worse}
                rows.append(row)
                if worse: regressions.append({'suite':suite,'backend':backend,**row})
            summary['backends'][backend] = {
                'baseline': {k:v for k,v in before.items() if k.startswith('mean_')},
                'candidate': {k:v for k,v in after.items() if k.startswith('mean_')}, 'queries':rows}
        results.append(summary)
    out = {'schema_version':1, 'scope':'Development/regression; same queries, gold, engines and context budgets. Baseline failures retained, not counted as candidate regressions.',
           'no_new_regressions':not regressions,'regressions':regressions,'suites':results,
           'script_sha256':sha(Path(__file__)), 'eval_script_sha256':sha(a.repo/'scripts/eval_knowledge.py')}
    (a.out/'comparison.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'no_new_regressions':not regressions,'regression_pairs':len(regressions),'out':str(a.out)}))
    return 0 if not regressions else 1

if __name__ == '__main__':
    raise SystemExit(main())
