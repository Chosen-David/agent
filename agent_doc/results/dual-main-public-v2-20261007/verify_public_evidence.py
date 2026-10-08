"""Public-files-only integrity/structure/arithmetic checks, not host authentication.

This does not recreate or read private raw logs, model/controller captures or
operational receipts. Historical testcase outcomes are derived published views;
independent archival equivalence review is separate from this content checker.
"""
import hashlib
import json
from pathlib import Path
import runpy


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local(root, name):
    p = Path(name)
    if p.is_absolute() or '..' in p.parts or any(part.startswith('.') for part in p.parts):
        raise ValueError('public artifact path must be project-relative')
    out = root / p
    if any(x.is_symlink() for x in (out,*out.parents) if x != root) or not out.resolve().is_relative_to(root.resolve()):
        raise ValueError('public artifact must stay within its public root')
    return out


def load(path):
    return json.loads(path.read_text())


def verify(base=None):
    base = Path(base) if base is not None else Path(__file__).resolve().parent
    repo = base.parents[2]
    manifest = load(base/'manifest.json')
    for name, expected in manifest['public_files'].items():
        if sha(local(base,name)) != expected:
            raise ValueError('public artifact changed: '+name)
    source = load(base/'source-freeze.json')
    for name, expected in source['files'].items():
        if sha(local(repo,name)) != expected:
            raise ValueError('source changed: '+name)
    derivations = load(base/'history/derivations.json')
    reviewed = 0
    failures = 0
    for row in derivations['views']:
        path = local(base,row['public_view']);view=load(path)
        if sha(path) != row['public_view_sha256'] or view['original_file_sha256'] != row['original_file_sha256']:
            raise ValueError('derived-view identity mismatch')
        if 'original_plan_sha256' in row and view.get('original_plan_sha256') != row['original_plan_sha256']:
            raise ValueError('historical original plan identity mismatch')
        if row['kind'] in ('non-executable-plan-view','complete-historical-review') and view.get('historical_only') is not True:
            raise ValueError('historical view cannot become a current authorization')
        if row['kind'] == 'non-executable-plan-view':
            if view.get('executable') is not False or view['schema_version'] != 'non-executable-plan-view/v1':
                raise ValueError('historical redacted view is not an executable approved DAG')
        elif row['kind'] == 'complete-historical-review':
            if view.get('executable') is not False or not view['review']['full_review']:
                raise ValueError('complete historical feedback and non-authority marker required')
            reviewed += 1
        elif row['kind'] == 'structured-log-view':
            for item in view['case_outcomes']:
                if item['status'] not in ('ok','FAIL','ERROR','skipped'):
                    raise ValueError('unknown recorded test status')
                parts=item['test_id'].split('.')
                if len(parts)>1 and parts[-1] == parts[-2]:
                    raise ValueError('invented duplicated testcase method identity')
            failures += len(view['failure_headers'])
    recorded_checks = {}
    for suite, count, skipped in (('repository',783,1),('reader',3,0)):
        check = load(base/'checks'/(suite+'.json'))
        statuses = [row['status'] for row in check['case_outcomes']]
        if (check['tests_run'] != count or len(statuses) != count or
                check['failures'] != 0 or check['errors'] != 0 or check['skipped'] != skipped or
                check['successful'] is not True or statuses.count('skipped') != skipped or
                statuses.count('passed') != count-skipped):
            raise ValueError('current structured check counts/outcomes disagree')
        recorded_checks[suite] = {'recorded_tests':count,'recorded_passed':count-skipped,'recorded_skipped':skipped}
    data=base/'data/finite-cpu';provenance=load(data/'provenance.json')
    for row in provenance['artifacts']:
        if sha(local(base,row['public_artifact'])) != row['public_file_sha256'] or row['original_file_sha256'] != row['public_file_sha256']:
            raise ValueError('historical public numeric/code bytes changed')
    values=load(data/'inputs.json')['n'];repeats=load(data/'config.json')['repeats']
    rows=load(data/'raw.json')['samples'];pairs=[(r['n'],r['repeat']) for r in rows]
    if len(rows)!=15 or len(set(pairs))!=15 or set(pairs)!={(n,r) for n in values for r in range(repeats)}:
        raise ValueError('finite sample IDs incomplete or duplicated')
    expected=lambda n:n*(n-1)*(2*n-1)//6
    if any(type(r['value']) is not int or r['value']!=expected(r['n']) for r in rows):
        raise ValueError('finite arithmetic mismatch')
    if load(data/'output.json')['sum'] != sum(r['value'] for r in rows):
        raise ValueError('finite aggregate mismatch')
    if sum(r['value'] for r in rows)!=6603:
        raise ValueError('unexpected finite aggregate')
    measure=runpy.run_path(str(data/'square_sum.py'))['measure']
    if any(measure(n)!=expected(n) for n in values):
        raise ValueError('published algorithm differs from closed-form values')
    rejected=0
    for value in (-1,1.5,'2',True):
        try:measure(value)
        except ValueError:rejected+=1
    if rejected!=4:
        raise ValueError('published input boundary changed')
    return {'status':'public-content-and-finite-data-consistent','source_files':len(source['files']),
            'historical_reviews':reviewed,'preserved_failure_headers':failures,'finite_samples':15,'finite_sum':6603,
            'authority':'content consistency only; no host/model identity, current scientific generality or publication permission',
            'current_recorded_checks':recorded_checks,'private_files_read':0,'model_calls':0}


if __name__ == '__main__':
    try:
        print(json.dumps(verify(),indent=2))
    except Exception as exc:
        # Keep CLI diagnostics structural; do not serialize private host paths.
        print(json.dumps({'status':'failed','error_type':type(exc).__name__,'detail':'public content check failed'}))
        raise SystemExit(1)
