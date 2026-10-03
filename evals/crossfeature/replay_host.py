#!/usr/bin/env python3
"""Replay archived receipts and hashes; never invent/re-run model turns."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import tarfile
import tempfile


def replay(archive):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        with tarfile.open(archive, 'r:gz') as stream:
            stream.extractall(root, filter='data')
        implementations = {}
        for source in (root/'recorders').glob('*.py'):
            spec = importlib.util.spec_from_file_location('frozen_'+source.stem, source)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            implementations[hashlib.sha256(source.read_bytes()).hexdigest()] = module
        reports = {}
        for run in sorted((root/'runs').iterdir()):
            manifest = json.loads((run/'manifest.json').read_text())
            implementation = implementations[manifest['implementation_hash']]
            reports[run.name] = implementation.report(run)
        return reports


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    result = replay(args.archive)
    print(json.dumps(result, indent=2))
    # Failed role criteria are data, not corruption. Integrity failure is fatal.
    raise SystemExit(any(r['integrity_errors'] for r in result.values()))
