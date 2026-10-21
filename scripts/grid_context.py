import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_runtime.grid_context import grid_view
from agent_runtime.context_serialization import render_context


def main():
    p = argparse.ArgumentParser(description='Complete SHA-bound coordinate grid with exact arithmetic transport.')
    p.add_argument('--root', required=True)
    p.add_argument('--path', required=True)
    p.add_argument('--sha256', required=True)
    p.add_argument('--full', action='store_true')
    p.add_argument('--compact', action='store_true')
    p.add_argument('--max-chars', type=int, default=20000)
    a = p.parse_args()
    try:
        value = grid_view(a.root, a.path, a.sha256, full=a.full,
                          max_chars=a.max_chars)
        print(render_context(value, compact=a.compact))
        return 0
    except (OSError, ValueError, TypeError, RecursionError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
