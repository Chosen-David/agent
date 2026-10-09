#!/usr/bin/env python3
"""Inspect a bound result; optional adapter is explicitly trusted host Python.

Without a verifier adapter, only provenance is checked and status stays pending.
Never choose an adapter specified by a worker-controlled manifest/plan/report.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_runtime.result_validation import inspect_result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--contract', required=True, help='controller-owned result contract JSON')
    parser.add_argument('--verifier-adapter', help='explicitly trusted host Python file exporting verify(root, manifest, plan)')
    parser.add_argument('--context-dir', help='opt-in recoverable display; project-relative agent_doc/results/<run_id>/ directory')
    args = parser.parse_args()
    verifier = None
    if args.verifier_adapter:
        spec = importlib.util.spec_from_file_location('trusted_experiment_verifier', args.verifier_adapter)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        verifier = module.verify
    result = inspect_result(args.root, json.loads(Path(args.contract).read_text()), verifier)
    display = result
    if args.context_dir:
        from agent_runtime.validation_context import write_validation_context
        display = write_validation_context(args.root, result, args.context_dir)
    print(json.dumps(display, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if result['status'] == 'usable-with-scope' else 2


if __name__ == '__main__':
    raise SystemExit(main())
