#!/usr/bin/env python3
"""Print an exact SHA-bound Python symbol view; no execution or writes."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_runtime.result_validation import _bytes, _json
from agent_runtime.context_serialization import (ContextBudgetError, configure_utf8_output,
                                                  render_cli_context)
from agent_runtime.source_context import source_context


def main(argv=None):
    configure_utf8_output()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', required=True)
    p.add_argument('--request', required=True)
    p.add_argument('--full', action='store_true')
    p.add_argument('--max-chars', type=int, default=20000)
    a = p.parse_args(argv)
    try:
        if not 1 <= a.max_chars <= 100000:
            raise ContextBudgetError('invalid display budget')
        root = Path(a.root)
        if not root.is_absolute():
            raise ValueError('absolute PROJECT_ROOT required')
        raw = _bytes(root.resolve(strict=True), a.request)
        if len(raw) > 65536:
            raise ValueError('request exceeds byte bound')
        view = source_context(root, _json(raw), full=a.full, max_chars=100000)
        output = render_cli_context(view, compact=True, max_chars=a.max_chars, max_chars_limit=100000)
    except ContextBudgetError as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False))
        return 1
    print(output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
