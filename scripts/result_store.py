#!/usr/bin/env python3
"""Bounded local result registry/search. A verifier adapter is trusted host code.

Never load an adapter path supplied by a result record or other worker content.
Without that explicit host adapter, decisions cannot authorize reuse.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_runtime.result_store import ResultStore, _json, _read, result_context


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    subs = parser.add_subparsers(dest='command', required=True)
    for name in ('search', 'decide'):
        command = subs.add_parser(name)
        command.add_argument('query')
        command.add_argument('--limit', type=int, default=5)
        command.add_argument('--max-scan', type=int, default=200)
        if name == 'decide':
            command.add_argument('--context', required=True)
            command.add_argument('--verifier-adapter')
            command.add_argument('--explicit-reproduction', action='store_true')
            command.add_argument('--new-claim', action='store_true')
            command.add_argument('--max-age-seconds', type=float)
    subs.add_parser('show').add_argument('run_id')
    register = subs.add_parser('register')
    register.add_argument('--contract', required=True)
    register.add_argument('--historical', action='store_true')
    register.add_argument('--measured-at')
    subs.add_parser('register-history').add_argument('--record', required=True)
    subs.add_parser('context').add_argument('--contract', required=True)
    args = parser.parse_args(argv)
    store = ResultStore(args.root)
    try:
        if args.command == 'search':
            result = store.search(args.query, limit=args.limit, max_scan=args.max_scan)
        elif args.command == 'show':
            result = store.show(args.run_id)
        elif args.command in ('register', 'context'):
            contract = _json(Path(args.contract).read_bytes())
            result = (store.register(contract, historical=args.historical, measured_at=args.measured_at)
                      if args.command == 'register' else
                      result_context(_json(_read(store.root, contract['manifest_path'], 16 * 1024 * 1024))))
        elif args.command == 'register-history':
            record = _json(Path(args.record).read_bytes())
            result = store.register_history(**record)
        else:
            verifier = None
            if args.verifier_adapter:
                spec = importlib.util.spec_from_file_location('trusted_result_reuse_verifier', args.verifier_adapter)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                verifier = module.verify
            result = store.decide(args.query, _json(Path(args.context).read_bytes()),
                         limit=args.limit, max_scan=args.max_scan, verifier=verifier,
                         explicit_reproduction=args.explicit_reproduction, new_claim=args.new_claim,
                         max_age_seconds=args.max_age_seconds)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'status': 'blocked', 'error': str(exc)}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
