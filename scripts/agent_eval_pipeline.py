#!/usr/bin/env python3
"""Pinned, host-driven evaluation records. This module does not invoke models."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_ROOTS = {'plugins', 'prompts', 'workflows', 'templates', 'config', 'agent_runtime'}
SNAPSHOT_DEPENDENCIES = {'docs/handoff_validation.md', 'docs/backend_handoff.md',
                         'docs/external_projects.md', 'scripts/validate_handoff.py',
                         'scripts/discover_backends.py', 'AGENTS.md',
                         'scripts/paper_exemplar_checks.py', 'scripts/validate_paper_delivery.py',
                         'scripts/data_visualization_checks.py',
                         'docs/task_supervisor_validation.md', 'docs/experiment_execution_upgrade.md'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def object_record(value):
    if not isinstance(value, dict):
        raise ValueError('JSON object required')
    return value


def write(path, value):
    with Path(path).open('xb') as stream:
        stream.write(encoded(value))


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def safe_relative(value):
    if not isinstance(value, str) or not value or '\\' in value:
        raise ValueError('invalid relative path')
    path = PurePosixPath(value)
    if path.is_absolute() or any(p in ('..', '.') for p in value.split('/')):
        raise ValueError('path escapes permitted root')
    return path


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', value):
        raise ValueError('invalid case identifier')
    return value


def hashes(directory):
    directory = Path(directory)
    if directory.is_symlink():
        raise ValueError('symlink directory forbidden')
    result = {}
    for path in sorted(directory.rglob('*')):
        if path.is_symlink():
            raise ValueError('symlink artifact forbidden')
        if path.is_file():
            result[path.relative_to(directory).as_posix()] = digest(path.read_bytes())
    return result


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.PIPE)


def prepare_run(repo, revision, out, tasks=None, rubric=None, fixture_root=None, adapter=None):
    """Freeze tracked skills and inputs; optional catalogs are explicit local files."""
    repo, out = Path(repo), Path(out)
    sha = git(repo, 'rev-parse', '--verify', revision + '^{commit}').decode().strip()
    blob = lambda name: git(repo, 'show', sha + ':' + name)
    task_data = object_record(read(tasks) if tasks else json.loads(blob('evals/tasks.json')))
    rubric_data = object_record(read(rubric) if rubric else json.loads(blob('evals/rubric.json')))
    cases, criteria = task_data.get('cases'), rubric_data.get('criteria')
    if not isinstance(cases, list) or not cases or not isinstance(criteria, dict):
        raise ValueError('nonempty cases and criteria required')
    seen, prepared = set(), []
    for original in cases:
        case = dict(object_record(original))
        cid = identifier(case.get('id'))
        if cid in seen:
            raise ValueError('duplicate case')
        seen.add(cid)
        checks = criteria.get(cid)
        if not isinstance(checks, list) or not checks or not all(map(nonempty, checks)) or len(set(checks)) != len(checks):
            raise ValueError('unique nonempty criteria required for every case')
        if not nonempty(case.get('prompt')) or not nonempty(case.get('role', cid)):
            raise ValueError('prompt and role required')
        skill = str(safe_relative(case.get('skill')))
        if skill.split('/')[0] not in SNAPSHOT_ROOTS:
            raise ValueError('skill must belong to frozen snapshot')
        fixtures = case.get('fixtures', [])
        if not isinstance(fixtures, list) or len(set(fixtures)) != len(fixtures):
            raise ValueError('unique fixture paths required')
        inputs = {}
        for name in fixtures:
            relative = str(safe_relative(name))
            if fixture_root:
                base = Path(fixture_root).resolve()
                source = base / relative
                if source.is_symlink() or not source.resolve().is_relative_to(base):
                    raise ValueError('fixture escapes explicit root')
                inputs[relative] = source.read_bytes()
            else:
                inputs[relative] = blob('evals/fixtures/' + relative)
        case.update(role=case.get('role', cid), skill=skill)
        prepared.append((case, inputs))
    if set(criteria) != seen:
        raise ValueError('criteria must match exact expected cases')
    snapshot = {}
    for entry in git(repo, 'ls-tree', '-rz', sha).split(b'\0'):
        if not entry:
            continue
        info, raw_name = entry.split(b'\t', 1)
        name = raw_name.decode()
        parts = safe_relative(name).parts
        if (parts[0] not in SNAPSHOT_ROOTS and name not in SNAPSHOT_DEPENDENCIES) or any(p in ('tests', 'evals', '__pycache__') for p in parts) or parts[-1] == 'rubric.json':
            continue
        if info.split()[0] not in (b'100644', b'100755'):
            raise ValueError('snapshot cannot contain symlinks or submodules')
        snapshot[name] = blob(name)
    if any(case['skill'] not in snapshot for case, _ in prepared):
        raise ValueError('skill absent from pinned snapshot')
    adapter = adapter or {'name': 'host', 'model': 'unspecified'}
    if not isinstance(adapter, dict) or not nonempty(adapter.get('name')):
        raise ValueError('adapter name required')
    adapter = dict(adapter)
    adapter.setdefault('max_attempts', 3)
    if type(adapter['max_attempts']) is not int or not 1 <= adapter['max_attempts'] <= 10:
        raise ValueError('max_attempts must be an integer between 1 and 10')
    out.mkdir(parents=True, exist_ok=False)
    for name, data in snapshot.items():
        target = out / 'snapshot' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    case_records = {}
    for case, inputs in prepared:
        directory = out / 'cases' / case['id']
        (directory / 'inputs').mkdir(parents=True)
        (directory / 'attempts').mkdir()
        (directory / 'task.txt').write_text(case['prompt'], encoding='utf-8')
        for name, data in inputs.items():
            target = directory / 'inputs' / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        case_records[case['id']] = {'role': case['role'], 'skill': case['skill'],
            'input_hashes': hashes(directory / 'inputs'), 'task_hash': digest((directory / 'task.txt').read_bytes())}
    write(out / 'rubric.json', rubric_data)
    manifest = {'schema_version': 1, 'revision': sha, 'adapter': adapter,
        'implementation_hash': digest(Path(__file__).read_bytes()),
        'expected_cases': [c['id'] for c, _ in prepared], 'cases': case_records,
        'snapshot_hashes': hashes(out / 'snapshot'), 'tasks_hash': digest(encoded(task_data)),
        'rubric_hash': digest((out / 'rubric.json').read_bytes()),
        'trust': 'Host supplied receipts are records, not cryptographic execution attestation.',
        'isolation': 'Separate task directories and reviewer instructions; shared filesystem is NOT a security sandbox.'}
    write(out / 'tasks.json', task_data)
    write(out / 'manifest.json', manifest)
    return manifest


def verify_run(run):
    run = Path(run)
    if run.is_symlink() or any(path.is_symlink() for path in run.rglob('*')):
        raise ValueError('symlink anywhere in run tree forbidden')
    manifest = object_record(read(run / 'manifest.json'))
    tasks = object_record(read(run / 'tasks.json')).get('cases')
    criteria = object_record(read(run / 'rubric.json')).get('criteria')
    if not isinstance(tasks, list) or not tasks or not isinstance(criteria, dict):
        raise ValueError('nonempty frozen tasks and rubric required')
    ids = [identifier(object_record(case).get('id')) for case in tasks]
    if len(set(ids)) != len(ids) or manifest.get('expected_cases') != ids or set(object_record(manifest.get('cases'))) != set(ids) or set(criteria) != set(ids):
        raise ValueError('manifest, tasks, and rubric case sets must match exactly')
    for checks in criteria.values():
        if not isinstance(checks, list) or not checks or not all(map(nonempty, checks)) or len(set(checks)) != len(checks):
            raise ValueError('invalid frozen criteria')
    errors = []
    if digest(Path(__file__).read_bytes()) != manifest['implementation_hash']:
        errors.append('pipeline implementation changed')
    if hashes(run / 'snapshot') != manifest['snapshot_hashes']:
        errors.append('snapshot changed')
    if digest((run / 'rubric.json').read_bytes()) != manifest['rubric_hash']:
        errors.append('rubric changed')
    if digest((run / 'tasks.json').read_bytes()) != manifest['tasks_hash']:
        errors.append('tasks changed')
    for cid in manifest['expected_cases']:
        expected, directory = manifest['cases'][cid], run / 'cases' / cid
        if hashes(directory / 'inputs') != expected['input_hashes']:
            errors.append(cid + ': inputs changed')
        if digest((directory / 'task.txt').read_bytes()) != expected['task_hash']:
            errors.append(cid + ': prompt changed')
    return manifest, errors


def context(run, case_id):
    run = Path(run)
    manifest, errors = verify_run(run)
    if errors:
        raise ValueError('; '.join(errors))
    if case_id not in manifest['expected_cases']:
        raise ValueError('unexpected case')
    return run, manifest, run / 'cases' / case_id / 'attempts'


def validate_receipt(receipt, kind, case_id, attempt, actor=None):
    receipt = object_record(receipt)
    for key in ('event_id', 'actor', 'adapter'):
        if not nonempty(receipt.get(key)):
            raise ValueError('receipt missing ' + key)
    if receipt.get('kind') != kind or receipt.get('case_id') != case_id or type(receipt.get('attempt')) is not int or receipt['attempt'] != attempt:
        raise ValueError('receipt does not match execution')
    if actor is not None and receipt['actor'] != actor:
        raise ValueError('receipt actor mismatch')
    return receipt


def receipt_record(receipt_path, kind, case_id, attempt, actor=None):
    return validate_receipt(read(receipt_path), kind, case_id, attempt, actor)


def event_ids(run):
    events = []
    for name in ('start.json', 'collection.json'):
        for path in (run / 'cases').glob('*/attempts/*/' + name):
            events.append(object_record(read(path))['receipt']['event_id'])
    if len(events) != len(set(events)):
        raise ValueError('duplicate host event')
    return events


def validate_start(run, manifest, directory, case_id):
    start = object_record(read(directory / 'start.json'))
    attempt = start.get('attempt')
    if type(attempt) is not int or attempt < 1 or directory.name != f'{attempt:04d}':
        raise ValueError('attempt must match numbered directory')
    if not nonempty(start.get('actor')):
        raise ValueError('worker actor required')
    validate_receipt(start.get('receipt'), 'start', case_id, attempt, start['actor'])
    if start['receipt']['adapter'] != manifest['adapter']['name'] or attempt > manifest['adapter']['max_attempts']:
        raise ValueError('start adapter or budget mismatch')
    if start.get('manifest_hash') != digest((run / 'manifest.json').read_bytes()):
        raise ValueError('manifest changed since dispatch')
    return start


def validate_collection(collection, start, case_id):
    collection = object_record(collection)
    receipt = validate_receipt(collection.get('receipt'), 'complete', case_id, start['attempt'], start['actor'])
    if collection.get('status') not in ('produced', 'infra_error', 'blocked') or collection['status'] != receipt.get('status'):
        raise ValueError('completion status mismatch')
    if receipt['adapter'] != start['receipt']['adapter'] or receipt['event_id'] == start['receipt']['event_id']:
        raise ValueError('completion adapter or event mismatch')
    object_record(collection.get('output_hashes'))
    return collection


def record_start(run, case_id, actor, receipt_path):
    run, manifest, attempts = context(run, case_id)
    if not nonempty(actor):
        raise ValueError('worker actor required')
    previous = sorted(attempts.iterdir())
    if previous and not (previous[-1] / 'collection.json').exists():
        raise ValueError('active attempt already exists')
    attempt = len(previous) + 1
    if attempt > manifest['adapter']['max_attempts']:
        raise ValueError('attempt budget exhausted')
    receipt = receipt_record(receipt_path, 'start', case_id, attempt, actor)
    if receipt['adapter'] != manifest['adapter']['name']:
        raise ValueError('receipt adapter does not match frozen configuration')
    if receipt['event_id'] in event_ids(run):
        raise ValueError('duplicate host event')
    directory = attempts / f'{attempt:04d}'
    directory.mkdir()
    (directory / 'outputs').mkdir()
    write(directory / 'start.json', {'actor': actor, 'attempt': attempt, 'receipt': receipt,
        'manifest_hash': digest((run / 'manifest.json').read_bytes())})
    return directory


def get_attempt(run, case_id, attempt):
    run, manifest, attempts = context(run, case_id)
    if type(attempt) is not int or attempt < 1:
        raise ValueError('positive attempt required')
    directory = attempts / f'{attempt:04d}'
    start = validate_start(run, manifest, directory, case_id)
    return run, manifest, directory, start


def collect(run, case_id, attempt, receipt_path, status=None):
    run, manifest, directory, start = get_attempt(run, case_id, attempt)
    if (directory / 'collection.json').exists():
        raise FileExistsError('collection record already exists')
    receipt = receipt_record(receipt_path, 'complete', case_id, attempt, start['actor'])
    status = status or receipt.get('status')
    if status not in ('produced', 'infra_error', 'blocked') or receipt.get('status') != status:
        raise ValueError('completion status mismatch')
    if receipt['adapter'] != start['receipt']['adapter'] or receipt['adapter'] != manifest['adapter']['name']:
        raise ValueError('completion adapter mismatch')
    if receipt['event_id'] in event_ids(run):
        raise ValueError('duplicate host event')
    result = {'status': status, 'receipt': receipt, 'output_hashes': hashes(directory / 'outputs')}
    write(directory / 'collection.json', result)
    return result


def validate_grade(grade, criteria, case_id, attempt, worker, output_hashes):
    grade = object_record(grade)
    if not nonempty(grade.get('grader')) or grade['grader'] == worker:
        raise ValueError('independent grader required')
    if grade.get('case_id') != case_id or type(grade.get('attempt')) is not int or grade['attempt'] != attempt:
        raise ValueError('grade does not match attempt')
    if grade.get('output_hashes') != output_hashes or not output_hashes:
        raise ValueError('grade must bind nonempty collected outputs')
    checks = grade.get('checks')
    if not isinstance(checks, list) or len(checks) != len(criteria):
        raise ValueError('exact required checks must be graded')
    names = [object_record(c).get('criterion') for c in checks]
    if not all(map(nonempty, names)):
        raise ValueError('criterion strings required')
    if len(set(names)) != len(names) or set(names) != set(criteria):
        raise ValueError('checks must match frozen rubric')
    for check in checks:
        evidence = check.get('evidence')
        if check.get('verdict') not in ('pass', 'fail', 'ungradable'):
            raise ValueError('invalid check verdict')
        if not isinstance(evidence, list) or not evidence or not all(map(nonempty, evidence)):
            raise ValueError('every check needs evidence locations or missing-evidence explanation')
        refs = check.get('artifact_refs')
        if refs is not None:
            if not isinstance(refs, list) or not all(isinstance(ref, str) for ref in refs):
                raise ValueError('artifact_refs must be relative output paths')
            for ref in refs:
                if str(safe_relative(ref)) not in output_hashes:
                    raise ValueError('unknown artifact reference')
        else:
            refs = [item.split(':', 1)[0] for item in evidence if item.split(':', 1)[0] in output_hashes]
        if check['verdict'] == 'pass' and not refs:
            raise ValueError('passing check requires a collected output artifact reference')


def grade_attempt(run, case_id, attempt, grade_path):
    run, manifest, directory, start = get_attempt(run, case_id, attempt)
    collection = validate_collection(read(directory / 'collection.json'), start, case_id)
    if collection['status'] != 'produced':
        raise ValueError('only produced artifacts can be graded')
    current = hashes(directory / 'outputs')
    if current != collection['output_hashes']:
        raise ValueError('outputs changed after collection')
    grade = read(grade_path)
    validate_grade(grade, read(run / 'rubric.json')['criteria'][case_id], case_id, attempt, start['actor'], current)
    write(directory / 'grade.json', grade)
    return grade


def report(run):
    run = Path(run)
    failures = (ValueError, OSError, KeyError, TypeError)
    try:
        manifest, errors = verify_run(run)
        event_ids(run)
    except failures as exc:
        try:
            expected = len(object_record(read(run / 'tasks.json'))['cases'])
        except failures:
            expected = None
        return {'expected': expected, 'passed': 0, 'first_pass': 0, 'complete': False,
                'integrity_errors': [str(exc)], 'cases': []}
    criteria = read(run / 'rubric.json')['criteria']
    results = []
    for cid in manifest['expected_cases']:
        attempts = []
        try:
            directories = sorted((run / 'cases' / cid / 'attempts').iterdir())
        except OSError as exc:
            errors.append(cid + ': ' + str(exc))
            directories = []
        for directory in directories:
            result = {'attempt': directory.name, 'status': 'not_collected', 'passed': False}
            try:
                start = validate_start(run, manifest, directory, cid)
                collection = validate_collection(read(directory / 'collection.json'), start, cid)
                result['status'] = collection['status']
                if hashes(directory / 'outputs') != collection['output_hashes']:
                    raise ValueError('outputs changed after collection')
                if collection['status'] == 'produced':
                    result['status'] = 'ungraded'
                    grade = read(directory / 'grade.json')
                    validate_grade(grade, criteria[cid], cid, start['attempt'], start['actor'], collection['output_hashes'])
                    result['passed'] = not errors and manifest['adapter']['name'] == 'host' and all(c['verdict'] == 'pass' for c in grade['checks'])
                    result['status'] = 'passed' if result['passed'] else 'not_passed'
            except failures as exc:
                result['reason'] = str(exc)
            attempts.append(result)
        results.append({'case_id': cid, 'attempts': attempts, 'passed': bool(attempts) and attempts[-1]['passed'],
                        'first_pass': bool(attempts) and attempts[0]['passed']})
    passed = sum(r['passed'] for r in results)
    return {'revision': manifest['revision'], 'expected': len(results), 'passed': passed,
        'first_pass': sum(r['first_pass'] for r in results), 'complete': bool(results) and passed == len(results) and not errors,
        'integrity_errors': errors, 'cases': results, 'evidence_scope': 'host-reported model tasks, not backend attestation or production success'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('prepare')
    p.add_argument('--repo', type=Path, default=ROOT)
    p.add_argument('--revision', required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--dev-eval', action='store_true',
                   help='explicitly enable synthetic development evaluation (never ordinary task routing)')
    for flag in ('tasks', 'rubric', 'fixture-root', 'adapter'):
        p.add_argument('--' + flag, type=Path)
    for name in ('record-start', 'collect', 'grade', 'report'):
        p = sub.add_parser(name)
        p.add_argument('--run', type=Path, required=True)
        if name == 'report':
            p.add_argument('--require-complete', action='store_true')
        if name != 'report':
            p.add_argument('--case', required=True)
        if name in ('collect', 'grade'):
            p.add_argument('--attempt', type=int, required=True)
        if name in ('record-start', 'collect'):
            p.add_argument('--receipt', type=Path, required=True)
        if name == 'record-start':
            p.add_argument('--actor', required=True)
        if name == 'collect':
            p.add_argument('--status', choices=('produced', 'infra_error', 'blocked'))
        if name == 'grade':
            p.add_argument('--grade', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'prepare' and not args.dev_eval:
        parser.error('prepare is development-only; pass --dev-eval explicitly')
    try:
        if args.command == 'prepare':
            result = prepare_run(args.repo, args.revision, args.out, args.tasks, args.rubric, args.fixture_root,
                                 read(args.adapter) if args.adapter else None)
        elif args.command == 'record-start':
            result = str(record_start(args.run, args.case, args.actor, args.receipt))
        elif args.command == 'collect':
            result = collect(args.run, args.case, args.attempt, args.receipt, args.status)
        elif args.command == 'grade':
            result = grade_attempt(args.run, args.case, args.attempt, args.grade)
        else:
            result = report(args.run)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if args.command == 'report' and args.require_complete and not result['complete']:
            parser.exit(1)
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        parser.exit(2, str(exc) + '\n')


if __name__ == '__main__':
    main()
