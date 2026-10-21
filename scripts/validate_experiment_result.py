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
from agent_runtime.context_serialization import render_context
from agent_runtime.external_json import ExternalJSONError, load_json
from agent_runtime.result_validation import inspect_result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--compact', action='store_true', help='preserve all JSON fields without formatting whitespace')
    parser.add_argument('--contract', required=True, help='controller-owned result contract JSON')
    parser.add_argument('--verifier-adapter', help='explicitly trusted host Python file exporting verify(root, manifest, plan)')
    parser.add_argument('--context-dir', help='opt-in recoverable display; project-relative agent_doc/results/<run_id>/ directory')
    parser.add_argument('--context-compact-storage', action='store_true')
    args = parser.parse_args()
    if args.context_compact_storage and not args.context_dir:
        parser.error('context-compact-storage requires context-dir')
    contract = load_json(args.contract)
    if not isinstance(contract, dict):
        raise ValueError('result contract must be a JSON object')
    verifier = None
    if args.verifier_adapter:
        spec = importlib.util.spec_from_file_location('trusted_experiment_verifier', args.verifier_adapter)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        verifier = module.verify
    result = inspect_result(args.root, contract, verifier)
    display = result
    if args.context_dir:
        from agent_runtime.validation_context import write_validation_context
        display = write_validation_context(args.root, result, args.context_dir, compact_storage=args.context_compact_storage)
    print((render_context(display, compact=True) if args.compact else json.dumps(display, ensure_ascii=False, indent=2, allow_nan=False)))
    return 0 if result['status'] == 'usable-with-scope' else 2


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ExternalJSONError, OSError, ValueError) as exc:
        print(json.dumps({'status': 'error', 'error': str(exc)}, ensure_ascii=False),
              file=sys.stderr)
        raise SystemExit(2)
