import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_runtime.reference_context import reference_view
from agent_runtime.context_serialization import configure_utf8_output, render_cli_context


def main():
    configure_utf8_output()
    p = argparse.ArgumentParser(description='Complete SHA-bound references with lossless directory-prefix transport.')
    p.add_argument('--root', required=True)
    p.add_argument('--path', required=True)
    p.add_argument('--sha256', required=True)
    p.add_argument('--full', action='store_true')
    p.add_argument('--compact', action='store_true')
    p.add_argument('--max-chars', type=int, default=20000)
    a = p.parse_args()
    try:
        if not 1 <= a.max_chars <= 1000000:
            raise ValueError('display max_chars must be 1..1000000')
        value = reference_view(a.root, a.path, a.sha256, full=a.full,
                               max_chars=1000000)
        print(render_cli_context(value, compact=a.compact, max_chars=a.max_chars))
        return 0
    except (OSError, ValueError, TypeError, RecursionError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
