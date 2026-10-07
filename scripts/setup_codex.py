#!/usr/bin/env python3
"""Install/sync committed Codex skills and a small managed global instruction block.

Stdlib only. Refuse unowned collisions or local edits before writing anything.
State/backups stay outside the public repository. No models or schedules started.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import time
import zipfile

BEGIN = b'<!-- chosen-agent:begin -->'
END = b'<!-- chosen-agent:end -->'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name('.' + path.name + '.chosen-agent-new')
    with temporary.open('xb') as stream:
        stream.write(data)
    os.replace(temporary, path)


def committed(repo):
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=repo, timeout=60)
    revision = git('rev-parse', 'HEAD').decode().strip()
    roles = json.loads(git('show', revision + ':config/role_registry.json'))['roles']
    paths = {}
    for role in roles:
        name, manifest = role['id'], PurePosixPath(role['skill'])
        if (not re.fullmatch(r'[a-z][a-z0-9-]*', name) or manifest.is_absolute()
                or '..' in manifest.parts or manifest.name != 'SKILL.md'):
            raise ValueError('Unsafe role registry path/name')
        if name in paths:
            raise ValueError('Duplicate role name')
        paths[name] = manifest.parent.as_posix()
    dirty = git('status', '--porcelain', '--', 'config/role_registry.json',
                'templates/codex_global_instructions.md', *paths.values())
    if dirty.strip():
        raise ValueError('Skill/template source is dirty; commit and verify before synchronization')
    archive = zipfile.ZipFile(io.BytesIO(git('-c', 'core.autocrlf=false', '-c', 'core.eol=lf', 'archive', '--format=zip', revision,
        'templates/codex_global_instructions.md', *paths.values())))
    files = {}
    for item in archive.infolist():
        if item.is_dir():
            continue
        if (item.external_attr >> 16) & 0o170000 == 0o120000:
            raise ValueError('Symlink in committed skill; review before installing')
        for name, prefix in paths.items():
            if item.filename.startswith(prefix + '/'):
                relative = PurePosixPath(item.filename[len(prefix) + 1:])
                if relative.is_absolute() or '..' in relative.parts:
                    raise ValueError('Unsafe archive path')
                files[name + '/' + relative.as_posix()] = archive.read(item)
    for name in paths:
        if name + '/SKILL.md' not in files:
            raise ValueError('Skill manifest missing: ' + name)
    template = archive.read('templates/codex_global_instructions.md')
    return revision, paths, files, template


def owned_path(destination, relative):
    relative = PurePosixPath(relative)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('Unsafe installed path')
    path = destination.joinpath(*relative.parts)
    # Reject links before resolving: never modify a symlink's target.
    for candidate in (path, *path.parents):
        if candidate == destination.parent:
            break
        if candidate.is_symlink():
            raise ValueError('Linked skill path requires manual review: ' + str(candidate))
    if not path.resolve().is_relative_to(destination.resolve()):
        raise ValueError('Installed path escapes destination')
    return path


def installed_files(destination, roles):
    result = {}
    for name in roles:
        directory = owned_path(destination, name)
        if directory.exists() and not directory.is_dir():
            raise ValueError('Skill destination is not a directory: ' + name)
        for path in directory.rglob('*'):
            relative = path.relative_to(destination).as_posix()
            owned_path(destination, relative)
            # Python generates these during legitimate knowledge-tool calls.
            if '__pycache__' in path.parts or path.suffix == '.pyc':
                continue
            if path.is_file():
                result[relative] = digest(path.read_bytes())
    return result


def check_file_layout(destination, files):
    """Refuse file/directory transitions and special targets before any writes.

    Ownership hashes describe regular files, so an empty local directory or a
    named pipe does not appear in installed_files. Never try to back up or
    replace those paths as files, or write through an existing file ancestor.
    """
    for relative in sorted(files):
        path = owned_path(destination, relative)
        for parent in path.parents:
            if parent == destination.parent:
                break
            if parent.exists() and not parent.is_dir():
                raise ValueError('Installation layout conflict: parent is not a directory; preserved: ' + str(parent))
        if path.exists() and not path.is_file():
            raise ValueError('Installation layout conflict: target is not a regular file; preserved: ' + str(path))


def merge_instructions(current, block):
    if current.count(BEGIN) != current.count(END) or current.count(BEGIN) > 1:
        raise ValueError('Malformed managed global instruction block')
    if BEGIN in current:
        start, finish = current.index(BEGIN), current.index(END) + len(END)
        if finish < start:
            raise ValueError('Malformed managed global instruction order')
        previous = current[start:finish]
        return current[:start] + block + current[finish:], previous
    return current + (b'\n\n' if current else b'') + block + b'\n', None


def synchronize(repo, destination, state, codex_home, *, adopt=False, check=False):
    repo, destination, state, codex_home = map(lambda p: Path(p).resolve(),
                                               (repo, destination, state, codex_home))
    revision, roles, files, template = committed(repo)
    wanted = {path: digest(data) for path, data in files.items()}
    manifest_path = state / 'installation.json'
    prior = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else None
    if (state/'pending.json').exists():
        raise ValueError('Interrupted sync; inspect pending.json and backups before recovery')
    actual = installed_files(destination, roles)
    if prior:
        if (prior['repository'] != str(repo) or prior['destination'] != str(destination)
                or prior['codex_home'] != str(codex_home) or set(prior['roles']) != set(roles)):
            raise ValueError('Installation location/role ownership changed; preserve for review')
        if actual != prior['files']:
            changed = sorted(k for k in set(actual) | set(prior['files'])
                             if actual.get(k) != prior['files'].get(k))
            raise ValueError('Locally changed installed skill files; preserved: ' + ', '.join(changed[:8]))
    else:
        existing = [name for name in roles if (destination/name).exists()]
        if existing and (not adopt or actual != wanted or len(existing) != len(roles)):
            raise ValueError('Unowned skill collision; explicit --adopt requires an exact committed snapshot')
    check_file_layout(destination, files)
    instruction_path = codex_home/'AGENTS.md'
    if (codex_home/'AGENTS.override.md').is_file():
        raise ValueError('Global AGENTS.override.md shadows integration; preserve and resolve explicitly')
    if instruction_path.is_symlink():
        raise ValueError('Linked global AGENTS.md requires manual review')
    current = instruction_path.read_bytes() if instruction_path.exists() else b''
    block = template.replace(b'{{REPOSITORY}}', repo.as_posix().encode('utf-8')).strip()
    instructions, old_block = merge_instructions(current, block)
    if prior and (old_block is None or digest(old_block) != prior['instruction_block_sha256']):
        raise ValueError('Managed global instructions were edited; preserved')
    if not prior and old_block is not None:
        raise ValueError('Unowned managed instruction block; preserve for review')
    new = {'schema_version': 1, 'repository': str(repo), 'revision': revision,
           'destination': str(destination), 'codex_home': str(codex_home),
           'roles': sorted(roles), 'files': wanted, 'instruction_block_sha256': digest(block)}
    if check:
        if not prior or actual != wanted or instructions != current or prior['revision'] != revision:
            raise ValueError('Installed snapshot is absent or stale; run synchronization between tasks')
        return {'status': 'configured', 'revision': revision, 'skills': len(roles),
                'files': len(files), 'model_probe': 'not_run', 'scheduler': 'not_started'}
    state.mkdir(parents=True, exist_ok=True)
    lock = state/'sync.lock'
    lock.mkdir()  # No stale-lock deletion or concurrent installer.
    try:
        # Recheck ownership under lock. All preflight checks above were read-only.
        if installed_files(destination, roles) != actual or (instruction_path.read_bytes() if instruction_path.exists() else b'') != current:
            raise ValueError('Installation changed during preflight; no files replaced')
        check_file_layout(destination, files)
        changed = {p: data for p, data in files.items() if actual.get(p) != wanted[p]}
        removed = sorted(set(prior['files']) - set(files)) if prior else []
        backup = state/'backups'/str(time.time_ns())
        for relative in [*changed, *removed]:
            path = owned_path(destination, relative)
            if path.exists():
                saved = backup/'skills'/relative
                saved.parent.mkdir(parents=True, exist_ok=True)
                saved.write_bytes(path.read_bytes())
        if current != instructions and instruction_path.exists():
            backup.mkdir(parents=True, exist_ok=True)
            (backup/'AGENTS.md').write_bytes(current)
        atomic(state/'pending.json', json.dumps({'before': prior, 'after': new,
            'backup': str(backup), 'writes': sorted(changed), 'removes': removed}, indent=2).encode())
        for relative, data in changed.items():
            atomic(owned_path(destination, relative), data)
        for relative in removed:
            owned_path(destination, relative).unlink()  # Only unchanged, manifest-owned files.
        if current != instructions:
            atomic(instruction_path, instructions)
        if installed_files(destination, roles) != wanted or instruction_path.read_bytes() != instructions:
            raise ValueError('Post-write verification failed; inspect pending.json and backups')
        atomic(manifest_path, json.dumps(new, ensure_ascii=False, indent=2).encode('utf-8'))
        (state/'pending.json').unlink()
    finally:
        lock.rmdir()
    return {'status': 'configured', 'revision': revision, 'skills': len(roles),
            'files': len(files), 'updated_files': len(changed), 'model_probe': 'not_run',
            'scheduler': 'not_started'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--dest', type=Path, default=Path.home()/'.agents/skills')
    parser.add_argument('--codex-home', type=Path, default=Path(os.environ.get('CODEX_HOME', str(Path.home()/'.codex'))))
    parser.add_argument('--state', type=Path)
    parser.add_argument('--adopt', action='store_true', help='Adopt an exact official-installer snapshot once')
    parser.add_argument('--check', action='store_true', help='Read-only source, installed files and instructions check')
    args = parser.parse_args()
    try:
        result = synchronize(args.repo, args.dest, args.state or args.codex_home/'chosen-agent',
                             args.codex_home, adopt=args.adopt, check=args.check)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(json.dumps({'status': 'blocked', 'reason': str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
