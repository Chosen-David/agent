#!/usr/bin/env python3
"""Run existing/new program tests and emit genuine case outcomes; does not call models."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests'))
from scripts.validate_handoff import validate


def summarize(cases):
    """Every observed case stays in the denominator; unknown outcomes fail closed."""
    counts = {key: 0 for key in ('pass', 'fail', 'not_run', 'known_gap')}
    for case in cases:
        outcome = case['outcome']
        counts[outcome if outcome in counts else 'fail'] += 1
    return counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    cases = []
    for filename in ('test_task_runtime.py', 'test_task_runtime_review.py', 'test_crossfeature_runtime.py'):
        spec = importlib.util.spec_from_file_location(Path(filename).stem, ROOT / 'tests' / filename)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module  # Multiprocessing spawn requires importable test class.
        spec.loader.exec_module(module)
        suite = unittest.defaultTestLoader.loadTestsFromModule(module)
        def flatten(suite):
            for test in suite:
                if isinstance(test, unittest.TestSuite):
                    yield from flatten(test)
                else:
                    yield test
        for test in flatten(suite):
            output = io.StringIO()
            result = unittest.TextTestRunner(stream=output, verbosity=2).run(unittest.TestSuite([test]))
            cases.append({'case_id': test.id(), 'mode': 'program',
                          'outcome': 'not_run' if result.skipped else 'pass' if result.wasSuccessful() else 'fail',
                          'sufficient_reason': result.wasSuccessful() and not result.skipped,
                          'actual_log': output.getvalue(),
                          'source_sha256': hashlib.sha256((ROOT / 'tests' / filename).read_bytes()).hexdigest()})
    fixtures = ROOT / 'evals/crossfeature/coordination_inputs'
    record = json.loads((fixtures / 'producer.json').read_text())
    consumer = json.loads((fixtures / 'consumer.json').read_text())
    actual_errors = validate(record, fixtures)
    consumer_errors = validate(record, fixtures, True,
                               expected_input_version=consumer['input_version'])
    cases.append({'case_id': 'consumer_input_version_mismatch', 'mode': 'program',
                  'expected_semantic_decision': 'reject',
                  'actual_integrity_errors': actual_errors,
                  'actual_integrity_accept': not actual_errors,
                  'actual_consumer_errors': consumer_errors,
                  'actual_consumer_accept': not consumer_errors,
                  'producer_version': record['input_version'], 'consumer_version': consumer['input_version'],
                  'outcome': 'pass' if not actual_errors and 'consumer input version mismatch' in consumer_errors else 'fail',
                  'false_negative': not consumer_errors,
                  'sufficient_reason': not actual_errors and 'consumer input version mismatch' in consumer_errors,
                  'reason': 'Trusted consumer version now independently checked; original producer byte integrity remains valid. Historical gap retained in runtime_results.json.'})
    summary = summarize(cases)
    report = {'schema_version': 1, 'skill_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'rubric_sha256': hashlib.sha256((ROOT / 'evals/crossfeature/runtime_followthrough_rubric.json').read_bytes()).hexdigest(),
              'host_model_results': 'not_in_this_program_report', 'summary': summary, 'cases': cases,
              'limitations': ['No semantic model certification.', 'No multi-host/NFS or large clock jump guarantees.',
                              'Terminal done artifact changes are outside runtime guarantee.',
                              'Deterministic holdout cases are distinct from legacy fixtures; not a generalization estimate.']}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(summary))
    return bool(summary['fail'] or summary['not_run'])


if __name__ == '__main__':
    raise SystemExit(main())
