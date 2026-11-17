import argparse
import hashlib
import json
from pathlib import Path


PHASES = ('creation', 'discovery', 'maintenance', 'diagnosis', 'execution')


def summarize(record, count_tokens):
    events, checks = record['events'], record['checks']
    if not events or not checks:
        raise ValueError('nonempty events and checks required')
    costs = dict.fromkeys(PHASES, 0)
    observed = set()
    for event in events:
        phase, text = event['phase'], event['text']
        if phase not in costs or not isinstance(text, str) or not text.strip():
            raise ValueError('known phase and actual nonempty transcript required')
        costs[phase] += count_tokens(text)
        observed.add(phase)
    seen, revisions = set(), set()
    detected = missed = errors = false_positives = unverified = defects = 0
    for check in checks:
        revision, case = check['revision'], check['case']
        if not isinstance(revision, str) or not revision.strip() or not isinstance(case, str) or not case.strip():
            raise ValueError('revision and case required')
        key = (revision, case)
        if key in seen:
            raise ValueError('duplicate revision/case; preserve retries in events')
        seen.add(key)
        revisions.add(revision)
        defective, outcome, evidence = check['defective'], check['outcome'], check['evidence']
        if type(defective) is not bool or outcome not in ('pass', 'detected', 'error'):
            raise ValueError('explicit defect label and pass/detected/error required')
        if not isinstance(evidence, str) or not evidence.strip():
            raise ValueError('raw outcome evidence required')
        defects += defective
        errors += outcome == 'error'
        if defective:
            detected += outcome == 'detected'
            missed += outcome == 'pass'
            unverified += outcome == 'error'
        else:
            false_positives += outcome == 'detected'
    missing = sorted(set(PHASES) - observed)
    return {'scope': 'supplied transcript payloads; labels require raw-evidence review',
            'phase_tokens': costs, 'payload_tokens': sum(costs.values()),
            'missing_phases': missing, 'revisions': len(revisions),
            'coverage_complete': not missing and len(revisions) >= 2 and not errors,
            'defects': defects, 'detected': detected, 'missed': missed,
            'errors': errors, 'unverified_defects': unverified,
            'false_positives': false_positives,
            'miss_rate': missed / defects if defects and not unverified else None,
            'end_to_end_savings': None,
            'excluded': ['unrecorded model reasoning and history', 'provider cache billing',
                         'unrecorded work; transcript completeness is not authenticated']}


def main():
    parser = argparse.ArgumentParser(description='Account for recorded verification lifecycle payloads and misses.')
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    import tiktoken
    raw = args.input.read_bytes()
    encoding = tiktoken.get_encoding('o200k_base')
    report = summarize(json.loads(raw), lambda text: len(encoding.encode(text, disallowed_special=())))
    report.update(input_sha256=hashlib.sha256(raw).hexdigest(),
                  encoding=encoding.name, tiktoken_version=tiktoken.__version__)
    with args.output.open('x') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
