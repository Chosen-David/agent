#!/usr/bin/env python3
"""Prepare isolated task inputs. Does NOT invoke a model or grade itself."""
import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def prepare(case, destination):
    destination.mkdir(parents=True, exist_ok=False)
    shutil.copytree((ROOT / case['skill']).parent, destination / 'skill')
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
    args = parser.parse_args()
    cases = json.loads((ROOT / 'evals/tasks.json').read_text())['cases']
    if args.case:
        missing = set(args.case) - {c['id'] for c in cases}
        if missing:
            parser.error('unknown cases: ' + ', '.join(sorted(missing)))
        cases = [c for c in cases if c['id'] in args.case]
    for case in cases:
        print(prepare(case, args.out / case['id']))

if __name__ == '__main__':
    main()
