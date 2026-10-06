#!/usr/bin/env python3
"""Bounded same-host benchmark. Inputs are generated in a deleted temp directory.
Python tracemalloc peak is NOT process RSS. Runtime repetitions exclude tracing
for the graph to avoid distorting its allocation-heavy implementation.
"""
import argparse
import hashlib
import importlib.util
import json
import platform
import statistics
import tempfile
import time
import tracemalloc
from pathlib import Path


def load(path):
    spec = importlib.util.spec_from_file_location('bench_validator', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture(path, digest, tasks):
    return dict(schema_version=1, run_id='bench', role='code-organization',
                input_version='synthetic-scaling-v1', status='completed', limitations=[],
                artifacts=[dict(id='data', path=path, sha256=digest)],
                checks=[dict(criterion='generated fixture integrity', status='pass', artifact_ids=['data'])],
                tasks=tasks)


def measure(module, record, root, request, trace):
    if trace:
        tracemalloc.start()
    started = time.perf_counter()
    errors = module.validate(record, root, True, consumer_request=request)
    seconds = time.perf_counter() - started
    peak = tracemalloc.get_traced_memory()[1] if trace else None
    if trace:
        tracemalloc.stop()
    if errors:
        raise RuntimeError(errors)
    return {'seconds': seconds, 'python_peak_bytes': peak, 'errors': errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--validator', type=Path, required=True)
    parser.add_argument('--file-mib', type=int, default=64)
    parser.add_argument('--chain', type=int, default=6000)
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if not (1 <= args.file_mib <= 128 and 1 <= args.chain <= 10000 and 3 <= args.repeats <= 5):
        parser.error('budget: file<=128MiB, chain<=10000, 3..5 repetitions')
    module = load(args.validator)
    result = {'validator_sha256': hashlib.sha256(args.validator.read_bytes()).hexdigest(),
              'environment': {'python': platform.python_version(), 'implementation': platform.python_implementation(),
                              'platform': platform.platform(), 'processor': platform.processor()},
              'parameters': {'file_mib': args.file_mib, 'chain': args.chain, 'repeats': args.repeats},
              'scope': 'synthetic CPU local validator; page-cache uncontrolled; tracemalloc is not RSS; no model performance'}
    with tempfile.TemporaryDirectory(prefix='handoff-scaling-') as directory:
        root = Path(directory)
        block = bytes(range(256)) * 4096
        digest = hashlib.sha256()
        with (root / 'large.bin').open('wb') as stream:
            for _ in range(args.file_mib):
                stream.write(block)
                digest.update(block)
        request = {'schema_version': 1, 'input_version': 'synthetic-scaling-v1', 'tasks': []}
        large = fixture('large.bin', digest.hexdigest(), [])
        result['file_runs'] = [measure(module, large, root, request, True) for _ in range(args.repeats)]
        (root / 'small.bin').write_bytes(b'fixed')
        tasks = [{'task_id': str(i), 'status': 'done', 'evidence': ['data'],
                  'depends_on': [str(i - 1)] if i else []} for i in range(args.chain)]
        request['tasks'] = [{'task_id': t['task_id']} for t in tasks]
        chain = fixture('small.bin', hashlib.sha256(b'fixed').hexdigest(), tasks)
        result['chain_runs'] = [measure(module, chain, root, request, False) for _ in range(args.repeats)]
    result['file_peak_median_bytes'] = statistics.median(r['python_peak_bytes'] for r in result['file_runs'])
    result['file_seconds_median'] = statistics.median(r['seconds'] for r in result['file_runs'])
    result['chain_seconds_median'] = statistics.median(r['seconds'] for r in result['chain_runs'])
    args.out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: result[key] for key in ('validator_sha256', 'file_peak_median_bytes', 'file_seconds_median', 'chain_seconds_median')}))


if __name__ == '__main__':
    main()
