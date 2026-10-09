#!/usr/bin/env python3
"""Emit an explicit composed prompt to stdout for a host model runner."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_runtime.prompt_context import compose_entries

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', required=True)
    p.add_argument('--entries', nargs='+', default=['decision','general','research'])
    p.add_argument('--keep-duplicates', action='store_true')
    p.add_argument('--max-chars', type=int, default=100000)
    p.add_argument('--json', action='store_true')
    a = p.parse_args()
    result = compose_entries(a.root, a.entries, deduplicate=not a.keep_duplicates, max_chars=a.max_chars)
    print(json.dumps(result, ensure_ascii=False) if a.json else result['prompt'])

if __name__ == '__main__':
    main()
