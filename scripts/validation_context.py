#!/usr/bin/env python3
"""Restore an observed validation record; this is not fresh acceptance."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_runtime.validation_context import restore_validation_context


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--path', required=True, help='project-relative saved context record')
    parser.add_argument('--sha256', required=True, help='exact digest from record_ref')
    args = parser.parse_args()
    result = restore_validation_context(args.root, {'path': args.path, 'sha256': args.sha256})
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
