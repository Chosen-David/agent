#!/usr/bin/env python3
"""Prepare isolated task inputs. Does NOT invoke a model or grade itself."""
import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from agent_runtime.project_docs import guard_write_path

def prepare(case, destination):
    guard_write_path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    source = (ROOT / case['skill']).parent
    def check_children(current, names):
        # copytree calls this before creating each directory; exclude nothing.
        target = destination / 'skill' / Path(current).relative_to(source)
        for name in names:
            guard_write_path(target / name)
        return ()
    shutil.copytree(source, destination / 'skill', ignore=check_children)
    inputs = destination / 'inputs'
    inputs.mkdir()
    for name in case['fixtures']:
        source = (ROOT / 'evals/fixtures' / name).resolve()
        if source.parent != (ROOT / 'evals/fixtures').resolve():
            raise ValueError('fixture must be a direct fixture file')
        shutil.copy2(source, inputs / name)
    (destination / 'outputs').mkdir()
    (destination / 'task.txt').write_text(case['prompt'], encoding='utf-8')
    return destination

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--case', action='append')
    parser.add_argument('--dev-eval', action='store_true')
    args = parser.parse_args()
    if not args.dev_eval:
        parser.error('synthetic fixtures are development-only; pass --dev-eval explicitly')
    try:
        guard_write_path(args.out)
    except (ValueError, OSError) as exc:
        parser.exit(2, str(exc) + '\n')
    cases = json.loads((ROOT / 'evals/tasks.json').read_text(encoding='utf-8'))['cases']
    if args.case:
        missing = set(args.case) - {c['id'] for c in cases}
        if missing:
            parser.error('unknown cases: ' + ', '.join(sorted(missing)))
        cases = [c for c in cases if c['id'] in args.case]
    try:
        for case in cases:
            print(prepare(case, args.out / case['id']))
    except (ValueError, OSError) as exc:
        parser.exit(2, str(exc) + '\n')

if __name__ == '__main__':
    main()
