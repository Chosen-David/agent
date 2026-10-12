import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_runtime.reference_context import reference_view
from agent_runtime.context_serialization import render_context


def main():
    p = argparse.ArgumentParser(description='Complete SHA-bound references with lossless directory-prefix transport.')
    p.add_argument('--root', required=True)
    p.add_argument('--path', required=True)
    p.add_argument('--sha256', required=True)
    p.add_argument('--full', action='store_true')
    p.add_argument('--compact', action='store_true')
    p.add_argument('--max-chars', type=int, default=20000)
    a = p.parse_args()
    print(render_context(reference_view(a.root, a.path, a.sha256, full=a.full, max_chars=a.max_chars), compact=a.compact))


if __name__ == '__main__':
    main()
