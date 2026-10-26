#!/usr/bin/env python3
"""Compare two project artifacts without dropping text or trusting a read cache."""
import argparse
import json
import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_runtime.artifact_context import compare_artifacts
from agent_runtime.result_validation import LIMIT, _bytes, _json
from agent_runtime.context_serialization import (ContextBudgetError, configure_utf8_output,
                                                  render_cli_context)


def main(argv=None):
    configure_utf8_output()
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--before', required=True, help='project-relative path/sha256 JSON binding')
    parser.add_argument('--after', required=True, help='project-relative path/sha256 JSON binding')
    parser.add_argument('--full', action='store_true', help='retain both full texts for explicit comparison')
    parser.add_argument('--reuse-identical', action='store_true',
                        help='represent an unchanged target by the complete base in this same packet')
    parser.add_argument('--multi-edit', action='store_true', help='encode separated edits without replaying their unchanged middle')
    parser.add_argument('--max-chars', type=int, default=20000)
    parser.add_argument('--encoding', help='optional explicit tiktoken encoding for whole-packet choice; never inferred from model')
    args=parser.parse_args(argv)
    try:
        if not 1 <= args.max_chars <= LIMIT or args.max_chars <= len(os.linesep):
            raise ContextBudgetError('invalid display budget')
        root=Path(args.root)
        if not root.is_absolute(): raise ValueError('absolute PROJECT_ROOT required')
        root=root.resolve()
        counter=None
        if args.encoding is not None:
            from agent_runtime.handoff_basis import make_token_counter
            counter=make_token_counter(args.encoding)
        result=compare_artifacts(root,_json(_bytes(root,args.before)),_json(_bytes(root,args.after)),
                                 full=args.full,max_chars=args.max_chars-len(os.linesep),reuse_identical=args.reuse_identical,multi_edit=args.multi_edit,token_counter=counter)
        output=render_cli_context(result,compact=True,max_chars=args.max_chars,max_chars_limit=LIMIT)
    except ContextBudgetError as exc:
        print(json.dumps({'error':str(exc)},ensure_ascii=False),file=sys.stderr);return 2
    except (OSError, ValueError) as exc:
        print(json.dumps({'error':str(exc)},ensure_ascii=False));return 1
    print(output);return 0


if __name__=='__main__':raise SystemExit(main())
