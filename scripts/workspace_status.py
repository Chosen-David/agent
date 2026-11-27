#!/usr/bin/env python3
"""Inspect the current checkout before choosing reuse, isolation or reclamation."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import re
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_runtime.project_docs import guard_write_path
from agent_runtime.external_json import regular_bytes
from agent_runtime.storage_budget import storage_budget


def git(repo, *args):
    return subprocess.check_output(['git', '--no-optional-locks', '-C', str(repo), *args],
                                   stderr=subprocess.PIPE)


RELEASE_REQUIREMENTS = 'requires authoritative owner, process, consumer, recovery and integration checks'


def inspect(repo, revision, intent, source):
    root = Path(os.fsdecode(git(repo, 'rev-parse', '--show-toplevel').rstrip(b'\n'))).resolve()
    target = git(root, 'rev-parse', '--verify', '--end-of-options',
                 revision + '^{commit}').decode().strip()
    head = git(root, 'rev-parse', 'HEAD').decode().strip()
    listing = git(root, 'worktree', 'list', '--porcelain', '-z')
    entries = [record.split(b'\0') for record in listing.split(b'\0\0') if record]
    current = next((fields for fields in entries if fields[0].startswith(b'worktree ')
                    and Path(os.fsdecode(fields[0][9:])).resolve() == root), None)
    gitdir = Path(os.fsdecode(git(root, 'rev-parse', '--absolute-git-dir').rstrip(b'\n')))
    common = Path(os.fsdecode(git(root, 'rev-parse', '--path-format=absolute',
                                  '--git-common-dir').rstrip(b'\n')))
    linked = gitdir.resolve() != common.resolve()
    superproject = os.fsdecode(git(root, 'rev-parse', '--show-superproject-working-tree').rstrip(b'\n'))
    if current is None and superproject and not linked:
        current = next((fields for fields in entries if fields[0].startswith(b'worktree ')
                        and Path(os.fsdecode(fields[0][9:])).resolve() == common.resolve()), None)
    if current is None:
        raise ValueError('current checkout absent from registered worktrees')
    reasons = []
    if intent == 'read':
        action = 'read-commit'
    else:
        status = git(root, 'status', '--porcelain=v1', '-z', '--ignored', '--untracked-files=all')
        if status:
            reasons.append('local changes, untracked or ignored files')
        if any(field.split(b' ', 1)[0] == b'locked' for field in current):
            reasons.append('registered worktree lock')
        if source != 'current-task':
            reasons.append('task ownership unverified or externally managed')
        if intent == 'reclaim':
            reasons.append(RELEASE_REQUIREMENTS)
            action = 'retain'
        elif intent == 'isolate' or head != target:
            action = 'request-host-isolation' if source == 'host' or linked else 'isolation-required'
        elif source == 'current-task' and 'registered worktree lock' not in reasons:
            action = 'review-local-state' if status else 'reuse-current'
        else:
            action = 'use-host' if source == 'host' else 'ownership-required'
    return dict(root=str(root), target=target, head=head, linked=linked, superproject=superproject or None,
                declared_source=source, action=action, reasons=reasons, dry_run=True)


def checkout(status, slot, task, run, sparse, required):
    if (status['action'] != 'isolation-required' or status['declared_source'] != 'current-task'
            or status['linked'] or status['superproject'] or status['reasons']):
        raise ValueError('local isolation requires a clean, task-owned unmanaged checkout')
    if not all(isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9_.-]{1,100}', value)
               for value in (task, run)):
        raise ValueError('task and run identities required')
    root, sha = Path(status['root']), status['target']
    slot = guard_write_path(slot)
    if slot.resolve() != slot or not slot.parent.is_dir() or slot.is_relative_to(root):
        raise ValueError('choose a new external slot under an existing physical parent')
    enclosing = subprocess.run(['git', '-C', str(slot.parent), 'rev-parse', '--git-dir'],
                               capture_output=True)
    if enclosing.returncode == 0 or any(p.name == '.git' for p in slot.parents):
        raise ValueError('isolation slot cannot be inside another repository')
    if sparse and not required:
        raise ValueError('sparse checkout requires explicit build/test/config dependency paths')
    for name in [*sparse, *required]:
        if (not name or name.startswith('-') or Path(name).is_absolute()
                or any(part in ('', '.', '..') for part in name.split('/')) or chr(92) in name):
            raise ValueError('canonical relative dependency path required')
    listing = git(root, 'ls-tree', '-r', '-l', '-z', sha)
    files = {}
    directories = set()
    cones = [Path(name) for name in sparse]
    for record in listing.split(b'\0'):
        if record:
            info, raw_name = record.split(b'\t', 1)
            fields = info.split()
            name = Path(os.fsdecode(raw_name))
            parent = name.parent
            if fields[1] != b'blob':
                continue
            if cones and not any(parent.is_relative_to(cone) or cone.is_relative_to(parent) for cone in cones):
                continue
            files[name] = int(fields[3])
            directories.update(name.parents)
    volume = storage_budget(slot.parent, {'allocations': {'checkout': {
        'disk_bytes': sum(files.values()), 'inodes': len(files) + len(directories), 'cpu_bytes': 0, 'pinned_bytes': 0}},
        'phases': [['checkout']]})
    if volume['status'] != 'fits':
        raise ValueError('checkout capacity insufficient or unknown')
    slot.mkdir(mode=0o700)
    tree = slot / 'tree'
    event = dict(task=task, run=run, owner='local-cli', source=str(root), target=str(tree),
                 revision=sha, reason='explicit unmanaged isolation', budget=volume)
    started = time.monotonic()
    def process_io():
        try:
            values = dict(line.split(':', 1) for line in Path('/proc/self/io').read_text().splitlines())
            return {key: int(values[key]) for key in ('write_bytes', 'syscw')}
        except (OSError, KeyError, ValueError):
            return None
    initial_io = process_io()
    def record(action):
        with (slot / 'events.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(dict(event, action=action, elapsed_seconds=time.monotonic()-started)) + '\n')
            stream.flush()
            os.fsync(stream.fileno())
    record('creating')
    try:
        git(root, 'worktree', 'add', '--detach', '--no-checkout', '--', str(tree), sha)
        if sparse:
            git(tree, 'sparse-checkout', 'set', '--cone', '--', *sparse)
        git(tree, 'read-tree', '-mu', 'HEAD')
        for name in required:
            path = tree / name
            if not path.resolve().is_relative_to(tree) or not path.is_file():
                raise ValueError('missing checkout dependency: ' + name)
        logical, allocated = 0, 0
        for name in files:
            info = (tree / name).lstat()
            logical += info.st_size
            if allocated is not None:
                allocated = allocated + info.st_blocks * 512 if hasattr(info, 'st_blocks') else None
        final_io = process_io()
        event.update(tracked_logical_bytes=logical, observed_tracked_allocated_bytes=allocated,
                     tracked_stat_count=len(files), worktrees_created=1,
                     linux_process_and_waited_children_io=(
                         {key: final_io[key] - initial_io[key] for key in initial_io}
                         if initial_io is not None and final_io is not None else None))
        record('created')
    except (OSError, ValueError, subprocess.CalledProcessError):
        record('failed-pending')
        raise
    return dict(event, action='created', dry_run=False)


def trusted_module(path):
    spec = importlib.util.spec_from_file_location('trusted_workspace_owner', path)
    if spec is None or spec.loader is None:
        raise ValueError('invalid workspace lease adapter')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def release_review(status, task, run, merged_into, provider):
    tree = Path(status['root'])
    reasons = [reason for reason in status['reasons'] if reason != RELEASE_REQUIREMENTS]
    if not status['linked'] or status['declared_source'] != 'current-task':
        reasons.append('local creation provenance required')
    if not reasons:
        raw = regular_bytes(tree.parent / 'events.jsonl', max_bytes=32768)
        events = [json.loads(line) for line in raw.splitlines()]
        if ([event.get('action') for event in events] != ['creating', 'created']
                or not all(event.get('task') == task and event.get('run') == run and
                           event.get('owner') == 'local-cli' and event.get('target') == str(tree)
                           for event in events)):
            reasons.append('creation receipt mismatch')
    if not reasons:
        base = git(tree, 'rev-parse', '--verify', '--end-of-options', merged_into + '^{commit}').decode().strip()
        merged = subprocess.run(['git', '-C', str(tree), 'merge-base', '--is-ancestor', status['head'], base])
        if merged.returncode:
            reasons.append('integration not established')
        facts = provider.release_facts(tree, task, run)
        if not isinstance(facts, dict) or facts.get('owner_verified') is not True:
            reasons.append('live owner unverified')
        for key in ('active_processes', 'tasks', 'consumers', 'recovery_dependencies', 'locks'):
            if not isinstance(facts, dict) or facts.get(key) != []:
                reasons.append('active or unknown ' + key)
    return dict(status, action='retain' if reasons else 'candidate-for-review', reasons=reasons)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--revision', default='HEAD')
    parser.add_argument('--intent', choices=('read', 'develop', 'isolate', 'reclaim'), required=True)
    parser.add_argument('--source', choices=('current-task', 'host', 'user', 'unknown'), default='unknown')
    parser.add_argument('--create-local-slot', type=Path, help='explicit new unmanaged isolation only')
    parser.add_argument('--lease-adapter', type=Path, help='trusted host provider of an exclusive task/workspace lease')
    parser.add_argument('--merged-into', help='integration revision for an owned worktree release review')
    parser.add_argument('--task')
    parser.add_argument('--run')
    parser.add_argument('--sparse-dir', action='append', default=[])
    parser.add_argument('--require-file', action='append', default=[])
    args = parser.parse_args()
    try:
        result = inspect(args.repo, args.revision, args.intent, args.source)
        if args.intent == 'reclaim' and args.lease_adapter and args.merged_into:
            result = release_review(result, args.task, args.run, args.merged_into,
                                    trusted_module(args.lease_adapter))
        if args.create_local_slot:
            if args.intent != 'isolate':
                raise ValueError('creation requires isolate intent')
            if result['action'] != 'isolation-required' or args.lease_adapter is None:
                raise ValueError('local isolation requires a compatible workspace and live owner lease')
            module = trusted_module(args.lease_adapter)
            with module.lease(Path(result['root']), args.create_local_slot, args.task, args.run) as grant:
                if grant is not True:
                    raise ValueError('task ownership or active workspace conflict')
                result = inspect(args.repo, args.revision, args.intent, args.source)
                result = checkout(result, args.create_local_slot, args.task, args.run,
                                  args.sparse_dir, args.require_file)
        print(json.dumps(result))
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        parser.exit(2, str(exc) + '\n')


if __name__ == '__main__':
    main()
