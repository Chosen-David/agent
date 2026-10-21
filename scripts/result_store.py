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
from agent_runtime.context_serialization import (ContextBudgetError, configure_utf8_output,
                                                 render_cli_context, render_context)
from agent_runtime.external_json import load_json
from agent_runtime.result_store import METADATA_LIMIT, ResultStore, _json, _read, result_context


def external_object(path):
    value = load_json(path, max_bytes=METADATA_LIMIT)
    if not isinstance(value, dict):
        raise ValueError('JSON object required')
    return value


def main(argv=None):
    configure_utf8_output()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    formatting = parser.add_mutually_exclusive_group()
    formatting.add_argument('--compact', action='store_true', default=None,
                            help='preserve every field; default for retrieval/decision replies')
    formatting.add_argument('--pretty', dest='compact', action='store_false', help='indent complete JSON replies')
    parser.add_argument('--compact-storage', action='store_true', help='compact new immutable registry records; independent of stdout formatting')
    subs = parser.add_subparsers(dest='command', required=True)
    for name in ('search', 'decide'):
        command = subs.add_parser(name)
        command.add_argument('query')
        command.add_argument('--limit', type=int, default=5)
        command.add_argument('--max-scan', type=int, default=200)
        command.add_argument('--max-chars', type=int, default=20000,
                             help='complete display character cap including newline (1..1000000)')
        if name == 'decide':
            command.add_argument('--context', required=True)
            command.add_argument('--verifier-adapter')
            command.add_argument('--explicit-reproduction', action='store_true')
            command.add_argument('--new-claim', action='store_true')
            command.add_argument('--max-age-seconds', type=float)
    showing = subs.add_parser('show')
    showing.add_argument('run_id')
    showing.add_argument('--max-chars', type=int, default=20000)
    register = subs.add_parser('register')
    register.add_argument('--contract', required=True)
    register.add_argument('--historical', action='store_true')
    register.add_argument('--measured-at')
    subs.add_parser('register-history').add_argument('--record', required=True)
    context_command = subs.add_parser('context')
    context_command.add_argument('--contract', required=True)
    context_command.add_argument('--max-chars', type=int, default=20000)
    args = parser.parse_args(argv)
    try:
        bounded = args.command in ('search', 'decide', 'show', 'context')
        if bounded and not 1 <= args.max_chars <= 1000000:
            raise ContextBudgetError('display max_chars must be 1..1000000')
        store = ResultStore(args.root, compact_storage=args.compact_storage)
        if args.command == 'search':
            result = store.search(args.query, limit=args.limit, max_scan=args.max_scan)
        elif args.command == 'show':
            result = store.show(args.run_id)
        elif args.command in ('register', 'context'):
            contract = external_object(args.contract)
            result = (store.register(contract, historical=args.historical, measured_at=args.measured_at)
                      if args.command == 'register' else
                      result_context(_json(_read(store.root, contract['manifest_path'], 16 * 1024 * 1024))))
        elif args.command == 'register-history':
            record = external_object(args.record)
            result = store.register_history(**record)
        else:
            context = external_object(args.context)
            verifier = None
            if args.verifier_adapter:
                spec = importlib.util.spec_from_file_location('trusted_result_reuse_verifier', args.verifier_adapter)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                verifier = module.verify
            result = store.decide(args.query, context,
                         limit=args.limit, max_scan=args.max_scan, verifier=verifier,
                         explicit_reproduction=args.explicit_reproduction, new_claim=args.new_claim,
                         max_age_seconds=args.max_age_seconds)
        compact = bounded if args.compact is None else args.compact
        output = (render_cli_context(result, compact=compact, indent=2, max_chars=args.max_chars)
                  if bounded else render_context(result, compact=compact, indent=2))
        print(output)
        return 0
    except ContextBudgetError as exc:
        print(json.dumps({'status': 'blocked', 'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'status': 'blocked', 'error': str(exc)}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
