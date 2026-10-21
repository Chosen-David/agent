import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_runtime.record_context import record_view
from agent_runtime.context_serialization import configure_utf8_output, render_cli_context


def main():
    configure_utf8_output()
    p = argparse.ArgumentParser(description='Read-only SHA-bound NDJSON records; host declares all dependencies.')
    p.add_argument('--root', required=True)
    p.add_argument('--path', required=True)
    p.add_argument('--sha256', required=True)
    p.add_argument('--line', action='append', type=int, required=True)
    p.add_argument('--global-line', action='append', type=int, required=True)
    p.add_argument('--max-chars', type=int, default=20000)
    p.add_argument('--compact', action='store_true')
    a = p.parse_args()
    try:
        if not 1 <= a.max_chars <= 1000000:
            raise ValueError('display max_chars must be 1..1000000')
        value = record_view(a.root, a.path, a.sha256, lines=a.line,
                            global_lines=a.global_line, max_chars=1000000)
        print(render_cli_context(value, compact=a.compact, max_chars=a.max_chars))
        return 0
    except (OSError, ValueError, TypeError, RecursionError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
