#!/usr/bin/env python3
"""Compare two project artifacts without dropping text or trusting a read cache."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_runtime.artifact_context import compare_artifacts
from agent_runtime.result_validation import _bytes, _json


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--before', required=True, help='project-relative path/sha256 JSON binding')
    parser.add_argument('--after', required=True, help='project-relative path/sha256 JSON binding')
    parser.add_argument('--full', action='store_true', help='retain both full texts for explicit comparison')
    parser.add_argument('--max-chars', type=int, default=20000)
    args=parser.parse_args(argv)
    try:
        root=Path(args.root)
        if not root.is_absolute(): raise ValueError('absolute PROJECT_ROOT required')
        root=root.resolve()
        result=compare_artifacts(root,_json(_bytes(root,args.before)),_json(_bytes(root,args.after)),
                                 full=args.full,max_chars=args.max_chars)
    except (OSError, ValueError) as exc:
        print(json.dumps({'error':str(exc)},ensure_ascii=False));return 1
    print(json.dumps(result,ensure_ascii=False,separators=(',', ':')));return 0


if __name__=='__main__':raise SystemExit(main())
