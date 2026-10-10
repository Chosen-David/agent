#!/usr/bin/env python3
"""Print an exact SHA-bound Python symbol view; no execution or writes."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_runtime.result_validation import _bytes, _json
from agent_runtime.source_context import source_context


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', required=True)
    p.add_argument('--request', required=True)
    p.add_argument('--full', action='store_true')
    p.add_argument('--max-chars', type=int, default=20000)
    a = p.parse_args(argv)
    try:
        root = Path(a.root)
        if not root.is_absolute():
            raise ValueError('absolute PROJECT_ROOT required')
        raw = _bytes(root.resolve(strict=True), a.request)
        if len(raw) > 65536:
            raise ValueError('request exceeds byte bound')
        view = source_context(root, _json(raw), full=a.full, max_chars=a.max_chars)
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(view, ensure_ascii=False, separators=(',', ':')))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
