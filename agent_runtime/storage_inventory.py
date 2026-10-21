"""Bounded metadata-only disk inventory; no reads, reclamation or atomic snapshot."""
import argparse
from heapq import heappush, heapreplace
import json
import os
import sys
from pathlib import Path

def inventory(root, *, max_entries=10000, max_directories=1000, top=10):
    if not Path(root).is_absolute():
        raise ValueError('absolute PROJECT_ROOT required')
    supplied = Path(root).absolute()
    if any(p.is_symlink() or getattr(p, 'is_junction', lambda: False)() for p in (supplied, *supplied.parents)):
        raise ValueError('storage root must not traverse links')
    if not supplied.is_dir():
        raise ValueError('existing project directory required')
    root = supplied.resolve()
    for value, ceiling in ((max_entries, 1000000), (max_directories, 100000), (top, 100)):
        if type(value) is not int or not 1 <= value <= ceiling:
            raise ValueError('invalid storage inventory bound')
    pending, directories, entries, files, links, total = [root], 1, 0, 0, 0, 0
    groups, largest = {}, []
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as children:
            for entry in children:
                entries += 1
                if entries > max_entries:
                    raise ValueError('storage inventory entry bound exceeded; narrow root')
                if entry.is_symlink() or getattr(entry, 'is_junction', lambda: False)():
                    links += 1
                    continue
                if entry.is_dir(follow_symlinks=False):
                    directories += 1
                    if directories > max_directories:
                        raise ValueError('storage directory bound exceeded; narrow root')
                    pending.append(Path(entry.path))
                elif entry.is_file(follow_symlinks=False):
                    size = entry.stat(follow_symlinks=False).st_size
                    rel = Path(entry.path).relative_to(root).as_posix()
                    group = ('private-memory' if rel.startswith('.agent-memory/') else
                             'runtime-cache' if rel.startswith(('.agent-runs/', '.cache/', '__pycache__/')) else
                             'results' if rel.startswith('agent_doc/results/') else
                             'markdown' if rel.lower().endswith('.md') else 'other')
                    values = groups.setdefault(group, {'files': 0, 'logical_bytes': 0})
                    values['files'] += 1; values['logical_bytes'] += size
                    files += 1; total += size
                    item = (size, rel)
                    if len(largest) < top:
                        heappush(largest, item)
                    elif item > largest[0]:
                        heapreplace(largest, item)
    return {'schema_version': 'storage-inventory/v1', 'project_root': str(root),
            'files': files, 'directories': directories, 'entries': entries, 'opaque_links': links,
            'logical_bytes': total, 'groups': dict(sorted(groups.items())),
            'largest': [{'path': name, 'logical_bytes': size} for size, name in sorted(largest, reverse=True)],
            'scope': 'metadata observation; concurrent changes are possible; logical sizes exclude link targets and do not measure allocated blocks or reclaimable space; no files read or deleted'}

def main(argv=None):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--max-entries', type=int, default=10000)
    parser.add_argument('--max-directories', type=int, default=1000)
    parser.add_argument('--top', type=int, default=10)
    args = parser.parse_args(argv)
    try:
        result = inventory(args.root, max_entries=args.max_entries, max_directories=args.max_directories, top=args.top)
        print(json.dumps(result, ensure_ascii=False, separators=(',', ':'), allow_nan=False))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({'status': 'blocked', 'error': str(exc)}, ensure_ascii=False, separators=(',', ':')))
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
